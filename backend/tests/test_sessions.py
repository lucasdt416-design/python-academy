"""Server-side sessions (backlog SEC-03): logout, expiry, forged cookies, deleted users, routes."""
import os
import tempfile
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + tempfile.mktemp(suffix='.db'))
os.environ.setdefault('SESSION_SECRET', 'test-secret-that-is-at-least-thirty-two-characters')
import base64
import json
import logging
import secrets

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import sessions
from app.db import Event, UserSession
from app.main import Base, User, app, engine, oauth

client = TestClient(app)
HEADERS = {'origin': 'http://localhost:3000'}
EMAIL = 'learner@example.com'
HOUR = 3600


class Clock:
    def __init__(self):
        self.now = 1_800_000_000.0

    def __call__(self):
        return self.now


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    client.cookies.clear()
    clock = Clock()
    monkeypatch.setattr(sessions, 'clock', clock)
    return clock


def sign_cookie(payload, secret=None):
    # Signed exactly as Starlette's SessionMiddleware signs it.
    return TimestampSigner(secret or os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps(payload).encode())).decode()


def read_cookie(value):
    return json.loads(base64.b64decode(value.split('.')[0]))


def use_cookie(value):
    client.cookies.clear()
    client.cookies.set('session', value, domain='testserver.local', path='/')


def google_sign_in(monkeypatch, sub='google-sub', email=EMAIL, role=None):
    """The real callback route, with only Google's answer replaced."""
    async def verified(request):
        return {'userinfo': {'sub': sub, 'email': email, 'email_verified': True}}
    monkeypatch.setattr(oauth.google, 'authorize_access_token', verified)
    assert client.get('/auth/google/callback', follow_redirects=False).status_code == 307
    if role:
        with Session(engine) as db:
            db.scalar(select(User).where(User.subject == sub)).role = role
            db.commit()
    return client.cookies.get('session')


def me():
    return client.get('/api/me').status_code


def rows():
    with Session(engine) as db:
        return list(db.scalars(select(UserSession)))


# The cookie and the stored row

def test_the_cookie_holds_only_a_random_session_id(monkeypatch):
    cookie = google_sign_in(monkeypatch)
    payload = read_cookie(cookie)
    assert set(payload) == {'sid'}
    assert len(payload['sid']) >= 43  # 32 random bytes
    assert EMAIL not in json.dumps(payload)
    [row] = rows()
    # The table stores a digest of the ID, never the ID the browser sends.
    assert row.id == sessions.digest(payload['sid']) and row.id != payload['sid']
    assert row.created == row.last_seen == int(sessions.clock())
    assert row.expires == row.created + sessions.ABSOLUTE


def test_a_copy_of_the_sessions_table_cannot_be_used_as_a_cookie(monkeypatch):
    google_sign_in(monkeypatch)
    [row] = rows()
    use_cookie(sign_cookie({'sid': row.id}))
    assert me() == 401


# Logout

def test_logout_makes_the_old_cookie_stop_working_at_once(monkeypatch):
    cookie = google_sign_in(monkeypatch)
    assert me() == 200
    assert client.post('/api/logout', json={}, headers=HEADERS).json() == {'ok': True}
    assert me() == 401
    # Someone who copied the cookie before logout cannot use it.
    use_cookie(cookie)
    assert me() == 401
    assert client.get('/api/history').status_code == 401
    assert rows() == []
    with Session(engine) as db:
        assert [e.action for e in db.scalars(select(Event).order_by(Event.id))] == ['signed_in', 'signed_out']


def test_logout_ends_only_this_browsers_session(monkeypatch):
    phone = google_sign_in(monkeypatch)
    client.cookies.clear()
    laptop = google_sign_in(monkeypatch)
    client.post('/api/logout', json={}, headers=HEADERS)
    use_cookie(phone)
    assert me() == 200
    use_cookie(laptop)
    assert me() == 401


def test_signing_in_again_replaces_the_browsers_session(monkeypatch):
    first = google_sign_in(monkeypatch)
    second = google_sign_in(monkeypatch)
    assert read_cookie(first)['sid'] != read_cookie(second)['sid']
    assert len(rows()) == 1
    use_cookie(first)
    assert me() == 401


def test_logout_without_a_session_is_harmless():
    assert client.post('/api/logout', json={}, headers=HEADERS).json() == {'ok': True}
    use_cookie(sign_cookie({'sid': 'not-a-real-session'}))
    assert client.post('/api/logout', json={}, headers=HEADERS).json() == {'ok': True}


# Expiry

def test_a_session_ends_after_seven_days_even_if_used_all_the_time(monkeypatch, clock):
    google_sign_in(monkeypatch)
    start = clock.now
    while clock.now + 12 * HOUR < start + sessions.ABSOLUTE:
        clock.now += 12 * HOUR
        assert me() == 200
    clock.now = start + sessions.ABSOLUTE
    assert me() == 401
    assert rows() == []


def test_a_session_ends_after_24_hours_unused(monkeypatch, clock):
    google_sign_in(monkeypatch)
    clock.now += sessions.IDLE - 1
    assert me() == 200            # used just in time, so the idle clock restarts
    clock.now += sessions.IDLE - 1
    assert me() == 200
    clock.now += sessions.IDLE
    assert me() == 401
    assert rows() == []


def test_last_seen_is_written_at_most_every_five_minutes(monkeypatch, clock):
    google_sign_in(monkeypatch)
    signed_in = clock.now
    clock.now += sessions.TOUCH_EVERY - 1
    assert me() == 200
    assert rows()[0].last_seen == signed_in
    clock.now += 1
    assert me() == 200
    assert rows()[0].last_seen == clock.now


def test_expired_sessions_are_deleted_at_the_next_sign_in(monkeypatch, clock):
    google_sign_in(monkeypatch, sub='a', email='a@example.com')
    client.cookies.clear()
    google_sign_in(monkeypatch, sub='b', email='b@example.com')
    clock.now += sessions.IDLE
    client.cookies.clear()
    google_sign_in(monkeypatch, sub='c', email='c@example.com')
    with Session(engine) as db:
        assert [db.get(User, r.user_id).email for r in rows()] == ['c@example.com']


# Forged and tampered cookies

def make_user(role='student'):
    with Session(engine) as db:
        user = User(subject=EMAIL, email=EMAIL, role=role)
        db.add(user)
        db.commit()
        return user.id


def real_sid(uid):
    token = secrets.token_urlsafe(32)
    now = int(sessions.clock())
    with Session(engine) as db:
        db.add(UserSession(id=sessions.digest(token), user_id=uid, created=now, last_seen=now, expires=now + sessions.ABSOLUTE))
        db.commit()
    return token


def tamper(cookie):
    # Change one character of the payload, keeping the signature.
    data, rest = cookie.split('.', 1)
    return data[:5] + ('A' if data[5] != 'A' else 'B') + data[6:] + '.' + rest


@pytest.mark.parametrize('forge', [
    pytest.param(lambda uid, sid: sign_cookie({'uid': uid}), id='old-cookie-with-a-user-id'),
    pytest.param(lambda uid, sid: sign_cookie({'sid': secrets.token_urlsafe(32)}), id='made-up-session-id'),
    pytest.param(lambda uid, sid: sign_cookie({'sid': sid}, secret='another-secret-of-at-least-32-chars!!'), id='wrong-signing-key'),
    pytest.param(lambda uid, sid: tamper(sign_cookie({'sid': sid})), id='tampered-payload'),
    pytest.param(lambda uid, sid: base64.b64encode(json.dumps({'sid': sid}).encode()).decode(), id='unsigned'),
    pytest.param(lambda uid, sid: sign_cookie({'sid': [sid]}), id='session-id-not-a-string'),
    pytest.param(lambda uid, sid: sign_cookie({'sid': sid, 'uid': uid})[:-3] + 'xyz', id='bad-signature'),
])
def test_forged_or_tampered_cookies_are_refused(forge):
    uid = make_user()
    sid = real_sid(uid)
    use_cookie(forge(uid, sid))
    assert me() == 401
    assert client.get('/api/progress').status_code == 401
    assert client.post('/api/attempts', json={'lesson_id': 'hello', 'code': '', 'output': ''}, headers=HEADERS).status_code == 401
    # The genuine session still works.
    use_cookie(sign_cookie({'sid': sid}))
    assert me() == 200


def test_an_old_cookie_with_a_user_id_is_refused_and_emptied():
    # Everyone signed in before SEC-03 has such a cookie; they are signed out once at deploy.
    use_cookie(sign_cookie({'uid': make_user()}))
    response = client.get('/api/me')
    assert response.status_code == 401
    assert 'session=null' in response.headers['set-cookie']


# Deleted users

def test_a_deleted_users_sessions_stop_working(monkeypatch):
    cookie = google_sign_in(monkeypatch, role='student')
    assert client.get('/api/progress').status_code == 200
    with Session(engine) as db:
        db.execute(delete(Event))
        db.execute(delete(User))
        db.commit()
    use_cookie(cookie)
    assert me() == 401
    assert client.get('/api/progress').status_code == 401
    assert rows() == []


# Every route is either public or checks the session

PUBLIC = {
    ('GET', '/health'), ('GET', '/auth/google'), ('GET', '/auth/google/callback'),
    ('POST', '/api/logout'), ('GET', '/api/lessons'), ('GET', '/api/catalog'),
    ('GET', '/api/goals'), ('POST', '/api/check'), ('GET', '/api/checks/{lesson_id}'),
}
ATTEMPT = {'lesson_id': 'hello', 'code': 'print("A forest.")\nprint("A dragon!")', 'output': 'A forest.\nA dragon!\n'}
# (role that may use it, a valid request body)
AUTHENTICATED = {
    ('GET', '/api/me'): ('pending', None),
    ('GET', '/api/history'): ('pending', None),
    ('POST', '/api/enroll'): ('pending', {'birthday': '1990-01-01'}),
    ('POST', '/api/invitations'): ('parent', {'email': 'kid@example.com'}),
    ('GET', '/api/family'): ('parent', None),
    ('GET', '/api/goal'): ('student', None),
    ('POST', '/api/goal'): ('student', {'goal': None}),
    ('GET', '/api/recommendation'): ('student', None),
    ('GET', '/api/awards'): ('student', None),
    ('POST', '/api/attempts'): ('student', ATTEMPT),
    ('GET', '/api/progress'): ('student', None),
}


def send(method, path, body):
    return client.request(method, path, json=body, headers=HEADERS)


def test_every_route_is_listed_as_public_or_authenticated():
    # A new route fails here until it is added to one list. Adding it to AUTHENTICATED makes the
    # next test prove it refuses requests without a live session.
    routes = {(m, r.path) for r in app.routes if isinstance(r, APIRoute) for m in r.methods - {'HEAD'}}
    assert routes == PUBLIC | AUTHENTICATED.keys()


@pytest.mark.parametrize('route', sorted(AUTHENTICATED), ids=lambda r: f'{r[0]} {r[1]}')
def test_authenticated_routes_refuse_requests_without_a_live_session(route, clock):
    method, path = route
    role, body = AUTHENTICATED[route]
    uid = make_user(role)
    # No cookie, an old pre-SEC-03 cookie, a logged-out session, an expired one.
    client.cookies.clear()
    assert send(method, path, body).status_code == 401
    use_cookie(sign_cookie({'uid': uid}))
    assert send(method, path, body).status_code == 401
    use_cookie(sign_cookie({'sid': real_sid(uid)}))
    client.post('/api/logout', json={}, headers=HEADERS)
    assert send(method, path, body).status_code == 401
    use_cookie(sign_cookie({'sid': real_sid(uid)}))
    clock.now += sessions.IDLE
    assert send(method, path, body).status_code == 401


@pytest.mark.parametrize('route', sorted(AUTHENTICATED), ids=lambda r: f'{r[0]} {r[1]}')
def test_authenticated_routes_still_work_with_a_live_session(route):
    method, path = route
    role, body = AUTHENTICATED[route]
    use_cookie(sign_cookie({'sid': real_sid(make_user(role))}))
    response = send(method, path, body)
    assert response.status_code == 200, response.text


# Logs

def test_sessions_never_log_ids_cookies_emails_or_user_ids(monkeypatch, clock, caplog):
    caplog.set_level(logging.DEBUG)
    cookie = google_sign_in(monkeypatch, role='student')
    sid = read_cookie(cookie)['sid']
    with Session(engine) as db:
        uid = db.scalar(select(User.id))
    client.post('/api/attempts', json=ATTEMPT, headers=HEADERS)
    client.post('/api/logout', json={}, headers=HEADERS)
    use_cookie(cookie)
    me()
    use_cookie(sign_cookie({'sid': real_sid(uid)}))
    clock.now += sessions.ABSOLUTE
    me()
    text = caplog.text
    for secret in (sid, sessions.digest(sid), cookie, EMAIL):
        assert secret not in text
    for record in caplog.records:
        assert uid not in (record.args if isinstance(record.args, tuple) else ())
        assert 'uid' not in record.getMessage() and 'user_id' not in record.getMessage()

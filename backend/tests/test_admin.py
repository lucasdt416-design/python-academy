"""Admin and tester roles (backlog FB-01): who is admin, the guard, admin sessions, the tester flag."""
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
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import admin, sessions
from app.db import Event, User, UserSession
from app.main import Base, app, engine, oauth

client = TestClient(app)
HEADERS = {'origin': 'http://localhost:3000'}
OWNER = 'owner@example.com'
OTHER_ADMIN = 'second-admin@example.com'  # in ADMIN_EMAILS, never signs in
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
    monkeypatch.setenv('ADMIN_EMAILS', f' Owner@Example.com ,, {OTHER_ADMIN.upper()} ')
    clock = Clock()
    monkeypatch.setattr(sessions, 'clock', clock)
    return clock


def google(monkeypatch, email, sub=None, verified=True):
    """The real callback, with only Google's answer replaced. Returns the response."""
    async def answer(request):
        return {'userinfo': {'sub': sub or email, 'email': email, 'email_verified': verified}}
    monkeypatch.setattr(oauth.google, 'authorize_access_token', answer)
    return client.get('/auth/google/callback', follow_redirects=False)


def account(email, role):
    with Session(engine) as db:
        user = User(subject=email, email=email, role=role)
        db.add(user)
        db.commit()
        return user.id


def sign_cookie(payload):
    return TimestampSigner(os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps(payload).encode())).decode()


def use_session(uid, admin_flag=False, extra=None):
    """A real session row, as the callback makes, and its cookie."""
    token = secrets.token_urlsafe(32)
    now = int(sessions.clock())
    with Session(engine) as db:
        db.add(UserSession(id=sessions.digest(token), user_id=uid, created=now, last_seen=now,
                           expires=now + (sessions.ADMIN_ABSOLUTE if admin_flag else sessions.ABSOLUTE), admin=admin_flag))
        db.commit()
    client.cookies.clear()
    client.cookies.set('session', sign_cookie({'sid': token, **(extra or {})}), domain='testserver.local', path='/')


def owner_signs_in(monkeypatch):
    assert google(monkeypatch, 'OWNER@example.com', sub='owner').status_code == 307
    with Session(engine) as db:
        return db.scalar(select(User.id).where(User.subject == 'owner'))


# Who is an admin

@pytest.mark.parametrize('value,expected', [
    (None, set()),
    ('', set()),
    ('  ,  , ', set()),
    ('a@example.com', {'a@example.com'}),
    (' A@Example.COM , b@example.com ,', {'a@example.com', 'b@example.com'}),
    ('a@example.com,a@EXAMPLE.com', {'a@example.com'}),
])
def test_admin_emails_ignore_spaces_case_and_empty_entries(monkeypatch, value, expected):
    if value is None:
        monkeypatch.delenv('ADMIN_EMAILS', raising=False)
    else:
        monkeypatch.setenv('ADMIN_EMAILS', value)
    assert admin.admin_emails() == expected


def test_a_verified_listed_email_starts_an_admin_session(monkeypatch, clock):
    owner_signs_in(monkeypatch)
    me = client.get('/api/me').json()
    assert (me['admin'], me['tester']) == (True, True)
    [row] = list(Session(engine).scalars(select(UserSession)))
    assert row.admin and row.expires == row.created + 8 * HOUR
    assert client.get('/api/admin/students').status_code == 200


@pytest.mark.parametrize('verified', [False, None, 'true'])
def test_an_unverified_email_is_never_admin(monkeypatch, verified):
    response = google(monkeypatch, OWNER, verified=verified)
    if response.status_code == 307:  # 'true' as text passes sign-in, but is not Google's verified flag
        assert client.get('/api/me').json()['admin'] is False
        assert client.get('/api/admin/students').status_code == 403
    else:
        assert response.status_code == 403
    assert all(not row.admin for row in Session(engine).scalars(select(UserSession)))


def test_an_unlisted_email_gets_a_normal_session(monkeypatch):
    google(monkeypatch, 'someone@example.com')
    [row] = list(Session(engine).scalars(select(UserSession)))
    assert not row.admin and row.expires == row.created + sessions.ABSOLUTE
    assert client.get('/api/me').json()['admin'] is False


def test_removing_an_email_from_the_list_ends_admin_access_at_once(monkeypatch):
    owner_signs_in(monkeypatch)
    assert client.get('/api/admin/students').status_code == 200
    monkeypatch.setenv('ADMIN_EMAILS', OTHER_ADMIN)
    assert client.get('/api/admin/students').status_code == 403


def test_an_email_match_alone_is_not_enough(monkeypatch):
    # The owner's account exists, but this session was not started as an admin session
    # (for example, signed in before their email was added to ADMIN_EMAILS).
    use_session(account(OWNER, 'parent'))
    assert client.get('/api/admin/students').status_code == 403


# Every admin route is guarded

BODIES = {('POST', '/api/admin/testers'): {'user_id': 1, 'tester': True}}
ADMIN_ROUTES = sorted((m, r.path) for r in app.routes if isinstance(r, APIRoute) and r.path.startswith('/api/admin') for m in r.methods - {'HEAD'})


def call(route):
    method, path = route
    return client.request(method, path, json=BODIES.get(route), headers=HEADERS)


def test_every_admin_route_has_the_guard():
    assert ADMIN_ROUTES == [('GET', '/api/admin/students'), ('POST', '/api/admin/testers')]
    for r in app.routes:
        if isinstance(r, APIRoute) and r.path.startswith('/api/admin'):
            assert admin.require_admin in [d.call for d in r.dependant.dependencies], r.path


@pytest.mark.parametrize('route', ADMIN_ROUTES, ids=lambda r: f'{r[0]} {r[1]}')
def test_admin_routes_refuse_everyone_but_an_admin(monkeypatch, route):
    client.cookies.clear()
    assert call(route).status_code == 401
    for role in ('pending', 'parent', 'student'):
        use_session(account(f'{role}@example.com', role))
        assert call(route).status_code == 403, role
    tester = account('tester@example.com', 'student')
    with Session(engine) as db:
        db.get(User, tester).tester = True
        db.commit()
    use_session(tester)
    assert call(route).status_code == 403
    use_session(account('x@example.com', 'student'))
    # Spoofed headers and an edited cookie change nothing.
    spoofed = client.request(route[0], route[1], json=BODIES.get(route), headers={**HEADERS, 'X-Admin': 'true', 'X-Forwarded-Email': OWNER, 'X-Forwarded-User': OWNER})
    assert spoofed.status_code == 403
    student = account('y@example.com', 'student')
    use_session(student, extra={'admin': True, 'uid': 1, 'email': OWNER})
    assert call(route).status_code == 403


def test_the_admin_gets_in_on_every_admin_route(monkeypatch):
    student = account('kid@example.com', 'student')
    owner_signs_in(monkeypatch)
    BODIES[('POST', '/api/admin/testers')] = {'user_id': student, 'tester': True}
    try:
        for route in ADMIN_ROUTES:
            assert call(route).status_code == 200, route
    finally:
        BODIES[('POST', '/api/admin/testers')] = {'user_id': 1, 'tester': True}


# Admin sessions are shorter

def test_an_admin_session_ends_after_8_hours_even_if_used(monkeypatch, clock):
    owner_signs_in(monkeypatch)
    start = clock.now
    while clock.now + HOUR / 2 < start + 8 * HOUR:
        clock.now += HOUR / 2
        assert client.get('/api/admin/students').status_code == 200
    clock.now = start + 8 * HOUR
    assert client.get('/api/admin/students').status_code == 401


def test_an_admin_session_ends_after_1_hour_unused(monkeypatch, clock):
    owner_signs_in(monkeypatch)
    clock.now += HOUR - 1
    assert client.get('/api/admin/students').status_code == 200
    clock.now += HOUR
    assert client.get('/api/admin/students').status_code == 401
    assert client.get('/api/me').status_code == 401


def test_learner_sessions_keep_their_lifetimes(monkeypatch, clock):
    google(monkeypatch, 'learner@example.com')
    clock.now += 23 * HOUR
    assert client.get('/api/me').status_code == 200


# The tester flag

def test_only_an_admin_sets_and_clears_the_tester_flag(monkeypatch):
    student = account('kid@example.com', 'student')
    parent = account('mum@example.com', 'parent')
    owner = owner_signs_in(monkeypatch)
    assert client.post('/api/admin/testers', json={'user_id': student, 'tester': True}, headers=HEADERS).json() == {'id': student, 'tester': True}
    assert [s['tester'] for s in client.get('/api/admin/students').json()] == [True]
    assert client.post('/api/admin/testers', json={'user_id': parent, 'tester': True}, headers=HEADERS).status_code == 422
    assert client.post('/api/admin/testers', json={'user_id': 9999, 'tester': True}, headers=HEADERS).status_code == 404
    assert client.post('/api/admin/testers', json={'user_id': student, 'tester': False}, headers=HEADERS).json()['tester'] is False
    with Session(engine) as db:
        events = [(e.user_id, e.action, e.detail) for e in db.scalars(select(Event).where(Event.action.like('tester%')).order_by(Event.id))]
        assert events == [(owner, 'tester_set', f'user {student}'), (owner, 'tester_cleared', f'user {student}')]
        assert db.get(User, parent).tester is False


def test_a_student_cannot_set_their_own_tester_flag(monkeypatch):
    student = account('kid@example.com', 'student')
    use_session(student)
    assert client.post('/api/admin/testers', json={'user_id': student, 'tester': True}, headers=HEADERS).status_code == 403
    with Session(engine) as db:
        assert db.get(User, student).tester is False
    assert client.get('/api/me').json()['tester'] is False


def test_a_tester_student_sees_tester_but_not_admin():
    student = account('kid@example.com', 'student')
    with Session(engine) as db:
        db.get(User, student).tester = True
        db.commit()
    use_session(student)
    assert {k: client.get('/api/me').json()[k] for k in ('admin', 'tester')} == {'admin': False, 'tester': True}


# The admin list never leaves the server

def test_the_admin_list_is_in_no_response_and_no_log(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    student = account('kid@example.com', 'student')
    bodies = []
    owner_signs_in(monkeypatch)
    for path in ('/api/me', '/api/history', '/api/admin/students', '/api/catalog', '/api/lessons'):
        bodies.append(client.get(path).text)
    bodies.append(client.post('/api/admin/testers', json={'user_id': student, 'tester': True}, headers=HEADERS).text)
    use_session(student)
    for path in ('/api/me', '/api/history', '/api/progress', '/api/awards', '/api/admin/students'):
        bodies.append(client.get(path).text)
    everything = '\n'.join(bodies).casefold()
    assert OTHER_ADMIN not in everything
    logs = caplog.text.casefold()
    assert OTHER_ADMIN not in logs and OWNER not in logs and 'admin_emails' not in logs

"""Anonymous tester feedback (backlog FB-02): who may send, what is stored, limits and retention."""
import os
import tempfile
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + tempfile.mktemp(suffix='.db'))
os.environ.setdefault('SESSION_SECRET', 'test-secret-that-is-at-least-thirty-two-characters')
import base64
import json
import logging
import secrets
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import feedback, sessions
from app.db import Event, Feedback, User, UserSession
from app.limits import LIMITER, RULES
from app.main import Base, app, engine, oauth

client = TestClient(app)
HEADERS = {'origin': 'http://localhost:3000'}
OWNER = 'owner@example.com'
DAY = 86400
START = 1_800_000_000.0  # 2027-01-15, a fixed day for the fake clock
TEXT = 'The second hint on Choose a path talks about a variable I have not met yet.'
CODE = 'path = input("Path? ")\nif path == "left":\n    print("A cave.")'


class Clock:
    def __init__(self):
        self.now = START

    def __call__(self):
        return self.now


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    client.cookies.clear()
    monkeypatch.setenv('ADMIN_EMAILS', OWNER)
    clock = Clock()
    for module in (sessions, feedback):
        monkeypatch.setattr(module, 'clock', clock)
    monkeypatch.setattr(LIMITER, 'clock', clock)
    monkeypatch.setattr(feedback, '_last_purge', None)
    return clock


def account(email, role, tester=False):
    with Session(engine) as db:
        user = User(subject=email, email=email, role=role, tester=tester)
        db.add(user)
        db.commit()
        return user.id


def use_session(uid, admin_flag=False):
    """A real session row, as the sign-in callback makes, and its cookie. Returns the session ID."""
    token = secrets.token_urlsafe(32)
    now = int(sessions.clock())
    with Session(engine) as db:
        db.add(UserSession(id=sessions.digest(token), user_id=uid, created=now, last_seen=now,
                           expires=now + (sessions.ADMIN_ABSOLUTE if admin_flag else sessions.ABSOLUTE), admin=admin_flag))
        db.commit()
    cookie = TimestampSigner(os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps({'sid': token}).encode())).decode()
    client.cookies.clear()
    client.cookies.set('session', cookie, domain='testserver.local', path='/')
    return token


def as_tester(email='tester@example.com'):
    uid = account(email, 'student', tester=True)
    use_session(uid)
    return uid


def admin_signs_in(monkeypatch):
    """The real Google callback, so the session is an admin session exactly as in production."""
    async def answer(request):
        return {'userinfo': {'sub': 'owner', 'email': OWNER, 'email_verified': True}}
    monkeypatch.setattr(oauth.google, 'authorize_access_token', answer)
    assert client.get('/auth/google/callback', follow_redirects=False).status_code == 307
    with Session(engine) as db:
        return db.scalar(select(User.id).where(User.subject == 'owner'))


def send(**fields):
    return client.post('/api/feedback', json={'category': 'confusing', 'message': TEXT, **fields}, headers=HEADERS)


def items():
    with Session(engine) as db:
        return [{c.name: getattr(f, c.name) for c in Feedback.__table__.columns} for f in db.scalars(select(Feedback).order_by(Feedback.id))]


def count():
    with Session(engine) as db:
        return db.scalar(select(func.count()).select_from(Feedback))


def stored(n, status='new', on=None):
    with Session(engine) as db:
        db.add_all(Feedback(created_on=on or date(2027, 1, 1), category='bug', message=f'item {i}', status=status) for i in range(n))
        db.commit()


# Who may send

@pytest.mark.parametrize('who,expected', [
    ('signed out', 401),
    ('pending', 403),
    ('parent', 403),
    ('student', 403),            # a student who is not a tester
    ('parent with tester flag', 403),  # the flag counts only on student accounts
    ('tester', 200),
    ('admin', 200),
])
def test_only_testers_and_the_admin_can_send(monkeypatch, who, expected):
    if who == 'admin':
        admin_signs_in(monkeypatch)
    elif who == 'tester':
        as_tester()
    elif who == 'parent with tester flag':
        use_session(account('mum@example.com', 'parent', tester=True))
    elif who != 'signed out':
        use_session(account(f'{who}@example.com', who))
    response = send()
    assert response.status_code == expected, response.text
    assert count() == (1 if expected == 200 else 0)


def test_the_admins_email_with_an_ordinary_session_is_not_enough():
    # Admin status is decided at sign-in (FB-01): this session was not started as an admin session.
    use_session(account(OWNER, 'parent'))
    assert send().status_code == 403


def test_a_student_cannot_send_after_the_tester_flag_is_cleared():
    uid = as_tester()
    assert send().status_code == 200
    with Session(engine) as db:
        db.get(User, uid).tester = False
        db.commit()
    assert send().status_code == 403
    assert count() == 1


def test_feedback_from_another_site_is_refused():
    as_tester()
    assert client.post('/api/feedback', json={'category': 'bug', 'message': TEXT}, headers={'origin': 'https://evil.example'}).status_code == 403
    assert client.post('/api/feedback', json={'category': 'bug', 'message': TEXT}).status_code == 403
    assert count() == 0


# Anonymity

def test_nothing_stored_or_returned_identifies_the_sender(monkeypatch, clock):
    uid = account('kid@example.com', 'student', tester=True)
    sid = use_session(uid)
    response = client.post('/api/feedback', json={'category': 'bug', 'message': TEXT, 'audience': 'high_school'},
                           headers={**HEADERS, 'cf-connecting-ip': '203.0.113.9', 'x-forwarded-for': '198.51.100.7'})
    assert response.json() == {'saved': True}
    owner = admin_signs_in(monkeypatch)
    admin_response = send(category='idea')
    assert admin_response.json() == {'saved': True}
    rows = items()
    assert [set(row) for row in rows] == [{'id', 'created_on', 'category', 'audience', 'message', 'code', 'status'}] * 2
    # The day only, not the time, so a row cannot be matched to a request by when it arrived.
    assert all(type(row['created_on']) is date for row in rows)
    assert rows[0] == {'id': 1, 'created_on': date(2027, 1, 15), 'category': 'bug', 'audience': 'high_school', 'message': TEXT, 'code': None, 'status': 'new'}
    everything = json.dumps(rows, default=str) + response.text + admin_response.text
    with Session(engine) as db:
        session_ids = [s.id for s in db.scalars(select(UserSession))]
    for secret in ['kid@example.com', OWNER, '203.0.113.9', '198.51.100.7', sid, sessions.digest(sid), *session_ids]:
        assert secret not in everything
    # No column holds a user ID (the row's own ID is just a counter).
    assert all(value not in (uid, owner) for row in rows for key, value in row.items() if key != 'id')


def test_sending_feedback_adds_nothing_to_the_account_history():
    as_tester()
    with Session(engine) as db:
        before = db.scalar(select(func.count()).select_from(Event))
    assert send().status_code == 200
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(Event)) == before


# What is accepted

def test_message_length_limits():
    as_tester()
    assert send(message='x' * feedback.MESSAGE_LIMIT).status_code == 200
    assert send(message='x' * (feedback.MESSAGE_LIMIT + 1)).status_code == 422
    assert send(message='').status_code == 422
    assert send(message='   \n\t ').status_code == 422
    assert count() == 1


@pytest.mark.parametrize('fields', [
    {'category': 'spam'}, {'category': 'Bug'}, {'category': None},
    {'audience': 'adult'}, {'audience': 'High school'},
    {'user_id': 1}, {'email': 'x@example.com'},  # nothing outside the form is accepted
    {'include_code': True, 'code': 'x' * (feedback.CODE_LIMIT + 1)},
])
def test_categories_audience_and_unknown_fields_are_validated(fields):
    as_tester()
    assert send(**fields).status_code == 422
    assert count() == 0


def test_every_category_and_audience_is_accepted():
    as_tester()
    for category in ('confusing', 'bug', 'wrong_grading', 'idea', 'other'):
        LIMITER.reset()  # more than an hour's worth; the limits have their own tests
        assert send(category=category).status_code == 200
    for audience in ('high_school', 'university', 'other', None):
        LIMITER.reset()
        assert send(audience=audience).status_code == 200
    assert [row['audience'] for row in items()][5:] == ['high_school', 'university', 'other', None]


def test_code_is_saved_only_when_the_sender_opts_in():
    as_tester()
    for fields in ({'code': CODE},                # sent, but the box was not ticked
                   {'include_code': False, 'code': CODE},
                   {'include_code': True, 'code': CODE},
                   {'include_code': True, 'code': '   '},
                   {'include_code': True},
                   {'include_code': True, 'code': 'x' * feedback.CODE_LIMIT}):
        LIMITER.reset()
        assert send(**fields).status_code == 200
    assert [row['code'] for row in items()] == [None, None, CODE, None, None, 'x' * feedback.CODE_LIMIT]


def test_text_is_stored_as_plain_text_without_hidden_characters_or_contact_details():
    as_tester()
    message = '<script>alert(1)</script> 🐉 مرحبا ‮evil‬\x00\x07 mail me: kid.name+1@school.example.org or +1 (416) 555-0199. Lesson 3, card 5, line 12.'
    assert send(message=message, include_code=True, code='print("hi")\x1b[31m').status_code == 200
    row = items()[0]
    assert row['message'] == '<script>alert(1)</script> 🐉 مرحبا evil mail me: [email removed] or [number removed]. Lesson 3, card 5, line 12.'
    assert row['code'] == 'print("hi")[31m'


# Rate limits

def test_five_an_hour_and_twenty_a_day_per_tester(clock):
    as_tester()
    per_hour, per_day = (limit for limit, _ in RULES['feedback'].user)
    for _ in range(per_hour):
        assert send().status_code == 200
    blocked = send()
    assert blocked.status_code == 429 and 'feedback messages' in blocked.json()['detail'] and int(blocked.headers['Retry-After']) > 0
    # Like every limit in app/limits.py, a refused request also counts, so the day has one place fewer.
    tries = per_hour + 1
    while tries < per_day:
        clock.now += 3600
        for _ in range(min(per_hour, per_day - tries)):
            assert send().status_code == 200
            tries += 1
    clock.now += 3600
    assert send().status_code == 429
    assert count() == per_day - 1
    clock.now = START + DAY
    assert send().status_code == 200


def test_a_total_limit_for_all_testers_together(clock):
    (total, _), = RULES['feedback'].everyone
    per_hour = RULES['feedback'].user[0][0]
    sent = 0
    for n in range(total // per_hour + 1):
        as_tester(f'tester{n}@example.com')
        for _ in range(per_hour):
            response = send()
            sent += response.status_code == 200
    assert sent == total
    as_tester('one-more@example.com')
    assert send().status_code == 429


def test_the_rate_counters_hold_no_message_text_or_user_id():
    uid = as_tester('kid@example.com')
    send(include_code=True, code=CODE)
    dump = json.dumps(LIMITER.counts)
    for value in (TEXT, CODE, 'kid@example.com', f'u:{uid}'):
        assert value not in dump
    # Only keyed hashes, a window start and a count.
    assert all(len(key) == 32 and isinstance(start, float) and isinstance(n, int) for key, (start, n) in LIMITER.counts.items())


# Retention

def purge_now(clock):
    clock.now += feedback.PURGE_EVERY  # retention runs at most once an hour, on any request
    client.get('/health')


def test_items_are_deleted_exactly_50_days_after_the_day_they_were_sent(clock):
    as_tester()
    send()
    sent_on = items()[0]['created_on']
    clock.now = START + 49 * DAY
    purge_now(clock)
    assert count() == 1, 'still there on day 49'
    clock.now = START + 50 * DAY - feedback.PURGE_EVERY
    purge_now(clock)
    assert feedback.today() == sent_on + timedelta(days=50)
    assert count() == 0, 'gone on day 50'


def test_retention_runs_when_feedback_is_sent_too(clock):
    stored(3, on=date(2026, 11, 26))  # 50 days before START's day
    stored(1, on=date(2026, 11, 27))
    as_tester()
    assert send().status_code == 200
    assert [row['created_on'] for row in items()] == [date(2026, 11, 27), date(2027, 1, 15)]


def test_a_full_inbox_deletes_the_oldest_resolved_item_first():
    stored(30, status='new', on=date(2026, 12, 1))       # older, but unresolved: never deleted for room
    stored(1, status='wont_fix', on=date(2026, 12, 20))
    stored(1, status='fixed', on=date(2026, 12, 10))     # the oldest resolved item
    stored(1, status='fixed', on=date(2026, 12, 10))
    stored(57, status='triaged', on=date(2027, 1, 1))
    assert count() == feedback.MAX_ITEMS
    first_fixed = min(row['id'] for row in items() if row['status'] == 'fixed')
    as_tester()
    assert send().status_code == 200
    rows = items()
    assert len(rows) == feedback.MAX_ITEMS
    assert first_fixed not in {row['id'] for row in rows}
    assert [row['status'] for row in rows].count('new') == 31 and [row['status'] for row in rows].count('fixed') == 1
    assert send().status_code == 200   # then the other fixed one (same day, lower ID first)
    assert send().status_code == 200   # then the wont_fix one
    assert {row['status'] for row in items()} == {'new', 'triaged'}


def test_a_full_inbox_of_unresolved_items_rejects_the_new_one(caplog):
    caplog.set_level(logging.INFO)
    stored(feedback.MAX_ITEMS, status='in_progress')
    before = items()
    as_tester()
    response = send()
    assert response.status_code == 409
    assert response.json()['detail'] == 'The feedback inbox is full right now, so this was not saved. Please try again in a few days.'
    assert items() == before
    assert 'Feedback rejected: inbox full' in caplog.text


def test_retention_failing_never_takes_the_app_down(monkeypatch, caplog):
    def broken(db):
        raise RuntimeError('database unavailable')
    monkeypatch.setattr(feedback, 'purge', broken)
    assert client.get('/health').status_code == 200
    assert 'Feedback retention failed: RuntimeError' in caplog.text


# Logs

def test_no_message_code_email_or_user_id_in_any_log_line(monkeypatch, caplog, clock):
    caplog.set_level(logging.DEBUG)
    uid = as_tester('kid@example.com')
    send(include_code=True, code=CODE, message=TEXT + ' kid@example.com')
    send(message='x' * (feedback.MESSAGE_LIMIT + 1))
    for _ in range(6):
        send()
    stored(feedback.MAX_ITEMS, status='new')
    clock.now += 2 * 3600
    send()
    admin_signs_in(monkeypatch)
    send(message='From the admin: ' + TEXT)
    clock.now += 51 * DAY
    purge_now(clock)
    logs = caplog.text
    assert 'Feedback accepted' in logs and 'Feedback rejected: inbox full' in logs and 'Rate limited: rule=feedback' in logs
    for secret in (TEXT, CODE[:20], 'xxxxxxxxxx', 'kid@example.com', OWNER, f'user={uid}', f'uid={uid}'):
        assert secret not in logs

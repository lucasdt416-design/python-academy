import os
import tempfile
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + tempfile.mktemp(suffix='.db'))
os.environ.setdefault('SESSION_SECRET', 'test-secret-that-is-at-least-thirty-two-characters')
import base64
import json
import logging
import secrets

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy import select, text
from sqlalchemy.orm import Session

import app.limits as limits
from app import sessions
from app.db import UserSession
from app.limits import LIMITER, RULES, client_ip
from app.main import Base, User, app, engine

client = TestClient(app)
HEADERS = {'origin': 'http://localhost:3000'}
CODE = 'print("A forest.")\nprint("A dragon!")'
SECRET_CODE = 'print("my-secret-learner-code")'
# Most tests run as production is expected to be configured: the edge's own header names the visitor.
EDGE = 'cf-connecting-ip'


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    client.cookies.clear()
    clock = Clock()
    monkeypatch.setattr(LIMITER, 'clock', clock)
    monkeypatch.setattr(limits, 'CLIENT_IP_HEADER', EDGE)
    monkeypatch.setattr(limits, 'TRUSTED_PROXY_HOPS', 0)
    monkeypatch.setattr(limits, 'DIAGNOSTIC', False)
    return clock


def signin(role, email='learner@example.com'):
    with Session(engine) as db:
        user = User(subject=email, email=email, role=role)
        db.add(user)
        db.commit()
        uid = user.id
    token = secrets.token_urlsafe(32)
    now = int(sessions.clock())
    with Session(engine) as db:
        db.add(UserSession(id=sessions.digest(token), user_id=uid, created=now, last_seen=now, expires=now + sessions.ABSOLUTE))
        db.commit()
    cookie = TimestampSigner(os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps({'sid': token}).encode())).decode()
    client.cookies.set('session', cookie, domain='testserver.local', path='/')
    return uid


def post(path, data, ip=None, extra=None):
    headers = dict(HEADERS, **({EDGE: ip} if ip else {}), **(extra or {}))
    return client.post('/api/' + path, json=data, headers=headers)


def check(ip=None, code=CODE, extra=None):
    return post('check', {'lesson_id': 'hello', 'code': code, 'output': 'A forest.\nA dragon!\n'}, ip, extra)


def assert_limited(response):
    assert response.status_code == 429
    wait = int(response.headers['retry-after'])
    assert wait >= 1
    detail = response.json()['detail']
    assert detail.startswith('Too many ') and 'Please wait' in detail
    return wait


def requests_until_limited(send, most=2000):
    for count in range(1, most + 1):
        response = send()
        if response.status_code == 429:
            return count, response
        assert response.status_code < 400, response.text
    raise AssertionError('never limited')


# Exceeding each limit

def test_signed_out_checks_are_limited_per_ip_with_retry_after(setup):
    count, response = requests_until_limited(lambda: check('203.0.113.5'))
    assert count == RULES['check'].ip[0][0] + 1
    assert assert_limited(response) == 60
    assert 'Your code is unchanged.' in response.json()['detail']
    # Another address is unaffected, and the same address recovers once the minute is over.
    assert check('203.0.113.6').status_code == 200
    setup.now += 30
    assert int(check('203.0.113.5').headers['retry-after']) == 30
    setup.now += 30
    assert check('203.0.113.5').status_code == 200


def test_signed_in_checks_are_limited_per_user_not_per_ip():
    signin('parent')
    count, response = requests_until_limited(lambda: check('203.0.113.5'))
    assert count == RULES['check'].user[0][0] + 1
    assert_limited(response)
    # Changing address does not reset a signed-in user's counter.
    assert check('198.51.100.9').status_code == 429
    client.cookies.clear()
    assert check('203.0.113.5').status_code == 200


def test_attempts_are_limited_per_student():
    signin('student')
    send = lambda: post('attempts', {'lesson_id': 'hello', 'code': CODE, 'output': 'A forest.\nA dragon!\n'})
    count, response = requests_until_limited(send)
    assert count == RULES['attempts'].user[0][0] + 1
    assert_limited(response)
    signin('student', 'other@example.com')
    assert send().status_code == 200


def test_hourly_limit_applies_even_when_each_minute_is_under(setup):
    signin('student')
    per_minute, per_hour = RULES['attempts'].user[0][0], RULES['attempts'].user[1][0]
    sent = 0
    while sent < per_hour:
        for _ in range(per_minute):
            assert post('attempts', {'lesson_id': 'hello', 'code': CODE, 'output': ''}).status_code == 200
            sent += 1
        setup.now += 60
    response = post('attempts', {'lesson_id': 'hello', 'code': CODE, 'output': ''})
    assert assert_limited(response) > 60


def test_invitations_are_limited_per_parent():
    signin('parent')
    count, response = requests_until_limited(lambda: post('invitations', {'email': 'kid@example.com'}))
    assert count == RULES['invitations'].user[0][0] + 1
    assert assert_limited(response) == 3600
    assert response.json()['detail'] == 'Too many invitations for now. Please wait 60 minutes and try again.'


def test_goal_changes_are_limited_per_student():
    signin('student')
    count, response = requests_until_limited(lambda: post('goal', {'goal': 'hackathon'}))
    assert count == RULES['goal'].user[0][0] + 1
    assert_limited(response)


def test_registration_attempts_are_limited():
    signin('pending')
    # Each attempt is refused (too young for a parent), and the refusals still count.
    send = lambda: post('enroll', {'birthday': '2020-01-01'})
    for _ in range(RULES['enroll'].user[0][0]):
        assert send().status_code == 422
    assert_limited(send())


@pytest.mark.parametrize('path,rule', [('/auth/google', 'signin'), ('/auth/google/callback', 'signin_callback')])
def test_sign_in_attempts_are_limited_per_ip_even_when_signed_in(path, rule):
    signin('student')
    limit = RULES[rule].ip[0][0]
    for _ in range(limit):
        assert client.get(path, headers={EDGE: '203.0.113.5'}, follow_redirects=False).status_code != 429
    response = client.get(path, headers={EDGE: '203.0.113.5'}, follow_redirects=False)
    assert assert_limited(response) == 600
    assert client.get(path, headers={EDGE: '203.0.113.6'}, follow_redirects=False).status_code != 429


def test_every_write_endpoint_has_a_limit():
    # A new POST route without a rate limit fails here until it gets one (or is listed as exempt).
    exempt = {'/api/logout'}
    from fastapi.routing import APIRoute
    from app.limits import limit
    for route in app.routes:
        if isinstance(route, APIRoute) and route.methods & {'POST', 'PUT', 'PATCH', 'DELETE'} and route.path not in exempt:
            names = {getattr(d.call, '__qualname__', '') for d in route.dependant.dependencies}
            assert any(name.startswith(limit.__qualname__) for name in names), route.path


# Normal use stays under the limits

def test_a_learner_working_through_lessons_is_never_limited(setup):
    signin('student')
    # A busy learner: a check every 15 seconds for a whole hour, plus a few goal changes.
    for _ in range(240):
        assert post('attempts', {'lesson_id': 'hello', 'code': CODE, 'output': ''}).status_code == 200
        setup.now += 15
    for _ in range(3):
        assert post('goal', {'goal': 'data'}).status_code == 200


def test_a_classroom_behind_one_address_can_sign_in_and_preview():
    # Thirty learners sharing a school address sign in and each try a few preview checks.
    for _ in range(30):
        assert client.get('/auth/google', headers={EDGE: '203.0.113.5'}, follow_redirects=False).status_code != 429
        assert client.get('/auth/google/callback', headers={EDGE: '203.0.113.5'}, follow_redirects=False).status_code != 429
    for _ in range(30):
        assert check('203.0.113.5').status_code == 200


def test_a_parent_inviting_a_family_is_never_limited():
    signin('parent')
    for n in range(5):
        assert post('invitations', {'email': f'kid{n}@example.com'}).status_code == 200


# What the counters and logs hold

def test_counters_and_logs_hold_no_code_ids_or_addresses(caplog):
    signin('parent')
    with caplog.at_level(logging.INFO):
        for _ in range(RULES['check'].user[0][0] + 1):
            check('203.0.113.77', SECRET_CODE)
    # ENG-11: the counters are in the database now, so that is where to look.
    with engine.connect() as conn:
        table = [tuple(row) for row in conn.execute(text('SELECT key, window_start, count FROM rate_limits'))]
    stored = json.dumps(table) + json.dumps(list(LIMITER.counts.items()))
    assert table
    for found in ('my-secret-learner-code', '203.0.113.77', 'u:1', 'learner@example.com'):
        assert found not in stored and found not in caplog.text
    assert 'Rate limited: rule=check scope=user' in caplog.text
    assert all(isinstance(start, int) and isinstance(count, int) for _, start, count in table)


def test_counter_memory_is_bounded(monkeypatch, setup):
    import app.limits as limits
    monkeypatch.setattr(limits, 'MAX_KEYS', 100)
    # Memory holds private counters, and all of them when the database is down.
    for n in range(300):
        LIMITER.hit('check', f'ip:{n}', RULES['check'].ip, private=True)
    assert len(LIMITER.counts) <= 2 * 100 + 2


# Which address is used, and that callers cannot choose it

SPOOFS = ['x-forwarded-for', 'x-real-ip', 'true-client-ip', 'forwarded', 'x-client-ip']


def spoofed(n):
    return {name: f'198.51.100.{n % 250}' if name != 'forwarded' else f'for=198.51.100.{n % 250}' for name in SPOOFS}


def test_spoofed_forwarding_headers_do_not_change_the_counter():
    # The production failure: a different made-up X-Forwarded-For on every request got a new counter.
    sent = iter(range(1, 1000))
    count, response = requests_until_limited(lambda: check('81.2.69.142', extra=spoofed(next(sent))))
    assert count == RULES['check'].ip[0][0] + 1
    assert_limited(response)


@pytest.mark.parametrize('setting', ['none', 'hops'])
def test_spoofed_headers_cannot_choose_a_counter_in_the_other_modes(monkeypatch, setting):
    monkeypatch.setattr(limits, 'CLIENT_IP_HEADER', '')
    if setting == 'hops':
        monkeypatch.setattr(limits, 'TRUSTED_PROXY_HOPS', 1)
    sent = iter(range(1, 1000))
    def send():
        n = next(sent)
        headers = dict(spoofed(n), **{EDGE: f'198.51.100.{n % 250}'})
        if setting == 'hops':
            # Made-up entries arrive on the left; the trusted proxy adds the real address on the right.
            headers['x-forwarded-for'] = f'198.51.100.{n % 250}, 10.9.8.{n % 250}, 81.2.69.142'
        return check(extra=headers)
    count, response = requests_until_limited(send)
    assert count == RULES['check'].ip[0][0] + 1
    assert_limited(response)


def test_different_visitors_get_different_counters_from_the_edge_header():
    requests_until_limited(lambda: check('81.2.69.142'))
    assert check('81.2.69.143').status_code == 200


class FakeRequest:
    def __init__(self, headers):
        self.headers = headers


@pytest.mark.parametrize('header,hops,headers,expected', [
    ('', 0, {}, ('shared', 'shared')),                                                     # nothing configured
    ('', 0, {'x-forwarded-for': '81.2.69.142', EDGE: '81.2.69.142'}, ('shared', 'shared')),  # headers ignored
    (EDGE, 0, {EDGE: '81.2.69.142', 'x-forwarded-for': '1.2.3.4'}, ('81.2.69.142', 'header')),
    (EDGE, 0, {EDGE: '2a00:1450:4001:1:2:3:4:5'}, ('2a00:1450:4001:1::/64', 'header')),     # IPv6 grouped by /64
    (EDGE, 0, {EDGE: '1.2.3.4, 5.6.7.8'}, ('shared', 'shared')),                           # not one address
    (EDGE, 0, {'x-forwarded-for': '81.2.69.142'}, ('shared', 'shared')),                   # header missing
    ('', 1, {'x-forwarded-for': '1.2.3.4, 81.2.69.142'}, ('81.2.69.142', 'hops')),
    ('', 2, {'x-forwarded-for': '1.2.3.4, 81.2.69.142, 10.0.0.1'}, ('81.2.69.142', 'hops')),
    ('', 2, {'x-forwarded-for': '81.2.69.142'}, ('shared', 'shared')),                     # fewer entries than hops
    ('', 1, {'x-forwarded-for': '81.2.69.142, garbage'}, ('shared', 'shared')),
])
def test_client_ip_only_trusts_the_configured_source(monkeypatch, header, hops, headers, expected):
    monkeypatch.setattr(limits, 'CLIENT_IP_HEADER', header)
    monkeypatch.setattr(limits, 'TRUSTED_PROXY_HOPS', hops)
    assert client_ip(FakeRequest(headers)) == expected


def test_diagnostic_logs_counts_names_and_a_hash_only(monkeypatch, caplog):
    monkeypatch.setattr(limits, 'DIAGNOSTIC', True)
    with caplog.at_level(logging.INFO):
        check('81.2.69.142', SECRET_CODE, extra={'x-forwarded-for': '198.51.100.7, 81.2.69.142', 'x-real-ip': '198.51.100.8'})
    [line] = [r.getMessage() for r in caplog.records if 'diagnostic' in r.getMessage()]
    assert line.startswith('Client address diagnostic: rule=check xff_entries=2 headers=cf-connecting-ip,x-forwarded-for,x-real-ip source=header chosen=')
    assert len(line.rsplit('chosen=', 1)[1]) == 8
    for text in ('81.2.69.142', '198.51.100', 'my-secret-learner-code'):
        assert text not in caplog.text


def test_diagnostic_is_off_by_default(caplog):
    with caplog.at_level(logging.INFO):
        check('81.2.69.142')
    assert 'diagnostic' not in caplog.text


# ENG-11: the counters live in the database

from sqlalchemy.exc import OperationalError
from app.db import RateCount


def rows():
    with Session(engine) as db:
        return db.scalars(select(RateCount)).all()


def test_counters_are_in_the_database_and_hold_only_hashes(setup):
    signin('student', 'counted@example.com')
    client.post('/api/check', json={'lesson_id': 'hello', 'code': CODE}, headers=HEADERS)
    found = rows()
    assert len(found) == 2  # a minute window and an hour window
    for row in found:
        assert len(row.key) == 32 and all(c in '0123456789abcdef' for c in row.key)
        assert row.count == 1 and row.window_start == 1_000_000
    with engine.connect() as conn:
        dumped = ' '.join(str(v) for row in conn.execute(text('SELECT * FROM rate_limits')) for v in row)
    assert 'counted' not in dumped and 'u:' not in dumped and 'hello' not in dumped


def test_two_instances_share_one_limit(setup):
    # A second API instance: its own process memory, the same database and SESSION_SECRET.
    other = limits.Limiter(clock=setup)
    windows = ((3, MINUTE_SECONDS),)
    assert [LIMITER.hit('check', 'ip:198.51.100.7', windows), other.hit('check', 'ip:198.51.100.7', windows), LIMITER.hit('check', 'ip:198.51.100.7', windows)] == [0, 0, 0]
    assert other.hit('check', 'ip:198.51.100.7', windows) == 60


def test_a_restart_does_not_reset_the_counters(setup):
    windows = ((1, MINUTE_SECONDS),)
    assert LIMITER.hit('goal', 'u:1', windows) == 0
    assert limits.Limiter(clock=setup).hit('goal', 'u:1', windows) == 60


def test_a_window_starts_again_once_it_is_over(setup):
    windows = ((1, MINUTE_SECONDS),)
    assert LIMITER.hit('goal', 'u:1', windows) == 0
    setup.now += 30
    assert LIMITER.hit('goal', 'u:1', windows) == 30
    setup.now += 30
    assert LIMITER.hit('goal', 'u:1', windows) == 0
    assert [r.count for r in rows()] == [1]


def test_feedbacks_per_tester_counters_never_reach_the_database(setup):
    LIMITER.hit('feedback', 'u:1', RULES['feedback'].user, private=True)
    assert rows() == []
    # Its total for everyone together holds no one's identity, so it is shared.
    LIMITER.hit('feedback', 'everyone', RULES['feedback'].everyone)
    assert len(rows()) == 1


def test_when_the_database_fails_the_limit_still_applies_in_memory(setup, monkeypatch, caplog):
    def broken(*args, **kwargs):
        raise OperationalError('SELECT 1', {}, Exception('database down'))
    monkeypatch.setattr(LIMITER, '_database', broken)
    windows = ((2, MINUTE_SECONDS),)
    with caplog.at_level(logging.WARNING, logger='uvicorn.error'):
        assert [LIMITER.hit('check', 'ip:198.51.100.9', windows) for _ in range(3)] == [0, 0, 60]
    assert 'counting in memory: rule=check' in caplog.text and '198.51.100.9' not in caplog.text


def test_old_windows_are_deleted(setup, monkeypatch):
    monkeypatch.setattr(limits, 'PRUNE_EVERY', 1)
    LIMITER.hit('goal', 'u:1', ((10, MINUTE_SECONDS),))
    setup.now += limits.LONGEST
    LIMITER.hit('goal', 'u:2', ((10, MINUTE_SECONDS),))
    assert len(rows()) == 1


MINUTE_SECONDS = 60

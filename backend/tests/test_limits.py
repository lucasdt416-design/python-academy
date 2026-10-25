import os
import tempfile
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + tempfile.mktemp(suffix='.db'))
os.environ.setdefault('SESSION_SECRET', 'test-secret-that-is-at-least-thirty-two-characters')
import base64
import json
import logging

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy.orm import Session

from app.limits import LIMITER, RULES, client_ip
from app.main import Base, User, app, engine

client = TestClient(app)
HEADERS = {'origin': 'http://localhost:3000'}
CODE = 'print("A forest.")\nprint("A dragon!")'
SECRET_CODE = 'print("my-secret-learner-code")'


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
    return clock


def signin(role, email='learner@example.com'):
    with Session(engine) as db:
        user = User(subject=email, email=email, role=role)
        db.add(user)
        db.commit()
        uid = user.id
    cookie = TimestampSigner(os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps({'uid': uid}).encode())).decode()
    client.cookies.set('session', cookie, domain='testserver.local', path='/')
    return uid


def post(path, data, ip=None):
    headers = dict(HEADERS, **({'x-forwarded-for': ip} if ip else {}))
    return client.post('/api/' + path, json=data, headers=headers)


def check(ip=None, code=CODE):
    return post('check', {'lesson_id': 'hello', 'code': code, 'output': 'A forest.\nA dragon!\n'}, ip)


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
        assert client.get(path, headers={'x-forwarded-for': '203.0.113.5'}, follow_redirects=False).status_code != 429
    response = client.get(path, headers={'x-forwarded-for': '203.0.113.5'}, follow_redirects=False)
    assert assert_limited(response) == 600
    assert client.get(path, headers={'x-forwarded-for': '203.0.113.6'}, follow_redirects=False).status_code != 429


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
        assert client.get('/auth/google', headers={'x-forwarded-for': '203.0.113.5'}, follow_redirects=False).status_code != 429
        assert client.get('/auth/google/callback', headers={'x-forwarded-for': '203.0.113.5'}, follow_redirects=False).status_code != 429
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
    stored = json.dumps(list(LIMITER.counts.items()))
    for text in ('my-secret-learner-code', '203.0.113.77', 'u:1', 'learner@example.com'):
        assert text not in stored and text not in caplog.text
    assert 'Rate limited: rule=check scope=user' in caplog.text
    assert all(isinstance(start, float) and isinstance(count, int) for start, count in LIMITER.counts.values())


def test_counter_memory_is_bounded(monkeypatch, setup):
    import app.limits as limits
    monkeypatch.setattr(limits, 'MAX_KEYS', 100)
    for n in range(300):
        LIMITER.hit('check', f'ip:{n}', RULES['check'].ip)
    assert len(LIMITER.counts) <= 2 * 100 + 2


# Which address is used (documentation ranges such as 203.0.113.0/24 are not public, so real ones are used here)

class FakeRequest:
    def __init__(self, forwarded, peer='10.0.0.2'):
        self.headers = {'x-forwarded-for': forwarded} if forwarded is not None else {}
        self.client = type('Peer', (), {'host': peer})()


@pytest.mark.parametrize('forwarded,peer,expected', [
    (None, '127.0.0.1', '127.0.0.1'),                       # local development and tests
    ('81.2.69.142', '10.0.0.2', '81.2.69.142'),             # Render proxy -> Next.js -> API
    ('81.2.69.142, 10.1.2.3', '10.0.0.2', '81.2.69.142'),   # with a private proxy hop appended
    ('1.2.3.4, 81.2.69.142', '10.0.0.2', '81.2.69.142'),    # a made-up entry on the left is ignored
    ('garbage, 81.2.69.142', '10.0.0.2', '81.2.69.142'),
    ('2a00:1450:4001:1:2:3:4:5', '10.0.0.2', '2a00:1450:4001:1::/64'),
    ('2606:4700:1:2:aaaa::1', '10.0.0.2', '2606:4700:1:2::/64'),  # IPv6 grouped by /64
    ('not-an-ip', '10.0.0.2', '10.0.0.2'),
])
def test_client_ip_uses_the_rightmost_public_address(forwarded, peer, expected):
    assert client_ip(FakeRequest(forwarded, peer)) == expected

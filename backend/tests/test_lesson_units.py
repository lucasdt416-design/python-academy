"""Lessons loaded one unit at a time (UI-05), and the browser-check answers the lesson page relies on.

Uses the TEST FIXTURE content in tests/fixtures/lesson_units/ (two released units with browser-check
lessons), served through the real API in place of nothing real: it is never part of backend/content/.
frontend/tests/fixtures/lesson-units-api.json holds the API's answers that the browser tests mock;
test_the_recorded_answers_are_the_real_apis proves they are exactly what the API says.
"""
import os
import tempfile
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + tempfile.mktemp(suffix='.db'))
os.environ.setdefault('SESSION_SECRET', 'test-secret-that-is-at-least-thirty-two-characters')
import base64
import json
import secrets
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import content, main, sessions
from app.db import Base, BadgeAward, User, UserSession, XpAward
from app.main import app, engine

FIXTURE_DIR = Path(__file__).with_name('fixtures') / 'lesson_units'
LEGACY = json.loads((Path(__file__).with_name('fixtures') / 'legacy_lessons_v1.json').read_text())
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/lesson-units-api.json'
HEADERS = {'origin': 'http://localhost:3000'}
UNITS = ('py.u01', 'fixture.u01', 'fixture.u02')
CHECKED = ('fixture.add-two', 'fixture.double')
# Expected output of the hidden cases: it must never be in an answer the page receives.
HIDDEN_EXPECTED = ('6144', '42')
NEW_FIELDS = {'course', 'unit', 'check'}


def serve_fixture(setattr=setattr, setitem=lambda d, k, v: d.__setitem__(k, v)):
    """Serve the TEST FIXTURE lessons through the real API, next to the real content."""
    catalog, lessons = content.load(FIXTURE_DIR)
    setattr(main, 'UNIT_LESSONS', {**main.UNIT_LESSONS, **content.unit_lessons(catalog, lessons)})
    setattr(main, 'CATALOG_VIEW', {**main.CATALOG_VIEW, 'courses': main.CATALOG_VIEW['courses'] + content.catalog_view(catalog, lessons)['courses']})
    for lesson_id, lesson in lessons.items():
        setitem(main.CONTENT, lesson_id, lesson)


def api_with_fixture():
    Base.metadata.create_all(engine)
    serve_fixture()
    return TestClient(app)


def recorded_gets(client):
    return {'catalog': client.get('/api/catalog').json(),
            'units': {unit: client.get(f'/api/units/{unit}/lessons').json() for unit in UNITS},
            'plans': {lesson: client.get(f'/api/checks/{lesson}').json() for lesson in CHECKED}}


def judge_answer(client, request):
    return client.post('/api/check', json=request, headers=HEADERS).json()


@pytest.fixture
def client(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    serve_fixture(monkeypatch.setattr, monkeypatch.setitem)
    test_client = TestClient(app)
    test_client.cookies.clear()
    return test_client


RECORDED = json.loads(RECORDED_FILE.read_text())


# The answers the browser tests use are the real API's

def test_the_recorded_answers_are_the_real_apis(client):
    gets = recorded_gets(client)
    assert {key: RECORDED[key] for key in gets} == gets
    assert len(RECORDED['scenarios']) >= 9
    for scenario in RECORDED['scenarios']:
        assert judge_answer(client, scenario['request']) == scenario['response'], scenario['name']


def test_the_recorded_scenarios_cover_every_result_state():
    results = {s['name']: s['response']['result'] for s in RECORDED['scenarios']}
    assert set(results.values()) == {'passed', 'needs_work', 'execution_error', 'unsupported', 'service_error'}
    assert {s['response']['failed']['reason'] for s in RECORDED['scenarios'] if s['response']['failed']} >= {'wrong_output', 'error', 'timeout', 'output_limit', 'missing_input', 'unsupported'}


def test_no_answer_the_page_receives_holds_a_hidden_expected_output():
    answers = json.dumps({key: RECORDED[key] for key in ('catalog', 'units', 'plans')}) + json.dumps([s['response'] for s in RECORDED['scenarios']])
    for value in HIDDEN_EXPECTED:
        assert f'"{value}"' not in answers and f'\\n{value}' not in answers and f' {value}' not in answers, value
    # Hidden cases are in the plans without their expected output, and lessons carry no cases at all.
    for plan in RECORDED['plans'].values():
        assert all(('expected' in case) == (case['visibility'] == 'visible') for case in plan['cases'])
    assert 'cases' not in json.dumps(RECORDED['units'])


# Lessons per unit

def test_unit_1_per_unit_is_the_original_lessons_with_three_fields_added(client):
    assert client.get('/api/lessons').json() == LEGACY  # unchanged, for pages from before UI-05
    per_unit = client.get('/api/units/py.u01/lessons').json()
    assert [lesson['id'] for lesson in per_unit] == [lesson['id'] for lesson in LEGACY]
    for new, old in zip(per_unit, LEGACY):
        assert set(new) - set(old) == NEW_FIELDS
        assert {key: new[key] for key in old} == old  # every original field, unchanged
        assert {key: new[key] for key in NEW_FIELDS} == {'course': 'py', 'unit': 'py.u01', 'check': 'bounded-story'}


def test_the_real_content_serves_only_released_units():
    assert list(main.UNIT_LESSONS) == ['py.u01', 'py.u02', 'py.u03']
    assert TestClient(app).get('/api/units/py.u04/lessons').status_code == 404  # coming soon
    assert TestClient(app).get('/api/units/nope/lessons').status_code == 404


def test_a_second_unit_is_served_on_its_own(client):
    second = client.get('/api/units/fixture.u02/lessons').json()
    assert [(l['id'], l['course'], l['unit'], l['check']) for l in second] == [('fixture.double', 'fixture', 'fixture.u02', 'browser-tests')]
    first = client.get('/api/units/fixture.u01/lessons').json()
    assert [l['id'] for l in first] == ['fixture.add-two']
    # The unit is found through the catalog, which lists both units.
    fixture = next(c for c in client.get('/api/catalog').json()['courses'] if c['id'] == 'fixture')
    assert [(u['id'], [l['id'] for l in u['lessons']]) for u in fixture['units']] == [('fixture.u01', ['fixture.add-two']), ('fixture.u02', ['fixture.double'])]


# Rule IDs for wrong output, and hints tagged with them

def test_wrong_output_names_its_case_as_a_rule(client):
    scenario = next(s for s in RECORDED['scenarios'] if s['name'] == 'needs_work')
    response = judge_answer(client, scenario['request'])
    assert (response['result'], response['rule'], response['failed']['id']) == ('needs_work', 'fixture.add-two.case.negative', 'negative')
    hidden = next(s for s in RECORDED['scenarios'] if s['name'] == 'hidden case fails')
    assert judge_answer(client, hidden['request'])['rule'] == 'fixture.add-two.case.large'
    # Only wrong output names a rule; the other results keep rule empty.
    for s in RECORDED['scenarios']:
        if s['response']['failed'] and s['response']['failed']['reason'] != 'wrong_output':
            assert s['response']['rule'] is None, s['name']


def test_a_hint_can_be_tagged_with_a_case_of_its_own_check(tmp_path):
    root = tmp_path / 'lesson_units'
    shutil.copytree(FIXTURE_DIR, root)
    path = root / 'fixture/u01/fixture.add-two.json'
    data = json.loads(path.read_text())
    data['tasks'][4]['error_hints'].append({'tags': ['fixture.add-two.case.nope'], 'text': 'No such case.'})
    path.write_text(json.dumps(data))
    with pytest.raises(content.ContentError, match='hint tag fixture.add-two.case.nope is not a Python error'):
        content.load(root)


# Saved progress, XP and badges

def sign_in_student():
    with Session(engine) as db:
        user = User(subject='kid', email='kid@example.com', role='student')
        db.add(user)
        db.flush()
        token, now = secrets.token_urlsafe(32), int(sessions.clock())
        db.add(UserSession(id=sessions.digest(token), user_id=user.id, created=now, last_seen=now, expires=now + sessions.ABSOLUTE))
        db.commit()
        uid = user.id
    return uid, TimestampSigner(os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps({'sid': token}).encode())).decode()


def test_a_learner_who_passed_before_keeps_xp_and_badges_and_gets_nothing_twice(client):
    uid, cookie = sign_in_student()
    client.cookies.set('session', cookie, domain='testserver.local', path='/')
    hello = {'lesson_id': 'hello', 'code': 'print("A forest.")\nprint("A dragon!")', 'output': 'A forest.\nA dragon!\n'}
    assert client.post('/api/attempts', json=hello, headers=HEADERS).json()['result'] == 'passed'
    before = client.get('/api/awards').json()
    assert before['xp'] == 100 and client.get('/api/progress').json() == ['hello']
    # Loading lessons per unit changes nothing that was earned.
    client.get('/api/units/py.u01/lessons')
    assert client.get('/api/awards').json() == before
    # Passing again, and passing a browser-check lesson twice, award once each.
    assert client.post('/api/attempts', json=hello, headers=HEADERS).json()['result'] == 'passed'
    passing = next(s for s in RECORDED['scenarios'] if s['name'] == 'passed')['request']
    for _ in range(2):
        assert client.post('/api/attempts', json=passing, headers=HEADERS).json()['result'] == 'passed'
    with Session(engine) as db:
        assert sorted((a.task_id, a.xp) for a in db.scalars(select(XpAward))) == [('fixture.add-two.challenge', 100), ('hello.challenge', 100)]
        assert db.scalar(select(func.count()).select_from(BadgeAward)) == 2
    assert client.get('/api/awards').json()['xp'] == 200

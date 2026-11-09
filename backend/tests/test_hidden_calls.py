"""Hidden function calls (decision 28, docs/plan/browser-checks.md sections 5 and 8).

Uses the TEST FIXTURE lesson in tests/fixtures/hidden_calls/, never shown to learners. The reports here are
what the browser sends for these programs; frontend/tests/hidden-calls.spec.ts proves it by running them in
Pyodide and comparing. To rewrite the recording: WRITE_HIDDEN_CALLS=1 python -m pytest -q tests/test_hidden_calls.py
"""
import os
import tempfile
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + tempfile.mktemp(suffix='.db'))
os.environ.setdefault('SESSION_SECRET', 'test-secret-that-is-at-least-thirty-two-characters')
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import content, main
from app.db import Base
from app.main import app, engine

FIXTURE_DIR = Path(__file__).with_name('fixtures') / 'hidden_calls'
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/hidden-calls-api.json'
LESSON_ID, UNIT_ID = 'fixture.hidden-calls', 'fixture.u10'
HEADERS = {'origin': 'http://localhost:3000'}
ANSWER = '171'
client = TestClient(app)


def run(case_id, returned):
    return {'id': case_id, 'status': 'ok', 'output': '', 'error_type': None, 'line': None, 'returned': returned}


def request(code, *runs):
    return {'lesson_id': LESSON_ID, 'code': code, 'output': '', 'inputs': [], 'runs': list(runs)}


SCENARIOS = [
    ('passed', request('def triple(n):\n    return n * 3\n', run('small', '6'), run('other', ANSWER))),
    ('hard-coded', request('def triple(n):\n    return 6\n', run('small', '6'), run('other', '6'))),
]


@pytest.fixture
def lesson(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    catalog, lessons = content.load(FIXTURE_DIR)
    monkeypatch.setattr(main, 'UNIT_LESSONS', {**main.UNIT_LESSONS, **content.unit_lessons(catalog, lessons)})
    monkeypatch.setattr(main, 'CATALOG_VIEW', {**main.CATALOG_VIEW, 'courses': main.CATALOG_VIEW['courses'] + content.catalog_view(catalog, lessons)['courses']})
    for lesson_id, found in lessons.items():
        monkeypatch.setitem(main.CONTENT, lesson_id, found)
    client.cookies.clear()
    return lessons[LESSON_ID]


def post(body):
    return client.post('/api/check', json=body, headers=HEADERS).json()


def test_the_plan_sends_the_arguments_and_never_the_answer(lesson):
    case = client.get(f'/api/checks/{LESSON_ID}').json()['cases'][1]
    assert case['call']['args'] == [57] and case['visibility'] == 'hidden'
    assert 'returns' not in case and 'expected' not in case and ANSWER not in json.dumps(case)


def test_a_correct_function_passes(lesson):
    assert post(SCENARIOS[0][1])['result'] == 'passed'


def test_a_hard_coded_function_fails_on_the_hidden_call_and_gives_nothing_away(lesson):
    answer = post(SCENARIOS[1][1])
    assert answer['result'] == 'needs_work' and answer['rule'] == f'{LESSON_ID}.case.other'
    assert answer['failed']['visibility'] == 'hidden' and 'expected_value' not in answer['failed'] and 'actual_value' not in answer['failed']
    text = json.dumps(answer)
    assert ANSWER not in text and '57' not in text


def test_the_answer_is_in_no_response(lesson):
    for path in ('/api/catalog', f'/api/units/{UNIT_ID}/lessons', f'/api/checks/{LESSON_ID}'):
        assert ANSWER not in client.get(path).text


def test_no_real_lesson_uses_a_hidden_call_yet():
    _, lessons = content.load()
    for found in lessons.values():
        check = found.task('challenge').check
        assert not (check and any(c.call and c.visibility == 'hidden' for c in check.cases)), found.id


def test_the_recorded_answers_are_the_real_apis(lesson):
    recorded = {'catalog': client.get('/api/catalog').json(), 'units': {UNIT_ID: client.get(f'/api/units/{UNIT_ID}/lessons').json()},
                'plans': {LESSON_ID: client.get(f'/api/checks/{LESSON_ID}').json()},
                'scenarios': [{'name': name, 'request': body, 'response': post(body)} for name, body in SCENARIOS]}
    if os.environ.get('WRITE_HIDDEN_CALLS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded

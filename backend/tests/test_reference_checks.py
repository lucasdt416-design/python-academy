"""Learner tests against reference programs (ENG-10, docs/plan/browser-checks.md section 11).

Uses the TEST FIXTURE lesson in tests/fixtures/reference_checks/, never shown to learners. tests/case_runner.py
plays the browser's part; frontend/tests/reference-checks.spec.ts runs the same programs in Pyodide, and the
requests must match exactly. To rewrite the recording: WRITE_REFERENCE_CHECKS=1 python -m pytest -q tests/test_reference_checks.py
"""
import os
import tempfile
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + tempfile.mktemp(suffix='.db'))
os.environ.setdefault('SESSION_SECRET', 'test-secret-that-is-at-least-thirty-two-characters')
import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import content, main
from app.db import Base
from app.main import app, engine
from case_runner import reports

FIXTURE_DIR = Path(__file__).with_name('fixtures') / 'reference_checks'
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/reference-checks-api.json'
LESSON_ID, UNIT_ID = 'fixture.tests', 'fixture.u11'
HEADERS = {'origin': 'http://localhost:3000'}
GOOD = 'assert score(7, 7) == 10\nassert score(9, 7) == 5\nassert score(20, 7) == 0\n'
client = TestClient(app)

SCENARIOS = [
    ('passed', GOOD),
    ('always true', 'assert True\n'),
    ('no tests', 'x = 1\n'),
    ('wrong test', 'assert score(7, 7) == 11\n'),
    ('misses the hidden bug', 'assert score(7, 7) == 10\nassert score(9, 7) == 5\n'),
    ('name error', 'assert scor(7, 7) == 10\n'),
    ('prints only', 'print(score(7, 7))\n'),
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


def body(lesson, code):
    runs = [r.model_dump() for r in reports(lesson, [code])[0]]
    return {'lesson_id': LESSON_ID, 'code': code, 'output': runs[0]['output'], 'inputs': [], 'runs': runs}


def judged(lesson, code):
    return client.post('/api/check', json=body(lesson, code), headers=HEADERS).json()


def test_good_tests_pass_and_other_correct_ones_too(lesson):
    for code in (GOOD, 'def check(g, s, want):\n    assert score(g, s) == want\ncheck(7, 7, 10)\ncheck(9, 7, 5)\ncheck(20, 7, 0)\n', lesson.task('challenge').other_ways[0].code):
        assert judged(lesson, code)['result'] == 'passed'


@pytest.mark.parametrize('code,case_id', [('assert True\n', 'always-ten'), ('x = 1\n', 'always-ten'), ('print(score(7, 7))\n', 'always-ten')])
def test_tests_that_catch_nothing_fail(lesson, code, case_id):
    answer = judged(lesson, code)
    assert (answer['result'], answer['failed']['reason'], answer['rule']) == ('needs_work', 'bug_missed', f'{LESSON_ID}.case.{case_id}')


def test_a_test_that_fails_on_correct_code_is_named_as_that(lesson):
    answer = judged(lesson, 'assert score(7, 7) == 11\n')
    assert (answer['result'], answer['failed']['reason'], answer['rule']) == ('needs_work', 'test_failed_correct', f'{LESSON_ID}.case.correct')
    assert 'which is correct' in answer['feedback']


def test_a_typo_is_a_python_error_and_not_a_bug_caught(lesson):
    answer = judged(lesson, 'assert scor(7, 7) == 10\n')
    assert answer['result'] == 'execution_error' and answer['failed']['error_type'] == 'NameError' and answer['failed']['line'] == 1


def test_a_missed_hidden_bug_is_named_by_its_description_only(lesson):
    answer = judged(lesson, 'assert score(7, 7) == 10\nassert score(9, 7) == 5\n')
    assert answer['failed']['visibility'] == 'hidden' and answer['rule'] == f'{LESSON_ID}.case.far'
    assert 'a scorer you cannot see (a hidden test case)' in answer['feedback']
    assert 'return 10 if' not in json.dumps(answer)


def test_a_crash_inside_a_broken_reference_counts_as_caught(lesson):
    runs = [r.model_dump() for r in reports(lesson, [GOOD])[0]]
    runs[1].update(status='error', error_type='TypeError', line=None)
    assert client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': GOOD, 'output': '', 'runs': runs}, headers=HEADERS).json()['result'] == 'passed'


def test_a_refused_import_is_not_counted_as_a_bug_caught(lesson):
    runs = [r.model_dump() for r in reports(lesson, [GOOD])[0]]
    for run in runs:
        run.update(status='error', error_type='ModuleNotFoundError', line=1)
    assert client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': 'import os\n', 'output': '', 'runs': runs}, headers=HEADERS).json()['result'] == 'unsupported'


def test_a_timeout_is_never_a_pass(lesson):
    answer = judged(lesson, 'while True:\n    pass\n')
    assert answer['result'] == 'execution_error' and answer['failed']['reason'] == 'timeout'


def test_the_plan_sends_references_and_hides_only_the_hidden_expected_result(lesson):
    plan = client.get(f'/api/checks/{LESSON_ID}').json()
    assert [c.get('test_should') for c in plan['cases']] == ['pass', 'fail', 'fail', None]
    assert all('reference' in c and 'expected' not in c for c in plan['cases'])


def test_ordinary_plans_are_unchanged():
    assert all('reference' not in c and 'test_should' not in c for c in client.get('/api/checks/py.for-range').json()['cases'])


def test_no_real_lesson_uses_references_yet():
    _, lessons = content.load()
    for found in lessons.values():
        check = found.task('challenge').check
        assert not (check and any(c.reference for c in check.cases)), found.id


# Content validation

def tree_with(tmp_path, change):
    root = tmp_path / 'content'
    shutil.copytree(FIXTURE_DIR, root)
    path = root / 'fixture/u11/fixture.tests.json'
    data = json.loads(path.read_text())
    change(data['tasks'][4]['check']['cases'])
    path.write_text(json.dumps(data))
    return root


@pytest.mark.parametrize('change,message', [
    (lambda c: c[0].pop('test_should'), 'together'),
    (lambda c: c[1].pop('reference'), 'together'),
    (lambda c: c[0].update(test_should='fail'), 'first case must be visible'),
    (lambda c: c[0].update(visibility='hidden', description='correct code'), 'first case must be visible'),
    (lambda c: [case.update(test_should='pass') for case in c], 'needs a broken reference'),
    (lambda c: c[1].update(expected='x'), 'compares nothing else'),
    (lambda c: c[1].update(reference='def ('), 'syntax error'),
    (lambda c: c.append({'id': 'plain', 'description': 'plain', 'expected': 'x'}), 'all must'),
], ids=['no-should', 'no-reference', 'first-fails', 'first-hidden', 'no-broken', 'with-expected', 'syntax', 'mixed'])
def test_bad_reference_cases_stop_content_loading(tmp_path, change, message):
    with pytest.raises(content.ContentError, match=message):
        content.load(tree_with(tmp_path, change))


# The answers the browser tests use are the real API's

def test_the_recorded_answers_are_the_real_apis(lesson):
    recorded = {'catalog': client.get('/api/catalog').json(), 'units': {UNIT_ID: client.get(f'/api/units/{UNIT_ID}/lessons').json()},
                'plans': {LESSON_ID: client.get(f'/api/checks/{LESSON_ID}').json()}, 'scenarios': []}
    for name, code in SCENARIOS:
        request = body(lesson, code)
        recorded['scenarios'].append({'name': name, 'request': request, 'response': client.post('/api/check', json=request, headers=HEADERS).json()})
    if os.environ.get('WRITE_REFERENCE_CHECKS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded

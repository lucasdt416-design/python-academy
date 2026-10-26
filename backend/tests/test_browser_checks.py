"""Browser behaviour checks (ENG-03): content schema, the API's judgement, and hidden cases kept hidden.

Uses the TEST FIXTURE lesson in tests/fixtures/browser_checks/, which is never shown to learners.
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
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import content, main, sessions
from app.db import Base, User, UserSession, XpAward
from app.main import app, engine

FIXTURE_DIR = Path(__file__).with_name('fixtures') / 'browser_checks'
LESSON_FILE = FIXTURE_DIR / 'fixture' / 'u01' / 'fixture.sum-two.json'
LESSON_ID = 'fixture.sum-two'
HIDDEN_EXPECTED = '6144'
HIDDEN_INPUTS = ['4096', '2048']
HEADERS = {'origin': 'http://localhost:3000'}
client = TestClient(app)


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / 'browser_checks'
    shutil.copytree(FIXTURE_DIR, root)
    return root


def edit_check(root, change):
    path = root / 'fixture' / 'u01' / 'fixture.sum-two.json'
    data = json.loads(path.read_text())
    change(data['tasks'][4])
    path.write_text(json.dumps(data))


def invalid(root, message):
    with pytest.raises(content.ContentError) as error:
        content.load(root)
    assert message in str(error.value)


# Content schema

def test_the_fixture_lesson_is_valid_and_never_in_real_content():
    _, lessons = content.load(FIXTURE_DIR)
    check = lessons[LESSON_ID].task('challenge').check
    assert [(c.id, c.visibility) for c in check.cases] == [('small', 'visible'), ('negative', 'visible'), ('large', 'hidden')]
    _, real = content.load()
    assert LESSON_ID not in real and LESSON_ID not in main.CONTENT
    # Unit 1 keeps its server-side checker and has no browser check.
    assert all(lesson.task('challenge').check is None for lesson in real.values())


@pytest.mark.parametrize('change,message', [
    (lambda t: t.pop('check'), 'needs a check exactly when its validator is browser-tests'),
    (lambda t: t['validator'].update(id='bounded-story'), 'needs a check exactly when its validator is browser-tests'),
    (lambda t: t['validator'].update(version=2), 'uses unknown validator browser-tests v2'),
    (lambda t: t['check']['cases'][1].update(id='small'), 'duplicate check case IDs'),
    (lambda t: [c.update(visibility='hidden', description='some numbers') for c in t['check']['cases']], 'at least one visible check case'),
    (lambda t: t['check'].update(require=['goto']), 'unknown construct goto'),
    (lambda t: t['check'].update(forbid=['int()']), 'both requires and forbids int()'),
    (lambda t: t['check']['cases'][2].update(description='4096 and 2048'), 'hidden case large: its description shows'),
    (lambda t: t['check']['cases'][2].update(description='numbers that add up to 6144'), 'hidden case large: its description shows'),
    (lambda t: t['check'].update(time_limit_ms=60000), 'time_limit_ms'),
    (lambda t: t['check']['cases'][0].update(inputs=['x' * 501]), 'inputs'),
    (lambda t: t['check'].update(cases=t['check']['cases'] * 4), 'cases'),
    (lambda t: t['check']['cases'][0].update(hidden=True), 'hidden'),  # a typo for visibility is rejected
    (lambda t: t['check']['cases'][0].update(expected='x' * 10001), 'expected'),
], ids=['no-check', 'check-without-validator', 'unknown-version', 'duplicate-ids', 'no-visible', 'unknown-construct',
        'require-and-forbid', 'description-shows-input', 'description-shows-expected', 'time-limit', 'long-input',
        'too-many-cases', 'unknown-field', 'long-expected'])
def test_invalid_checks_stop_content_loading(tree, change, message):
    edit_check(tree, change)
    invalid(tree, message)


# The API judges what the browser reported

@pytest.fixture
def fixture_lesson(monkeypatch):
    _, lessons = content.load(FIXTURE_DIR)
    monkeypatch.setitem(main.CONTENT, LESSON_ID, lessons[LESSON_ID])
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    client.cookies.clear()
    return lessons[LESSON_ID]


GOOD = 'a = int(input())\nb = int(input())\nprint(a + b)'


def run(case_id, status='ok', output='', error_type=None, line=None):
    return {'id': case_id, 'status': status, 'output': output, 'error_type': error_type, 'line': line}


def correct():
    return [run('small', output='5\n'), run('negative', output='6\n'), run('large', output='6144\n')]


def check(code=GOOD, runs=None):
    response = client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': code, 'output': '', 'runs': correct() if runs is None else runs}, headers=HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def test_a_correct_solution_passes(fixture_lesson):
    body = check()
    assert (body['passed'], body['result'], body['assessment'], body['failed']) == (True, 'passed', 'browser_tests', None)
    assert body['feedback'].startswith('Your program printed the expected output for all 3 test cases, including 1 hidden case.')
    assert '?' in body['feedback']
    assert body['cases'] == [{'id': 'small', 'visibility': 'visible', 'status': 'passed'},
                             {'id': 'negative', 'visibility': 'visible', 'status': 'passed'},
                             {'id': 'large', 'visibility': 'hidden', 'status': 'passed'}]


def test_trailing_spaces_blank_lines_and_windows_newlines_do_not_matter(fixture_lesson):
    assert check(runs=[run('small', output='5   \r\n\n'), run('negative', output='6'), run('large', output='6144\n\n')])['passed']


def test_a_wrong_answer_on_a_visible_case_shows_the_first_different_line(fixture_lesson):
    body = check(runs=[run('small', output='-1\n'), run('negative', output='14\n'), run('large', output='2048\n')])
    assert body['result'] == 'needs_work'
    assert body['feedback'] == 'For the numbers 2 and 3, line 1 should be "5", but your program printed "-1".'
    assert body['failed'] == {'id': 'small', 'visibility': 'visible', 'description': 'the numbers 2 and 3', 'reason': 'wrong_output',
                              'error_type': None, 'line': None, 'line_number': 1, 'expected_line': '5', 'actual_line': '-1'}
    assert [c['status'] for c in body['cases']] == ['failed', 'failed', 'failed']


@pytest.mark.parametrize('output,message', [
    ('', 'For the numbers 2 and 3, your program stopped printing before line 1, which should be "5".'),
    ('5\nextra\n', 'For the numbers 2 and 3, your program printed an extra line 2: "extra".'),
])
def test_missing_and_extra_lines_are_described(fixture_lesson, output, message):
    assert check(runs=[run('small', output=output), run('negative', output='6'), run('large', output='6144')])['feedback'] == message


def test_a_wrong_answer_only_on_the_hidden_case_reveals_nothing_about_it(fixture_lesson):
    # For example a program that only works for small numbers.
    body = check(runs=[run('small', output='5'), run('negative', output='6'), run('large', output='9999')])
    assert body['result'] == 'needs_work'
    assert body['feedback'] == ('Your program printed something different for two larger numbers (a hidden test case). '
                                'Check that it works from the replies it is given, not from fixed values.')
    assert body['failed'] == {'id': 'large', 'visibility': 'hidden', 'description': 'two larger numbers', 'reason': 'wrong_output', 'error_type': None, 'line': None}
    assert HIDDEN_EXPECTED not in json.dumps(body) and '9999' not in json.dumps(body)


def test_an_endless_loop_stopped_by_the_browser_is_an_execution_error(fixture_lesson):
    body = check(code='while True:\n    pass\nint(input())', runs=[run('small', 'timeout'), run('negative', 'not_run'), run('large', 'not_run')])
    assert body['result'] == 'execution_error'
    assert body['feedback'] == ('Your program was still running after 3 seconds on the numbers 2 and 3, so it was stopped. '
                                'Check for a loop that never ends.')
    assert body['failed']['reason'] == 'timeout'
    assert [c['status'] for c in body['cases']] == ['failed', 'not_run', 'not_run']


def test_runaway_output_capped_by_the_browser_is_an_execution_error(fixture_lesson):
    body = check(code='while True:\n    print(int(input()))', runs=[run('small', 'output_limit', 'x' * 10000)] + [run(i, 'output_limit') for i in ('negative', 'large')])
    assert body['result'] == 'execution_error'
    assert body['feedback'].startswith('Your program printed more than 10,000 characters on the numbers 2 and 3')
    assert body['failed']['reason'] == 'output_limit'


def test_an_error_names_its_type_line_and_case_for_the_feedback_engine(fixture_lesson):
    body = check(code='a = int(input())\nprint(a + missing)', runs=[run(i, 'error', error_type='NameError', line=2) for i in ('small', 'negative', 'large')])
    assert body['result'] == 'execution_error'
    assert body['feedback'].startswith('Python stopped with NameError on line 2 while running the numbers 2 and 3.')
    assert body['failed'] == {'id': 'small', 'visibility': 'visible', 'description': 'the numbers 2 and 3', 'reason': 'error', 'error_type': 'NameError', 'line': 2}


def test_asking_for_too_many_replies_needs_work(fixture_lesson):
    body = check(code='int(input())\nint(input())\nint(input())', runs=[run(i, 'error', error_type='EOFError', line=3) for i in ('small', 'negative', 'large')])
    assert (body['result'], body['failed']['reason']) == ('needs_work', 'missing_input')
    assert 'asked for more replies than the numbers 2 and 3 gives' in body['feedback']


def test_a_module_the_browser_does_not_have_is_unsupported(fixture_lesson):
    body = check(code='int(input())\nprint(int(input()))', runs=[run(i, 'error', error_type='ModuleNotFoundError', line=1) for i in ('small', 'negative', 'large')])
    assert (body['result'], body['failed']['reason']) == ('unsupported', 'unsupported')


def test_a_syntax_error_is_found_by_parsing_on_the_server(fixture_lesson):
    body = check(code='a = int(input()\nprint(a)', runs=[run(i, 'error', error_type='SyntaxError', line=1) for i in ('small', 'negative', 'large')])
    assert body['result'] == 'execution_error'
    assert body['failed'] == {'id': None, 'reason': 'error', 'error_type': 'SyntaxError', 'line': 1}


@pytest.mark.parametrize('code,message,construct', [
    ('import math\nprint(int(input()) + int(input()))', 'This task asks you not to use import here.', 'import'),
    ('print(5)', 'This task asks you to use input().', 'input()'),
    ('a = input()\nb = input()\nprint(5)', 'This task asks you to use int().', 'int()'),
])
def test_required_and_forbidden_constructs(fixture_lesson, code, message, construct):
    body = check(code=code)
    assert (body['result'], body['feedback'], body['failed']) == ('needs_work', message, {'id': None, 'reason': 'construct', 'construct': construct})


@pytest.mark.parametrize('runs', [
    [],
    [run('small', output='5'), run('negative', output='6')],
    [run('large', output='6144'), run('small', output='5'), run('negative', output='6')],
    [run('small', 'unavailable'), run('negative', 'unavailable'), run('large', 'unavailable')],
    [run('small', output='5'), run('negative', 'not_run'), run('large', 'not_run')],
    None,
], ids=['none', 'missing-case', 'reordered', 'python-unavailable', 'not-run-without-failure', 'no-runs-field'])
def test_reports_that_do_not_match_the_check_are_a_service_error(fixture_lesson, runs):
    payload = {'lesson_id': LESSON_ID, 'code': GOOD, 'output': ''}
    if runs is not None:
        payload['runs'] = runs
    body = client.post('/api/check', json=payload, headers=HEADERS).json()
    assert (body['result'], body['passed']) == ('service_error', False)
    assert body['feedback'].startswith('Unable to assess this right now.')


def test_reports_are_bounded(fixture_lesson):
    too_long = client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': GOOD, 'output': '', 'runs': [run('small', output='x' * 10001)]}, headers=HEADERS)
    too_many = client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': GOOD, 'output': '', 'runs': [run('small')] * 11}, headers=HEADERS)
    odd_status = client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': GOOD, 'output': '', 'runs': [run('small', 'passed')]}, headers=HEADERS)
    odd_type = client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': GOOD, 'output': '', 'runs': [run('small', 'error', error_type='<script>')]}, headers=HEADERS)
    assert [r.status_code for r in (too_long, too_many, odd_status, odd_type)] == [422, 422, 422, 422]


def test_the_server_never_runs_the_learners_code(fixture_lesson, tmp_path):
    marker = tmp_path / 'ran.txt'
    code = f'open({str(marker)!r}, "w").write("ran")\nprint(int(input()) + int(input()))'
    check(code=code)
    assert not marker.exists()


def student_session():
    with Session(engine) as db:
        user = User(subject='s', email='student@example.com', role='student')
        db.add(user)
        db.flush()
        token = secrets.token_urlsafe(32)
        now = int(sessions.clock())
        db.add(UserSession(id=sessions.digest(token), user_id=user.id, created=now, last_seen=now, expires=now + sessions.ABSOLUTE))
        db.commit()
        uid = user.id
    cookie = TimestampSigner(os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps({'sid': token}).encode())).decode()
    client.cookies.set('session', cookie, domain='testserver.local', path='/')
    return uid


def test_saved_attempts_use_the_same_judgement_and_award_once(fixture_lesson):
    uid = student_session()
    wrong = client.post('/api/attempts', json={'lesson_id': LESSON_ID, 'code': GOOD, 'output': '5\n', 'runs': [run('small', output='5'), run('negative', output='6'), run('large', output='1')]}, headers=HEADERS).json()
    assert wrong['result'] == 'needs_work' and wrong['failed']['visibility'] == 'hidden'
    for _ in range(2):
        assert client.post('/api/attempts', json={'lesson_id': LESSON_ID, 'code': GOOD, 'output': '5\n', 'runs': correct()}, headers=HEADERS).json()['result'] == 'passed'
    with Session(engine) as db:
        assert [(a.task_id, a.xp) for a in db.scalars(select(XpAward).where(XpAward.user_id == uid))] == [('fixture.sum-two.challenge', 100)]


# Hidden cases are not leaked in any API response

def test_the_check_plan_has_no_expected_output_for_hidden_cases(fixture_lesson):
    plan = client.get(f'/api/checks/{LESSON_ID}').json()
    assert plan == {
        'lesson_id': LESSON_ID, 'task_id': 'fixture.sum-two.challenge', 'version': 1, 'time_limit_ms': 3000, 'output_limit': 10000,
        'cases': [
            {'id': 'small', 'visibility': 'visible', 'description': 'the numbers 2 and 3', 'inputs': ['2', '3'], 'expected': '5'},
            {'id': 'negative', 'visibility': 'visible', 'description': '10 and -4', 'inputs': ['10', '-4'], 'expected': '6'},
            # The browser needs the inputs to run the case; the expected output stays on the server.
            {'id': 'large', 'visibility': 'hidden', 'description': 'two larger numbers', 'inputs': HIDDEN_INPUTS},
        ]}
    assert client.get('/api/checks/hello').status_code == 404
    assert client.get('/api/checks/no-such-lesson').status_code == 404


def every_response(path_lesson):
    """The body of every GET route, signed out and as a student, plus checks and attempts with many reports."""
    bodies = {}
    for signed_in in (False, True):
        client.cookies.clear()
        if signed_in:
            student_session()
        for route in app.routes:
            if isinstance(route, APIRoute) and 'GET' in route.methods and not route.path.startswith('/auth'):
                path = route.path.replace('{lesson_id}', path_lesson)
                bodies[f'GET {path} signed_in={signed_in}'] = client.get(path).text
        for name, runs in {
            'passing': correct(),
            'hidden-wrong': [run('small', output='5'), run('negative', output='6'), run('large', output='1')],
            'hidden-timeout': [run('small', output='5'), run('negative', output='6'), run('large', 'timeout')],
            'hidden-error': [run('small', output='5'), run('negative', output='6'), run('large', 'error', error_type='ValueError', line=1)],
            'hidden-output-limit': [run('small', output='5'), run('negative', output='6'), run('large', 'output_limit')],
        }.items():
            for endpoint in ('check', 'attempts'):
                response = client.post(f'/api/{endpoint}', json={'lesson_id': path_lesson, 'code': GOOD, 'output': '', 'runs': runs}, headers=HEADERS)
                bodies[f'POST /api/{endpoint} {name} signed_in={signed_in}'] = response.text
    return bodies


def test_hidden_expected_output_is_in_no_response_and_hidden_inputs_only_in_the_plan(fixture_lesson):
    bodies = every_response(LESSON_ID)
    assert len(bodies) > 30
    for where, body in bodies.items():
        assert HIDDEN_EXPECTED not in body, where
        if not where.startswith(f'GET /api/checks/{LESSON_ID}'):
            assert not any(value in body for value in HIDDEN_INPUTS), where


def test_unit_1_checks_are_unchanged(fixture_lesson):
    body = client.post('/api/check', json={'lesson_id': 'hello', 'code': 'print("A forest.")\nprint("A dragon!")', 'output': 'A forest.\nA dragon!\n'}, headers=HEADERS).json()
    assert set(body) == {'passed', 'result', 'feedback', 'assessment'}
    assert (body['passed'], body['assessment']) == (True, 'browser_practice')

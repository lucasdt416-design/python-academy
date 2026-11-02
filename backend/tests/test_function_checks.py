"""Function-call checks (ENG-06, docs/plan/browser-checks.md section 8).

Uses the TEST FIXTURE lesson in tests/fixtures/function_checks/, which is never shown to learners.
The browser's part runs in Pyodide in frontend/tests/function-checks.spec.ts; here the API gets the
reports the browser sends, and frontend/tests/fixtures/function-checks-api.json is proved to hold
exactly the API's answers.
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

from app import browser_checks, content, main
from app.browser_checks import same_value
from app.db import Base
from app.main import app, engine

FIXTURE_DIR = Path(__file__).with_name('fixtures') / 'function_checks'
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/function-checks-api.json'
LESSON_ID = 'fixture.calls'
UNIT_ID = 'fixture.u09'
HEADERS = {'origin': 'http://localhost:3000'}
GOOD = 'def double(n):\n    return n * 2\ndef share(t, p):\n    return t / p\ndef greet(name):\n    print("Hello,", name)\n'
client = TestClient(app)


def serve(setattr=setattr, setitem=lambda d, k, v: d.__setitem__(k, v)):
    catalog, lessons = content.load(FIXTURE_DIR)
    setattr(main, 'UNIT_LESSONS', {**main.UNIT_LESSONS, **content.unit_lessons(catalog, lessons)})
    setattr(main, 'CATALOG_VIEW', {**main.CATALOG_VIEW, 'courses': main.CATALOG_VIEW['courses'] + content.catalog_view(catalog, lessons)['courses']})
    for lesson_id, lesson in lessons.items():
        setitem(main.CONTENT, lesson_id, lesson)


@pytest.fixture
def lesson(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    serve(monkeypatch.setattr, monkeypatch.setitem)
    client.cookies.clear()
    return main.CONTENT[LESSON_ID]


def run(case_id, status='ok', output='', returned=None, error_type=None, line=None):
    report = {'id': case_id, 'status': status, 'output': output, 'error_type': error_type, 'line': line}
    return {**report, 'returned': returned} if returned is not None else report


def correct(**replace):
    runs = {'double-two': run('double-two', returned='4'), 'double-big': run('double-big', returned='42'),
            'share-third': run('share-third', returned='0.3333333333333333'),
            'greet-kai': run('greet-kai', output='Hello, Kai\n', returned='null')}
    runs.update(replace)
    return list(runs.values())


def check(runs, code=GOOD):
    response = client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': code, 'output': '', 'runs': runs}, headers=HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def test_the_fixture_is_valid_and_never_in_real_content():
    _, lessons = content.load(FIXTURE_DIR)
    assert LESSON_ID in lessons and LESSON_ID not in content.load()[1]


# The plan

def test_the_plan_gives_the_browser_the_call_and_nothing_extra_for_ordinary_cases(lesson):
    plan = client.get(f'/api/checks/{LESSON_ID}').json()
    assert plan['cases'][0] == {'id': 'double-two', 'visibility': 'visible', 'description': 'double(2)', 'inputs': [],
                                'call': {'function': 'double', 'args': [2], 'kwargs': {}}, 'returns': {'value': 4, 'tolerance': None}}
    assert plan['cases'][3]['expected'] == 'Hello, Kai'


def test_ordinary_cases_keep_exactly_the_plan_shape_they_had():
    for lesson in content.load()[1].values():
        if browser_checks.applies(lesson):
            for case in browser_checks.plan(lesson)['cases']:
                assert set(case) == ({'id', 'visibility', 'description', 'inputs', 'expected'} if case['visibility'] == 'visible' else {'id', 'visibility', 'description', 'inputs'})


# The judge: right and wrong functions

def test_a_correct_set_of_functions_passes(lesson):
    result = check(correct())
    assert result['passed'] and result['result'] == 'passed' and result['failed'] is None


def test_a_wrong_return_value_names_both_values(lesson):
    result = check(correct(**{'double-two': run('double-two', returned='5')}))
    assert result['result'] == 'needs_work' and result['rule'] == f'{LESSON_ID}.case.double-two'
    assert result['feedback'] == 'For double(2), your function should return 4, but it returned 5.'
    assert result['failed'] | {'id': 'double-two', 'reason': 'wrong_return', 'expected_value': '4', 'actual_value': '5'} == result['failed']


def test_printing_instead_of_returning_is_explained(lesson):
    result = check(correct(**{'double-two': run('double-two', output='4\n', returned='null')}))
    assert result['feedback'].startswith('For double(2), your function should return 4, but it returned None.')
    assert 'printing shows a value, and return hands it back' in result['feedback']


def test_returning_none_without_printing_does_not_claim_it_printed(lesson):
    assert 'printed' not in check(correct(**{'double-two': run('double-two', returned='null')}))['feedback']


def test_wrong_printed_output_from_a_call_is_a_wrong_output(lesson):
    result = check(correct(**{'greet-kai': run('greet-kai', output='Hi, Kai\n', returned='null')}))
    assert result['failed']['reason'] == 'wrong_output' and result['failed']['expected_line'] == 'Hello, Kai'


def test_a_right_output_with_a_wrong_return_fails(lesson):
    result = check(correct(**{'greet-kai': run('greet-kai', output='Hello, Kai\n', returned='1')}))
    assert result['failed']['reason'] == 'wrong_return'


@pytest.mark.parametrize('case,message', [
    ('double-two', 'Your program should define a function called double that takes 1 argument.'),
    ('share-third', 'Your program should define a function called share that takes 2 arguments.'),
])
def test_a_missing_function_says_what_to_define(lesson, case, message):
    result = check(correct(**{case: run(case, status='no_function')}))
    assert result['result'] == 'needs_work' and result['feedback'] == message
    assert result['failed']['reason'] == 'no_function' and result['rule'] == f'{LESSON_ID}.case.{case}'


def test_a_wrong_parameter_count_says_what_to_define(lesson):
    result = check(correct(**{'share-third': run('share-third', status='bad_signature')}))
    assert result['result'] == 'needs_work' and result['failed']['reason'] == 'wrong_arguments'
    assert result['feedback'].startswith('Your program should define a function called share that takes 2 arguments.')


def test_a_value_the_check_cannot_compare_is_named_not_a_crash(lesson):
    result = check(correct(**{'double-two': run('double-two', status='not_comparable', error_type='set')}))
    assert result['result'] == 'needs_work' and result['failed']['reason'] == 'not_comparable' and '(set)' in result['feedback']


def test_an_exception_inside_the_function_is_a_python_error_with_its_line(lesson):
    result = check(correct(**{'double-two': run('double-two', status='error', error_type='TypeError', line=2)}))
    assert result['result'] == 'execution_error' and result['failed']['reason'] == 'error'
    assert result['failed']['line'] == 2 and result['failed']['error_type'] == 'TypeError'


def test_an_endless_loop_in_the_function_is_stopped_and_named(lesson):
    runs = correct(**{'double-two': run('double-two', status='timeout'), 'double-big': run('double-big', status='not_run'),
                      'share-third': run('share-third', status='not_run'), 'greet-kai': run('greet-kai', status='not_run')})
    result = check(runs)
    assert result['result'] == 'execution_error' and result['failed']['reason'] == 'timeout'
    assert 'after 3 seconds' in result['feedback']


@pytest.mark.parametrize('runs', [
    pytest.param(lambda: correct(**{'double-two': run('double-two')}), id='no-value-reported-page-is-older'),
    pytest.param(lambda: correct(**{'double-two': run('double-two', returned='not json')}), id='not-json'),
    pytest.param(lambda: correct(**{'double-two': run('double-two', returned='NaN')}), id='nan'),
    pytest.param(lambda: correct(**{'double-two': run('double-two', returned='[' * 5000)}), id='deep'),
])
def test_a_report_with_no_usable_value_is_a_service_error_not_a_learner_mistake(lesson, runs):
    assert check(runs())['result'] == 'service_error'


def test_a_function_status_on_an_ordinary_case_is_not_believed(monkeypatch):
    _, lessons = content.load(Path(__file__).with_name('fixtures') / 'browser_checks')
    target = lessons['fixture.sum-two']
    ids = [case.id for case in target.task('challenge').check.cases]
    runs = [browser_checks.CaseRun(id=i, status='no_function') for i in ids]
    assert browser_checks.judge(target, 'a = int(input())\nb = int(input())\nprint(a + b)', runs)['result'] == 'service_error'


def test_a_long_returned_value_is_refused_by_the_api(lesson):
    response = client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': GOOD, 'output': '', 'runs': correct(**{'double-two': run('double-two', returned='1' * 10001)})}, headers=HEADERS)
    assert response.status_code == 422


def test_the_server_never_runs_the_function(lesson, tmp_path):
    marker = tmp_path / 'ran'
    code = f'def double(n):\n    open({str(marker)!r}, "w")\n    return n * 2\n'
    check(correct(), code=code)
    assert not marker.exists()


# The equality rule

@pytest.mark.parametrize('want,got,tolerance,same', [
    (4, 4, None, True),
    (4, 4.0, None, True),
    (4, 5, None, False),
    (True, 1, None, False),
    (1, True, None, False),
    (True, True, None, True),
    (False, 0, None, False),
    (None, None, None, True),
    (None, 0, None, False),
    ('', None, None, False),
    ('a', 'a', None, True),
    ('a', 'A', None, False),
    ('4', 4, None, False),
    ([1, 2], [1, 2], None, True),
    ([1, 2], [2, 1], None, False),
    ([1, 2], [1], None, False),
    ({'a': 1}, {'a': 1}, None, True),
    ({'a': 1}, {'a': 2}, None, False),
    ({'a': 1}, {'b': 1}, None, False),
    ([1], {'a': 1}, None, False),
    (0.3, 0.1 + 0.2, 1e-9, True),
    (0.3, 0.4, 0.001, False),
    (2.5, 2.5005, 0.001, True),
    ([0.3, {'a': 0.3}], [0.1 + 0.2, {'a': 0.1 + 0.2}], 1e-9, True),
    (1.5, 10 ** 400, 0.1, False),
    (10 ** 400, 10 ** 400, None, True),
])
def test_the_equality_rule(want, got, tolerance, same):
    assert same_value(want, got, tolerance) is same


# Hidden values

@pytest.fixture
def tree(tmp_path):
    root = tmp_path / 'content'
    shutil.copytree(FIXTURE_DIR, root)
    return root


def edit_check(root, change):
    path = root / 'fixture' / 'u09' / f'{LESSON_ID}.json'
    data = json.loads(path.read_text())
    change(data['tasks'][4]['check'])
    path.write_text(json.dumps(data))


def test_a_hidden_call_is_refused_so_its_arguments_cannot_reach_the_browser(tree):
    edit_check(tree, lambda c: c['cases'][1].update(visibility='hidden', description='another number'))
    with pytest.raises(content.ContentError, match='cannot be hidden, because its arguments would reach the browser'):
        content.load(tree)


def test_a_hidden_ordinary_case_beside_calls_keeps_its_expected_output_on_the_server(tree, monkeypatch):
    secret = 'SECRET-EXPECTED-LINE'
    edit_check(tree, lambda c: c['cases'].append({'id': 'quiet', 'description': 'the program alone', 'expected': secret, 'visibility': 'hidden'}))
    _, lessons = content.load(tree)
    target = lessons[LESSON_ID]
    assert secret not in json.dumps(browser_checks.plan(target))
    runs = [browser_checks.CaseRun(**r) for r in correct()] + [browser_checks.CaseRun(id='quiet', status='ok', output='different')]
    assert secret not in json.dumps(browser_checks.judge(target, GOOD, runs))


def test_a_returned_value_of_a_case_handled_as_hidden_is_never_named():
    """Content validation refuses this today. If it ever allows it, the answer must stay on the server."""
    _, lessons = content.load(FIXTURE_DIR)
    target = lessons[LESSON_ID]
    challenge = target.task('challenge')
    hidden = challenge.check.cases[0].model_copy(update={'visibility': 'hidden'})
    check_ = challenge.check.model_copy(update={'cases': [hidden, *challenge.check.cases[1:]]})
    tasks = [t.model_copy(update={'check': check_}) if t.type == 'challenge' else t for t in target.tasks]
    secret_lesson = target.model_copy(update={'tasks': tasks})
    plan_case = browser_checks.plan(secret_lesson)['cases'][0]
    assert 'returns' not in plan_case and 'expected' not in plan_case
    runs = [browser_checks.CaseRun(id='double-two', status='ok', returned='987654')]
    runs += [browser_checks.CaseRun(**r) for r in correct()[1:]]
    result = browser_checks.judge(secret_lesson, GOOD, runs)
    assert result['result'] == 'needs_work' and '987654' not in json.dumps(result)
    assert 'expected_value' not in result['failed'] and ' 4' not in result['feedback']


# Content validation

@pytest.mark.parametrize('change,message', [
    (lambda c: c['cases'][0].pop('returns'), 'needs expected output, returns, or both'),
    (lambda c: c['cases'][0]['call'].update(function='not a name'), 'function'),
    (lambda c: c['cases'][0]['call'].update(function='class'), 'class cannot be a function name'),
    (lambda c: c['cases'][0]['call'].update(kwargs={'not ok': 1}), 'not ok cannot be a keyword argument'),
    (lambda c: c['cases'][0]['call'].update(kwargs={'for': 1}), 'for cannot be a keyword argument'),
    (lambda c: c['cases'][0]['call'].update(args=list(range(11))), 'args'),
    (lambda c: c['cases'][0]['call'].update(args=['x' * 2001]), 'arguments must be plain JSON'),
    (lambda c: c['cases'][0]['call'].update(args=[float('nan')]), 'arguments must be plain JSON'),
    (lambda c: c['cases'][0]['returns'].update(value=2.5), 'a return value with a fraction needs a tolerance'),
    (lambda c: c['cases'][0]['returns'].update(value=[1, {'a': 0.1}]), 'a return value with a fraction needs a tolerance'),
    (lambda c: c['cases'][0]['returns'].update(value='text', tolerance=0.1), 'a tolerance needs a number'),
    (lambda c: c['cases'][0]['returns'].update(tolerance=-1), 'tolerance'),
    (lambda c: c['cases'][0]['returns'].update(value='x' * 10001), 'the return value must be plain JSON'),
    (lambda c: c['cases'][0]['returns'].pop('value'), 'value'),
    (lambda c: c['cases'][0].update(oops=1), 'oops'),
    (lambda c: c['cases'].append({'id': 'plain', 'description': 'x'}), 'needs expected output'),
    (lambda c: c['cases'].append({'id': 'plain', 'description': 'x', 'expected': 'y', 'returns': {'value': 1}}), 'has returns but no call'),
])
def test_invalid_calls_stop_content_loading(tree, change, message):
    edit_check(tree, change)
    with pytest.raises(content.ContentError, match=message):
        content.load(tree)


def test_a_whole_number_needs_no_tolerance_and_a_whole_float_is_fine(tree):
    edit_check(tree, lambda c: c['cases'][0]['returns'].update(value=4.0))
    content.load(tree)


# The answers the browser tests use are the real API's

def test_the_recorded_answers_are_the_real_apis(lesson):
    recorded = json.loads(RECORDED_FILE.read_text())
    assert recorded['units'] == {UNIT_ID: client.get(f'/api/units/{UNIT_ID}/lessons').json()}
    assert recorded['plans'] == {LESSON_ID: client.get(f'/api/checks/{LESSON_ID}').json()}
    fixture_course = [c for c in client.get('/api/catalog').json()['courses'] if c['id'] == 'fixture']
    assert [c for c in recorded['catalog']['courses'] if c['id'] == 'fixture'] == fixture_course
    assert len(recorded['scenarios']) >= 7
    for scenario in recorded['scenarios']:
        assert client.post('/api/check', json=scenario['request'], headers=HEADERS).json() == scenario['response'], scenario['name']

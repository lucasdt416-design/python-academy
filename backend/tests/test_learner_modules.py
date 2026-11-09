"""A learner's own files (ENG-08b, docs/plan/browser-checks.md section 12, decision 30).

Uses the TEST FIXTURE lesson in tests/fixtures/learner_modules/, which is never shown to learners. The
browser's part runs in Pyodide in frontend/tests/learner-modules.spec.ts; here the API gets the reports
the browser sends, and frontend/tests/fixtures/learner-modules-api.json is proved to hold its answers.
To rewrite it: WRITE_MODULE_RECORDINGS=1 python -m pytest -q tests/test_learner_modules.py
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

FIXTURE_DIR = Path(__file__).with_name('fixtures') / 'learner_modules'
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/learner-modules-api.json'
LESSON_ID = 'fixture.modules'
UNIT_ID = 'fixture.u09'
HEADERS = {'origin': 'http://localhost:3000'}
MAIN = 'import scores\n\nnumbers = [int(n) for n in input().split()]\nprint(scores.total(numbers))\n'
GOOD = 'def total(numbers):\n    result = 0\n    for n in numbers:\n        result = result + n\n    return result\n'
client = TestClient(app)

# (name, the program, the learner's scores.py). Only the program and the reports go to the API.
SCENARIOS = [
    ('passed', MAIN, GOOD),
    ('needs_work', MAIN, 'def total(numbers):\n    return 7\n'),
    ('error in the module', MAIN, 'def total(numbers):\n    return sum(number)\n'),
    ('module not written', MAIN, '# Write total(numbers) here: it returns the sum of the list.\n'),
]


def serve(setattr=setattr, setitem=lambda d, k, v: d.__setitem__(k, v)):
    catalog, lessons = content.load(FIXTURE_DIR)
    setattr(main, 'UNIT_LESSONS', {**main.UNIT_LESSONS, **content.unit_lessons(catalog, lessons)})
    setattr(main, 'CATALOG_VIEW', {**main.CATALOG_VIEW, 'courses': main.CATALOG_VIEW['courses'] + content.catalog_view(catalog, lessons)['courses']})
    for lesson_id, lesson in lessons.items():
        setitem(main.CONTENT, lesson_id, lesson)
    return lessons[LESSON_ID]


@pytest.fixture
def lesson(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    found = serve(monkeypatch.setattr, monkeypatch.setitem)
    client.cookies.clear()
    return found


def copy_with(tmp_path, change):
    root = tmp_path / 'content'
    shutil.copytree(FIXTURE_DIR, root)
    path = root / 'fixture/u09/fixture.modules.json'
    data = json.loads(path.read_text())
    change(data['tasks'])
    path.write_text(json.dumps(data))
    return root


# Content validation: decision 30, no file may stand in for one of Python's own modules

@pytest.mark.parametrize('name', ['random.py', 'os.py', 'math.py', 'json.py', 'sys.py', 'js.py', 'pyodide.py', 'datetime.py'])
def test_a_learner_file_named_like_a_python_module_is_refused(tmp_path, name):
    root = copy_with(tmp_path, lambda t: t[4].update(modules={name: ''}))
    with pytest.raises(content.ContentError, match="would hide Python's own"):
        content.load(root)


@pytest.mark.parametrize('name', ['Scores.py', 'scores', 'scores.txt', 'my-scores.py', '_scores.py', '1scores.py', 'notes/scores.py', 'class.py', 'a' * 40 + '.py'])
def test_a_learner_file_needs_a_short_lowercase_module_name(tmp_path, name):
    root = copy_with(tmp_path, lambda t: t[4].update(modules={name: ''}))
    with pytest.raises(content.ContentError, match='short lowercase name'):
        content.load(root)


def test_the_try_it_cards_learner_files_are_checked_too(tmp_path):
    root = copy_with(tmp_path, lambda t: t[1].update(modules={'random.py': ''}))
    with pytest.raises(content.ContentError, match="would hide Python's own"):
        content.load(root)


def test_too_many_learner_files_are_refused(tmp_path):
    root = copy_with(tmp_path, lambda t: t[4].update(modules={f'part{n}.py': '' for n in range(4)}))
    with pytest.raises(content.ContentError, match='more than 3 learner files'):
        content.load(root)


def test_a_learner_file_may_not_share_a_name_with_a_given_file(tmp_path):
    root = copy_with(tmp_path, lambda t: t[4]['check']['cases'][0].update(files={'scores.py': 'x'}))
    with pytest.raises(content.ContentError, match='both a learner file and a given file'):
        content.load(root)


def test_a_given_file_named_like_a_python_module_is_refused_too(tmp_path):
    root = copy_with(tmp_path, lambda t: t[4]['check']['cases'][0].update(files={'random.py': 'x'}))
    with pytest.raises(content.ContentError, match="would hide Python's own random module"):
        content.load(root)


def test_a_given_python_file_with_its_own_name_is_still_fine(tmp_path):
    content.load(copy_with(tmp_path, lambda t: t[4]['check']['cases'][0].update(files={'data.py': 'x', 'notes/random.py': 'x'})))


def test_only_a_browser_check_can_have_learner_files(tmp_path):
    def change(tasks):
        tasks[4].update(validator={'id': 'bounded-story', 'version': 2})
        tasks[4].pop('check')
    with pytest.raises(content.ContentError, match='only a browser check can run'):
        content.load(copy_with(tmp_path, change))


# What the API sends and receives

def test_the_lesson_view_gives_each_cards_learner_files_and_their_starting_code(lesson):
    view = client.get(f'/api/units/{UNIT_ID}/lessons').json()[0]
    assert view['exampleModules'] == {'greet.py': 'def hello(name):\n    return "Hello, " + name\n'}
    assert view['challengeModules'] == {'scores.py': '# Write total(numbers) here: it returns the sum of the list.\n'}


def test_a_lesson_without_learner_files_keeps_the_view_it_always_had():
    for view in client.get('/api/lessons').json():
        assert 'exampleModules' not in view and 'challengeModules' not in view


def test_no_real_lesson_has_learner_files_yet():
    catalog, lessons = content.load()
    assert not any(lesson.task('example').modules or lesson.task('challenge').modules for lesson in lessons.values())


# The test runner plays the worker's part

def test_the_runner_imports_the_learners_file_and_starts_it_again_in_every_case(lesson):
    counter = 'calls = []\ndef total(numbers):\n    calls.append(1)\n    return len(calls)\n'
    found = reports(lesson, [MAIN], modules={'scores.py': counter})[0]
    assert [r.output for r in found] == ['1\n', '1\n']


def test_a_correct_module_passes_and_a_hard_coded_one_fails(lesson):
    for module, result in ((GOOD, 'passed'), ('def total(numbers):\n    return 7\n', 'needs_work')):
        runs = [r.model_dump() for r in reports(lesson, [MAIN], modules={'scores.py': module})[0]]
        assert client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': MAIN, 'output': runs[0]['output'], 'runs': runs}, headers=HEADERS).json()['result'] == result


# The answers the browser tests use are the real API's

def build_recordings():
    recorded = {'catalog': client.get('/api/catalog').json(),
                'units': {UNIT_ID: client.get(f'/api/units/{UNIT_ID}/lessons').json()},
                'plans': {LESSON_ID: client.get(f'/api/checks/{LESSON_ID}').json()},
                'scenarios': []}
    for name, code, module in SCENARIOS:
        runs = [r.model_dump() for r in reports(main.CONTENT[LESSON_ID], [code], modules={'scores.py': module})[0]]
        request = {'lesson_id': LESSON_ID, 'code': code, 'output': runs[0]['output'], 'inputs': [], 'runs': runs}
        recorded['scenarios'].append({'name': name, 'module': module, 'request': request, 'response': client.post('/api/check', json=request, headers=HEADERS).json()})
    return recorded


def test_the_recorded_answers_are_the_real_apis(lesson):
    recorded = build_recordings()
    if os.environ.get('WRITE_MODULE_RECORDINGS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded
    results = {s['name']: s['response'] for s in recorded['scenarios']}
    assert results['passed']['result'] == 'passed' and results['needs_work']['result'] == 'needs_work'
    assert results['error in the module']['result'] == 'execution_error' and results['error in the module']['failed']['error_type'] == 'NameError'
    assert results['module not written']['failed']['error_type'] == 'AttributeError'

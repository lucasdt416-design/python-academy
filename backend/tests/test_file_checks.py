"""File fixtures (ENG-08, docs/plan/browser-checks.md section 9).

Uses the TEST FIXTURE lesson in tests/fixtures/file_checks/, which is never shown to learners. The
browser's part runs in Pyodide in frontend/tests/file-checks.spec.ts; here the API gets the reports the
browser sends, and frontend/tests/fixtures/file-checks-api.json is proved to hold the API's answers.
To rewrite it: WRITE_FILE_RECORDINGS=1 python -m pytest -q tests/test_file_checks.py
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
from app.db import Base
from app.main import app, engine
from case_runner import reports

FIXTURE_DIR = Path(__file__).with_name('fixtures') / 'file_checks'
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/file-checks-api.json'
LESSON_ID = 'fixture.files'
UNIT_ID = 'fixture.u08'
HEADERS = {'origin': 'http://localhost:3000'}
GOOD = 'total = 0\nwith open("scores.txt") as f:\n    for line in f:\n        total = total + int(line)\nprint(total)\n'
client = TestClient(app)

SCENARIOS = [
    ('passed', GOOD),
    ('other way passed', 'print(sum(int(n) for n in open("scores.txt")))\n'),
    ('needs_work', 'print(7)\n'),
    ('hidden', 'print(7 if len(open("scores.txt").read()) == 4 else 10)\n'),
    ('missing file', 'print(open("score.txt").read())\n'),
    ('leftover between cases', 'try:\n    open("left.txt")\n    print(1)\nexcept FileNotFoundError:\n    print(0)\nopen("left.txt", "w").write("x")\n'),
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
    path = root / 'fixture/u08/fixture.files.json'
    data = json.loads(path.read_text())
    change(data['tasks'])
    path.write_text(json.dumps(data))
    return root


def case_of(tasks, index=0):
    return tasks[4]['check']['cases'][index]


# Content validation

@pytest.mark.parametrize('path', ['../up.txt', '/etc/passwd', 'a/../b.txt', '.hidden', 'a//b.txt', 'a\\b.txt', 'with space.txt', 'a/', '', 'x' * 101])
def test_a_file_path_must_stay_in_the_programs_folder(tmp_path, path):
    root = copy_with(tmp_path, lambda t: case_of(t)['files'].update({path: 'x'}))
    with pytest.raises(content.ContentError, match='unsafe file path'):
        content.load(root)


@pytest.mark.parametrize('path', ['scores.txt', 'saves/game.json', 'a-b_c.tar.gz', 'one/two/three.csv', 'noextension'])
def test_ordinary_paths_are_fine(tmp_path, path):
    content.load(copy_with(tmp_path, lambda t: case_of(t)['files'].update({path: 'x'})))


def test_an_examples_paths_are_checked_too(tmp_path):
    root = copy_with(tmp_path, lambda t: t[1]['files'].update({'../up.txt': 'x'}))
    with pytest.raises(content.ContentError, match='unsafe file path'):
        content.load(root)


def test_too_many_files_are_refused(tmp_path):
    root = copy_with(tmp_path, lambda t: case_of(t)['files'].update({f'f{i}.txt': 'x' for i in range(content.FILES_PER_CASE)}))
    with pytest.raises(content.ContentError, match='more than 10 files'):
        content.load(root)


def test_too_large_a_file_is_refused(tmp_path):
    root = copy_with(tmp_path, lambda t: case_of(t)['files'].update({'big.txt': 'x' * (content.FILE_LIMIT + 1)}))
    with pytest.raises(Exception):
        content.load(root)


def test_a_hidden_description_may_not_show_a_line_of_its_files(tmp_path):
    root = copy_with(tmp_path, lambda t: case_of(t, 2).update(description='a file holding 21 and more'))
    with pytest.raises(content.ContentError, match='file lines'):
        content.load(root)


# What the API sends

def test_the_plan_sends_each_cases_files_and_never_a_hidden_expected_output(lesson):
    plan = client.get(f'/api/checks/{LESSON_ID}').json()
    files = {c['id']: c['files'] for c in plan['cases']}
    assert files == {'small': {'scores.txt': '3\n4\n'}, 'nested': {'scores.txt': '10\n', 'notes/old.txt': 'ignore me'}, 'other': {'scores.txt': '20\n21\n22\n'}}
    assert 'expected' not in plan['cases'][2] and '63' not in json.dumps(plan)


def test_a_case_with_no_files_keeps_the_plan_it_always_had():
    plan = client.get('/api/checks/py.for-range').json()
    assert all('files' not in c for c in plan['cases'])


def test_the_lesson_view_shows_a_visible_sample_never_a_hidden_file(lesson):
    view = client.get(f'/api/units/{UNIT_ID}/lessons').json()[0]
    assert view['exampleFiles'] == {'note.txt': 'hello from the file'}
    assert view['challengeFiles'] == {'scores.txt': '3\n4\n'}
    assert '22' not in json.dumps(view)


def test_a_lesson_with_no_files_keeps_the_view_it_always_had():
    for view in client.get('/api/lessons').json():
        assert 'exampleFiles' not in view and 'challengeFiles' not in view


def test_no_real_lesson_has_files_yet():
    catalog, lessons = content.load()
    assert not any(lesson.task('example').files or any(c.files for c in (lesson.task('challenge').check.cases if lesson.task('challenge').check else [])) for lesson in lessons.values())


# The test runner plays the worker's part, with a folder of its own per case

def test_the_runner_gives_each_case_only_its_own_files(lesson):
    found = reports(lesson, ['import os\nprint(sorted(os.listdir(".")))\n'])[0]
    assert [r.output for r in found] == ["['scores.txt']\n", "['notes', 'scores.txt']\n", "['scores.txt']\n"]


def test_a_correct_program_passes_and_a_hard_coded_one_fails(lesson):
    for code, result in ((GOOD, 'passed'), ('print(7)\n', 'needs_work')):
        runs = [r.model_dump() for r in reports(lesson, [code])[0]]
        assert client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': code, 'output': runs[0]['output'], 'runs': runs}, headers=HEADERS).json()['result'] == result


def test_a_missing_file_is_an_error_with_a_tagged_hint(lesson):
    code = 'print(open("score.txt").read())\n'
    runs = [r.model_dump() for r in reports(lesson, [code])[0]]
    answer = client.post('/api/check', json={'lesson_id': LESSON_ID, 'code': code, 'output': '', 'runs': runs}, headers=HEADERS).json()
    assert answer['result'] == 'execution_error' and answer['failed']['error_type'] == 'FileNotFoundError' and answer['failed']['line'] == 1


# The answers the browser tests use are the real API's

def build_recordings():
    recorded = {'catalog': client.get('/api/catalog').json(),
                'units': {UNIT_ID: client.get(f'/api/units/{UNIT_ID}/lessons').json()},
                'plans': {LESSON_ID: client.get(f'/api/checks/{LESSON_ID}').json()},
                'scenarios': []}
    for name, code in SCENARIOS:
        runs = [r.model_dump() for r in reports(main.CONTENT[LESSON_ID], [code])[0]]
        request = {'lesson_id': LESSON_ID, 'code': code, 'output': runs[0]['output'], 'inputs': [], 'runs': runs}
        recorded['scenarios'].append({'name': name, 'request': request, 'response': client.post('/api/check', json=request, headers=HEADERS).json()})
    return recorded


def test_the_recorded_answers_are_the_real_apis(lesson):
    recorded = build_recordings()
    if os.environ.get('WRITE_FILE_RECORDINGS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded
    results = {s['name']: s['response'] for s in recorded['scenarios']}
    assert results['passed']['result'] == 'passed' and results['needs_work']['result'] == 'needs_work'
    assert results['hidden']['failed']['visibility'] == 'hidden' and results['missing file']['result'] == 'execution_error'
    # The program that looks for what an earlier case left behind finds nothing, so it fails on what it prints.
    assert [r['output'] for r in next(s for s in recorded['scenarios'] if s['name'] == 'leftover between cases')['request']['runs'][:1]] == ['0\n']

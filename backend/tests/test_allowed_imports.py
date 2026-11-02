"""ENG-07: the modules a learner's program may import, and seeded random. docs/plan/browser-checks.md section 9.

The guard itself runs in the browser worker, so frontend/tests/allowed-imports.spec.ts tests what it does
in real Pyodide. These tests hold the list to one place, keep the blocked modules off it, and cover what
the API does: the seed in the plan, and the "unsupported" result.

frontend/tests/fixtures/seeded-random.json holds a program and what CPython 3.12 prints for it, which the
browser test compares with Pyodide. To rewrite it: WRITE_SEEDED_RANDOM=1 python -m pytest -q tests/test_allowed_imports.py
"""
import json
import os
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import test_unit2_lessons as helpers
from app import browser_checks, content
from app.main import app
from case_runner import reports

ROOT = Path(__file__).resolve().parents[2]
WORKER = (ROOT / 'frontend/public/python-worker.js').read_text()
SPEC = (ROOT / 'frontend/tests/allowed-imports.spec.ts').read_text()
SEEDED_FILE = ROOT / 'frontend/tests/fixtures/seeded-random.json'
# The plan's list (master run Part 9). None of these may ever be allowed.
BLOCKED = {'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests', 'pyodide', 'js', 'ctypes', 'importlib'}
ALLOWED = {'math', 'random', 'datetime', 'json', 'csv', 're'}


def allowed_in_worker():
    return set(json.loads(re.search(r"const ALLOWED_MODULES = (\[.*?\]);", WORKER).group(1).replace("'", '"')))


def test_the_list_is_exactly_what_the_lessons_need():
    assert allowed_in_worker() == ALLOWED


def test_no_blocked_module_is_on_the_list():
    assert not allowed_in_worker() & BLOCKED


def test_the_list_is_in_one_place():
    assert WORKER.count('ALLOWED_MODULES = ') == 1
    for path in [*ROOT.glob('backend/app/*.py'), *ROOT.glob('frontend/app/*.ts*'), ROOT / 'frontend/public/check-runner.js']:
        assert 'ALLOWED_MODULES' not in path.read_text(), path


def test_the_browser_test_tries_every_blocked_module_and_every_allowed_one():
    for name in BLOCKED | ALLOWED:
        assert f"'{name}'" in SPEC, name


def test_the_guard_is_on_before_any_learner_code_in_both_modes():
    assert WORKER.count('await guardImports(py') == 2
    for start, code in (("noNetwork();\n  await guardImports(py);", 'await py.runPythonAsync(data.code)'), ("await guardImports(py, cases.some", 'await py.runPythonAsync(code, {globals: namespace})')):
        assert start in WORKER and WORKER.index(start) < WORKER.index(code)


def test_the_worker_imports_nothing_after_the_guard_is_on():
    # Its own imports would be refused too, because they would look like the learner's.
    after = WORKER[WORKER.index('const REPLIES = '):]
    lines = [line for line in after.split('const CALLER = `')[0].splitlines() + after.split('`;', 2)[2].splitlines() if re.match(r'\s*(import|from) \w', line)]
    assert lines == []
    assert 'runPython(\'import' not in WORKER and 'runPythonAsync(\'import' not in WORKER


def test_no_lesson_imports_anything():
    # So the guard changes nothing for a lesson's own samples.
    for lesson in helpers.LESSONS.values():
        for task in lesson.tasks:
            code = getattr(task, 'code', None) or ''
            others = [way.code for way in getattr(task, 'other_ways', [])]
            assert not any(re.search(r'^\s*(import|from) \w', text, re.M) for text in [code, *others]), lesson.id


# The result

def judged(error_type='ModuleNotFoundError', line=1):
    lesson = helpers.LESSONS['py.for-range']
    runs = [{'id': c.id, 'status': 'error', 'output': '', 'error_type': error_type, 'line': line} for c in lesson.task('challenge').check.cases]
    return TestClient(app).post('/api/check', json={'lesson_id': lesson.id, 'code': 'import os\n', 'output': '', 'runs': runs}, headers=helpers.HEADERS).json()


def test_a_refused_import_is_not_checked_and_says_so_truthfully():
    answer = judged()
    assert answer['result'] == 'unsupported' and answer['failed']['reason'] == 'unsupported'
    assert answer['feedback'] == "These checks can use only a few of Python's modules, so that import can't be used here."
    assert 'built-in' not in answer['feedback']


# Seeded random

def lesson_with(cases):
    return SimpleNamespace(task=lambda kind: SimpleNamespace(check=SimpleNamespace(cases=cases)))


def case(seed=None):
    return SimpleNamespace(id='a', inputs=[], seed=seed)


SEEDED = 'import random\nprint(random.randint(1, 100))\nprint(random.choice(["moon", "star", "sun"]))\nitems = [1, 2, 3, 4, 5]\nrandom.shuffle(items)\nprint(items)\nprint(random.random())\n'


def test_the_same_seed_gives_the_same_numbers_and_another_seed_does_not():
    first, second, other = reports(lesson_with([case(7)]), [SEEDED])[0][0].output, reports(lesson_with([case(7)]), [SEEDED])[0][0].output, reports(lesson_with([case(8)]), [SEEDED])[0][0].output
    assert first == second and first != other


def test_no_seed_means_seed_0():
    assert reports(lesson_with([case()]), [SEEDED])[0][0].output == reports(lesson_with([case(0)]), [SEEDED])[0][0].output


def test_the_recorded_seeded_output_is_cpythons():
    recorded = {'code': SEEDED, 'seed': 7, 'output': reports(lesson_with([case(7)]), [SEEDED])[0][0].output, 'default_output': reports(lesson_with([case()]), [SEEDED])[0][0].output}
    if os.environ.get('WRITE_SEEDED_RANDOM') == '1':
        SEEDED_FILE.write_text(json.dumps(recorded, indent=1) + '\n')
    assert json.loads(SEEDED_FILE.read_text()) == recorded


@pytest.mark.parametrize('seed,ok', [(0, True), (2**31 - 1, True), (-1, False), (2**31, False), (None, True)])
def test_a_seed_must_be_in_range(seed, ok):
    data = {'id': 'a', 'description': 'd', 'expected': '', 'seed': seed}
    if ok:
        assert content.CheckCase(**data).seed == seed
    else:
        with pytest.raises(ValueError):
            content.CheckCase(**data)


def test_the_plan_sends_a_seed_only_when_a_case_sets_one():
    lesson = helpers.LESSONS['py.for-range']
    assert all('seed' not in c for c in browser_checks.plan(lesson)['cases'])
    challenge = lesson.task('challenge')
    seeded = challenge.check.cases[0].model_copy(update={'seed': 5})
    check = challenge.check.model_copy(update={'cases': [seeded, *challenge.check.cases[1:]]})
    changed = SimpleNamespace(id=lesson.id, task=lambda kind: challenge.model_copy(update={'check': check}))
    assert browser_checks.plan(changed)['cases'][0]['seed'] == 5

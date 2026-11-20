"""The three Python Foundations final projects (docs/plan/courses/py-final-project.md), built first.

Each reference version must run the way the browser runs learner code: in a folder of its own, with
typed-in replies, seeded random, the learner's own files importable by name, and only the modules the
import guard allows. Its own test file must pass, and a play-through must behave as the brief says.
"""
import ast
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace

import pytest

from case_runner import reports

ROOT = Path(__file__).resolve().parents[2] / 'docs/plan/final-projects'
ALLOWED = {'math', 'random', 'datetime', 'json', 'csv', 're'}  # the worker's import guard
PROJECTS = {'lockpick': 'lockpick.py', 'site-builder': 'builder.py', 'planner': 'planner.py'}


def files(project):
    return {p.name: p.read_text() for p in sorted((ROOT / project).iterdir()) if p.is_file()}


def run(project, program, inputs=(), extra_files=None):
    """(output, error type) for one run of program, with the project's other files beside it."""
    own = files(project)
    modules = {n: t for n, t in own.items() if n.endswith('.py') and n != program and not n.startswith('test_')}
    data = {n: t for n, t in own.items() if not n.endswith('.py')}
    case = SimpleNamespace(id='run', inputs=list(inputs), files={**data, **(extra_files or {})}, seed=None, reference=None, call=None)
    lesson = SimpleNamespace(task=lambda kind: SimpleNamespace(check=SimpleNamespace(cases=[case]), modules=modules))
    report = reports(lesson, [own[program]], modules=modules)[0][0]
    return report.output, report.error_type


@pytest.mark.parametrize('project', PROJECTS)
def test_imports_only_what_the_browser_allows_and_no_file_shadows_a_python_module(project):
    own = files(project)
    names = {n[:-3] for n in own if n.endswith('.py')}
    assert not names & set(sys.stdlib_module_names), 'a learner file would shadow a Python module'
    for name, text in own.items():
        if name.endswith('.py'):
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    found = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module]
                    assert {m.split('.')[0] for m in found} <= ALLOWED | names, (name, found)


@pytest.mark.parametrize('project,tests,name', [('lockpick', 'test_lockpick.py', 'Lockpick'), ('site-builder', 'test_builder.py', 'Site Builder'), ('planner', 'test_planner.py', 'Planner')])
def test_the_learners_own_tests_pass(project, tests, name):
    assert run(project, tests) == (f'All {name} tests passed.\n', None)


def test_lockpick_a_round_won_a_round_lost_and_bad_guesses_explained():
    one_word = {'words.txt': 'vault\n'}
    output, error = run('lockpick', 'lockpick.py', ['v', 'ab', 'v', 'a', 'u', 'l', 't', 'y',
                                                    'q', 'w', 'e', 'r', 'i', 'o', 'n'], one_word)
    assert error is None
    assert 'Type one letter, a to z.' in output and 'You already tried v.' in output
    assert 'Click! The vault opens: vault' in output and 'The lock jams. The word was vault.' in output
    assert output.rstrip().endswith('The lock jams. The word was vault.\nVaults opened: 1 of 2')   # then n: no third round


def test_site_builder_writes_every_page_and_escapes_what_the_data_says():
    output, error = run('site-builder', 'builder.py')
    assert error is None and output.count('Wrote ') == 4
    namespace = {}
    exec((ROOT / 'site-builder/builder.py').read_text(), namespace)
    pages = namespace['build'](json.loads((ROOT / 'site-builder/site.json').read_text()))

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.tags, self.links = [], []

        def handle_starttag(self, tag, attrs):
            self.tags.append(tag)
            self.links += [v for k, v in attrs if k == 'href']

    for name, html in pages.items():
        parsed = Links()
        parsed.feed(html)
        assert set(parsed.links) <= set(pages), (name, parsed.links)   # no broken links
        assert 'b' not in parsed.tags and 'mystery' not in parsed.tags   # data text never becomes a tag
        assert 'script' not in parsed.tags


def test_planner_a_session_and_its_saved_file_reloaded_in_the_next_run():
    output, error = run('planner', 'planner.py', ['add Read chapter 3 by 2099-01-02', 'add Practice', 'done 2', 'done 7', 'list', 'quit'])
    assert error is None
    assert output.startswith('No saved plan yet: starting a new one.')
    assert 'There is no task 7. Pick 1 to 2.' in output
    assert '1. [ ] Read chapter 3 (due 2099-01-02)\n2. [x] Practice' in output
    assert output.rstrip().endswith('Saved 2 tasks.')
    # The browser keeps no file between runs today: the next run is given the saved file by hand, as
    # the project workspace (engineering item E1 in the plan) would.
    saved = json.dumps([{'title': 'Read chapter 3', 'due': '2099-01-02', 'done': False}, {'title': 'Practice', 'due': None, 'done': True}])
    output, error = run('planner', 'planner.py', ['stats', 'quit'], {'plan.json': saved})
    assert error is None and 'Loaded 2 tasks.' in output and '1 of 2 done, 0 late.' in output
    output, error = run('planner', 'planner.py', ['quit'], {'plan.json': '{oops'})
    assert error is None and 'plan.json could not be read' in output

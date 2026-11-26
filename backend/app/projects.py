"""E1: the project workspace (docs/plan/courses/py-final-project.md, section 3).

A project is a few text files (code and data) kept with the learner's account and restored next time.
Nothing here ever runs: the browser runs main.py in its worker, as it runs lessons, with the other .py
files importable and the rest given as files the program can open. When the learner turns on "keep the
files my program writes", the page saves what the program wrote, like any other edit.

Only the learner sees their projects. The title and README.md go through the text policy before they
are kept. Other files are code and data: a date like 2026-12-01 in a save file looks like a phone number
to the policy, so they are not checked, and nothing here is shown to anyone else.
"""
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from . import text_policy

MAX_PROJECTS = 20
MAX_FILES = 20
MAX_FILE_CHARS = 50_000
MAX_TOTAL_CHARS = 200_000
MAX_TITLE = 60
MAIN = 'main.py'
EXTENSIONS = ('py', 'txt', 'csv', 'json', 'md', 'html', 'css')
# Lowercase, at the top of the project, as the worker's own check for importable files asks.
NAME = re.compile(rf'[a-z][a-z0-9_-]{{0,30}}\.({"|".join(EXTENSIONS)})')
# The worker refuses a .py file named like one of Python's own modules, since it would hide it.
PYTHON_NAMES = frozenset(sys.stdlib_module_names) | frozenset(sys.builtin_module_names) | {'js', 'pyodide', 'pyodide_js', 'micropip'}
STARTERS_DIR = Path(__file__).resolve().parent.parent / 'content' / 'projects'


@dataclass(frozen=True)
class Starter:
    id: str
    title: str
    about: str
    final: bool


STARTERS = {s.id: s for s in [
    Starter('blank', 'Empty project', 'Just main.py, for anything you want to build.', False),
    Starter('lockpick', 'Lockpick', 'A word game: guess letters to open a vault before six misses jam the lock. Comes with words.txt and empty versions of the four functions the game is built on.', True),
    Starter('site-builder', 'Site Builder', 'Turn a data file into a small website, one page per item. Comes with site.json and empty versions of the three functions the site is built on.', True),
    Starter('planner', 'Planner', 'A to-do app that remembers your plan between runs. Comes split into main.py, commands.py and storage.py.', True),
]}


def starter_files(starter_id):
    folder = STARTERS_DIR / starter_id
    return {p.name: p.read_text() for p in sorted(folder.iterdir()) if p.is_file()}


def name_problem(name):
    """None if a file may have this name, otherwise what to change."""
    if not NAME.fullmatch(name):
        return (f'"{name[:40]}" can\'t be a file name here. Use lowercase letters, digits, _ or -, '
                f'starting with a letter, and end with one of: {", ".join("." + e for e in EXTENSIONS)}.')
    if name.endswith('.py') and '-' in name:
        return f'{name} can\'t be imported with a - in its name. Use _ instead, like {name.replace("-", "_")}.'
    if name.endswith('.py') and name[:-3] in PYTHON_NAMES:
        return f'{name} would hide Python\'s own {name[:-3]} module, so choose another name.'
    return None


def clean_title(title):
    title = ' '.join(title.split())
    if not title:
        raise ValueError('Give your project a name.')
    if len(title) > MAX_TITLE:
        raise ValueError(f'Keep the name to {MAX_TITLE} characters.')
    if (reason := text_policy.problem(title)):
        raise ValueError(reason)
    return title


def clean_files(files):
    """The files as they may be kept, or ValueError saying what to change."""
    if MAIN not in files:
        raise ValueError('A project always has main.py: it is what runs.')
    if len(files) > MAX_FILES:
        raise ValueError(f'A project can hold {MAX_FILES} files. Delete one to make room.')
    for name, text in files.items():
        if (reason := name_problem(name)):
            raise ValueError(reason)
        if len(text) > MAX_FILE_CHARS:
            raise ValueError(f'{name} is over {MAX_FILE_CHARS:,} characters. Split it into smaller files.')
    if sum(len(t) for t in files.values()) > MAX_TOTAL_CHARS:
        raise ValueError(f'A project can hold {MAX_TOTAL_CHARS:,} characters in all. Delete a file you no longer need.')
    if 'readme.md' in files and (reason := text_policy.problem(files['readme.md'])):
        raise ValueError(f'readme.md: {reason}')
    return dict(sorted(files.items(), key=lambda kv: (kv[0] != MAIN, kv[0])))


def summary(row):
    files = json.loads(row.files)
    return {'id': row.id, 'title': row.title, 'starter': row.starter, 'files': len(files), 'updated': row.updated, 'revision': row.revision}


def view(row):
    return {**summary(row), 'keep_written': row.keep_written, 'files': json.loads(row.files)}


def starters_view():
    return [{'id': s.id, 'title': s.title, 'about': s.about, 'final': s.final, 'files': list(starter_files(s.id))} for s in STARTERS.values()]

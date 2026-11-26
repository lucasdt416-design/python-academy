"""E1: the project workspace (app/projects.py, /api/projects).

Projects are text kept for one learner. Nothing in them runs on the server; these tests prove what is
kept, what is refused and why, that nobody else can read or change a learner's project, and that a save
from an old copy of the page never overwrites newer work.
"""
import ast
import json

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

import test_unit2_lessons as helpers
from app import projects
from app.db import Event, Project, User
from app.main import engine
from test_profiles import sign_in
from test_unit2_lessons import client  # noqa: F401

H = helpers.HEADERS


def create(client, starter='blank', title=''):
    r = client.post('/api/projects', json={'starter': starter, 'title': title}, headers=H)
    assert r.status_code == 200, r.text
    return r.json()


def save(client, project, **change):
    return client.put(f'/api/projects/{project["id"]}', json={'revision': project['revision'], **change}, headers=H)


def test_only_signed_in_learners_have_projects(client):
    assert client.get('/api/projects').status_code == 401
    sign_in(client, 'parent')
    assert client.get('/api/projects').status_code == 403
    assert client.post('/api/projects', json={'starter': 'blank'}, headers=H).status_code == 403


def test_starters_are_listed_for_everyone_and_each_one_parses(client):
    starters = client.get('/api/project-starters').json()
    assert [s['id'] for s in starters] == ['blank', 'lockpick', 'site-builder', 'planner']
    for s in starters:
        files = projects.starter_files(s['id'])
        assert s['files'] == list(files) and projects.MAIN in files
        assert projects.clean_files(files)
        for name, text in files.items():
            if name.endswith('.py'):
                ast.parse(text, name)


@pytest.mark.parametrize('starter, functions', [
    ('lockpick', {'load_words', 'mask', 'problem_with', 'is_open'}),
    ('site-builder', {'escape', 'slug', 'build'}),
])
def test_final_project_starters_name_the_functions_the_plan_requires(starter, functions):
    # The names in py-final-project.md section 1. The bodies are left for the learner.
    tree = ast.parse(projects.starter_files(starter)['main.py'])
    assert functions <= {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}


def test_a_learner_creates_edits_and_reopens_a_project(client):
    sign_in(client)
    made = create(client, 'lockpick')
    assert made['title'] == 'Lockpick' and made['revision'] == 1 and not made['keep_written']
    assert list(made['files']) == ['main.py', 'words.txt']
    files = {**made['files'], 'main.py': 'print("mine")', 'notes.md': 'Ideas'}
    saved = save(client, made, files=files, title='  My   vault ', keep_written=True).json()
    assert saved['revision'] == 2 and saved['title'] == 'My vault' and saved['keep_written']
    again = client.get(f'/api/projects/{made["id"]}').json()
    assert again['files'] == {'main.py': 'print("mine")', 'notes.md': 'Ideas', 'words.txt': made['files']['words.txt']}
    listed = client.get('/api/projects').json()
    assert listed['projects'] == [{'id': made['id'], 'title': 'My vault', 'starter': 'lockpick', 'files': 3, 'updated': again['updated'], 'revision': 2}]
    with Session(engine) as db:
        events = [e.action for e in db.scalars(select(Event))]
        # The title is the learner's own words, so the history records only that a project was made.
        assert 'project_created' in events and all('vault' not in (e.detail or '') for e in db.scalars(select(Event)))


def test_a_save_from_an_old_copy_is_refused_and_the_newer_work_kept(client):
    sign_in(client)
    made = create(client)
    first = save(client, made, files={'main.py': 'print(1)'})
    assert first.status_code == 200
    stale = save(client, made, files={'main.py': 'print("old tab")'})
    assert stale.status_code == 409 and 'another tab' in stale.json()['detail']
    assert client.get(f'/api/projects/{made["id"]}').json()['files'] == {'main.py': 'print(1)'}


@pytest.mark.parametrize('files, message', [
    ({'helpers.py': ''}, 'always has main.py'),
    ({'main.py': '', 'Main.PY': ''}, "can't be a file name"),
    ({'main.py': '', '../secret.txt': ''}, "can't be a file name"),
    ({'main.py': '', 'site/index.html': ''}, "can't be a file name"),
    ({'main.py': '', 'photo.png': ''}, "can't be a file name"),
    ({'main.py': '', 'random.py': ''}, "hide Python's own random module"),
    ({'main.py': '', 'my-tools.py': ''}, 'Use _ instead, like my_tools.py'),
    ({'main.py': 'x' * (projects.MAX_FILE_CHARS + 1)}, 'Split it into smaller files'),
    ({'main.py': '', **{f'f{i}.txt': '' for i in range(projects.MAX_FILES)}}, 'Delete one to make room'),
    ({'main.py': '', **{f'f{i}.txt': 'x' * 41_000 for i in range(5)}}, 'characters in all'),
    ({'main.py': '', 'readme.md': 'Mail me at kid@example.com'}, 'readme.md: Please leave out personal details'),
])
def test_files_that_cannot_be_kept_say_what_to_change(client, files, message):
    sign_in(client)
    made = create(client)
    r = save(client, made, files=files)
    assert r.status_code == 422 and message in json.dumps(r.json()), r.text
    assert client.get(f'/api/projects/{made["id"]}').json()['revision'] == 1


def test_data_files_are_not_put_through_the_text_policy():
    # A save file full of dates looks like phone numbers to the policy, and it is the learner's own data.
    assert projects.clean_files({'main.py': '', 'plan.json': '[{"title": "Read", "due": "2026-12-01"}]'})


@pytest.mark.parametrize('title, message', [('', 'Give your project a name'), ('x' * 61, '60 characters'), ('call 416 555 0199', 'personal details')])
def test_titles_go_through_the_text_policy(client, title, message):
    sign_in(client)
    made = create(client)
    r = save(client, made, title=title)
    assert r.status_code == 422 and message in r.json()['detail']


def test_a_learner_cannot_see_or_change_someone_elses_project(client):
    sign_in(client)
    theirs = create(client)
    with Session(engine) as db:
        db.scalars(select(User)).one().subject = 'someone-else'
        db.commit()
    sign_in(client)
    for method, body in [('GET', None), ('PUT', {'revision': 1, 'files': {'main.py': 'mine now'}}), ('DELETE', None)]:
        r = client.request(method, f'/api/projects/{theirs["id"]}', json=body, headers=H)
        assert r.status_code == 404 and r.json()['detail'] == 'That project is not in your account'
    assert client.get('/api/projects').json()['projects'] == []
    with Session(engine) as db:
        assert json.loads(db.get(Project, theirs['id']).files) == projects.starter_files('blank')


def test_deleting_a_project_removes_it(client):
    sign_in(client)
    made = create(client)
    assert client.delete(f'/api/projects/{made["id"]}', headers=H).json() == {'deleted': True}
    assert client.get(f'/api/projects/{made["id"]}').status_code == 404


def test_an_account_keeps_at_most_twenty_projects(client):
    sign_in(client)
    for _ in range(projects.MAX_PROJECTS):
        create(client)
    r = client.post('/api/projects', json={'starter': 'blank'}, headers=H)
    assert r.status_code == 409 and 'Delete one to start another' in r.json()['detail']


def test_unknown_starters_are_refused(client):
    sign_in(client)
    assert client.post('/api/projects', json={'starter': 'minecraft'}, headers=H).status_code == 422

"""Profiles (/api/profile): an avatar from fixed choices, an optional nickname, and a progress summary.

Only the signed-in person can read or change their own profile; nothing in it is shown to anyone else.
"""
import json
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

import test_unit2_lessons as helpers
from app import profiles
from app.db import Event, Profile, User, XpAward
from app.main import engine
from lesson_suite import attempt
from test_unit2_lessons import client  # noqa: F401

AVATAR = {'skin': 'honey', 'hair': 'curly', 'hair_colour': 'teal', 'outfit': 'moss', 'item': 'map'}


def sign_in(client, role='student'):
    cookie = helpers.sign_in_student()
    with Session(engine) as db:
        user = db.scalars(select(User).order_by(User.id.desc())).first()
        user.role = role
        uid = user.id
        db.commit()
    client.cookies.set('session', cookie, domain='testserver.local', path='/')
    return uid


def test_signed_out_and_unenrolled_people_have_no_profile(client):
    assert client.get('/api/profile').status_code == 401
    assert client.put('/api/profile', json={'nickname': '', 'avatar': AVATAR}, headers=helpers.HEADERS).status_code == 401
    sign_in(client, 'pending')
    assert client.get('/api/profile').status_code == 403
    assert client.put('/api/profile', json={'nickname': '', 'avatar': AVATAR}, headers=helpers.HEADERS).status_code == 403


def test_a_new_student_sees_the_default_avatar_and_their_progress(client):
    sign_in(client)
    p = client.get('/api/profile').json()
    assert (p['saved'], p['nickname'], p['avatar']) == (False, '', profiles.DEFAULT_AVATAR)
    assert p['xp'] == 0 and p['level'] == {'number': 1, 'title': 'Explorer', 'xp_into_level': 0, 'xp_for_next': 500}
    assert p['completed'] == 0 and p['released'] == 52 and len(p['units']) == 11
    assert p['units'][0] == {'id': 'py.u01', 'title': 'Build Your Own Adventure', 'done': 0, 'total': 5, 'more_coming': False}
    assert p['choices'] == profiles.AVATAR_CHOICES and p['streak'] == 0 and p['active_days'] == []


def test_saving_keeps_the_choices_and_records_an_event_without_the_nickname(client):
    uid = sign_in(client)
    r = client.put('/api/profile', json={'nickname': '  Nova   the  brave ', 'avatar': AVATAR}, headers=helpers.HEADERS)
    assert r.status_code == 200
    assert (r.json()['saved'], r.json()['nickname'], r.json()['avatar']) == (True, 'Nova the brave', AVATAR)
    assert client.get('/api/profile').json()['nickname'] == 'Nova the brave'
    with Session(engine) as db:
        events = db.scalars(select(Event).where(Event.user_id == uid, Event.action == 'profile_saved')).all()
        assert [e.detail for e in events] == ['']
        assert json.loads(db.get(Profile, uid).avatar) == AVATAR
    # Saving again changes the one row.
    client.put('/api/profile', json={'nickname': '', 'avatar': {**AVATAR, 'item': 'none'}}, headers=helpers.HEADERS)
    with Session(engine) as db:
        assert db.scalar(select(Profile.nickname).where(Profile.user_id == uid)) == ''
        assert len(db.scalars(select(Profile)).all()) == 1


@pytest.mark.parametrize('nickname', ['x' * 25, '<script>', 'a@b.com', 'semi;colon', 'curly{brace}'])
def test_a_nickname_outside_the_rules_is_refused(client, nickname):
    sign_in(client)
    r = client.put('/api/profile', json={'nickname': nickname, 'avatar': AVATAR}, headers=helpers.HEADERS)
    assert r.status_code == 422 and 'saved' not in r.text


@pytest.mark.parametrize('avatar', [{}, {**AVATAR, 'skin': 'green'}, {**AVATAR, 'hat': 'top'}, {k: v for k, v in AVATAR.items() if k != 'item'},
                                    {**AVATAR, 'item': 'https://example.com/a.png'}])
def test_an_avatar_outside_the_fixed_choices_is_refused(client, avatar):
    sign_in(client)
    r = client.put('/api/profile', json={'nickname': 'Nova', 'avatar': avatar}, headers=helpers.HEADERS)
    assert r.status_code == 422
    assert client.get('/api/profile').json()['saved'] is False


def test_names_in_other_alphabets_are_welcome(client):
    sign_in(client)
    r = client.put('/api/profile', json={'nickname': "Zoë O'Brien-Łukasz", 'avatar': AVATAR}, headers=helpers.HEADERS)
    assert r.status_code == 200 and r.json()['nickname'] == "Zoë O'Brien-Łukasz"


def test_xp_level_units_and_badges_come_from_the_ledgers(client):
    sign_in(client)
    for lesson_id in ['py.lists', 'py.indexing']:
        spec = __import__('test_unit4_lessons').__dict__[{'py.lists': 'LISTS', 'py.indexing': 'INDEXING'}[lesson_id]]
        assert attempt(client, lesson_id, spec.reference)['result'] == 'passed'
    p = client.get('/api/profile').json()
    assert p['xp'] == 200 and p['completed'] == 2
    assert [b['title'] for b in p['badges']] == ['Pack keeper', 'Quartermaster']
    unit4 = next(u for u in p['units'] if u['id'] == 'py.u04')
    assert (unit4['done'], unit4['total']) == (2, 5)
    assert p['streak'] == 1 and p['active_days'] == [p['today']]


def test_levels_and_streaks():
    assert profiles.level(0)['number'] == 1 and profiles.level(499)['number'] == 1
    assert profiles.level(500) == {'number': 2, 'title': 'Pathfinder', 'xp_into_level': 0, 'xp_for_next': 500}
    assert profiles.level(100_000)['title'] == 'Lorekeeper'
    with Session(engine) as db:
        from app.db import Base
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        db.add(User(id=1, subject='s', email='s@example.com', role='student'))
        for i, day in enumerate(['2026-11-17', '2026-11-18', '2026-11-20', '2026-06-01']):
            db.add(XpAward(user_id=1, task_id=f't{i}', task_version=1, xp=100, source='practice', created=f'{day}T12:00:00+00:00'))
        db.commit()
        # Today counts if there is XP today; otherwise the streak runs up to yesterday.
        assert profiles.active_days(db, 1, date(2026, 11, 20)) == (['2026-11-17', '2026-11-18', '2026-11-20'], 1)
        assert profiles.active_days(db, 1, date(2026, 11, 19)) == (['2026-11-17', '2026-11-18'], 2)
        assert profiles.active_days(db, 1, date(2026, 11, 22))[1] == 0


def test_a_parent_has_an_avatar_but_no_learning_summary(client):
    sign_in(client, 'parent')
    p = client.get('/api/profile').json()
    assert p['role'] == 'parent' and 'xp' not in p and 'units' not in p
    assert client.put('/api/profile', json={'nickname': 'Mum', 'avatar': AVATAR}, headers=helpers.HEADERS).status_code == 200


def test_the_profile_is_never_in_the_parents_family_view_or_anyone_elses_answer(client):
    # Nothing about a profile leaves the owner's own /api/profile.
    sign_in(client)
    client.put('/api/profile', json={'nickname': 'Secretname', 'avatar': AVATAR}, headers=helpers.HEADERS)
    for path in ('/api/me', '/api/awards', '/api/progress', '/api/catalog', '/api/recommendation', '/api/history'):
        assert 'Secretname' not in client.get(path).text, path


def test_profile_changes_are_rate_limited(client):
    sign_in(client)
    codes = [client.put('/api/profile', json={'nickname': '', 'avatar': AVATAR}, headers=helpers.HEADERS).status_code for _ in range(21)]
    assert codes[:20] == [200] * 20 and codes[20] == 429

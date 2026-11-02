import os
import tempfile
from datetime import date
os.environ['DATABASE_URL'] = 'sqlite:///' + tempfile.mktemp(suffix='.db')
os.environ['SESSION_SECRET'] = 'test-secret-that-is-at-least-thirty-two-characters'
from app.main import app, engine, Base, User, Invitation, Attempt, LESSONS, age_on
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select
from itsdangerous import TimestampSigner
import base64
import secrets
from app import sessions
from app.db import UserSession
import json
import pytest
from hypothesis import given, strategies as st

client = TestClient(app)
HEADERS = {'origin': 'http://localhost:3000'}

@pytest.fixture(autouse=True)
def clean():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    client.cookies.clear()

def signin(role='pending', email='learner@example.com', parent_id=None):
    with Session(engine) as db:
        u = User(subject=email, email=email, role=role, parent_id=parent_id)
        db.add(u)
        db.commit()
        uid = u.id
    login_as(uid)
    return uid

def session_cookie(payload, secret=None):
    # Signed exactly as Starlette's SessionMiddleware signs it.
    return TimestampSigner(secret or os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps(payload).encode())).decode()

def new_session(uid):
    # A real server-side session row, as the Google callback would create.
    token = secrets.token_urlsafe(32)
    now = int(sessions.clock())
    with Session(engine) as db:
        db.add(UserSession(id=sessions.digest(token), user_id=uid, created=now, last_seen=now, expires=now + sessions.ABSOLUTE))
        db.commit()
    return token

def login_as(uid):
    client.cookies.set('session',session_cookie({'sid':new_session(uid)}),domain='testserver.local',path='/')

def post(path, data):
    return client.post('/api/'+path, json=data, headers=HEADERS)

def test_health_and_no_anonymous_access():
    assert client.get('/health').json() == {'status':'ok'}
    assert client.get('/api/me').status_code == 401
    assert post('invitations', {'email':'a@b.com'}).status_code == 401

def test_age_boundary():
    assert age_on(date(2000,10,25),date(2026,10,24)) == 25
    assert age_on(date(2000,10,24),date(2026,10,24)) == 26
    signin()
    today=date.today()
    assert post('enroll', {'birthday':today.replace(year=today.year-25).isoformat()}).status_code == 422
    assert post('enroll', {'birthday':today.replace(year=today.year-26).isoformat()}).json() == {'role':'parent'}

def test_invitation_ownership_age_and_single_use():
    parent = signin('parent','parent@example.com')
    response=post('invitations', {'email':'learner@example.com'})
    assert response.status_code == 200
    token=response.json()['url'].split('invite=')[1]
    signin('pending','wrong@example.com')
    assert post('enroll',{'birthday':'2010-01-01','invitation':token}).status_code == 400
    student=signin('pending','learner@example.com')
    assert post('enroll',{'birthday':'2020-01-01','invitation':token}).status_code == 422
    assert post('enroll',{'birthday':'2010-01-01','invitation':token}).json()=={'role':'student'}
    with Session(engine) as db:
        assert db.get(User,student).parent_id == parent
        assert db.scalar(select(Invitation)).used
    assert post('enroll',{'birthday':'2010-01-01','invitation':token}).status_code == 403

def test_csrf_and_role_restrictions():
    signin('student')
    assert client.post('/api/logout',json={}).status_code == 403
    assert client.post('/api/logout',json={},headers={'origin':'https://evil.example'}).status_code == 403
    assert post('invitations',{'email':'a@b.com'}).status_code==403
    assert client.get('/api/family').status_code ==403

def test_practice_checks_and_persistence():
    signin('student')
    assert post('attempts',{'lesson_id':'hello','code':'print("wrong")','output':'wrong\n'}).json()['passed'] is False
    assert post('attempts',{'lesson_id':'hello','code':'print("A forest.")\nprint("A dragon!")','output':'A forest.\nA dragon!\n'}).json()['passed'] is True
    assert post('attempts',{'lesson_id':'hello','code':'pass','output':'Hello, Python!'}).json()['passed'] is False
    assert post('attempts',{'lesson_id':'missing','code':'','output':''}).status_code ==404
    with Session(engine) as db:
        assert len(list(db.scalars(select(Attempt))))==3
    assert len(client.get('/api/history').json())==3

def test_family_isolation():
    other=signin('parent','other@example.com')
    signin('student','otherchild@example.com',other)
    signin('parent','mine@example.com')
    assert client.get('/api/family').json() == []

@given(st.dates(min_value=date(1900,1,1), max_value=date(2026,10,24)))
def test_age_invariant(birthday):
    age=age_on(birthday,date(2026,10,24))
    assert 0 <= age <=126
    assert age in {2026-birthday.year,2025-birthday.year}

def test_expired_invitation_and_exact_student_boundary():
    from datetime import datetime,timedelta,timezone
    signin('parent','parent@example.com')
    token=post('invitations',{'email':'student@example.com'}).json()['url'].split('invite=')[1]
    signin('pending','student@example.com')
    today=date.today()
    birthday=today.replace(year=today.year-13).isoformat()
    with Session(engine) as db:
        inv=db.scalar(select(Invitation))
        inv.expires=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
        db.commit()
    assert post('enroll',{'birthday':birthday,'invitation':token}).status_code==400
    with Session(engine) as db:
        inv=db.scalar(select(Invitation))
        inv.expires=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
        db.commit()
    assert post('enroll',{'birthday':birthday,'invitation':token}).json()=={'role':'student'}


def test_future_birthday_and_invalid_email_are_rejected():
    from datetime import timedelta
    signin()
    assert post('enroll', {'birthday': (date.today() + timedelta(days=1)).isoformat()}).status_code == 422
    assert post('enroll', {'birthday': 'not-a-date'}).status_code == 422
    signin('parent', 'parent@example.com')
    assert post('invitations', {'email': 'not-an-email'}).status_code == 422


def test_oversized_submission_and_logout():
    signin('student')
    assert post('attempts', {'lesson_id': 'hello', 'code': 'x' * 20001, 'output': ''}).status_code == 422
    assert post('logout', {}).status_code == 200
    assert client.get('/api/me').status_code == 401


def test_unverified_google_account_cannot_create_user(monkeypatch):
    from app.main import oauth
    async def unverified(request):
        return {'userinfo': {'sub': 'unverified', 'email': 'user@example.com', 'email_verified': False}}
    monkeypatch.setattr(oauth.google, 'authorize_access_token', unverified)
    assert client.get('/auth/google/callback').status_code == 403
    with Session(engine) as db:
        assert db.scalar(select(User)) is None


def test_google_callback_records_account_and_rotates_session(monkeypatch):
    from app.main import oauth
    async def verified(request):
        return {'userinfo': {'sub': 'verified-google-sub', 'email': 'USER@example.com', 'email_verified': True}}
    monkeypatch.setattr(oauth.google, 'authorize_access_token', verified)
    response = client.get('/auth/google/callback', follow_redirects=False)
    assert response.status_code == 307
    assert response.headers['location'] == 'http://localhost:3000'
    assert client.get('/api/me').json()['email'] == 'user@example.com'
    assert client.get('/api/history').json()[0]['action'] == 'signed_in'



@pytest.mark.parametrize('code,output,passed', [
    ('print("Mars")\nprint("A robot waves")', 'Mars\nA robot waves\n', True),
    ("print('Ocean')\nprint('A fish speaks')", 'Ocean\nA fish speaks\n', True),
    ('# Scene\nprint("Moon")\nprint("Footsteps")', 'Moon\nFootsteps\n', True),
    ('print("Mars")\nprint("A robot waves")', 'A robot waves\nMars\n', False),
    ('print("Only one")', 'Only one\n', False),
    ('print("Unclosed)', '', False),
    ('print("")\nprint("Surprise")', '\nSurprise\n', False),
    ('print("A", "B")\nprint("C")', 'A B\nC\n', True),
    ('import os\nprint("A")', 'A\n', False),
    ('print("A")\nprint("B", end="")', 'A\nB', False),
])
def test_opening_accepts_creativity_and_explains_mistakes(code, output, passed):
    from app.main import check_opening
    result, feedback = check_opening(code, output)
    assert result is passed
    assert feedback


# "Open the story" refuses its own worked example copied unchanged (ASSESS-07), so tests that need
# a passing hello answer use this one. The other lessons' worked examples still pass their checks.
HELLO = {'code': 'print("A forest.")\nprint("A dragon!")', 'output': 'A forest.\nA dragon!\n'}

def answer(lesson):
    if lesson['id'] == 'hello':
        return dict(HELLO, inputs=[])
    return {'code': lesson['example'], 'output': lesson['exampleOutput'] + '\n', 'inputs': list(lesson['exampleInputs'])}

@pytest.mark.parametrize('lesson', LESSONS, ids=lambda lesson: lesson['id'])
def test_authored_examples_execute_and_pass_checks(lesson):
    import contextlib, io
    from app.lesson_checks import check_story
    stream = io.StringIO()
    replies = iter(lesson['exampleInputs'])
    with contextlib.redirect_stdout(stream):
        exec(lesson['example'], {'input': lambda prompt='': next(replies)})
    assert stream.getvalue().rstrip() == lesson['exampleOutput']
    passed, feedback = check_story(lesson['id'], lesson['example'], stream.getvalue(), lesson['exampleInputs'])
    # Copying the worked example is not "making it your own" in the first lesson.
    assert passed is (lesson['id'] != 'hello'), feedback

@pytest.mark.parametrize('lesson_id,code,inputs,output,passed', [
    ('variables', 'hero="Kai"\ntool="rope"\nprint(f"{hero} carries {tool}")', [], 'Kai carries rope\n', True),
    ('variables', 'hero="Kai"\ntool="rope"\nprint("Kai carries rope")', [], 'Kai carries rope\n', False),
    ('input', 'name=input("Name? ")\nprint(f"Hello, {name}!")', ['Mira'], 'Hello, Mira!\n', True),
    ('input', 'name=input("Name? ")\nprint("Hello, Nova!")', ['Nova'], 'Hello, Nova!\n', False),
    ('choices', 'p=input("Path? ")\nif p != "right":\n print("Lake")\nelse:\n print("Mountain")', ['left'], 'Lake\n', True),
    ('choices', 'p=input("Path? ")\nif p == "left":\n print("Lake")\nelse:\n print("Lake")', ['left'], 'Lake\n', False),
    ('choices', 'p=input("Path? ")\nif True:\n print("Lake")\nelse:\n print("Mountain")', ['left'], 'Lake\n', False),
    ('hello', 'import os\nos.system("touch /tmp/unwanted")', [], '', False),
    ('hello', 'while True:\n pass', [], '', False),
    ('hello', 'print("One")\nprint("Two")', [], 'forged output\n', False),
])
def test_checks_validate_behavior_and_accept_alternatives(lesson_id,code,inputs,output,passed):
    from app.lesson_checks import check_story
    result, feedback = check_story(lesson_id,code,output,inputs)
    assert result is passed
    assert feedback

def test_public_preview_checks_do_not_create_history():
    lesson = LESSONS[0]
    response = post('check', dict(answer(lesson), lesson_id=lesson['id']))
    assert response.json()['passed']
    with Session(engine) as db:
        assert list(db.scalars(select(Attempt))) == []
    assert client.get('/api/progress').status_code == 401
    assert client.get('/api/family').status_code == 401

def test_student_progress_is_persisted_and_isolated():
    signin('student','one@example.com')
    lesson=LESSONS[0]
    payload=dict(answer(lesson), lesson_id='hello')
    assert post('attempts',payload).json()['passed']
    assert post('attempts',payload).json()['passed']
    assert client.get('/api/progress').json() == ['hello']
    signin('student','two@example.com')
    assert client.get('/api/progress').json() == []

def test_lessons_api_is_unchanged_by_the_content_format():
    from pathlib import Path
    fixture = Path(__file__).with_name('fixtures') / 'legacy_lessons_v1.json'
    assert client.get('/api/lessons').json() == json.loads(fixture.read_text())

def test_checks_report_result_states_alongside_passed():
    lesson = LESSONS[0]
    passed = post('check', dict(answer(lesson), lesson_id='hello')).json()
    assert passed['passed'] is True and passed['result'] == 'passed'
    unsupported = post('check', {'lesson_id':'hello','code':'import os\nprint("A")','output':'A\n'}).json()
    assert unsupported['passed'] is False and unsupported['result'] == 'unsupported'
    signin('student')
    saved = post('attempts', {'lesson_id':'hello','code':'print("Only one")','output':'Only one\n'}).json()
    assert saved['passed'] is False and saved['result'] == 'needs_work'
    with Session(engine) as db:
        assert db.scalar(select(Attempt)).passed is False

def test_passing_challenge_awards_xp_and_badge_once_and_stores_results():
    from app.awards import badges, total_xp
    from app.db import XpAward
    uid = signin('student')
    good = {'lesson_id':'hello','code':'print("A forest.")\nprint("A dragon!")','output':'A forest.\nA dragon!\n'}
    for _ in range(3):
        assert post('attempts', good).json()['result'] == 'passed'
    assert post('attempts', {'lesson_id':'hello','code':'print("Only one")','output':'Only one\n'}).json()['result'] == 'needs_work'
    assert post('attempts', {'lesson_id':'input','code':'import os','output':''}).json()['result'] == 'unsupported'
    with Session(engine) as db:
        attempts = list(db.scalars(select(Attempt).order_by(Attempt.id)))
        assert [a.result for a in attempts] == ['passed', 'passed', 'passed', 'needs_work', 'unsupported']
        awards = list(db.scalars(select(XpAward)))
        assert [(a.task_id, a.task_version, a.xp, a.source, a.attempt_id) for a in awards] == [('hello.challenge', 3, 100, 'practice', attempts[0].id)]
        assert total_xp(db, uid) == 100
        assert badges(db, uid) == {'py.badge.story-spark'}
    assert client.get('/api/progress').json() == ['hello']

def test_new_task_or_badge_version_does_not_award_again():
    from app.awards import award_challenge
    from app.db import BadgeAward, XpAward
    from app.main import CONTENT
    uid = signin('student')
    lesson = CONTENT['hello']
    # As production holds it: awarded under challenge v1, before ASSESS-07 (v2) and ENG-04 part 2a (v3).
    original = lesson.model_copy(update={
        'tasks': [t.model_copy(update={'version': 1}) if t.type == 'challenge' else t for t in lesson.tasks],
        'badge': lesson.badge.model_copy(update={'version': 1}),
    })
    revised = lesson.model_copy(update={'badge': lesson.badge.model_copy(update={'version': 2})})
    assert lesson.task('challenge').version == 3
    with Session(engine) as db:
        attempt = Attempt(user_id=uid, lesson_id='hello', code='', output='', passed=True, result='passed')
        db.add(attempt)
        db.flush()
        award_challenge(db, uid, original, attempt.id)
        award_challenge(db, uid, lesson, attempt.id)
        award_challenge(db, uid, revised, attempt.id)
        db.commit()
        assert [(a.task_version, a.xp) for a in db.scalars(select(XpAward))] == [(1, 100)]
        assert [b.badge_version for b in db.scalars(select(BadgeAward))] == [1]

def pass_lesson(lesson_id):
    lesson = next(l for l in LESSONS if l['id'] == lesson_id)
    response = post('attempts', dict(answer(lesson), lesson_id=lesson_id))
    assert response.json()['result'] == 'passed'

def test_catalog_is_public_and_frozen_for_the_interface():
    from pathlib import Path
    fixture = Path(__file__).with_name('fixtures') / 'catalog_v1.json'
    response = client.get('/api/catalog')
    assert response.status_code == 200
    assert response.json() == json.loads(fixture.read_text())
    py = response.json()['courses'][0]
    assert [l['id'] for l in py['units'][0]['lessons']] == ['hello', 'variables', 'input', 'choices', 'adventure']
    assert [l['id'] for l in py['units'][1]['lessons']] == ['py.arithmetic', 'py.int-float', 'py.convert-input', 'py.compare', 'py.boolean-logic', 'py.elif']
    # complete: a new field only (EDU-04 part 2); unit 1's other fields are as before.
    assert [u['complete'] for u in py['units'][:3]] == [True, True, False]
    assert [l['id'] for l in py['units'][2]['lessons']] == ['py.while-loops', 'py.loop-termination', 'py.for-range']
    assert all(u['lessons'] == [] for u in py['units'][3:])

def test_awards_are_private_to_the_student_and_in_catalog_order():
    assert client.get('/api/awards').status_code == 401
    signin('parent', 'parent@example.com')
    assert client.get('/api/awards').status_code == 403
    signin('student')
    assert client.get('/api/awards').json() == {'xp': 0, 'completed': [], 'badges': []}
    pass_lesson('adventure')
    pass_lesson('hello')
    pass_lesson('hello')
    assert client.get('/api/awards').json() == {
        'xp': 200, 'completed': ['hello', 'adventure'],
        'badges': [{'id': 'py.badge.story-spark', 'title': 'Story spark'}, {'id': 'py.badge.adventure-maker', 'title': 'Adventure maker'}]}
    assert client.get('/api/progress').json() == ['hello', 'adventure']

def test_family_completed_lessons_come_from_the_ledger():
    parent = signin('parent', 'parent@example.com')
    child = signin('student', 'child@example.com', parent)
    pass_lesson('hello')
    with Session(engine) as db:
        db.add(Attempt(user_id=child, lesson_id='variables', code='stars=7\nprint(stars*3)', output='21\n', passed=True))
        db.commit()
    login_as(parent)
    [learner] = client.get('/api/family').json()
    assert len(learner['attempts']) == 2
    assert learner['completed'] == ['hello']

def test_goals_are_public_and_frozen_for_the_interface():
    from pathlib import Path
    fixture = Path(__file__).with_name('fixtures') / 'goals_v1.json'
    assert client.get('/api/goals').json() == json.loads(fixture.read_text())
    assert [g['id'] for g in client.get('/api/goals').json()] == ['scratch', 'hackathon', 'university', 'websites', 'data', 'explore']

def test_only_students_choose_goals_and_skipping_gives_the_default():
    assert client.get('/api/goal').status_code == 401
    assert post('goal', {'goal': 'data'}).status_code == 401
    signin('parent', 'parent@example.com')
    assert client.get('/api/goal').status_code == 403
    assert post('goal', {'goal': 'data'}).status_code == 403
    signin('student')
    assert client.get('/api/goal').json() == {'goal': None, 'chosen': False, 'asked': False}
    assert post('goal', {'goal': 'astronaut'}).status_code == 422
    assert post('goal', {}).json() == {'goal': 'scratch', 'chosen': False, 'asked': True}
    assert post('goal', {'goal': 'hackathon'}).json() == {'goal': 'hackathon', 'chosen': True, 'asked': True}
    assert [(e['action'], e['detail']) for e in client.get('/api/history').json()[:2]] == [('goal_chosen', 'hackathon'), ('goal_skipped', 'scratch')]

def test_recommendation_follows_the_goal_and_progress():
    assert client.get('/api/recommendation').status_code == 401
    signin('student')
    first = client.get('/api/recommendation').json()
    assert (first['kind'], first['lesson'], first['reason']) == ('start', 'hello', 'Start of your Learn to code path.')
    post('goal', {'goal': 'hackathon'})
    assert client.get('/api/recommendation').json()['reason'] == 'Start of your hackathon path.'
    pass_lesson('hello')
    after = client.get('/api/recommendation').json()
    assert (after['kind'], after['lesson'], after['reason']) == ('continue', 'variables', "You're partway through Python Foundations.")
    assert after['rules_version'] == 2

def test_parents_see_their_learners_goal():
    parent = signin('parent', 'parent@example.com')
    signin('student', 'child@example.com', parent)
    post('goal', {'goal': 'university'})
    login_as(parent)
    assert client.get('/api/family').json()[0]['goal'] == 'Prepare for university CS or engineering'

def test_player_replies_are_bounded():
    assert post('check', {'lesson_id':'input','code':'','output':'','inputs':['x'*501]}).status_code == 422


def test_story_checks_bound_f_string_expansion():
    from app.lesson_checks import check_story
    code = 'x="text"\n' + 'x=f"{x}{x}"\n'*18 + 'print(x)'
    passed, feedback = check_story('hello', code, '', [])
    assert not passed
    assert '20,000' in feedback


def test_legacy_arithmetic_does_not_earn_character_badge():
    uid=signin('student')
    with Session(engine) as db:
        db.add(Attempt(user_id=uid, lesson_id='variables', code='stars=7\nprint(stars*3)', output='21\n', passed=True))
        db.commit()
    assert client.get('/api/progress').json() == []

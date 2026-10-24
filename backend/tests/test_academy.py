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
    cookie = TimestampSigner(os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps({'uid':uid}).encode())).decode()
    client.cookies.set('session',cookie,domain='testserver.local',path='/')
    return uid

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
    assert post('attempts',{'lesson_id':'hello','code':LESSONS[0]['starter'],'output':'Hello, Python!\n'}).json()['passed'] is True
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

@pytest.mark.parametrize('lesson',LESSONS)
def test_reference_curriculum(lesson):
    import contextlib,io
    # Only trusted authored reference solutions execute in tests.
    solutions={'hello':'print("Hello, Python!")','variables':'stars=7\nprint(stars*3)','loop':'for n in range(1,6):\n print(n)'}
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream):
        exec(solutions[lesson['id']],{})
    assert stream.getvalue()==lesson['expected']

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

from . import content
from .lesson_checks import assess, check_story
import hashlib
import os
import secrets
from datetime import date, datetime, timedelta, timezone

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Date, ForeignKey, String, Text, create_engine, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from starlette.middleware.sessions import SessionMiddleware

PRODUCTION = os.getenv('ENVIRONMENT') == 'production'
SECRET = os.getenv('SESSION_SECRET', '')
if PRODUCTION and len(SECRET) < 32:
    raise RuntimeError('SESSION_SECRET must contain at least 32 characters')
ORIGIN = os.getenv('APP_ORIGIN', 'http://localhost:3000').rstrip('/')
API_ORIGIN = os.getenv('API_ORIGIN', ORIGIN).rstrip('/')
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///./academy.db').replace('postgres://', 'postgresql+psycopg://', 1)
if DB_URL.startswith('postgresql://'):
    DB_URL = DB_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
engine = create_engine(DB_URL, connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite') else {})

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(320))
    role: Mapped[str] = mapped_column(String(20), default='pending')
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)

class Invitation(Base):
    __tablename__ = 'invitations'
    id: Mapped[int] = mapped_column(primary_key=True)
    digest: Mapped[str] = mapped_column(String(64), unique=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    email: Mapped[str] = mapped_column(String(320))
    expires: Mapped[str] = mapped_column(String(40))
    used: Mapped[bool] = mapped_column(default=False)

class Event(Base):
    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    action: Mapped[str] = mapped_column(String(80))
    detail: Mapped[str] = mapped_column(Text, default='')
    created: Mapped[str] = mapped_column(String(40), default=lambda: datetime.now(timezone.utc).isoformat())

class Attempt(Base):
    __tablename__ = 'attempts'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    lesson_id: Mapped[str] = mapped_column(String(80))
    code: Mapped[str] = mapped_column(Text)
    output: Mapped[str] = mapped_column(Text)
    passed: Mapped[bool] = mapped_column(default=False)

CATALOG, CONTENT = content.load()
LESSONS = content.legacy_lessons(CATALOG, CONTENT)

def check_opening(code, output):
    return check_story('hello', code, output, [])

Base.metadata.create_all(engine)
app = FastAPI(title='Python Academy')
app.add_middleware(SessionMiddleware, secret_key=SECRET or secrets.token_urlsafe(48), same_site='lax', https_only=PRODUCTION, max_age=86400)
oauth = OAuth()
oauth.register(name='google', client_id=os.getenv('GOOGLE_CLIENT_ID'), client_secret=os.getenv('GOOGLE_CLIENT_SECRET'), server_metadata_url='https://accounts.google.com/.well-known/openid-configuration', client_kwargs={'scope': 'openid email profile'})

@app.middleware('http')
async def security(request: Request, call_next):
    if request.method in {'POST', 'PUT', 'DELETE', 'PATCH'} and request.headers.get('origin') != ORIGIN:
        return JSONResponse({'detail': 'Untrusted origin'}, status_code=403)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Cache-Control'] = 'no-store'
    return response

def age_on(birthday: date, today: date | None = None) -> int:
    today = today or date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

def current(request: Request, db: Session, role: str | None = None):
    user = db.get(User, request.session.get('uid', -1))
    if not user:
        raise HTTPException(401, 'Sign in to continue')
    if role and user.role != role:
        raise HTTPException(403, 'This action is unavailable for this account')
    return user

def audit(db, user, action, detail=''):
    db.add(Event(user_id=user.id, action=action, detail=detail))

@app.get('/health')
def health():
    with engine.connect() as conn:
        conn.exec_driver_sql('SELECT 1')
    return {'status': 'ok'}

@app.get('/auth/google')
async def login(request: Request):
    if not os.getenv('GOOGLE_CLIENT_ID') or not os.getenv('GOOGLE_CLIENT_SECRET'):
        raise HTTPException(503, 'Google sign-in is awaiting configuration')
    return await oauth.google.authorize_redirect(request, API_ORIGIN + '/auth/google/callback')

@app.get('/auth/google/callback')
async def callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        info = token['userinfo']
        if not info.get('email_verified'):
            raise HTTPException(403, 'A verified Google email is required')
    except (OAuthError, KeyError):
        raise HTTPException(400, 'Sign-in could not be verified. Please try again.')
    with Session(engine) as db:
        user = db.scalar(select(User).where(User.subject == info['sub']))
        if not user:
            user = User(subject=info['sub'], email=info['email'].lower())
            db.add(user)
            db.flush()
        request.session.clear()
        request.session['uid'] = user.id
        audit(db, user, 'signed_in')
        db.commit()
    return RedirectResponse(ORIGIN)

@app.post('/api/logout')
def logout(request: Request):
    request.session.clear()
    return {'ok': True}

@app.get('/api/me')
def me(request: Request):
    with Session(engine) as db:
        u = current(request, db)
        return {'id': u.id, 'email': u.email, 'role': u.role}

class Enrollment(BaseModel):
    birthday: date
    invitation: str = Field(default='', max_length=200)

@app.post('/api/enroll')
def enroll(data: Enrollment, request: Request):
    with Session(engine) as db:
        u = current(request, db, 'pending')
        age = age_on(data.birthday)
        if age < 0 or age > 120:
            raise HTTPException(422, 'Enter a valid date of birth')
        if data.invitation:
            inv = db.scalar(select(Invitation).where(Invitation.digest == hashlib.sha256(data.invitation.encode()).hexdigest()))
            if not inv or inv.used or datetime.fromisoformat(inv.expires) < datetime.now(timezone.utc) or inv.email != u.email:
                raise HTTPException(400, 'This invitation is invalid, expired, used, or for another email')
            if age < 13:
                raise HTTPException(422, 'Students must be at least 13')
            claimed = db.execute(update(Invitation).where(Invitation.id == inv.id, Invitation.used == False).values(used=True))
            if claimed.rowcount != 1:
                raise HTTPException(409, 'Invitation already used')
            u.role, u.parent_id = 'student', inv.parent_id
        else:
            if age <= 25:
                raise HTTPException(422, 'Parents must be over 25')
            u.role = 'parent'
        u.birthday = data.birthday
        audit(db, u, 'enrolled', u.role)
        db.commit()
        return {'role': u.role}

class InviteInput(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

@app.post('/api/invitations')
def invite(data: InviteInput, request: Request):
    with Session(engine) as db:
        u = current(request, db, 'parent')
        token = secrets.token_urlsafe(32)
        db.add(Invitation(digest=hashlib.sha256(token.encode()).hexdigest(), parent_id=u.id, email=data.email.lower(), expires=(datetime.now(timezone.utc)+timedelta(days=7)).isoformat()))
        audit(db, u, 'invitation_created')
        db.commit()
        return {'url': ORIGIN + '/?invite=' + token, 'expires_in_days': 7}

@app.get('/api/family')
def family(request: Request):
    with Session(engine) as db:
        u = current(request, db, 'parent')
        return [{'id': s.id, 'email': s.email, 'attempts': [{'lesson_id': a.lesson_id, 'passed': a.passed} for a in db.scalars(select(Attempt).where(Attempt.user_id == s.id))]} for s in db.scalars(select(User).where(User.parent_id == u.id))]

@app.get('/api/history')
def history(request: Request):
    with Session(engine) as db:
        u = current(request, db)
        return [{'action': e.action, 'created': e.created, 'detail': e.detail} for e in db.scalars(select(Event).where(Event.user_id == u.id).order_by(Event.id.desc()).limit(100))]

@app.get('/api/lessons')
def lessons():
    return LESSONS

class Submission(BaseModel):
    lesson_id: str
    code: str = Field(max_length=20000)
    output: str = Field(max_length=20000)
    inputs: list[str] = Field(default_factory=list, max_length=10)

    @field_validator('inputs')
    @classmethod
    def bounded_inputs(cls, values):
        if any(len(value) > 500 for value in values):
            raise ValueError('Keep each player reply under 500 characters')
        return values

@app.post('/api/attempts')
def attempt(data: Submission, request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        lesson = next((l for l in LESSONS if l['id'] == data.lesson_id), None)
        if not lesson:
            raise HTTPException(404, 'Unknown lesson')
        # Safe, bounded checks of taught syntax; learner code never executes here.
        result, feedback = assess(data.lesson_id, data.code, data.output, data.inputs)
        db.add(Attempt(user_id=u.id, lesson_id=data.lesson_id, code=data.code, output=data.output, passed=result == 'passed'))
        audit(db, u, 'practice_saved', data.lesson_id)
        db.commit()
        return {'passed': result == 'passed', 'result': result, 'feedback': feedback, 'assessment': 'browser_practice'}



@app.post('/api/check')
def check_preview(data: Submission):
    if not any(lesson['id'] == data.lesson_id for lesson in LESSONS):
        raise HTTPException(404, 'Unknown lesson')
    result, feedback = assess(data.lesson_id, data.code, data.output, data.inputs)
    return {'passed': result == 'passed', 'result': result, 'feedback': feedback, 'assessment': 'browser_practice'}

@app.get('/api/progress')
def progress(request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        attempts = db.scalars(select(Attempt).where(Attempt.user_id == u.id, Attempt.passed == True))
        # Legacy arithmetic exercises used the variables ID. They do not earn
        # the new character-creation badge, but their history remains intact.
        return list({a.lesson_id for a in attempts if a.lesson_id != 'variables' or check_story('variables', a.code, a.output, [])[0]})

from . import browser_checks, content, migrate, sessions
from . import awards
from . import admin
from . import profiles
from . import review
from . import insights
from . import self_review
from . import feedback as tester_feedback
from .awards import award_challenge
from .db import Attempt, Base, Event, Invitation, LearnerGoal, SelfReviewRecord, User, engine
from .lesson_checks import check_story, judge, rule_errors
from .limits import limit
from .recommend import DEFAULT_GOAL, GOALS, recommend
import hashlib
import json
import logging
import os
import secrets
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

PRODUCTION = os.getenv('ENVIRONMENT') == 'production'
SECRET = os.getenv('SESSION_SECRET', '')
if PRODUCTION and len(SECRET) < 32:
    raise RuntimeError('SESSION_SECRET must contain at least 32 characters')
ORIGIN = os.getenv('APP_ORIGIN', 'http://localhost:3000').rstrip('/')
API_ORIGIN = os.getenv('API_ORIGIN', ORIGIN).rstrip('/')
CATALOG, CONTENT = content.load()
# Check messages in the content must match the rules the checker uses (lesson-feedback.md section 6).
if errors := rule_errors(CONTENT):
    raise content.ContentError('Invalid course content:\n- ' + '\n- '.join(errors))
LESSONS = content.legacy_lessons(CATALOG, CONTENT)
UNIT_LESSONS = content.unit_lessons(CATALOG, CONTENT)
LESSON_ORDER = content.lesson_order(CATALOG)
CATALOG_VIEW = content.catalog_view(CATALOG, CONTENT)

def check_opening(code, output):
    return check_story('hello', code, output, [])

migrate.upgrade(engine)
logging.getLogger('uvicorn.error').info('Database schema is at migration %s', migrate.current(engine))
app = FastAPI(title='Python Academy')
# The cookie holds only a session ID; app/sessions.py decides when the session really ends.
app.add_middleware(SessionMiddleware, secret_key=SECRET or secrets.token_urlsafe(48), same_site='lax', https_only=PRODUCTION, max_age=sessions.ABSOLUTE)
oauth = OAuth()
oauth.register(name='google', client_id=os.getenv('GOOGLE_CLIENT_ID'), client_secret=os.getenv('GOOGLE_CLIENT_SECRET'), server_metadata_url='https://accounts.google.com/.well-known/openid-configuration', client_kwargs={'scope': 'openid email profile'})

admin.register(app)
tester_feedback.register(app)

@app.middleware('http')
async def security(request: Request, call_next):
    if request.method in {'POST', 'PUT', 'DELETE', 'PATCH'} and request.headers.get('origin') != ORIGIN:
        return JSONResponse({'detail': 'Untrusted origin'}, status_code=403)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Cache-Control'] = 'no-store'
    # The API only returns JSON and redirects, so nothing here needs to load or be framed (SEC-04).
    response.headers['Content-Security-Policy'] = "default-src 'none'; frame-ancestors 'none'"
    if PRODUCTION:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

def age_on(birthday: date, today: date | None = None) -> int:
    today = today or date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

def current(request: Request, db: Session, role: str | None = None):
    uid = sessions.user_id(request)
    user = db.get(User, uid) if uid is not None else None
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

@app.get('/auth/google', dependencies=[Depends(limit('signin'))])
async def login(request: Request):
    if not os.getenv('GOOGLE_CLIENT_ID') or not os.getenv('GOOGLE_CLIENT_SECRET'):
        raise HTTPException(503, 'Google sign-in is awaiting configuration')
    return await oauth.google.authorize_redirect(request, API_ORIGIN + '/auth/google/callback')

@app.get('/auth/google/callback', dependencies=[Depends(limit('signin_callback'))])
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
        sessions.start(db, request, user.id, admin=admin.admin_at_sign_in(info))
        audit(db, user, 'signed_in')
        db.commit()
    return RedirectResponse(ORIGIN)

@app.post('/api/logout')
def logout(request: Request):
    uid = sessions.user_id(request)
    sessions.end(request)
    if uid is not None:
        with Session(engine) as db:
            db.add(Event(user_id=uid, action='signed_out', detail=''))
            db.commit()
    return {'ok': True}

@app.get('/api/me')
def me(request: Request):
    with Session(engine) as db:
        u = current(request, db)
        return {'id': u.id, 'email': u.email, 'role': u.role, 'admin': admin.is_admin(request, u), 'tester': admin.is_tester(request, u)}

class Enrollment(BaseModel):
    birthday: date
    invitation: str = Field(default='', max_length=200)

@app.post('/api/enroll', dependencies=[Depends(limit('enroll'))])
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

@app.post('/api/invitations', dependencies=[Depends(limit('invitations'))])
def invite(data: InviteInput, request: Request):
    with Session(engine) as db:
        u = current(request, db, 'parent')
        token = secrets.token_urlsafe(32)
        db.add(Invitation(digest=hashlib.sha256(token.encode()).hexdigest(), parent_id=u.id, email=data.email.lower(), expires=(datetime.now(timezone.utc)+timedelta(days=7)).isoformat()))
        audit(db, u, 'invitation_created')
        db.commit()
        # SEC-06: after '#', so the token never reaches a server, a proxy or a request log.
        return {'url': ORIGIN + '/#invite=' + token, 'expires_in_days': 7}

@app.get('/api/family')
def family(request: Request):
    with Session(engine) as db:
        u = current(request, db, 'parent')
        return [{'id': s.id, 'email': s.email,
                 'attempts': [{'lesson_id': a.lesson_id, 'passed': a.passed} for a in db.scalars(select(Attempt).where(Attempt.user_id == s.id))],
                 'completed': awards.completed_lessons(db, s.id, CONTENT, LESSON_ORDER),
                 # Decision 2: parents see the learner's goal (never placement answers).
                 'goal': goal_label(db.get(LearnerGoal, s.id))}
                for s in db.scalars(select(User).where(User.parent_id == u.id))]

@app.get('/api/history')
def history(request: Request):
    with Session(engine) as db:
        u = current(request, db)
        return [{'action': e.action, 'created': e.created, 'detail': e.detail} for e in db.scalars(select(Event).where(Event.user_id == u.id).order_by(Event.id.desc()).limit(100))]

@app.get('/api/lessons')
def lessons():
    return LESSONS

@app.get('/api/units/{unit_id}/lessons')
def unit_lessons(unit_id: str):
    # The lesson page reads one unit at a time (UI-05). /api/lessons stays as it was for older pages.
    if unit_id not in UNIT_LESSONS:
        raise HTTPException(404, 'This unit has no lessons yet')
    return UNIT_LESSONS[unit_id]

@app.get('/api/catalog')
def catalog():
    return CATALOG_VIEW

@app.get('/api/goals')
def goals():
    return [{'id': g.id, 'label': g.label, 'description': g.description} for g in GOALS.values()]

def goal_label(row):
    return GOALS[row.goal].label if row and row.goal in GOALS else None

def goal_state(db, user_id):
    row = db.get(LearnerGoal, user_id)
    return {'goal': row.goal if row else None, 'chosen': bool(row and row.chosen), 'asked': row is not None}

class GoalChoice(BaseModel):
    # None means the learner skipped the goal card; they get the default goal.
    goal: str | None = Field(default=None, max_length=20)

@app.get('/api/goal')
def my_goal(request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        return goal_state(db, u.id)

@app.post('/api/goal', dependencies=[Depends(limit('goal'))])
def set_goal(data: GoalChoice, request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        if data.goal is not None and data.goal not in GOALS:
            raise HTTPException(422, 'Choose one of the listed goals')
        goal, chosen = (data.goal, True) if data.goal else (DEFAULT_GOAL, False)
        row = db.get(LearnerGoal, u.id)
        if row:
            row.goal, row.chosen = goal, chosen
        else:
            db.add(LearnerGoal(user_id=u.id, goal=goal, chosen=chosen))
        audit(db, u, 'goal_chosen' if chosen else 'goal_skipped', goal)
        db.commit()
        return goal_state(db, u.id)

class ProfileChoice(BaseModel):
    nickname: str = Field(default='', max_length=60)
    avatar: dict[str, str] = Field(default_factory=dict, max_length=10)


def profile_user(request, db):
    """Profiles are for enrolled students and parents; an account still being set up has none."""
    u = current(request, db)
    if u.role not in ('student', 'parent'):
        raise HTTPException(403, 'This action is unavailable for this account')
    return u


@app.get('/api/profile')
def my_profile(request: Request):
    with Session(engine) as db:
        return profiles.view(db, profile_user(request, db), CATALOG, CONTENT, LESSON_ORDER)


@app.put('/api/profile', dependencies=[Depends(limit('profile'))])
def save_profile(data: ProfileChoice, request: Request):
    with Session(engine) as db:
        u = profile_user(request, db)
        try:
            nickname, avatar = profiles.clean_nickname(data.nickname), profiles.clean_avatar(data.avatar)
        except ValueError as error:
            raise HTTPException(422, str(error))
        profiles.save(db, u, nickname, avatar)
        # No detail: the nickname is never copied into the account history.
        audit(db, u, 'profile_saved')
        db.commit()
        return profiles.view(db, u, CATALOG, CONTENT, LESSON_ORDER)


REVIEW_CARDS = review.load(Path(__file__).resolve().parent.parent / 'content' / 'review', CONTENT)


class ReviewAnswer(BaseModel):
    card_id: str = Field(max_length=160)
    choice: int | None = Field(default=None, ge=0, le=20)
    lines: list[str] | None = Field(default=None, max_length=30)


def today_utc():
    return datetime.now(timezone.utc).date()


@app.get('/api/review')
def review_session(request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        done = set(awards.completed_lessons(db, u.id, CONTENT, LESSON_ORDER))
        return review.session(db, u.id, REVIEW_CARDS, CATALOG, done, today_utc())


@app.post('/api/review/answer', dependencies=[Depends(limit('review'))])
def review_answer(data: ReviewAnswer, request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        card = REVIEW_CARDS.get(data.card_id)
        done = set(awards.completed_lessons(db, u.id, CONTENT, LESSON_ORDER))
        if card is None or card.lesson not in done:
            raise HTTPException(404, 'That review card is not open to you yet')
        if (card.kind == 'order') != (data.lines is not None) or (card.kind != 'order' and data.choice is None):
            raise HTTPException(422, 'Answer with a choice, or with the lines in order')
        result = review.answer(db, u.id, card, data.choice, data.lines, today_utc())
        db.commit()
        return result


class SelfReviewAnswer(BaseModel):
    done: bool = False
    evidence: str = Field(default='', max_length=self_review.MAX_CHARS)


class SelfReviewSubmission(BaseModel):
    lesson_id: str = Field(max_length=80)
    answers: dict[str, SelfReviewAnswer] = Field(default={}, max_length=8)


def self_reviewed(lesson_id):
    lesson = CONTENT.get(lesson_id)
    if lesson is None or lesson.task('challenge').self_review is None:
        raise HTTPException(404, 'That lesson has no self review')
    return lesson


def review_problems(lesson, data):
    return self_review.judge(lesson.task('challenge').self_review, {k: v.model_dump() for k, v in data.answers.items()})


@app.post('/api/self-review/preview', dependencies=[Depends(limit('self_review'))])
def self_review_preview(data: SelfReviewSubmission):
    """ENG-09 in a preview: the same notes on the writing, and nothing saved."""
    problems = review_problems(self_reviewed(data.lesson_id), data)
    return {'recorded': False, 'result': 'needs_work' if problems else 'ready', 'problems': problems, 'evidence': 'self_reported',
            'feedback': self_review.NEEDS_WORK if problems else 'Every part is ready to record. In a preview nothing is saved.'}


@app.post('/api/self-review', dependencies=[Depends(limit('self_review'))])
def self_review_submit(data: SelfReviewSubmission, request: Request):
    """ENG-09: keep a finished self review and award the lesson, labelled self-reported. A review with
    anything left to change is not kept: drafts stay on the page."""
    with Session(engine) as db:
        u = current(request, db, 'student')
        lesson = self_reviewed(data.lesson_id)
        if (problems := review_problems(lesson, data)):
            return {'recorded': False, 'result': 'needs_work', 'problems': problems, 'evidence': 'self_reported', 'feedback': self_review.NEEDS_WORK}
        challenge = lesson.task('challenge')
        written = {c.id: data.answers[c.id].evidence.strip() for c in challenge.self_review.criteria}
        db.add(SelfReviewRecord(user_id=u.id, lesson_id=lesson.id, task_id=challenge.id, task_version=challenge.version, answers=json.dumps(written)))
        award_challenge(db, u.id, lesson, None, source='self_reported')
        audit(db, u, 'self_review_saved', lesson.id)
        db.commit()
        return {'recorded': True, 'result': 'recorded', 'problems': {}, 'evidence': 'self_reported', 'feedback': self_review.RECORDED}


@app.get('/api/self-review/{lesson_id}')
def self_review_latest(lesson_id: str, request: Request):
    """The learner's own latest recorded review of a lesson, so a brief can be read back while they
    build. Only ever the signed-in learner's own writing."""
    with Session(engine) as db:
        u = current(request, db, 'student')
        self_reviewed(lesson_id)
        row = db.scalars(select(SelfReviewRecord).where(SelfReviewRecord.user_id == u.id, SelfReviewRecord.lesson_id == lesson_id)
                         .order_by(SelfReviewRecord.id.desc()).limit(1)).first()
        return {'answers': json.loads(row.answers), 'recorded': row.created} if row else {'answers': None, 'recorded': None}


@app.get('/api/recommendation')
def next_recommendation(request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        row = db.get(LearnerGoal, u.id)
        done = awards.completed_lessons(db, u.id, CONTENT, LESSON_ORDER)
        return recommend(row.goal if row else DEFAULT_GOAL, CATALOG, done).as_dict()

@app.get('/api/awards')
def my_awards(request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        return awards.summary(db, u.id, CONTENT, LESSON_ORDER)

class Submission(BaseModel):
    lesson_id: str
    code: str = Field(max_length=20000)
    output: str = Field(max_length=20000)
    inputs: list[str] = Field(default_factory=list, max_length=10)
    # Browser behaviour checks only: one report per check case, from public/check-runner.js.
    runs: list[browser_checks.CaseRun] | None = Field(default=None, max_length=10)

    @field_validator('inputs')
    @classmethod
    def bounded_inputs(cls, values):
        if any(len(value) > 500 for value in values):
            raise ValueError('Keep each player reply under 500 characters')
        return values

def browser_checked(lesson_id):
    lesson = CONTENT.get(lesson_id)
    return lesson if lesson and browser_checks.applies(lesson) else None

@app.get('/api/checks/{lesson_id}')
def check_plan(lesson_id: str):
    # The cases the browser runs. Hidden cases have no expected output here (docs/plan/browser-checks.md).
    lesson = browser_checked(lesson_id)
    if not lesson:
        raise HTTPException(404, 'This lesson has no browser checks')
    return browser_checks.plan(lesson)

@app.post('/api/attempts', dependencies=[Depends(limit('attempts'))])
def attempt(data: Submission, request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        if lesson := browser_checked(data.lesson_id):
            # The browser ran the code; this only compares what it reported.
            outcome = browser_checks.judge(lesson, data.code, data.runs)
            result, feedback = outcome['result'], outcome['feedback']
        else:
            outcome = None
            lesson = next((l for l in LESSONS if l['id'] == data.lesson_id), None)
            if not lesson:
                raise HTTPException(404, 'Unknown lesson')
            # Safe, bounded checks of taught syntax; learner code never executes here.
            result, feedback, rule = judge(data.lesson_id, data.code, data.output, data.inputs)
        saved = Attempt(user_id=u.id, lesson_id=data.lesson_id, code=data.code, output=data.output, passed=result == 'passed', result=result)
        db.add(saved)
        db.flush()
        if result == 'passed':
            award_challenge(db, u.id, CONTENT[data.lesson_id], saved.id)
        audit(db, u, 'practice_saved', data.lesson_id)
        db.commit()
        return outcome or {'passed': result == 'passed', 'result': result, 'feedback': feedback, 'rule': rule, 'assessment': 'browser_practice'}

@app.post('/api/check', dependencies=[Depends(limit('check'))])
def check_preview(data: Submission):
    if lesson := browser_checked(data.lesson_id):
        return browser_checks.judge(lesson, data.code, data.runs)
    if not any(lesson['id'] == data.lesson_id for lesson in LESSONS):
        raise HTTPException(404, 'Unknown lesson')
    result, feedback, rule = judge(data.lesson_id, data.code, data.output, data.inputs)
    # rule: the named check rule that decided the result, so the page can offer the hint tagged for it.
    return {'passed': result == 'passed', 'result': result, 'feedback': feedback, 'rule': rule, 'assessment': 'browser_practice'}

class InsightRequest(BaseModel):
    lesson_id: str = Field(max_length=80)
    code: str = Field(max_length=20000)


@app.post('/api/insights', dependencies=[Depends(limit('insights'))])
def likely_causes(data: InsightRequest):
    """Likely causes for a program that did not pass: read from its syntax tree, never run, never stored."""
    if data.lesson_id not in CONTENT:
        raise HTTPException(404, 'Unknown lesson')
    return {'insights': insights.find(data.code)}

@app.get('/api/progress')
def progress(request: Request):
    with Session(engine) as db:
        u = current(request, db, 'student')
        # The XP ledger is the record of completed lessons. Migrations 0003/0004 backfilled it
        # from older attempts, excluding legacy arithmetic under the variables ID.
        return awards.completed_lessons(db, u.id, CONTENT, LESSON_ORDER)

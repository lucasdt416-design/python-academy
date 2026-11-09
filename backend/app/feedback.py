"""Anonymous tester feedback: storage, limits and retention (backlog FB-02; docs/plan/feedback-security.md).

Sign-in is required only to stop bots. A stored item holds no user ID, name, email, IP address or
session ID, and only the date it was sent, not the time, so it cannot be matched to a person by
the rate-limit counters (app/limits.py keeps feedback's per-tester counters in memory, holding only
keyed hashes, even though other counters are in the database since ENG-11) or by
the account history (sending feedback adds no event). Log lines say "accepted" or why an item was
rejected, never who sent it, the message or the code.

Retention (decision 18): items are deleted 50 days after the day they were sent, and at most 90
are kept. When the inbox is full, the oldest resolved item (fixed or wont_fix) is deleted to make
room; if nothing is resolved, the new item is rejected. Unresolved items are never deleted to make
room.
"""
import logging
import re
import threading
import time
from datetime import date, datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from . import admin, sessions
from .db import Feedback, User, engine
from .limits import limit

log = logging.getLogger('uvicorn.error')

KEEP_DAYS = 50
MAX_ITEMS = 90
MESSAGE_LIMIT = 2000
CODE_LIMIT = 20000
STATUSES = ('new', 'triaged', 'in_progress', 'fixed', 'wont_fix')
RESOLVED = ('fixed', 'wont_fix')
FULL = 'The feedback inbox is full right now, so this was not saved. Please try again in a few days.'

clock = time.time  # replaced by a fake clock in tests


def today() -> date:
    return datetime.fromtimestamp(clock(), timezone.utc).date()


# Control characters other than new line and tab, and the Unicode direction overrides that can make
# text display differently from what it says (feedback-security.md section 2).
UNSAFE = re.compile(r'[\x00-\x08\x0b-\x1f\x7f-\x9f‪-‮⁦-⁩]')
EMAIL = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
PHONE = re.compile(r'(?<![\w+])\+?\(?\d[\d ().-]{6,}\d(?!\w)')


def clean(text: str) -> str:
    return UNSAFE.sub('', text)


def redact(text: str) -> str:
    """Best effort (section 5): email addresses and phone numbers. Names cannot be detected."""
    text = EMAIL.sub('[email removed]', text)
    return PHONE.sub(lambda m: '[number removed]' if 9 <= sum(c.isdigit() for c in m.group()) <= 15 else m.group(), text)


def require_tester(request: Request) -> None:
    """The guard on sending feedback: 401 when signed out, 403 for anyone but a tester or the admin."""
    uid = sessions.user_id(request)
    if uid is None:
        raise HTTPException(401, 'Sign in to continue')
    with Session(engine) as db:
        if not admin.is_tester(request, db.get(User, uid)):
            raise HTTPException(403, 'This action is unavailable for this account')


class FeedbackIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    category: Literal['confusing', 'bug', 'wrong_grading', 'idea', 'other']
    message: str = Field(min_length=1, max_length=MESSAGE_LIMIT)
    # Optional, so feedback can be compared between groups; never derived from a birthdate.
    audience: Literal['high_school', 'university', 'other'] | None = None
    # Code is stored only when the sender ticked "Include my code" (decision 17).
    include_code: bool = False
    code: str | None = Field(default=None, max_length=CODE_LIMIT)


def purge(db: Session) -> int:
    """Delete items sent KEEP_DAYS or more days ago. Returns how many were deleted."""
    return db.execute(delete(Feedback).where(Feedback.created_on <= today() - timedelta(days=KEEP_DAYS))).rowcount


def make_room(db: Session) -> bool:
    """Free one place if the inbox is full, by deleting the oldest resolved items. False if it cannot."""
    extra = db.scalar(select(func.count()).select_from(Feedback)) - MAX_ITEMS + 1
    if extra <= 0:
        return True
    oldest = db.scalars(select(Feedback.id).where(Feedback.status.in_(RESOLVED)).order_by(Feedback.created_on, Feedback.id).limit(extra)).all()
    if len(oldest) < extra:
        return False
    db.execute(delete(Feedback).where(Feedback.id.in_(oldest)))
    return True


# One submission at a time, so two at once cannot both take the last place (one API instance).
WRITE = threading.Lock()


def submit(data: FeedbackIn):
    message = redact(clean(data.message)).strip()
    if not message:
        raise HTTPException(422, 'Write a message before sending.')
    code = clean(data.code) if data.include_code and data.code and data.code.strip() else None
    with WRITE, Session(engine) as db:
        purge(db)
        if not make_room(db):
            db.commit()
            log.info('Feedback rejected: inbox full')
            raise HTTPException(409, FULL)
        db.add(Feedback(created_on=today(), category=data.category, audience=data.audience, message=message, code=code))
        db.commit()
    log.info('Feedback accepted')
    return {'saved': True}


PURGE_EVERY = 3600
_last_purge = None


def purge_if_due():
    """Run retention at most once an hour, so items go on time even when nobody sends feedback."""
    global _last_purge
    now = clock()
    if _last_purge is not None and now - _last_purge < PURGE_EVERY:
        return
    _last_purge = now
    try:
        with WRITE, Session(engine) as db:
            if purge(db):
                log.info('Feedback retention: expired items deleted')
            db.commit()
    except Exception as error:
        # Retention must never take the app down; it runs again within the hour.
        log.error('Feedback retention failed: %s', type(error).__name__)


def register(app: FastAPI):
    """Add the feedback route on the app itself (not an included router, which the route-listing
    safety tests could not see), behind the tester guard and its own rate limit."""
    app.add_api_route('/api/feedback', submit, methods=['POST'], dependencies=[Depends(require_tester), Depends(limit('feedback'))])

    @app.middleware('http')
    async def retention(request: Request, call_next):
        await run_in_threadpool(purge_if_due)
        return await call_next(request)

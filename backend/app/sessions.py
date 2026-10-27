"""Server-side sessions (backlog SEC-03).

The signed session cookie holds only a random session ID. The `sessions` table holds who it
belongs to and when it ends, so deleting the row ends the session at once: after logout, a
copied cookie stops working on the next request.

A session ends at whichever comes first:
- ABSOLUTE: 7 days after sign-in, however often it is used, so a stolen cookie cannot be kept
  alive forever by using it.
- IDLE: 24 hours without a request. Before SEC-03 the signed cookie was renewed on every
  response and expired after 24 hours unused, so learners are not signed out more often than
  before, except once a week.

Admin sessions (backlog FB-01) are shorter: ADMIN_ABSOLUTE 8 hours and ADMIN_IDLE 1 hour, because
an admin can change other accounts. Whether a session is an admin session is decided once, at
sign-in, and stored on the row; the cookie never says.

Nothing here logs: not the session ID, the cookie, the user ID or the email.
"""
import hashlib
import secrets
import time

from fastapi import Request
from sqlalchemy import delete, or_, select, update
from sqlalchemy.orm import Session

from .db import User, UserSession, engine

DAY = 86400
ABSOLUTE = 7 * DAY
IDLE = DAY
ADMIN_ABSOLUTE = 8 * 3600
ADMIN_IDLE = 3600
# last_seen is written at most this often, so most requests do not write to the database.
# The idle timeout is therefore exact to within these 5 minutes.
TOUCH_EVERY = 300
COOKIE_KEY = 'sid'
clock = time.time


def digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def start(db: Session, request: Request, user_id: int, admin: bool = False):
    """Begin a new session for user_id: a fresh ID, and anything else in the cookie dropped."""
    now = int(clock())
    # Expired rows are only ever removed here and when they are next used, which keeps the
    # table small without a scheduled job.
    db.execute(delete(UserSession).where(or_(UserSession.expires <= now, UserSession.last_seen <= now - IDLE)))
    # Signing in again from the same browser ends that browser's previous session.
    previous = request.session.get(COOKIE_KEY)
    if isinstance(previous, str):
        db.execute(delete(UserSession).where(UserSession.id == digest(previous)))
    token = secrets.token_urlsafe(32)
    db.add(UserSession(id=digest(token), user_id=user_id, created=now, last_seen=now,
                       expires=now + (ADMIN_ABSOLUTE if admin else ABSOLUTE), admin=admin))
    request.session.clear()
    request.session[COOKIE_KEY] = token


def end(request: Request):
    """Delete this browser's session row, if any, and empty the cookie."""
    token = request.session.get(COOKIE_KEY)
    if isinstance(token, str):
        with Session(engine) as db:
            db.execute(delete(UserSession).where(UserSession.id == digest(token)))
            db.commit()
    request.session.clear()


def user_id(request: Request) -> int | None:
    """The signed-in user's ID, or None. Looked up once per request, then reused."""
    return _cached(request)[0]


def admin_session(request: Request) -> bool:
    """Whether this browser's live session was started as an admin session."""
    return _cached(request)[1]


def _cached(request: Request) -> tuple[int | None, bool]:
    if not hasattr(request.state, 'session_user'):
        request.state.session_user = _lookup(request)
    return request.state.session_user


def _lookup(request: Request) -> tuple[int | None, bool]:
    # Cookies from before SEC-03 held the user ID itself. Drop it, so the browser stops sending
    # it and a rollback to the old code would not accept it again.
    request.session.pop('uid', None)
    token = request.session.get(COOKIE_KEY)
    if not isinstance(token, str):
        return None, False
    key, now = digest(token), int(clock())
    with Session(engine) as db:
        row = db.get(UserSession, key)
        alive = row is not None and now < row.expires and now - row.last_seen < (ADMIN_IDLE if row.admin else IDLE)
        if alive and db.scalar(select(User.id).where(User.id == row.user_id)) is None:
            alive = False  # the account was deleted
        if not alive:
            if row is not None:
                db.execute(delete(UserSession).where(UserSession.id == key))
                db.commit()
            # Also clears the browser's cookie on this response.
            request.session.clear()
            return None, False
        if now - row.last_seen >= TOUCH_EVERY:
            db.execute(update(UserSession).where(UserSession.id == key).values(last_seen=now))
            db.commit()
        return row.user_id, row.admin

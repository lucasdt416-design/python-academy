"""Admin and tester roles (backlog FB-01; docs/plan/feedback-security.md section 1).

Who is an admin is decided only by the ADMIN_EMAILS environment variable on the API service: a
comma-separated list of Google emails. It is read on the server and never stored, logged or sent
in a response. A session is an admin session only if, at sign-in, Google said the email was
verified and that email was in the list. Every request re-checks the list, so removing an email
ends that person's admin access at once.

Testers are student accounts with the tester flag, which only an admin can set or clear. An admin
account also counts as a tester.
"""
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import sessions
from .db import Event, User, engine
from .limits import limit


def admin_emails() -> frozenset[str]:
    """The configured admin emails, lower-cased, with spaces and empty entries ignored."""
    return frozenset(part.strip().casefold() for part in os.getenv('ADMIN_EMAILS', '').split(',') if part.strip())


def admin_at_sign_in(userinfo: dict) -> bool:
    """Whether a Google sign-in may start an admin session. An email match alone is not enough."""
    email = userinfo.get('email')
    return userinfo.get('email_verified') is True and isinstance(email, str) and email.strip().casefold() in admin_emails()


def is_admin(request: Request, user: User | None) -> bool:
    return bool(user and sessions.admin_session(request) and user.email.casefold() in admin_emails())


def is_tester(request: Request, user: User | None) -> bool:
    return bool(user and (is_admin(request, user) or (user.role == 'student' and user.tester)))


def require_admin(request: Request) -> int:
    """The guard on every /api/admin route: 401 when signed out, 403 for anyone but an admin."""
    uid = sessions.user_id(request)
    if uid is None:
        raise HTTPException(401, 'Sign in to continue')
    with Session(engine) as db:
        if not is_admin(request, db.get(User, uid)):
            raise HTTPException(403, 'This action is unavailable for this account')
    return uid


def students():
    with Session(engine) as db:
        return [{'id': s.id, 'email': s.email, 'tester': s.tester}
                for s in db.scalars(select(User).where(User.role == 'student').order_by(User.id))]


class TesterChange(BaseModel):
    user_id: int
    tester: bool


def set_tester(data: TesterChange, admin_id: int = Depends(require_admin)):
    with Session(engine) as db:
        student = db.get(User, data.user_id)
        if not student:
            raise HTTPException(404, 'No such account')
        if student.role != 'student':
            raise HTTPException(422, 'Only student accounts can be testers')
        student.tester = data.tester
        # Recorded in the admin's own history, by user ID only, never by email.
        db.add(Event(user_id=admin_id, action='tester_set' if data.tester else 'tester_cleared', detail=f'user {student.id}'))
        db.commit()
        return {'id': student.id, 'tester': student.tester}


def register(app: FastAPI):
    """Add the admin routes, each behind require_admin.

    They are added to the app itself rather than through an included APIRouter: this FastAPI
    version keeps an included router as one opaque entry in app.routes, which the route-listing
    safety tests (sessions, rate limits) would not see. A test checks every /api/admin route has
    the guard.
    """
    guard = [Depends(require_admin)]
    app.add_api_route('/api/admin/students', students, methods=['GET'], dependencies=guard)
    app.add_api_route('/api/admin/testers', set_tester, methods=['POST'], dependencies=guard + [Depends(limit('admin'))])

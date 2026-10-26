"""Database engine and tables. The schema itself is owned by Alembic migrations (backend/migrations)."""
import os
from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String, Text, UniqueConstraint, create_engine, false
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def database_url(url=None):
    url = url or os.getenv('DATABASE_URL', 'sqlite:///./academy.db')
    for prefix in ('postgres://', 'postgresql://'):
        if url.startswith(prefix):
            return 'postgresql+psycopg://' + url[len(prefix):]
    return url


DB_URL = database_url()
engine = create_engine(DB_URL, connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite') else {})


def now():
    return datetime.now(timezone.utc).isoformat()


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
    # Testers see tester features (backlog FB-01). Only an admin sets it, and only on students.
    tester: Mapped[bool] = mapped_column(default=False, server_default=false())


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
    created: Mapped[str] = mapped_column(String(40), default=now)


class Attempt(Base):
    __tablename__ = 'attempts'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    lesson_id: Mapped[str] = mapped_column(String(80))
    code: Mapped[str] = mapped_column(Text)
    output: Mapped[str] = mapped_column(Text)
    passed: Mapped[bool] = mapped_column(default=False)
    # One of lesson_checks.RESULTS; null for attempts saved before result states existed.
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)


class XpAward(Base):
    """Append-only XP ledger. Total XP is the sum of rows; the unique key stops retries inflating it."""
    __tablename__ = 'xp_awards'
    __table_args__ = (UniqueConstraint('user_id', 'task_id', 'task_version', name='uq_xp_awards_user_task_version'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    task_id: Mapped[str] = mapped_column(String(160))
    task_version: Mapped[int] = mapped_column(Integer)
    xp: Mapped[int] = mapped_column(Integer)
    attempt_id: Mapped[int | None] = mapped_column(ForeignKey('attempts.id'), nullable=True)
    # practice: earned through the app; backfill: rebuilt from attempts saved before the ledger existed.
    source: Mapped[str] = mapped_column(String(20))
    created: Mapped[str] = mapped_column(String(40), default=now)


class BadgeAward(Base):
    """One row per badge version a learner earned. Corrections are recorded, never deleted."""
    __tablename__ = 'badge_awards'
    __table_args__ = (UniqueConstraint('user_id', 'badge_id', 'badge_version', name='uq_badge_awards_user_badge_version'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    badge_id: Mapped[str] = mapped_column(String(160))
    badge_version: Mapped[int] = mapped_column(Integer)
    attempt_id: Mapped[int | None] = mapped_column(ForeignKey('attempts.id'), nullable=True)
    source: Mapped[str] = mapped_column(String(20))
    created: Mapped[str] = mapped_column(String(40), default=now)
    corrected: Mapped[str | None] = mapped_column(String(40), nullable=True)
    correction_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


def insert_once(db, model, **values):
    """Insert a row unless it would break a unique constraint. Returns True if inserted.

    Uses INSERT ... ON CONFLICT DO NOTHING so two simultaneous requests cannot both award.
    RETURNING tells us whether a row was added; rowcount is unreliable here on PostgreSQL.
    """
    insert = postgresql_insert if db.get_bind().dialect.name == 'postgresql' else sqlite_insert
    statement = insert(model.__table__).values(**values).on_conflict_do_nothing().returning(model.__table__.c.id)
    return db.execute(statement).first() is not None


class LearnerGoal(Base):
    """A student's current goal (plan section 2). Changes are also recorded as account events."""
    __tablename__ = 'learner_goals'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    goal: Mapped[str] = mapped_column(String(20))
    # False when the learner skipped the goal card and got the default.
    chosen: Mapped[bool] = mapped_column(default=True)
    updated: Mapped[str] = mapped_column(String(40), default=now, onupdate=now)


class UserSession(Base):
    """One signed-in browser (backlog SEC-03). The cookie holds only a random session ID.

    The row is keyed by a SHA-256 digest of that ID, so a copy of this table cannot be used as a
    cookie. Times are whole Unix seconds (UTC) so expiry is a plain comparison on every database.
    """
    __tablename__ = 'sessions'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    created: Mapped[int] = mapped_column(BigInteger)
    last_seen: Mapped[int] = mapped_column(BigInteger)
    expires: Mapped[int] = mapped_column(BigInteger)
    # Started by a verified Google email that was in ADMIN_EMAILS at sign-in; shorter lifetimes apply.
    admin: Mapped[bool] = mapped_column(default=False, server_default=false())

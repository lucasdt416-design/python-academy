"""XP and badge awards (docs/plan/course-catalog.md section 6). Idempotent: retries never add more."""
from sqlalchemy import func, select

from .db import BadgeAward, XpAward, insert_once

# Decision 6: 100 XP per lesson challenge, once.
CHALLENGE_XP = 100


def award_challenge(db, user_id, lesson, attempt_id, source='practice'):
    """Award a passed lesson challenge's XP and badge, unless any version was awarded before.

    Call inside the transaction that saves the attempt, so both are kept or neither.
    """
    challenge = lesson.task('challenge')
    if not db.scalar(select(XpAward.id).where(XpAward.user_id == user_id, XpAward.task_id == challenge.id).limit(1)):
        insert_once(db, XpAward, user_id=user_id, task_id=challenge.id, task_version=challenge.version,
                    xp=CHALLENGE_XP, attempt_id=attempt_id, source=source)
    badge = lesson.badge
    if badge and not db.scalar(select(BadgeAward.id).where(BadgeAward.user_id == user_id, BadgeAward.badge_id == badge.id).limit(1)):
        insert_once(db, BadgeAward, user_id=user_id, badge_id=badge.id, badge_version=badge.version,
                    attempt_id=attempt_id, source=source)


def total_xp(db, user_id):
    return db.scalar(select(func.coalesce(func.sum(XpAward.xp), 0)).where(XpAward.user_id == user_id))


def badges(db, user_id):
    """Badge IDs currently held, excluding corrected awards."""
    return set(db.scalars(select(BadgeAward.badge_id).where(BadgeAward.user_id == user_id, BadgeAward.corrected.is_(None))))

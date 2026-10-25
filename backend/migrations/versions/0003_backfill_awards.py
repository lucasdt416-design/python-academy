"""Backfill XP and badges from attempts saved before the award ledgers existed.

Awards match what /api/progress already shows: one award per learner per lesson with a
passing attempt, except legacy arithmetic attempts under the variables ID, which never
earned Character creator. Safe to re-run: existing awards are left alone.

Revision ID: 0003
Revises: 0002
"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

# Frozen at the time of this migration so later content edits cannot change it:
# lesson ID -> (challenge task ID, task version, badge ID, badge version).
AWARDS = {
    'hello': ('hello.challenge', 1, 'py.badge.story-spark', 1),
    'variables': ('variables.challenge', 1, 'py.badge.character-creator', 1),
    'input': ('input.challenge', 1, 'py.badge.conversation-starter', 1),
    'choices': ('choices.challenge', 1, 'py.badge.path-finder', 1),
    'adventure': ('adventure.challenge', 1, 'py.badge.adventure-maker', 1),
}
CHALLENGE_XP = 100

attempts = sa.table('attempts', sa.column('id'), sa.column('user_id'), sa.column('lesson_id'),
                    sa.column('code'), sa.column('output'), sa.column('passed'))
xp_awards = sa.table('xp_awards', sa.column('user_id'), sa.column('task_id'), sa.column('task_version'),
                     sa.column('xp'), sa.column('attempt_id'), sa.column('source'), sa.column('created'))
badge_awards = sa.table('badge_awards', sa.column('user_id'), sa.column('badge_id'), sa.column('badge_version'),
                        sa.column('attempt_id'), sa.column('source'), sa.column('created'))


def upgrade():
    # The same bounded checker /api/progress uses to exclude legacy arithmetic attempts.
    # It interprets code without executing it.
    from app.lesson_checks import check_story

    bind = op.get_bind()
    insert = postgresql_insert if bind.dialect.name == 'postgresql' else sqlite_insert
    created = datetime.now(timezone.utc).isoformat()
    rows = bind.execute(sa.select(attempts).where(attempts.c.passed == sa.true()).order_by(attempts.c.id)).all()
    done = set()
    for row in rows:
        if row.lesson_id not in AWARDS or (row.user_id, row.lesson_id) in done:
            continue
        if row.lesson_id == 'variables' and not check_story('variables', row.code, row.output, [])[0]:
            continue
        done.add((row.user_id, row.lesson_id))
        task_id, task_version, badge_id, badge_version = AWARDS[row.lesson_id]
        bind.execute(insert(xp_awards).values(user_id=row.user_id, task_id=task_id, task_version=task_version, xp=CHALLENGE_XP,
                                              attempt_id=row.id, source='backfill', created=created).on_conflict_do_nothing())
        bind.execute(insert(badge_awards).values(user_id=row.user_id, badge_id=badge_id, badge_version=badge_version,
                                                 attempt_id=row.id, source='backfill', created=created).on_conflict_do_nothing())


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.delete(xp_awards).where(xp_awards.c.source == 'backfill'))
    bind.execute(sa.delete(badge_awards).where(badge_awards.c.source == 'backfill'))

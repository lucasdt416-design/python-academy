"""Rate-limit counters in the database (ENG-11).

Only adds a new table, so the previous app version keeps working during a deploy: it keeps counting
in memory. A row holds a keyed hash, a window start and a count: no user ID, address or request
content. Downgrading deletes the table, and the counters start again from zero.

Numbered 0010, not 0009: owner decision 29 keeps 0009 for the sign-ups switch (S04), which will then
revise this one. Alembic orders migrations by down_revision, not by number.

Revision ID: 0010
Revises: 0008
"""
from alembic import op
import sqlalchemy as sa

revision = '0010'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'rate_limits',
        sa.Column('key', sa.String(32), primary_key=True),
        sa.Column('window_start', sa.BigInteger(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
    )


def downgrade():
    op.drop_table('rate_limits')

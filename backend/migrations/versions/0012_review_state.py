"""Spaced review: one row per learner and review card, with its box and next due day.

Only adds a table, so the previous app version keeps working during a deploy. Downgrading deletes the
table and every learner's review schedule; XP, badges and progress are untouched.

Revision ID: 0012
Revises: 0011
"""
from alembic import op
import sqlalchemy as sa

revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'review_state',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('card_id', sa.String(length=160), nullable=False),
        sa.Column('box', sa.Integer(), nullable=False),
        sa.Column('due', sa.String(length=10), nullable=False),
        sa.Column('seen', sa.Integer(), nullable=False),
        sa.Column('correct', sa.Integer(), nullable=False),
        sa.Column('updated', sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('user_id', 'card_id'),
    )


def downgrade():
    op.drop_table('review_state')

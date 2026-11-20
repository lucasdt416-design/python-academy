"""Profiles: an avatar built from fixed options, and an optional nickname, per account.

Only adds a table, so the previous app version keeps working during a deploy. Downgrading deletes the
table, and with it every profile's choices; XP, badges and progress are untouched.

Revision ID: 0011
Revises: 0010
"""
from alembic import op
import sqlalchemy as sa

revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'profiles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('nickname', sa.String(length=24), nullable=False),
        sa.Column('avatar', sa.String(length=300), nullable=False),
        sa.Column('updated', sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('user_id'),
    )


def downgrade():
    op.drop_table('profiles')

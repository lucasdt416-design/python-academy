"""Baseline: the four tables the app created with create_all before migrations existed.

Databases that already have these tables are stamped with this revision instead of
running it (app/migrate.py), so production data is never recreated.

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('birthday', sa.Date(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subject'),
    )
    op.create_table(
        'invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('digest', sa.String(length=64), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('expires', sa.String(length=40), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('digest'),
    )
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=80), nullable=False),
        sa.Column('detail', sa.Text(), nullable=False),
        sa.Column('created', sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.String(length=80), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('output', sa.Text(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    raise NotImplementedError('Refusing to drop the original tables; restore from a backup instead.')

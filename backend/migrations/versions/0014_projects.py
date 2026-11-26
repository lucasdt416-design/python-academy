"""E1: the project workspace, one row per learner project with its files as text.

Only adds a table, so the previous app version keeps working during a deploy. Downgrading deletes the
table and every learner's projects; XP, badges and progress are untouched.

Revision ID: 0014
Revises: 0013
"""
from alembic import op
import sqlalchemy as sa

revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=60), nullable=False),
        sa.Column('starter', sa.String(length=20), nullable=False),
        sa.Column('files', sa.Text(), nullable=False),
        sa.Column('keep_written', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.Column('created', sa.String(length=40), nullable=False),
        sa.Column('updated', sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])


def downgrade():
    op.drop_index('ix_projects_user_id', table_name='projects')
    op.drop_table('projects')

"""ENG-09: finished self reviews, one row each, in the learner's own words.

Only adds a table, so the previous app version keeps working during a deploy. Downgrading deletes the
table and every learner's written reviews; XP, badges and progress are untouched.

Revision ID: 0013
Revises: 0012
"""
from alembic import op
import sqlalchemy as sa

revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'self_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.String(length=80), nullable=False),
        sa.Column('task_id', sa.String(length=160), nullable=False),
        sa.Column('task_version', sa.Integer(), nullable=False),
        sa.Column('answers', sa.Text(), nullable=False),
        sa.Column('created', sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_self_reviews_user_id', 'self_reviews', ['user_id'])


def downgrade():
    op.drop_index('ix_self_reviews_user_id', table_name='self_reviews')
    op.drop_table('self_reviews')

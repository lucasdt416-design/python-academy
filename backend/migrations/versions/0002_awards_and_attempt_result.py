"""Add XP and badge award ledgers, and store each attempt's result state.

Only adds tables and a nullable column, so the previous app version keeps working
while a new deploy starts.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('attempts') as batch:
        batch.add_column(sa.Column('result', sa.String(length=20), nullable=True))
    op.create_table(
        'xp_awards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=160), nullable=False),
        sa.Column('task_version', sa.Integer(), nullable=False),
        sa.Column('xp', sa.Integer(), nullable=False),
        sa.Column('attempt_id', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('created', sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(['attempt_id'], ['attempts.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'task_id', 'task_version', name='uq_xp_awards_user_task_version'),
    )
    op.create_index('ix_xp_awards_user_id', 'xp_awards', ['user_id'])
    op.create_table(
        'badge_awards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('badge_id', sa.String(length=160), nullable=False),
        sa.Column('badge_version', sa.Integer(), nullable=False),
        sa.Column('attempt_id', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('created', sa.String(length=40), nullable=False),
        sa.Column('corrected', sa.String(length=40), nullable=True),
        sa.Column('correction_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['attempt_id'], ['attempts.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'badge_id', 'badge_version', name='uq_badge_awards_user_badge_version'),
    )
    op.create_index('ix_badge_awards_user_id', 'badge_awards', ['user_id'])


def downgrade():
    op.drop_index('ix_badge_awards_user_id', table_name='badge_awards')
    op.drop_table('badge_awards')
    op.drop_index('ix_xp_awards_user_id', table_name='xp_awards')
    op.drop_table('xp_awards')
    with op.batch_alter_table('attempts') as batch:
        batch.drop_column('result')

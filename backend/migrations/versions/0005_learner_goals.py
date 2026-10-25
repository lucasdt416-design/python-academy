"""Store each student's learning goal.

Only adds a table, so the previous app version keeps working during a deploy.

Revision ID: 0005
Revises: 0004
"""
from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'learner_goals',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('goal', sa.String(length=20), nullable=False),
        sa.Column('chosen', sa.Boolean(), nullable=False),
        sa.Column('updated', sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('user_id'),
    )


def downgrade():
    op.drop_table('learner_goals')

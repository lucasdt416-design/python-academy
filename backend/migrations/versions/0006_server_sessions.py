"""Store sign-in sessions on the server so logout ends them (backlog SEC-03).

Only adds a table, so the previous app version keeps working during a deploy. Cookies made
before this migration hold a user ID instead of a session ID; the new code ignores them, so
everyone signs in again once.

Revision ID: 0006
Revises: 0005
"""
from alembic import op
import sqlalchemy as sa

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created', sa.BigInteger(), nullable=False),
        sa.Column('last_seen', sa.BigInteger(), nullable=False),
        sa.Column('expires', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])


def downgrade():
    op.drop_index('ix_sessions_user_id', table_name='sessions')
    op.drop_table('sessions')

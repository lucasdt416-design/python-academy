"""Tester flag on accounts, and admin sessions (backlog FB-01).

Only adds two columns with a default of false, so the previous app version keeps working
during a deploy and every existing account and session stays as it was.

Revision ID: 0007
Revises: 0006
"""
from alembic import op
import sqlalchemy as sa

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('tester', sa.Boolean(), nullable=False, server_default=sa.false()))
    with op.batch_alter_table('sessions') as batch:
        batch.add_column(sa.Column('admin', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('sessions') as batch:
        batch.drop_column('admin')
    with op.batch_alter_table('users') as batch:
        batch.drop_column('tester')

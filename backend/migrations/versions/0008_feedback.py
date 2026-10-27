"""Anonymous tester feedback (backlog FB-02).

Only adds a new table, so the previous app version keeps working during a deploy. The table has
no user ID, email, IP address or session ID, and stores the date an item was sent, not the time.
Downgrading deletes the table and every feedback item in it.

Revision ID: 0008
Revises: 0007
"""
from alembic import op
import sqlalchemy as sa

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('created_on', sa.Date(), nullable=False),
        sa.Column('category', sa.String(20), nullable=False),
        sa.Column('audience', sa.String(20), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('code', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='new'),
    )


def downgrade():
    op.drop_table('feedback')

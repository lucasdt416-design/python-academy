"""Alembic environment. Uses the app's connection when called from app/migrate.py."""
from alembic import context
from sqlalchemy import create_engine

from app.db import Base, database_url

config = context.config


def run(connection):
    # render_as_batch lets column changes work on SQLite, which cannot ALTER most columns.
    context.configure(connection=connection, target_metadata=Base.metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise SystemExit('Offline (SQL script) mode is not supported; run migrations against a database.')
connection = config.attributes.get('connection')
if connection is not None:
    run(connection)
else:
    with create_engine(database_url()).begin() as connection:
        run(connection)

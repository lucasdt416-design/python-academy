"""Bring the database schema up to date when the app starts.

Production tables were first made by create_all, before migrations existed. A database
with exactly those tables and no migration history is stamped as revision 0001 and then
upgraded; a database whose tables differ is left untouched and startup stops.
"""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

BACKEND = Path(__file__).resolve().parent.parent
BASELINE = '0001'
BASELINE_SCHEMA = {
    'users': {'id', 'subject', 'email', 'role', 'birthday', 'parent_id'},
    'invitations': {'id', 'digest', 'parent_id', 'email', 'expires', 'used'},
    'events': {'id', 'user_id', 'action', 'detail', 'created'},
    'attempts': {'id', 'user_id', 'lesson_id', 'code', 'output', 'passed'},
}
# Arbitrary constant: one deploy at a time may migrate a PostgreSQL database.
LOCK_ID = 7_301_440


class SchemaMismatch(RuntimeError):
    pass


def config(connection):
    cfg = Config(str(BACKEND / 'alembic.ini'))
    cfg.attributes['connection'] = connection
    return cfg


def upgrade(engine, revision='head'):
    """Stamp a pre-migration database if needed, then upgrade, all in one transaction."""
    with engine.begin() as connection:
        if connection.dialect.name == 'postgresql':
            connection.exec_driver_sql(f'SELECT pg_advisory_xact_lock({LOCK_ID})')
        cfg = config(connection)
        inspector = inspect(connection)
        tables = set(inspector.get_table_names())
        if 'alembic_version' not in tables and tables & BASELINE_SCHEMA.keys():
            found = {t: {c['name'] for c in inspector.get_columns(t)} for t in BASELINE_SCHEMA if t in tables}
            if found != BASELINE_SCHEMA:
                raise SchemaMismatch(f'Existing tables do not match migration baseline {BASELINE}; nothing was changed. Found: {found}')
            command.stamp(cfg, BASELINE)
        command.upgrade(cfg, revision)


def downgrade(engine, revision):
    with engine.begin() as connection:
        command.downgrade(config(connection), revision)


def current(engine):
    with engine.connect() as connection:
        return connection.exec_driver_sql('SELECT version_num FROM alembic_version').scalar()

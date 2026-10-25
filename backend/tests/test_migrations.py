"""Migrations on SQLite always, and on PostgreSQL when TEST_POSTGRES_URL points at a server."""
import os
import uuid

import pytest
import sqlalchemy as sa
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy.orm import Session

from app import migrate
from app.db import Base, User, XpAward, database_url, insert_once

# The tables exactly as create_all made them before migrations existed (models at commit a293798).
LEGACY = sa.MetaData()
sa.Table('users', LEGACY,
         sa.Column('id', sa.Integer, primary_key=True),
         sa.Column('subject', sa.String(255), nullable=False, unique=True),
         sa.Column('email', sa.String(320), nullable=False),
         sa.Column('role', sa.String(20), nullable=False),
         sa.Column('birthday', sa.Date, nullable=True),
         sa.Column('parent_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True))
sa.Table('invitations', LEGACY,
         sa.Column('id', sa.Integer, primary_key=True),
         sa.Column('digest', sa.String(64), nullable=False, unique=True),
         sa.Column('parent_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
         sa.Column('email', sa.String(320), nullable=False),
         sa.Column('expires', sa.String(40), nullable=False),
         sa.Column('used', sa.Boolean, nullable=False))
sa.Table('events', LEGACY,
         sa.Column('id', sa.Integer, primary_key=True),
         sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
         sa.Column('action', sa.String(80), nullable=False),
         sa.Column('detail', sa.Text, nullable=False),
         sa.Column('created', sa.String(40), nullable=False))
sa.Table('attempts', LEGACY,
         sa.Column('id', sa.Integer, primary_key=True),
         sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
         sa.Column('lesson_id', sa.String(80), nullable=False),
         sa.Column('code', sa.Text, nullable=False),
         sa.Column('output', sa.Text, nullable=False),
         sa.Column('passed', sa.Boolean, nullable=False))

HELLO = ('print("A forest.")\nprint("A dragon!")', 'A forest.\nA dragon!\n')
VARIABLES = ('hero="Kai"\ntool="rope"\nprint(f"{hero} carries {tool}")', 'Kai carries rope\n')
ARITHMETIC = ('stars=7\nprint(stars*3)', '21\n')  # legacy exercise under the variables ID
HEAD = '0004'


@pytest.fixture(params=['sqlite', 'postgresql'])
def engine(request, tmp_path):
    if request.param == 'sqlite':
        engine = sa.create_engine(f'sqlite:///{tmp_path / "migrations.db"}')
        yield engine
        engine.dispose()
        return
    server = os.getenv('TEST_POSTGRES_URL')
    if not server:
        pytest.skip('Set TEST_POSTGRES_URL to run migration tests on PostgreSQL')
    admin = sa.create_engine(database_url(server), isolation_level='AUTOCOMMIT')
    name = 'migration_test_' + uuid.uuid4().hex[:12]
    with admin.connect() as conn:
        conn.exec_driver_sql(f'CREATE DATABASE {name}')
    engine = sa.create_engine(sa.make_url(database_url(server)).set(database=name))
    yield engine
    engine.dispose()
    with admin.connect() as conn:
        conn.exec_driver_sql(f'DROP DATABASE {name}')
    admin.dispose()


def table_rows(engine, names):
    with engine.connect() as conn:
        return {n: [tuple(r) for r in conn.execute(sa.select(LEGACY.tables[n]).order_by(LEGACY.tables[n].c.id))] for n in names}


def seed_legacy(engine):
    LEGACY.create_all(engine)
    t = LEGACY.tables
    with engine.begin() as conn:
        conn.execute(t['users'].insert(), [
            dict(id=1, subject='g-parent', email='parent@example.com', role='parent', birthday=None, parent_id=None),
            dict(id=2, subject='g-ava', email='ava@example.com', role='student', birthday=None, parent_id=1),
            dict(id=3, subject='g-ben', email='ben@example.com', role='student', birthday=None, parent_id=1),
            dict(id=4, subject='g-new', email='new@example.com', role='pending', birthday=None, parent_id=None),
        ])
        conn.execute(t['invitations'].insert(), [dict(id=1, digest='d' * 64, parent_id=1, email='ben@example.com', expires='2026-10-30T00:00:00+00:00', used=True)])
        conn.execute(t['events'].insert(), [dict(id=1, user_id=2, action='signed_in', detail='', created='2026-10-20T10:00:00+00:00')])
        conn.execute(t['attempts'].insert(), [
            dict(id=1, user_id=2, lesson_id='hello', code=HELLO[0], output=HELLO[1], passed=True),
            dict(id=2, user_id=2, lesson_id='hello', code=HELLO[0], output=HELLO[1], passed=True),
            dict(id=3, user_id=2, lesson_id='hello', code='print("x")', output='x\n', passed=False),
            dict(id=4, user_id=2, lesson_id='variables', code=ARITHMETIC[0], output=ARITHMETIC[1], passed=True),
            dict(id=5, user_id=2, lesson_id='choices', code='', output='', passed=False),
            dict(id=6, user_id=2, lesson_id='loops', code='for i in range(3): print(i)', output='0\n1\n2\n', passed=True),
            dict(id=7, user_id=3, lesson_id='variables', code=VARIABLES[0], output=VARIABLES[1], passed=True),
            dict(id=8, user_id=3, lesson_id='variables', code=ARITHMETIC[0], output=ARITHMETIC[1], passed=True),
            dict(id=9, user_id=3, lesson_id='adventure', code='', output='', passed=True),
        ])
        if conn.dialect.name == 'postgresql':
            for name in ('users', 'invitations', 'events', 'attempts'):
                conn.exec_driver_sql(f"SELECT setval(pg_get_serial_sequence('{name}', 'id'), (SELECT max(id) FROM {name}))")


def awards(engine):
    with engine.connect() as conn:
        xp = sorted(tuple(r) for r in conn.exec_driver_sql('SELECT user_id, task_id, task_version, xp, attempt_id, source FROM xp_awards'))
        badges = sorted(tuple(r) for r in conn.exec_driver_sql('SELECT user_id, badge_id, badge_version, attempt_id, source FROM badge_awards'))
    return xp, badges


EXPECTED_XP = [
    (2, 'hello.challenge', 1, 100, 1, 'backfill'),
    (3, 'adventure.challenge', 1, 100, 9, 'backfill'),
    (3, 'variables.challenge', 1, 100, 7, 'backfill'),
]
EXPECTED_BADGES = [
    (2, 'py.badge.story-spark', 1, 1, 'backfill'),
    (3, 'py.badge.adventure-maker', 1, 9, 'backfill'),
    (3, 'py.badge.character-creator', 1, 7, 'backfill'),
]


def test_fresh_database_built_by_migrations_matches_the_models(engine):
    migrate.upgrade(engine)
    assert migrate.current(engine) == HEAD
    with engine.connect() as conn:
        assert compare_metadata(MigrationContext.configure(conn), Base.metadata) == []


def test_baseline_matches_the_tables_create_all_made(engine):
    migrate.upgrade(engine, '0001')
    with engine.connect() as conn:
        assert compare_metadata(MigrationContext.configure(conn), LEGACY) == []


def test_existing_database_is_adopted_without_changing_learner_data(engine):
    seed_legacy(engine)
    before = table_rows(engine, ['users', 'invitations', 'events', 'attempts'])
    migrate.upgrade(engine)
    assert migrate.current(engine) == HEAD
    assert table_rows(engine, ['users', 'invitations', 'events', 'attempts']) == before
    with engine.connect() as conn:
        assert conn.exec_driver_sql('SELECT count(*) FROM attempts WHERE result IS NOT NULL').scalar() == 0


def test_backfill_matches_progress_rules_and_is_idempotent(engine):
    seed_legacy(engine)
    migrate.upgrade(engine)
    # Ava: hello once (two passes, one award); legacy arithmetic and the retired loops lesson earn nothing.
    # Ben: real variables solution counts even though a later arithmetic attempt exists; adventure counts.
    assert awards(engine) == (EXPECTED_XP, EXPECTED_BADGES)
    migrate.upgrade(engine)
    assert awards(engine) == (EXPECTED_XP, EXPECTED_BADGES)


def test_backfill_rerun_awards_passes_saved_by_pre_ledger_code_during_deploy(engine):
    seed_legacy(engine)
    migrate.upgrade(engine, '0003')
    # The previous app version, which wrote no awards, saves a pass while the new one starts.
    with engine.begin() as conn:
        conn.execute(LEGACY.tables['attempts'].insert(), [dict(id=10, user_id=2, lesson_id='input', code='n=input()\nprint(n)', output='Nova\n', passed=True)])
    assert (2, 'input.challenge', 1, 100, 10, 'backfill') not in awards(engine)[0]
    migrate.upgrade(engine)
    xp, badges = awards(engine)
    assert xp == sorted(EXPECTED_XP + [(2, 'input.challenge', 1, 100, 10, 'backfill')])
    assert badges == sorted(EXPECTED_BADGES + [(2, 'py.badge.conversation-starter', 1, 10, 'backfill')])


def test_unexpected_existing_tables_are_left_untouched(engine):
    with engine.begin() as conn:
        conn.exec_driver_sql('CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(320))')
    with pytest.raises(migrate.SchemaMismatch):
        migrate.upgrade(engine)
    assert set(sa.inspect(engine).get_table_names()) == {'users'}


def test_downgrade_then_upgrade_keeps_learner_data_and_rebuilds_awards(engine):
    seed_legacy(engine)
    migrate.upgrade(engine)
    before = table_rows(engine, ['users', 'invitations', 'events', 'attempts'])
    migrate.downgrade(engine, '0001')
    assert {'xp_awards', 'badge_awards'}.isdisjoint(sa.inspect(engine).get_table_names())
    migrate.upgrade(engine)
    assert table_rows(engine, ['users', 'invitations', 'events', 'attempts']) == before
    assert awards(engine) == (EXPECTED_XP, EXPECTED_BADGES)
    with pytest.raises(NotImplementedError):
        migrate.downgrade(engine, 'base')


def test_award_insert_is_ignored_when_it_would_duplicate(engine):
    migrate.upgrade(engine)
    with Session(engine) as db:
        db.add(User(subject='s', email='s@example.com', role='student'))
        db.flush()
        values = dict(user_id=1, task_id='hello.challenge', task_version=1, xp=100, source='practice')
        assert insert_once(db, XpAward, **values) is True
        assert insert_once(db, XpAward, **values) is False
        db.commit()
        assert db.query(XpAward).count() == 1

"""The Practice Arena (app/review.py, /api/review): spaced review cards.

Every card's answer is proved by running its code in Python 3.12 here, the way the cards were made.
"""
import itertools
import json
from datetime import date, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

import test_unit2_lessons as helpers
from app import review
from app.db import ReviewState, User
from app.main import CATALOG, CONTENT, REVIEW_CARDS, engine
from case_runner import run_program
from lesson_suite import attempt
from test_profiles import sign_in
from test_unit2_lessons import client  # noqa: F401
import test_unit4_lessons as u4

CARDS = list(REVIEW_CARDS.values())


def test_there_are_cards_for_every_lesson_and_four_kinds():
    assert {c.lesson for c in CARDS} == set(CONTENT)
    assert {c.kind for c in CARDS} == {'predict', 'trace', 'order', 'bug'}
    assert len(CARDS) >= 99


@pytest.mark.parametrize('card', [c for c in CARDS if c.kind == 'order'], ids=lambda c: c.id)
def test_an_order_card_prints_what_it_shows_and_no_swap_of_two_lines_does(card):
    want = card.expected + '\n'
    assert run_program('\n'.join(card.lines), card.inputs) == (want, None)
    for i, j in itertools.combinations(range(len(card.lines)), 2):
        swapped = card.lines[:]
        swapped[i], swapped[j] = swapped[j], swapped[i]
        assert run_program('\n'.join(swapped), card.inputs) != (want, None), (i, j)


@pytest.mark.parametrize('card', [c for c in CARDS if c.kind == 'trace'], ids=lambda c: c.id)
def test_a_trace_card_answer_is_what_the_name_really_holds(card):
    output, error = run_program(card.code + f'\nprint("@@", {card.probe})', [])
    assert error is None
    assert output.rstrip('\n').split('@@ ')[-1] == card.options[card.answer]


@pytest.mark.parametrize('card', [c for c in CARDS if c.kind == 'bug'], ids=lambda c: c.id)
def test_a_bug_card_points_at_the_only_line_that_changes_and_the_fix_behaves_differently(card):
    assert run_program(card.code, ['5']) != run_program(card.fixed, ['5'])
    assert run_program(card.fixed, ['5'])[1] is None
    line = int(card.options[card.answer].split(':')[0].removeprefix('Line '))
    assert card.code.split('\n')[line - 1] != card.fixed.split('\n')[line - 1]


def test_a_predict_card_is_the_lessons_own_checked_predict_card():
    for card in (c for c in CARDS if c.kind == 'predict'):
        p = CONTENT[card.lesson].task('predict')
        assert (card.prompt, card.options, card.answer, card.why, card.code) == (p.question, p.options, p.answer, p.why, CONTENT[card.lesson].task('example').code)


def test_bad_cards_are_refused(tmp_path):
    good = REVIEW_CARDS['hello.review.predict'].model_dump()
    for broken, message in [({**good, 'answer': 9}, 'an answer among them'), ({**good, 'lesson': 'nope'}, 'not for a real lesson'),
                            ({**good, 'options': ['a', 'a']}, 'different options')]:
        (tmp_path / 'py.json').write_text(json.dumps({'cards': [broken]}))
        with pytest.raises(ValueError, match=message):
            review.load(tmp_path, CONTENT)


def test_a_card_shows_no_answer_before_it_is_answered():
    import random
    for card in CARDS:
        shown = review.public(card, random.Random(1))
        assert set(shown) <= {'id', 'lesson', 'kind', 'prompt', 'code', 'options', 'lines', 'expected', 'inputs'}
        if card.kind == 'order':
            assert sorted(shown['lines']) == sorted(card.lines) and shown['lines'] != card.lines


# The API

def test_signed_out_and_parents_have_no_arena(client):
    assert client.get('/api/review').status_code == 401
    sign_in(client, 'parent')
    assert client.get('/api/review').status_code == 403


def test_nothing_is_offered_before_a_lesson_is_finished(client):
    sign_in(client)
    r = client.get('/api/review').json()
    assert (r['cards'], r['unlocked'], r['creature'], r['tamed']) == ([], False, None, [])
    assert client.post('/api/review/answer', json={'card_id': 'hello.review.predict', 'choice': 0}, headers=helpers.HEADERS).status_code == 404


def finish(client, *lesson_ids):
    specs = {'py.lists': u4.LISTS, 'py.indexing': u4.INDEXING, 'py.iterate-lists': u4.ITERATE, 'py.dicts': u4.DICTS, 'py.sets': u4.SETS}
    for lesson_id in lesson_ids:
        assert attempt(client, lesson_id, specs[lesson_id].reference)['result'] == 'passed'


def test_a_session_offers_only_finished_lessons_cards_mixed_across_lessons(client):
    sign_in(client)
    finish(client, 'py.lists', 'py.indexing', 'py.dicts')
    r = client.get('/api/review').json()
    assert r['unlocked'] and len(r['cards']) == 5
    assert {c['lesson'] for c in r['cards']} <= {'py.lists', 'py.indexing', 'py.dicts'}
    assert len({c['lesson'] for c in r['cards']}) == 3
    assert r['creature']['name'] == 'Packrat'
    assert 'answer' not in json.dumps(r['cards']) and 'why' not in json.dumps(r['cards'])


def test_answers_move_cards_through_the_boxes_and_never_touch_xp(client):
    uid = sign_in(client)
    finish(client, 'py.lists')
    xp = client.get('/api/awards').json()['xp']
    card = REVIEW_CARDS['py.lists.review.predict']
    wrong = (card.answer + 1) % len(card.options)
    r = client.post('/api/review/answer', json={'card_id': card.id, 'choice': wrong}, headers=helpers.HEADERS).json()
    assert r == {'correct': False, 'why': card.why, 'back_in_days': 1, 'answer': card.answer}
    for days in (1, 3, 7, 30, 30):
        r = client.post('/api/review/answer', json={'card_id': card.id, 'choice': card.answer}, headers=helpers.HEADERS).json()
        assert r['correct'] is True and r['back_in_days'] == {1: 3, 3: 7, 7: 30, 30: 30}.get(days, days)
    with Session(engine) as db:
        state = db.get(ReviewState, (uid, card.id))
        assert (state.box, state.seen, state.correct) == (4, 6, 5)
    assert client.get('/api/awards').json()['xp'] == xp


def test_an_order_card_is_answered_with_its_lines(client):
    sign_in(client)
    finish(client, 'py.lists')
    order = [c for c in CARDS if c.kind == 'order' and c.lesson == 'py.lists']
    if not order:
        pytest.skip('py.lists has no order card')
    card = order[0]
    r = client.post('/api/review/answer', json={'card_id': card.id, 'lines': list(reversed(card.lines))}, headers=helpers.HEADERS).json()
    assert r['correct'] is False and r['lines'] == card.lines
    assert client.post('/api/review/answer', json={'card_id': card.id, 'lines': card.lines}, headers=helpers.HEADERS).json()['correct'] is True
    assert client.post('/api/review/answer', json={'card_id': card.id, 'choice': 0}, headers=helpers.HEADERS).status_code == 422


def test_due_cards_come_first_and_practice_ahead_only_when_nothing_is_due():
    from app.db import Base
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    today = date(2026, 11, 20)
    lesson_cards = [c.id for c in CARDS if c.lesson == 'py.lists']
    with Session(engine) as db:
        db.add(User(id=1, subject='s', email='s@example.com', role='student'))
        db.add(ReviewState(user_id=1, card_id=lesson_cards[0], box=2, due='2026-11-19', seen=2, correct=2))
        for card_id in lesson_cards[1:]:
            db.add(ReviewState(user_id=1, card_id=card_id, box=3, due='2026-12-01', seen=3, correct=3))
        db.commit()
        s = review.session(db, 1, REVIEW_CARDS, CATALOG, {'py.lists'}, today)
        assert [c['id'] for c in s['cards']] == [lesson_cards[0]] and s['due'] == 1 and s['ahead'] is False
        db.get(ReviewState, (1, lesson_cards[0])).due = '2026-12-05'
        db.commit()
        s = review.session(db, 1, REVIEW_CARDS, CATALOG, {'py.lists'}, today)
        assert s['ahead'] is True and len(s['cards']) == len(lesson_cards) and s['due'] == 0


def test_a_creature_is_tamed_after_five_right_answers_in_its_unit(client):
    sign_in(client)
    finish(client, 'py.lists', 'py.indexing', 'py.dicts')
    unit4 = [c for c in CARDS if c.lesson in ('py.lists', 'py.indexing', 'py.dicts') and c.kind != 'order'][:5]
    for card in unit4[:4]:
        client.post('/api/review/answer', json={'card_id': card.id, 'choice': card.answer}, headers=helpers.HEADERS)
    assert client.get('/api/review').json()['tamed'] == []
    client.post('/api/review/answer', json={'card_id': unit4[4].id, 'choice': unit4[4].answer}, headers=helpers.HEADERS)
    assert client.get('/api/review').json()['tamed'] == ['py.u04']

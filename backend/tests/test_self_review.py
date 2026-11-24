"""ENG-09: self-reviewed challenges (app/self_review.py, /api/self-review).

The writing is checked so a review cannot be clicked through; the work itself is not, so every record
says self-reported: the XP row's source, the response, and the page.
"""
import json

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

import test_unit2_lessons as helpers
from app import content, self_review
from app.db import SelfReviewRecord, User, XpAward
from app.main import CONTENT, engine
from test_profiles import sign_in
from test_unit2_lessons import client  # noqa: F401

LESSONS = ['py.when-not-oop', 'py.final-brief']
GOOD = {
    'py.when-not-oop': {
        'data-only': 'The settings in my quiz program were one record read at the start, so a plain dict was enough there.',
        'class-earns': 'The heroes in my battle each kept health and took hits, so health and take_hit belonged in one class.',
        'plain-function': 'Working out a price with tax needs only the price, so I tested it with one assert and no object at all.',
    },
    'py.final-brief': {
        'choice': 'Lockpick, because I finished unit nine and want something I can actually finish this month.',
        'user': 'My younger cousin, who likes guessing games on long car rides and wants quick rounds.',
        'must': 'Show the word as underscores, take one letter at a time, explain bad guesses, stop after six misses, offer another round.',
        'not-yet': 'Hints that cost a try, and a two player mode.',
        'milestones': 'First the word prints as underscores, then one guess updates it, then the whole round ends with a win or a loss.',
    },
}


def answers(lesson_id, **change):
    out = {k: {'done': True, 'evidence': v} for k, v in GOOD[lesson_id].items()}
    for k, v in change.items():
        out[k] = v
    return out


def review(lesson_id):
    return CONTENT[lesson_id].task('challenge').self_review


@pytest.mark.parametrize('lesson_id', LESSONS)
def test_the_lessons_are_self_reviewed_and_released(lesson_id):
    challenge = CONTENT[lesson_id].task('challenge')
    assert challenge.validator.id == content.SELF_REVIEW and challenge.check is None
    assert self_review.judge(challenge.self_review, answers(lesson_id)) == {}


def test_a_review_that_cannot_be_recorded_says_why_for_each_part():
    r = review('py.final-brief')
    got = self_review.judge(r, answers('py.final-brief',
        choice={'done': False, 'evidence': GOOD['py.final-brief']['choice']},
        user={'done': True, 'evidence': 'my cousin'},
        must={'done': True, 'evidence': 'I listed what it must do. List three to five things it must do. I listed what it must do.'},
        milestones={'done': True, 'evidence': 'blue blue blue blue blue blue green blue blue blue blue blue blue blue'}))
    assert got['choice'] == 'Tick this when you have done it.'
    assert got['user'].startswith('Say a little more, in your own words: at least 8 words (2 so far)')
    assert got['must'].startswith('That mostly repeats the question')
    assert got['milestones'] == 'That repeats itself. Say what you actually did.'
    assert 'not-yet' not in got


def test_personal_details_and_blocked_words_are_refused_in_a_review():
    r = review('py.final-brief')
    found = self_review.judge(r, answers('py.final-brief', user={'done': True, 'evidence': 'My cousin Sam, email him at sam.lee@example.com when the game is ready to try'}))
    assert found == {'user': 'Please leave out personal details: no email addresses, phone numbers, links or addresses.'}


def test_bad_content_is_refused():
    catalog, lessons = content.load()
    good = lessons['py.final-brief'].model_dump()
    for broken, message in [(lambda c: c.update(self_review=None), 'needs a self review exactly when'),
                            (lambda c: c['self_review']['criteria'].append(dict(c['self_review']['criteria'][0])), 'two review criteria with the same ID')]:
        lesson = json.loads(json.dumps(good))
        broken(lesson['tasks'][4])
        errors = content.validate(catalog, {**lessons, 'py.final-brief': content.Lesson(**lesson)})
        assert any(message in e for e in errors), errors


# The API

def test_preview_gives_the_same_notes_and_saves_nothing(client):
    r = client.post('/api/self-review/preview', json={'lesson_id': 'py.final-brief', 'answers': answers('py.final-brief', user={'done': True, 'evidence': 'x'})}, headers=helpers.HEADERS).json()
    assert (r['recorded'], r['result'], r['evidence'], list(r['problems'])) == (False, 'needs_work', 'self_reported', ['user'])
    r = client.post('/api/self-review/preview', json={'lesson_id': 'py.final-brief', 'answers': answers('py.final-brief')}, headers=helpers.HEADERS).json()
    assert (r['recorded'], r['result'], r['problems']) == (False, 'ready', {})
    with Session(engine) as db:
        assert db.scalars(select(SelfReviewRecord)).all() == []


def test_only_students_record_and_only_self_reviewed_lessons_take_a_review(client):
    body = {'lesson_id': 'py.final-brief', 'answers': answers('py.final-brief')}
    assert client.post('/api/self-review', json=body, headers=helpers.HEADERS).status_code == 401
    sign_in(client, 'parent')
    assert client.post('/api/self-review', json=body, headers=helpers.HEADERS).status_code == 403
    assert client.post('/api/self-review/preview', json={**body, 'lesson_id': 'py.lists'}, headers=helpers.HEADERS).status_code == 404
    assert client.post('/api/self-review/preview', json={**body, 'answers': {f'a{i}': {} for i in range(9)}}, headers=helpers.HEADERS).status_code == 422
    assert client.post('/api/self-review/preview', json={**body, 'answers': {'choice': {'done': True, 'evidence': 'x' * 2001}}}, headers=helpers.HEADERS).status_code == 422


def test_a_finished_review_is_kept_labelled_self_reported_and_awarded_once(client):
    uid = sign_in(client)
    unfinished = client.post('/api/self-review', json={'lesson_id': 'py.final-brief', 'answers': answers('py.final-brief', user={'done': True, 'evidence': 'x'})}, headers=helpers.HEADERS).json()
    assert unfinished['recorded'] is False and client.get('/api/awards').json()['xp'] == 0
    r = client.post('/api/self-review', json={'lesson_id': 'py.final-brief', 'answers': answers('py.final-brief')}, headers=helpers.HEADERS).json()
    assert (r['recorded'], r['result'], r['evidence']) == (True, 'recorded', 'self_reported')
    assert 'self-reported' in r['feedback']
    awards = client.get('/api/awards').json()
    assert awards['xp'] == 100 and 'py.final-brief' in awards['completed'] and awards['badges'] == [{'id': 'py.badge.project-planner', 'title': 'Project planner'}]
    client.post('/api/self-review', json={'lesson_id': 'py.final-brief', 'answers': answers('py.final-brief')}, headers=helpers.HEADERS)
    assert client.get('/api/awards').json()['xp'] == 100
    with Session(engine) as db:
        assert [x.source for x in db.scalars(select(XpAward).where(XpAward.user_id == uid))] == ['self_reported']
        kept = db.scalars(select(SelfReviewRecord).where(SelfReviewRecord.user_id == uid)).all()
        assert len(kept) == 2 and json.loads(kept[0].answers) == GOOD['py.final-brief']



def test_a_recorded_review_can_be_read_back_by_its_learner_only(client):
    """The lesson says the brief is kept so it can be read back while you build: this is that."""
    assert client.get('/api/self-review/py.final-brief').status_code == 401
    uid = sign_in(client)
    assert client.get('/api/self-review/py.final-brief').json() == {'answers': None, 'recorded': None}
    assert client.get('/api/self-review/py.lists').status_code == 404
    client.post('/api/self-review', json={'lesson_id': 'py.final-brief', 'answers': answers('py.final-brief')}, headers=helpers.HEADERS)
    later = answers('py.final-brief', user={'done': True, 'evidence': 'My friends at the coding club, who want a short game between lessons.'})
    client.post('/api/self-review', json={'lesson_id': 'py.final-brief', 'answers': later}, headers=helpers.HEADERS)
    got = client.get('/api/self-review/py.final-brief').json()
    assert got['answers'] == {k: v['evidence'] for k, v in later.items()} and got['recorded']
    with Session(engine) as db:  # the same reviews, now someone else's: this learner no longer sees them
        other = User(subject='other', email='other@example.com', role='student')
        db.add(other)
        db.flush()
        for row in db.scalars(select(SelfReviewRecord).where(SelfReviewRecord.user_id == uid)):
            row.user_id = other.id
        db.commit()
    assert client.get('/api/self-review/py.final-brief').json()['answers'] is None

# The answers frontend/tests/self-review.spec.ts mocks: real requests and the real API's replies.
RECORDED_FILE = __import__('pathlib').Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/self-review-api.json'
SHORT = {'choice': {'done': True, 'evidence': GOOD['py.final-brief']['choice']}, 'user': {'done': True, 'evidence': 'my cousin'}}


def build_recordings():
    import os
    from fastapi.testclient import TestClient
    from app.db import Base
    from app.main import app
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    client = TestClient(app)
    full = answers('py.final-brief')
    calls = [('/api/self-review/preview', {'lesson_id': 'py.final-brief', 'answers': SHORT}),
             ('/api/self-review/preview', {'lesson_id': 'py.final-brief', 'answers': full})]
    recorded = {'good': GOOD['py.final-brief'], 'short': SHORT, 'calls': [{'path': p, 'request': b, 'response': client.post(p, json=b, headers=helpers.HEADERS).json()} for p, b in calls]}
    sign_in(client)
    before = client.get('/api/self-review/py.final-brief').json()
    body = {'lesson_id': 'py.final-brief', 'answers': full}
    recorded['calls'].append({'path': '/api/self-review', 'request': body, 'response': client.post('/api/self-review', json=body, headers=helpers.HEADERS).json()})
    after = client.get('/api/self-review/py.final-brief').json()
    after['recorded'] = after['recorded'] and '2026-11-23T10:00:00+00:00'  # when it was saved varies; the rest is as sent
    recorded['reads'] = {'before': before, 'after': after}
    if os.environ.get('WRITE_SELF_REVIEW_RECORDINGS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    return recorded


def test_the_recorded_self_reviews_are_the_real_api():
    recorded = build_recordings()
    assert json.loads(RECORDED_FILE.read_text()) == recorded
    assert [c['response']['result'] for c in recorded['calls']] == ['needs_work', 'ready', 'recorded']

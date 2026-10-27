"""ASSESS-07: unit 1 checks say only what they verified, and no hint adds up to an answer.

See docs/plan/lesson-feedback.md appendix A and section 8.
"""
import os
import tempfile
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + tempfile.mktemp(suffix='.db'))
os.environ.setdefault('SESSION_SECRET', 'test-secret-that-is-at-least-thirty-two-characters')
import ast
import base64
import itertools
import json
import secrets

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import content, sessions
from app.awards import CHALLENGE_XP
from app.db import BadgeAward, User, UserSession, XpAward
from app.lesson_checks import Story, UnsupportedError, PracticeError, assess
from app.main import Base, app, engine

client = TestClient(app)
HEADERS = {'origin': 'http://localhost:3000'}
CATALOG, LESSONS = content.load()
UNIT_1 = ['hello', 'variables', 'input', 'choices', 'adventure']


def run(lesson_id, code, replies=()):
    """Check code the way the app does: the output is what the program really prints."""
    try:
        output = Story(list(replies)).run(ast.parse(code).body).output
    except (SyntaxError, PracticeError, UnsupportedError):
        output = ''
    return assess(lesson_id, code, output, list(replies))


def two_lines(first, second):
    return f'print({json.dumps(first)})\nprint({json.dumps(second)})'


# Appendix A: the cases that were investigated, and what happens now

@pytest.mark.parametrize('code,result,message', [
    # Still passes, deliberately: two different messages in words. Meaning is the learner's call.
    (two_lines('hi', 'woah'), 'passed', 'Python printed your two different messages in order.'),
    (two_lines('hi', 'hi'), 'needs_work', 'Both lines say the same thing.'),
    (two_lines('.', '.'), 'needs_work', 'Use words for each message'),
    ('print(1)\nprint(2)', 'needs_work', 'Use words for each message'),
    (two_lines('You arrive at a moonlit castle.', 'A tiny dragon opens the gate.'), 'needs_work', "That's the example from the card."),
    (two_lines('You land on Mars.', 'A robot offers you tea.'), 'needs_work', "That's the example from the card."),
    ('print("hi")', 'needs_work', 'Write two print statements'),
], ids=['hi-woah', 'same-line-twice', 'punctuation', 'numbers', 'worked-example', 'old-hint-3', 'one-line'])
def test_appendix_a_cases(code, result, message):
    got, feedback = run('hello', code)
    assert (got, feedback.startswith(message)) == (result, True), feedback


# Every answer that passed before ASSESS-07 and should not now

@pytest.mark.parametrize('first,second', [
    ('hi', 'hi'), ('Hi', 'hi!'), ('A  cave', 'a cave.'),  # the same words, differently typed
    ('.', '.'), ('!!!', '???'), ('42', 'Hello'), ('🐉', 'A dragon'),  # a line with no letters
    ('YOU ARRIVE AT A MOONLIT CASTLE', 'a tiny dragon opens the gate'),  # the example, re-cased
    ('You land on Mars', 'A robot offers you tea'),  # hint 3 as published before
    ('You wake up in ___.', 'A door creaks open.'),  # the new hint's pattern, unfilled
])
def test_old_passing_answers_now_need_work(first, second):
    assert run('hello', two_lines(first, second))[0] == 'needs_work'


@pytest.mark.parametrize('first,second', [
    ('Mars.', 'Boom!'),  # short and creative is fine: no word minimum (decision 5)
    ('You wake up in a library.', 'The books start whispering.'),  # the hint's pattern, filled in
    ('You arrive at a moonlit castle.', 'A goose steals your hat.'),  # one example line kept, one changed
    ('Café Lune, at midnight', 'Ça alors, the cat speaks!'),
    ('Room 101', 'The lights go out'),
])
def test_own_stories_still_pass(first, second):
    assert run('hello', two_lines(first, second))[0] == 'passed'


# Success messages say only what was checked, and ask the learner to judge the rest

PASSING = {
    'hello': (two_lines('A forest.', 'A dragon!'), []),
    'variables': ('hero = "Kai"\ntool = "rope"\nprint(hero + " carries a " + tool)', []),
    'input': ('player = input("Name? ")\nprint("Hello, " + player)', ['Kai']),
    'choices': ('path = input("Which way? ")\nif path == "left":\n    print("A river.")\nelse:\n    print("A tower.")', ['left']),
    'adventure': ('print("A storm rolls in.")\nhero = input("Name? ")\nprint("Hi, " + hero)\npath = input("Way? ")\nif path == "left":\n    print("You sail away.")\nelse:\n    print("You find shelter.")', ['Kai', 'left']),
}
OLD_CLAIMS = ['Your scene has a setting and a surprise', 'Your hero and tool both come from variables',
              'Your greeting responds to different names', 'Both paths work', 'Your adventure welcomes different players']


@pytest.mark.parametrize('lesson_id', UNIT_1)
def test_success_messages_claim_only_what_was_checked_and_ask_a_question(lesson_id):
    result, feedback = run(lesson_id, *PASSING[lesson_id])
    assert result == 'passed', feedback
    assert not any(claim in feedback for claim in OLD_CLAIMS)
    assert '?' in feedback, 'includes a self-check question for the learner'


# No hint, or combination of hints, is a complete passing answer

def statements(hint):
    """Every print(...) call and `name = input(...)` assignment written out in a hint."""
    found = []
    for start in [i for i in range(len(hint)) if hint.startswith('print(', i)] + [m for m in _assignments(hint)]:
        depth, quote = 0, None
        for end in range(start, len(hint)):
            ch = hint[end]
            if quote:
                quote = None if ch == quote else quote
            elif ch in '"\'':
                quote = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    found.append(hint[start:end + 1])
                    break
    return found


def _assignments(hint):
    import re
    return [m.start() for m in re.finditer(r'\b[a-z_]+ = input\(', hint)]


def candidates(starter, hints):
    """Programs a learner could build from the starter and the hints alone, with nothing of their own."""
    pieces = [s for hint in hints for s in statements(hint)]
    whole = [hint[min(i for i in (hint.find('print('), len(hint)) if i >= 0):].rstrip('.') for hint in hints if 'print(' in hint]
    programs = set(whole)
    for size in range(1, len(pieces) + 1):
        for chosen in itertools.combinations(pieces, size):
            body = '\n'.join(chosen)
            programs.update({body, starter + body})
            # Starters with `pass` placeholders: put the hinted statements in their place.
            if 'pass' in starter:
                for fill in itertools.product(chosen, repeat=starter.count('    pass')):
                    program = starter
                    for statement in fill:
                        program = program.replace('    pass', '    ' + statement, 1)
                    programs.add(program)
    return programs


def replies_for(lesson):
    return list(lesson.task('example').inputs)


def given(challenge):
    """Everything a learner can be shown before passing: the hint ladder, the tagged hints, and the
    similar example (ENG-04 part 2a). Each example line counts as a statement on its own."""
    example = challenge.similar_example.code.splitlines() if challenge.similar_example else []
    return [*challenge.hints, *(h.text for h in challenge.error_hints), *example]


@pytest.mark.parametrize('lesson_id', UNIT_1)
def test_no_combination_of_hints_passes_the_check(lesson_id):
    lesson = LESSONS[lesson_id]
    challenge = lesson.task('challenge')
    programs = candidates(challenge.starter, given(challenge))
    assert programs, 'the audit found something to try'
    passing = [p for p in programs if run(lesson_id, p, replies_for(lesson))[0] == 'passed']
    assert passing == []


@pytest.mark.parametrize('lesson_id', UNIT_1)
def test_the_similar_example_does_not_pass_but_every_other_way_does(lesson_id):
    lesson = LESSONS[lesson_id]
    challenge = lesson.task('challenge')
    example = challenge.similar_example.code
    for program in (example, challenge.starter + example):
        assert run(lesson_id, program, replies_for(lesson))[0] != 'passed', program
    # "Other ways" appear only after passing, and must really be valid solutions.
    for way in challenge.other_ways:
        assert run(lesson_id, way.code, replies_for(lesson))[0] == 'passed', way.code


# The audit itself catches hints that give the answer away (control, with the hints published before)

OLD_HINTS = {
    'hello': ['Start with lowercase print, followed by parentheses.', 'Put one message in matching quotes inside each print call.',
              'Example: print("You land on Mars.")\nprint("A robot offers you tea.")'],
    'input': ['Store the returned text: player = input("Name? ").', 'Join your message to player: print("Welcome, " + player).',
              'Another valid option is an f-string: print(f"Ready for adventure, {player}?")'],
}


def test_the_hint_audit_catches_the_old_input_hints():
    lesson = LESSONS['input']
    programs = candidates(lesson.task('challenge').starter, OLD_HINTS['input'])
    assert any(run('input', p, ['Kai'])[0] == 'passed' for p in programs)


def test_the_old_hello_hint_would_pass_if_it_were_not_refused():
    # Under v1 rules (two non-empty lines) the old hint 3 was a full answer; v2 refuses it by name.
    programs = candidates(LESSONS['hello'].task('challenge').starter, OLD_HINTS['hello'])
    assert two_lines('You land on Mars.', 'A robot offers you tea.') in programs
    assert run('hello', two_lines('You land on Mars.', 'A robot offers you tea.'))[0] == 'needs_work'


# Versions, IDs, XP and badges

def test_changed_challenges_are_new_versions_and_nothing_else_moved():
    fixture = json.loads((content.CONTENT_DIR.parent / 'tests/fixtures/legacy_lessons_v1.json').read_text())
    assert [lesson['id'] for lesson in fixture] == UNIT_1
    for lesson_id in UNIT_1:
        lesson = LESSONS[lesson_id]
        challenge = lesson.task('challenge')
        # v3: messages and hints reworded (ENG-04 part 2a); the check itself (validator v2) is unchanged.
        assert (lesson.version, challenge.version, challenge.validator.id, challenge.validator.version) == (3, 3, 'bounded-story', 2)
        assert challenge.id == f'{lesson_id}.challenge'
        assert lesson.badge.version == 1
        assert all(task.version == 1 for task in lesson.tasks if task.type != 'challenge')
    assert content.VALIDATORS == {'bounded-story': {2}}
    assert CHALLENGE_XP == 100


@pytest.fixture
def student():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = User(subject='s', email='student@example.com', role='student')
        db.add(user)
        db.flush()
        token = secrets.token_urlsafe(32)
        now = int(sessions.clock())
        db.add(UserSession(id=sessions.digest(token), user_id=user.id, created=now, last_seen=now, expires=now + sessions.ABSOLUTE))
        db.commit()
        uid = user.id
    cookie = TimestampSigner(os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps({'sid': token}).encode())).decode()
    client.cookies.clear()
    client.cookies.set('session', cookie, domain='testserver.local', path='/')
    return uid


def test_completions_from_before_stay_valid_and_are_not_awarded_again(student):
    # A learner who passed "Open the story" under v1, perhaps with print("hi") twice.
    with Session(engine) as db:
        db.add(XpAward(user_id=student, task_id='hello.challenge', task_version=1, xp=100, source='practice'))
        db.add(BadgeAward(user_id=student, badge_id='py.badge.story-spark', badge_version=1, source='practice'))
        db.commit()
    assert client.get('/api/progress').json() == ['hello']
    before = client.get('/api/awards').json()
    assert before['xp'] == 100 and [b['id'] for b in before['badges']] == ['py.badge.story-spark']
    code, _ = PASSING['hello']
    response = client.post('/api/attempts', json={'lesson_id': 'hello', 'code': code, 'output': 'A forest.\nA dragon!\n'}, headers=HEADERS)
    assert response.json()['result'] == 'passed'
    assert client.get('/api/awards').json() == before
    with Session(engine) as db:
        assert [(a.task_version, a.xp) for a in db.scalars(select(XpAward))] == [(1, 100)]


def test_the_hi_woah_response_the_lesson_page_test_shows_is_the_real_one():
    # frontend/tests/feedback.spec.ts shows this response on the page (ENG-04); it must not drift from the API.
    fixture = json.loads((content.CONTENT_DIR.parents[1] / 'frontend/tests/fixtures/hello-hi-woah.json').read_text())
    assert client.post('/api/check', json=fixture['request'], headers=HEADERS).json() == fixture['response']

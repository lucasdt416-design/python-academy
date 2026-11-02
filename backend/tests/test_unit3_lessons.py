"""Python unit 3, part 1 (EDU-03): py.while-loops, py.loop-termination and py.for-range, released with
more lessons coming (py.accumulate and py.nested-loops are part 2).

The same checks as unit 2 (tests/test_unit2_lessons.py and test_unit2_part2.py, whose helpers this file
reuses): tests/case_runner.py plays the browser's part, and the real judge decides. Loops add three ways a
program can fail to finish: it asks for more replies than a case gives (EOFError, judged "missing reply"),
it prints for ever (the output limit), or it runs silently for ever (the time limit). The runner stops a
case the way the browser does, so all three are tested here.

frontend/tests/fixtures/unit3-api.json holds the API's answers that the unit 3 browser tests mock.
To rewrite it after a deliberate content change: WRITE_UNIT3_RECORDINGS=1 python -m pytest -q tests/test_unit3_lessons.py
"""
import itertools
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import test_unit2_lessons as part1
from app import content, recommend as rules
from app.main import app
from case_runner import reports, run, run_program

LESSONS = part1.LESSONS
UNIT_3 = ['py.while-loops', 'py.loop-termination', 'py.for-range']
PART_2 = ['py.accumulate', 'py.nested-loops']  # the rest of py.u03, proposed for the next PR
HEADERS = part1.HEADERS
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/unit3-api.json'
challenge, case_rules, judge, judge_all = part1.challenge, part1.case_rules, part1.judge, part1.judge_all

ASK = 'secret = int(input("Secret number? "))\nguess = int(input("Your guess? "))\n'
TOP = 'top = int(input("Top step? "))\n'

REFERENCE = {
    'py.while-loops': ASK + 'while guess != secret:\n    print(guess > secret)\n    guess = int(input("Your guess? "))\n',
    'py.loop-termination': ASK + 'tries = 1\nwhile guess != secret and tries < 3:\n    guess = int(input("Your guess? "))\n    tries = tries + 1\nprint(tries)\nprint(guess == secret)\n',
    'py.for-range': TOP + 'for step in range(2, top + 1, 2):\n    print(step)\n',
}

CREATIVE = {
    'py.while-loops': [
        ASK + 'while not guess == secret:\n    if guess > secret:\n        print(True)\n    else:\n        print(False)\n    guess = int(input())',
        'secret = int(input())\nwhile True:\n    guess = int(input())\n    if guess == secret:\n        break\n    print(guess > secret)',
        'secret = int(input())\nguess = None\nwhile guess != secret:\n    if guess is not None:\n        print(guess > secret)\n    guess = int(input())',
    ],
    'py.loop-termination': [
        'secret = int(input())\nsolved = False\ntries = 0\nfor attempt in range(3):\n    guess = int(input())\n    tries = attempt + 1\n    if guess == secret:\n        solved = True\n        break\nprint(tries)\nprint(solved)',
        ASK + 'left = 2\nwhile guess != secret and left > 0:\n    guess = int(input())\n    left = left - 1\nprint(3 - left)\nprint(guess == secret)',
        ASK + 'tries = 1\nwhile tries <= 2 and guess != secret:\n    tries += 1\n    guess = int(input())\nprint(tries)\nprint(guess == secret)',
    ],
    'py.for-range': [
        TOP + 'for n in range(1, top // 2 + 1):\n    print(n * 2)',
        TOP + 'for step in range(top + 1):\n    if step > 0 and step % 2 == 0:\n        print(step)',
        'top = int(input())\nstep = 2\nwhile step <= top:\n    print(step)\n    step += 2',
    ],
}

# Lesson 1's starter asks for the two numbers, so its samples follow those lines; lessons 2 and 3 leave
# that to the learner, so their samples are whole programs.
STARTER_LINES = {'py.while-loops': ASK, 'py.loop-termination': '', 'py.for-range': ''}

WRONG = {
    'py.while-loops': [
        ('if instead of while', 'if guess != secret:\n    print(guess > secret)\n    guess = int(input())', 'needs_work', 'py.while-loops.case.three-tries'),
        ('the condition the wrong way round', 'while guess == secret:\n    print(guess > secret)\n    guess = int(input())', 'needs_work', 'py.while-loops.case.three-tries'),
        ('prints before the loop checks', 'print(guess > secret)\nwhile guess != secret:\n    guess = int(input())\n    if guess != secret:\n        print(guess > secret)', 'needs_work', 'py.while-loops.case.first-try'),
        ('contrived: stops after two wrong guesses', 'wrong = 0\nwhile guess != secret and wrong < 2:\n    print(guess > secret)\n    wrong = wrong + 1\n    guess = int(input())', 'needs_work', 'py.while-loops.case.many-low'),
        ('contrived: compares sizes without the sign', 'while guess != secret:\n    print(abs(guess) > abs(secret))\n    guess = int(input())', 'needs_work', 'py.while-loops.case.below-zero'),
        ('contrived: stops after four wrong guesses', 'wrong = 0\nwhile guess != secret and wrong < 4:\n    print(guess > secret)\n    wrong = wrong + 1\n    guess = int(input())', 'needs_work', 'py.while-loops.case.long'),
        ('never asks again: prints for ever', 'while guess != secret:\n    print(guess > secret)', 'execution_error', ('output_limit', None, None)),
        ('while True with no way out', 'while True:\n    print(guess > secret)\n    guess = int(input())', 'needs_work', ('missing_input', 'EOFError', 5)),
        ('asks again but forgets int()', 'while guess != secret:\n    print(guess > secret)\n    guess = input()', 'execution_error', ('error', 'TypeError', 4)),
        ('a misspelt name', 'while gues != secret:\n    print(guess > secret)', 'execution_error', ('error', 'NameError', 3)),
        ('a loop line with no indent', 'while guess != secret:\nprint(guess > secret)', 'execution_error', ('error', 'IndentationError', 4)),
        ('a module the browser does not have', 'import pygame\nprint(guess > secret)', 'unsupported', ('unsupported', 'ModuleNotFoundError', 3)),
    ],
    'py.loop-termination': [
        ('no limit on tries', ASK + 'tries = 1\nwhile guess != secret:\n    guess = int(input())\n    tries = tries + 1\nprint(tries)\nprint(guess == secret)', 'needs_work', 'py.loop-termination.case.extra-replies'),
        ('four tries instead of three', ASK + 'tries = 1\nwhile guess != secret and tries < 4:\n    guess = int(input())\n    tries = tries + 1\nprint(tries)\nprint(guess == secret)', 'needs_work', 'py.loop-termination.case.extra-replies'),
        ('two tries: stops one early', ASK + 'tries = 1\nwhile guess != secret and tries < 2:\n    guess = int(input())\n    tries = tries + 1\nprint(tries)\nprint(guess == secret)', 'needs_work', 'py.loop-termination.case.third-try'),
        ('counter starts at 0', ASK + 'tries = 0\nwhile guess != secret and tries < 3:\n    guess = int(input())\n    tries = tries + 1\nprint(tries)\nprint(guess == secret)', 'needs_work', 'py.loop-termination.case.first-try'),
        ('contrived: the secret 7 is always right', ASK + 'tries = 1\nwhile guess != secret and tries < 3:\n    guess = int(input())\n    tries = tries + 1\nprint(tries)\nprint(guess == secret or secret == 7)', 'needs_work', 'py.loop-termination.case.out-of-tries'),
        ('contrived: assumes the secret is above zero', ASK + 'tries = 1\nwhile guess != secret and tries < 3:\n    guess = int(input())\n    tries = tries + 1\nprint(tries)\nprint(guess == secret and secret > 0)', 'needs_work', 'py.loop-termination.case.below-zero'),
        ('contrived: reports 2 tries as 3', ASK + 'tries = 1\nwhile guess != secret and tries < 3:\n    guess = int(input())\n    tries = tries + 1\nif tries == 2 and secret > 0:\n    tries = 3\nprint(tries)\nprint(guess == secret)', 'needs_work', 'py.loop-termination.case.second-try'),
        ('or instead of and', ASK + 'tries = 1\nwhile guess != secret or tries < 3:\n    guess = int(input())\n    tries = tries + 1\nprint(tries)\nprint(guess == secret)', 'needs_work', ('missing_input', 'EOFError', 5)),
        ('the loop changes nothing: runs for ever', ASK + 'tries = 1\nwhile guess != secret and tries < 3:\n    tries = tries\nprint(tries)\nprint(guess == secret)', 'execution_error', ('timeout', None, None)),
        ('a misspelt name', ASK + 'tries = 1\nwhile gues != secret and tries < 3:\n    guess = int(input())', 'execution_error', ('error', 'NameError', 4)),
    ],
    'py.for-range': [
        ('the stop of range() is the top', TOP + 'for step in range(2, top, 2):\n    print(step)', 'needs_work', 'py.for-range.case.even-top'),
        ('starts at 0', TOP + 'for step in range(0, top + 1, 2):\n    print(step)', 'needs_work', 'py.for-range.case.even-top'),
        ('every step, not every second one', TOP + 'for step in range(1, top + 1):\n    print(step)', 'needs_work', 'py.for-range.case.even-top'),
        ('the stop two past the top', TOP + 'for step in range(2, top + 2, 2):\n    print(step)', 'needs_work', 'py.for-range.case.odd-top'),
        ('always prints step 2 first', TOP + 'print(2)\nfor step in range(4, top + 1, 2):\n    print(step)', 'needs_work', 'py.for-range.case.none'),
        ('contrived: stops at step 10', TOP + 'for step in range(2, min(top, 10) + 1, 2):\n    print(step)', 'needs_work', 'py.for-range.case.bigger'),
        ('contrived: an odd top above 10 counts one more', TOP + 'if top > 10 and top % 2 == 1:\n    top = top + 1\nfor step in range(2, top + 1, 2):\n    print(step)', 'needs_work', 'py.for-range.case.odd-bigger'),
        ('a while loop that never moves on: prints for ever', TOP + 'step = 2\nwhile step <= top:\n    print(step)', 'execution_error', ('output_limit', None, None)),
        ('a while loop that never moves on, silently', TOP + 'step = 2\nwhile step <= top:\n    step = step', 'execution_error', ('timeout', None, None)),
        ('forgets int()', 'top = input()\nfor step in range(2, top + 1, 2):\n    print(step)', 'execution_error', ('error', 'TypeError', 2)),
        ('a misspelt name', TOP + 'for step in range(2, tpo + 1, 2):\n    print(step)', 'execution_error', ('error', 'NameError', 2)),
        ('a loop line with no indent', TOP + 'for step in range(2, top + 1, 2):\nprint(step)', 'execution_error', ('error', 'IndentationError', 3)),
    ],
}


def wrong_program(lesson_id, body):
    return STARTER_LINES[lesson_id] + body


# The unit, released in parts

def test_unit_3_is_released_with_its_first_three_lessons_and_more_coming():
    py = next(c for c in part1.CATALOG.courses if c.id == 'py')
    unit = next(u for u in py.units if u.id == 'py.u03')
    assert (unit.status, unit.lessons, unit.more_lessons_coming) == ('released', UNIT_3, True)
    assert 'come next' in unit.summary
    assert not set(PART_2) & set(LESSONS), 'part 2 lessons belong to the next PR'
    assert [u.id for u in py.units if u.status == 'released'] == ['py.u01', 'py.u02', 'py.u03']


def test_the_catalog_says_unit_3_is_not_complete_and_units_1_and_2_are():
    units = {u['id']: u for c in TestClient(app).get('/api/catalog').json()['courses'] for u in c['units']}
    assert (units['py.u01']['complete'], units['py.u02']['complete'], units['py.u03']['complete']) == (True, True, False)
    assert [l['id'] for l in units['py.u03']['lessons']] == UNIT_3


def test_the_recommendation_rules_did_not_change():
    # Unit 3 is the first real use of more_lessons_coming (PR #31). The rules already handle it, so
    # the version stays 2.
    assert rules.RULES_VERSION == 2


@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_each_lesson_is_a_browser_check_with_visible_and_hidden_cases(lesson_id):
    lesson = LESSONS[lesson_id]
    task = challenge(lesson_id)
    assert (lesson.course, lesson.unit, lesson.version) == ('py', 'py.u03', 1)
    assert (task.validator.id, task.validator.version, task.version) == ('browser-tests', 1, 1)
    assert task.check.time_limit_ms == 3000
    visible = [c for c in task.check.cases if c.visibility == 'visible']
    hidden = [c for c in task.check.cases if c.visibility == 'hidden']
    assert len(visible) >= 3 and len(hidden) == 2
    assert task.messages == [] and task.check.require == [] and task.check.forbid == []
    assert len(task.hints) == 3 and task.similar_example and len(task.other_ways) == 2
    assert lesson.badge.category == 'practice' and lesson.badge.version == 1
    assert 'Print just the' in task.prompt


def test_correct_outputs_stay_far_below_the_output_limit():
    for lesson_id in UNIT_3:
        for case in challenge(lesson_id).check.cases:
            assert len(case.expected) < 200, (lesson_id, case.id)


def test_badges_are_new_and_one_per_lesson():
    badges = [LESSONS[i].badge.id for i in UNIT_3]
    assert badges == ['py.badge.patient-guesser', 'py.badge.loop-closer', 'py.badge.step-counter']
    assert not {LESSONS[i].badge.id for i in LESSONS if i not in UNIT_3} & set(badges)


def test_support_fades_across_the_three_lessons():
    assert 'int(input(' in challenge('py.while-loops').starter
    for lesson_id in ('py.loop-termination', 'py.for-range'):
        assert all(line.startswith('#') for line in challenge(lesson_id).starter.splitlines())
    assert len(challenge('py.for-range').starter.splitlines()) < len(challenge('py.loop-termination').starter.splitlines())


def test_for_is_taught_and_the_while_version_is_one_of_the_other_ways():
    ways = [way.code for way in challenge('py.for-range').other_ways]
    assert any('while ' in code for code in ways)
    assert 'for ' in REFERENCE['py.for-range']


# What the cards say is what Python does

@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_every_worked_example_prints_what_its_card_shows(lesson_id):
    example = LESSONS[lesson_id].task('example')
    assert run_program(example.code, example.inputs) == (example.output + '\n', None)


EXAMPLE = {i: LESSONS[i].task('example').code for i in UNIT_3}

CLAIMS = [
    ('while predict: moon first', EXAMPLE['py.while-loops'], ['moon'], 'The door opens.'),
    ('while similar example', challenge('py.while-loops').similar_example.code, [], '81'),
    ('termination: count = 5', EXAMPLE['py.loop-termination'].replace('count = 3', 'count = 5'), [], '5\n4\n3\n2\n1\nopen'),
    ('termination: >= instead of >', EXAMPLE['py.loop-termination'].replace('count > 0', 'count >= 0'), [], '3\n2\n1\n0\nopen'),
    ('termination similar example', challenge('py.loop-termination').similar_example.code, [], '2\n4'),
    ('for discover: range(1, 4)', 'for n in range(1, 4):\n    print(n)', [], '1\n2\n3'),
    ('for discover: range(4) and a step', 'print(list(range(4)))\nprint(list(range(2, 9, 2)))\nprint(list(range(3, 0, -1)))', [], '[0, 1, 2, 3]\n[2, 4, 6, 8]\n[3, 2, 1]'),
    ('for predict', 'for n in range(2, 7, 2):\n    print(n)', [], '2\n4\n6'),
    ('for approach hint', 'rows = 10\nfor seat in range(1, rows + 1, 3):\n    print(seat)', [], '1\n4\n7\n10'),
    ('for similar example', challenge('py.for-range').similar_example.code, [], '10\n7\n4\n1'),
]


@pytest.mark.parametrize('where,code,replies,shown', CLAIMS, ids=[c[0] for c in CLAIMS])
def test_what_the_cards_say_python_prints_is_what_it_prints(where, code, replies, shown):
    assert run_program(code, replies) == (shown + '\n', None)


def test_the_predict_answers_are_right():
    predict = LESSONS['py.while-loops'].task('predict')
    assert predict.options[predict.answer] == 'Only The door opens.'
    predict = LESSONS['py.for-range'].task('predict')
    assert predict.options[predict.answer] == '2, 4 and 6'
    # Deleting count = count - 1 makes the loop print 3 for ever, so the output limit stops it.
    endless = EXAMPLE['py.loop-termination'].replace('    count = count - 1\n', '')
    assert 'count - 1' not in endless
    found = reports(LESSONS['py.loop-termination'], [endless])[0][0]
    assert found.status == 'output_limit' and set(found.output.split()) == {'3'}
    predict = LESSONS['py.loop-termination'].task('predict')
    assert 'never finish' in predict.options[predict.answer]


def test_running_out_of_replies_on_the_try_it_card_is_an_eoferror():
    # The guided card says to try three wrong replies; the worker then raises EOFError, which the page
    # explains as "Not enough player replies" (frontend/app/feedback.ts, translation "replies").
    assert run_program(EXAMPLE['py.while-loops'], ['star', 'sun', 'comet']) == ('The door stays shut.\n' * 3, 'EOFError')


def test_the_error_hints_describe_real_errors():
    assert run_program('guess = input()\nprint(guess > 7)', ['9'])[1] == 'TypeError'
    assert run_program('top = input()\nfor step in range(2, top + 1, 2):\n    print(step)', ['8'])[1] == 'TypeError'


def test_the_example_is_not_the_challenge():
    for lesson_id in UNIT_3:
        example = EXAMPLE[lesson_id]
        for program in (example, STARTER_LINES[lesson_id] + example):
            assert judge(lesson_id, program)['result'] != 'passed'


# Correct programs pass, wrong ones fail with the right rule

@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_reference_creative_and_other_ways_all_pass(lesson_id):
    programs = [REFERENCE[lesson_id], *CREATIVE[lesson_id], *(way.code for way in challenge(lesson_id).other_ways)]
    results = judge_all(lesson_id, programs)
    assert [r['result'] for r in results] == ['passed'] * len(programs), [r['feedback'] for r in results]


@pytest.mark.parametrize('lesson_id,label,body,result,expect', [(l, *w) for l in UNIT_3 for w in WRONG[l]],
                         ids=[f'{l}: {w[0]}' for l in UNIT_3 for w in WRONG[l]])
def test_wrong_programs_fail_with_the_right_rule(lesson_id, label, body, result, expect):
    answer = judge(lesson_id, wrong_program(lesson_id, body))
    assert answer['result'] == result, answer['feedback']
    if isinstance(expect, str):
        assert (answer['rule'], answer['failed']['reason']) == (expect, 'wrong_output')
        case = next(c for c in challenge(lesson_id).check.cases if expect.endswith('.case.' + c.id))
        assert case.description in answer['feedback']
    else:
        reason, error_type, line = expect
        assert (answer['rule'], answer['failed']['reason'], answer['failed']['error_type'], answer['failed']['line']) == (None, reason, error_type, line)


def test_every_way_a_loop_can_fail_to_finish_is_caught():
    endings = {expect[0] for lesson_id in UNIT_3 for *_, expect in WRONG[lesson_id] if not isinstance(expect, str)}
    assert {'timeout', 'output_limit', 'missing_input'} <= endings
    # A loop that never ends is never a pass, and it says what happened in words a beginner can use.
    answer = judge('py.for-range', wrong_program('py.for-range', next(w[1] for w in WRONG['py.for-range'] if 'silently' in w[0])))
    assert answer['feedback'].startswith('Your program was still running after 3 seconds on a top step of 8, so it was stopped.')


@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_every_case_rule_has_a_wrong_sample_and_a_message(lesson_id):
    sampled = {expect for _, _, _, expect in WRONG[lesson_id] if isinstance(expect, str)}
    assert sampled == case_rules(lesson_id)
    for case in challenge(lesson_id).check.cases:
        assert case.description.strip() and len(case.description) <= 60


@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_printing_the_expected_text_without_doing_the_work_fails(lesson_id):
    cases = challenge(lesson_id).check.cases
    visible = [c for c in cases if c.visibility == 'visible']
    fixed = [f'print({json.dumps(c.expected)})' for c in visible]
    table = {tuple(c.inputs): c.expected for c in visible}
    # Read every reply a case could give, then look the answer up: right on every visible case.
    lookup = ('replies = []\nwhile True:\n    try:\n        replies.append(input())\n    except EOFError:\n        break\n'
              f'print({table!r}.get(tuple(replies), ""))')
    answers = judge_all(lesson_id, [*fixed, lookup])
    for answer in answers:
        assert answer['result'] == 'needs_work'
    assert answers[-1]['failed']['visibility'] == 'hidden' and answers[-1]['rule'] in case_rules(lesson_id)


@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_every_tagged_hint_is_for_a_rule_or_error_this_lesson_can_report(lesson_id):
    tags = {tag for hint in challenge(lesson_id).error_hints for tag in hint.tags}
    errors = {expect[1] for _, _, _, expect in WRONG[lesson_id] if not isinstance(expect, str)}
    assert tags <= case_rules(lesson_id) | errors, tags - case_rules(lesson_id) - errors


# No hint, tagged hint or similar example, alone or together, passes the check

@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_the_audit_finds_the_code_in_the_hints(lesson_id):
    pieces, _ = part1.hint_pieces(lesson_id)
    expected = {
        'py.while-loops': {'while word != "moon":'},
        'py.loop-termination': {'while answer != key and turns < 5:'},
        'py.for-range': {'for seat in range(1, rows + 1, 3):'},
    }[lesson_id]
    assert expected <= set(pieces), pieces


@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_no_combination_of_hints_passes_the_check(lesson_id):
    programs = part1.candidates(lesson_id)
    # Also after the replies are read, as a learner would put them before the hinted lines.
    programs += [ASK + p for p in programs] + [TOP + p for p in programs]
    assert len(programs) > 10
    passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
    assert passing == []


RENAMED = {
    'py.while-loops': {'word': 'guess', '"moon"': 'secret', 'steps': 'guess'},
    'py.loop-termination': {'answer': 'guess', 'key': 'secret', 'turns': 'tries', 'fuel': 'guess', 'trips': 'tries'},
    'py.for-range': {'seat': 'step', 'rows': 'top', 'floor': 'step'},
}


@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_the_hints_with_the_challenges_own_names_still_do_not_pass(lesson_id):
    task = challenge(lesson_id)
    names = RENAMED[lesson_id]
    pieces = [part1.renamed(p, names) for text in [*task.hints, *(h.text for h in task.error_hints)] for p in part1.fragments(text)]
    example = part1.renamed(task.similar_example.code, names)
    start = ASK + 'tries = 1\n' if lesson_id != 'py.for-range' else TOP
    programs = {start + example}
    for size in range(1, len(pieces) + 1):
        for chosen in itertools.combinations(pieces, size):
            for body in {part1.assemble(chosen), part1.assemble(chosen, greedy=True)}:
                programs.update({start + body, start + body + '\n' + example})
    programs = sorted(programs)
    passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
    assert passing == []


def test_the_audit_catches_a_hint_that_spells_out_the_loop():
    # Control: a hint that writes the whole loop out is found, and with the starter it passes.
    leak = 'Write while guess != secret: then print(guess > secret) and guess = int(input()) inside it.'
    pieces = part1.fragments(leak)
    program = challenge('py.while-loops').starter + part1.assemble(pieces, greedy=True)
    assert judge('py.while-loops', program)['result'] == 'passed'


# Hidden expected output never reaches the browser

@pytest.mark.parametrize('lesson_id', UNIT_3)
def test_no_answer_holds_a_hidden_expected_output(lesson_id):
    client = TestClient(app)
    plan = client.get(f'/api/checks/{lesson_id}').json()
    assert all(('expected' in case) == (case['visibility'] == 'visible') for case in plan['cases'])
    answers = [client.get(path).text for path in ('/api/catalog', '/api/lessons', '/api/units/py.u03/lessons', f'/api/checks/{lesson_id}')]
    for _, body, _, _ in WRONG[lesson_id]:
        code = wrong_program(lesson_id, body)
        runs = [r.model_dump() for r in run(LESSONS[lesson_id], code)]
        answers.append(client.post('/api/check', json={'lesson_id': lesson_id, 'code': code, 'output': runs[0]['output'], 'runs': runs}, headers=HEADERS).text)
    visible = {json.dumps(c.expected) for c in challenge(lesson_id).check.cases if c.visibility == 'visible'}
    for case in challenge(lesson_id).check.cases:
        value = json.dumps(case.expected)
        if case.visibility == 'hidden' and value not in visible and case.expected:
            for answer in answers:
                assert value not in answer, value


# XP and badges, once each

def test_each_lesson_awards_100_xp_and_its_badge_once():
    from app.db import Base, BadgeAward, XpAward
    from app.main import engine
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    client = TestClient(app)
    client.cookies.set('session', part1.sign_in_student(), domain='testserver.local', path='/')
    for lesson_id in UNIT_3:
        assert part1.attempt(client, lesson_id, wrong_program(lesson_id, WRONG[lesson_id][0][1]))['result'] != 'passed'
    assert client.get('/api/awards').json()['xp'] == 0
    for _ in range(2):
        for lesson_id in UNIT_3:
            assert part1.attempt(client, lesson_id, REFERENCE[lesson_id])['result'] == 'passed'
    awards = client.get('/api/awards').json()
    assert awards['xp'] == 300 and awards['completed'] == UNIT_3
    assert [b['title'] for b in awards['badges']] == ['Patient guesser', 'Loop closer', 'Step counter']
    with Session(engine) as db:
        assert sorted((a.task_id, a.task_version, a.xp) for a in db.scalars(select(XpAward))) == sorted((f'{i}.challenge', 1, 100) for i in UNIT_3)
        assert db.scalar(select(func.count()).select_from(BadgeAward)) == 3


# The answers the browser tests use are the real API's

SCENARIOS = [
    ('while passed', 'py.while-loops', REFERENCE['py.while-loops'], None),
    ('while needs_work', 'py.while-loops', wrong_program('py.while-loops', WRONG['py.while-loops'][0][1]) + '\n', None),
    ('while out of replies', 'py.while-loops', wrong_program('py.while-loops', 'while True:\n    print(guess > secret)\n    guess = int(input())') + '\n', None),
    ('while prints for ever', 'py.while-loops', wrong_program('py.while-loops', 'while guess != secret:\n    print(guess > secret)') + '\n', None),
    ('while name error', 'py.while-loops', wrong_program('py.while-loops', 'while gues != secret:\n    print(guess > secret)') + '\n', None),
    ('while endless loop', 'py.while-loops', ASK + 'while True:\n    pass\n', 'timeout'),
    ('while unsupported', 'py.while-loops', 'import turtle\n' + REFERENCE['py.while-loops'], 'unsupported'),
    ('termination passed', 'py.loop-termination', REFERENCE['py.loop-termination'], None),
    ('termination needs_work', 'py.loop-termination', WRONG['py.loop-termination'][0][1] + '\n', None),
    ('termination indentation error', 'py.loop-termination', ASK + 'tries = 1\nwhile guess != secret and tries < 3:\nguess = int(input())\n', None),
    ('termination endless loop', 'py.loop-termination', ASK + 'tries = 1\nwhile tries < 3:\n    tries = tries\n', 'timeout'),
    ('termination unsupported', 'py.loop-termination', 'import turtle\n' + REFERENCE['py.loop-termination'], 'unsupported'),
    ('for passed', 'py.for-range', REFERENCE['py.for-range'], None),
    ('for needs_work', 'py.for-range', WRONG['py.for-range'][0][1] + '\n', None),
    ('for hidden', 'py.for-range', WRONG['py.for-range'][5][1] + '\n', None),
    ('for type error', 'py.for-range', 'top = input("Top step? ")\nfor step in range(2, top + 1, 2):\n    print(step)\n', None),
    ('for endless loop', 'py.for-range', TOP + 'step = 2\nwhile step <= top:\n    step = step\n', 'timeout'),
    ('for unsupported', 'py.for-range', 'import turtle\n' + REFERENCE['py.for-range'], 'unsupported'),
]

ALL_RELEASED = [l for c in part1.CATALOG.courses for u in c.units if u.status == 'released' for l in u.lessons]


def recommendation_after(lessons):
    """The real /api/recommendation for a student who has finished these lessons."""
    from app.db import Base, XpAward
    from app.main import engine
    from sqlalchemy.orm import Session
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    client = TestClient(app)
    client.cookies.set('session', part1.sign_in_student(), domain='testserver.local', path='/')
    from app.db import User
    from sqlalchemy import select
    with Session(engine) as db:
        uid = db.scalars(select(User)).one().id
        for lesson_id in lessons:
            task = LESSONS[lesson_id].task('challenge')
            db.add(XpAward(user_id=uid, task_id=task.id, task_version=task.version, xp=100, source='practice'))
        db.commit()
    return client.get('/api/recommendation').json()


def build_recordings():
    client = TestClient(app)
    recorded = {'catalog': client.get('/api/catalog').json(),
                'units': {'py.u03': client.get('/api/units/py.u03/lessons').json()},
                'plans': {i: client.get(f'/api/checks/{i}').json() for i in UNIT_3},
                'recommendation': recommendation_after(ALL_RELEASED),
                'scenarios': []}
    for name, lesson_id, code, kind in SCENARIOS:
        runs = None
        if kind == 'timeout':
            runs = part1.stopped(lesson_id, 'timeout')
        elif kind == 'unsupported':
            runs = part1.stopped(lesson_id, 'error', 'error', error_type='ModuleNotFoundError', line=1)
        s = part1.scenario(name, lesson_id, code, runs)
        s['response'] = client.post('/api/check', json=s['request'], headers=HEADERS).json()
        recorded['scenarios'].append(s)
    return recorded


def test_the_home_recommendation_says_unit_3_has_more_lessons_and_never_names_unit_4():
    r = recommendation_after(ALL_RELEASED)
    assert r['kind'] == 'caught_up' and r['lesson'] is None
    assert r['notes'][0] == 'Python Foundations unit 3, Repeat and explore, has more lessons on the way. You have finished every lesson in it so far.'
    assert 'unit 4' not in json.dumps(r) and 'Keep track of a world' not in json.dumps(r)
    # Partway through unit 3: continue it.
    r = recommendation_after([l for l in ALL_RELEASED if l != 'py.for-range'])
    assert (r['kind'], r['unit'], r['lesson']) == ('continue', 'py.u03', 'py.for-range')


def test_the_recorded_answers_are_the_real_apis():
    recorded = build_recordings()
    if os.environ.get('WRITE_UNIT3_RECORDINGS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded
    results = {s['name']: s['response'] for s in recorded['scenarios']}
    for lesson in ('while', 'termination', 'for'):
        assert results[f'{lesson} passed']['result'] == 'passed' and results[f'{lesson} needs_work']['result'] == 'needs_work'
        assert results[f'{lesson} endless loop']['result'] == 'execution_error' and results[f'{lesson} unsupported']['result'] == 'unsupported'
    assert results['while out of replies']['failed']['reason'] == 'missing_input'
    assert results['while prints for ever']['failed']['reason'] == 'output_limit'

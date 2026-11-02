"""Python unit 3, part 2 (EDU-03): py.accumulate and py.nested-loops, and the unit being complete.

The same checks as part 1 (tests/test_unit3_lessons.py, and the helpers in test_unit2_lessons.py):
tests/case_runner.py plays the browser's part, and the real judge decides. There are no construct rules:
a loop inside a loop cannot be told from one loop that works out its row and column, so that program
passes and is shown under "Other ways".

frontend/tests/fixtures/unit3-part2-api.json holds the API's answers that the browser tests mock.
To rewrite it after a deliberate content change: WRITE_UNIT3_RECORDINGS=1 python -m pytest -q tests/test_unit3_part2.py
"""
import itertools
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import test_unit2_lessons as helpers
import test_unit3_lessons as part1
from app import recommend as rules
from app.main import app
from case_runner import reports, run, run_program

LESSONS = helpers.LESSONS
PART_2 = ['py.accumulate', 'py.nested-loops']
UNIT_3 = part1.UNIT_3 + PART_2
HEADERS = helpers.HEADERS
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/unit3-part2-api.json'
challenge, case_rules, judge, judge_all = helpers.challenge, helpers.case_rules, helpers.judge, helpers.judge_all

ROUNDS = 'rounds = int(input("Rounds? "))\n'
MAP = 'rows = int(input("Rows? "))\ncolumns = int(input("Columns? "))\n'
START = {'py.accumulate': ROUNDS, 'py.nested-loops': MAP}

SCORE = 'total = 0\nempty = 0\nfor game in range(rounds):\n    points = int(input("Points? "))\n    total = total + points\n    if points == 0:\n        empty = empty + 1\n'
SHOW = 'print(total)\nprint(empty)\nprint(total / rounds)\n'
WALK = 'total = 0\nfor row in range(1, rows + 1):\n    for column in range(1, columns + 1):\n        print(row * column)\n        total = total + row * column\nprint(total)\n'

REFERENCE = {
    'py.accumulate': ROUNDS + SCORE + SHOW,
    'py.nested-loops': MAP + WALK,
}

CREATIVE = {
    'py.accumulate': [
        ROUNDS + 'replies = []\nfor game in range(rounds):\n    replies.append(int(input()))\nprint(sum(replies))\nprint(replies.count(0))\nprint(sum(replies) / len(replies))',
        ROUNDS + 'total = 0\nempty = 0\nleft = rounds\nwhile left > 0:\n    points = int(input())\n    total += points\n    empty += points == 0\n    left -= 1\nprint(total)\nprint(empty)\nprint(total / rounds)',
        ROUNDS + 'total = 0\nscored = 0\nfor game in range(1, rounds + 1):\n    points = int(input())\n    if points:\n        total += points\n        scored += 1\nprint(total)\nprint(rounds - scored)\nprint(float(total) / rounds)',
    ],
    'py.nested-loops': [
        MAP + 'total = 0\nfor row in range(rows):\n    for column in range(columns):\n        coins = (row + 1) * (column + 1)\n        print(coins)\n        total += coins\nprint(total)',
        MAP + 'total = 0\nrow = 1\nwhile row <= rows:\n    for column in range(row, row * columns + 1, row):\n        print(column)\n        total += column\n    row += 1\nprint(total)',
        MAP + 'for row in range(1, rows + 1):\n    for column in range(1, columns + 1):\n        print(row * column)\nprint(rows * (rows + 1) // 2 * (columns * (columns + 1) // 2))',
    ],
}

WRONG = {
    'py.accumulate': [
        ('the total starts at 1', ROUNDS + SCORE.replace('total = 0', 'total = 1') + SHOW, 'needs_work', 'py.accumulate.case.one-round'),
        ('the counter starts at 1', ROUNDS + SCORE.replace('empty = 0', 'empty = 1') + SHOW, 'needs_work', 'py.accumulate.case.one-round'),
        ('// for the average', ROUNDS + SCORE + 'print(total)\nprint(empty)\nprint(total // rounds)\n', 'needs_work', 'py.accumulate.case.one-round'),
        ('asks for one round too few', ROUNDS + SCORE.replace('range(rounds)', 'range(1, rounds)') + SHOW, 'needs_work', 'py.accumulate.case.one-round'),
        ('the total goes back to 0 inside the loop', ROUNDS + 'empty = 0\nfor game in range(rounds):\n    total = 0\n    points = int(input())\n    total = total + points\n    if points == 0:\n        empty = empty + 1\n' + SHOW, 'needs_work', 'py.accumulate.case.three-rounds'),
        ('the counter goes back to 0 inside the loop', ROUNDS + 'total = 0\nfor game in range(rounds):\n    empty = 0\n    points = int(input())\n    total = total + points\n    if points == 0:\n        empty = empty + 1\n' + SHOW, 'needs_work', 'py.accumulate.case.three-rounds'),
        ('the prints are inside the loop', ROUNDS + 'total = 0\nempty = 0\nfor game in range(rounds):\n    points = int(input())\n    total = total + points\n    if points == 0:\n        empty = empty + 1\n    print(total)\n    print(empty)\n    print(total / rounds)\n', 'needs_work', 'py.accumulate.case.three-rounds'),
        ('counts the rounds that scored', ROUNDS + 'total = 0\nempty = 0\nfor game in range(rounds):\n    points = int(input())\n    total = total + points\n    if points > 0:\n        empty = empty + 1\n' + SHOW, 'needs_work', 'py.accumulate.case.one-round'),
        ('contrived: a 0 only counts after a score', ROUNDS + 'total = 0\nempty = 0\nfor game in range(rounds):\n    points = int(input())\n    if points == 0 and total > 0:\n        empty = empty + 1\n    total = total + points\n' + SHOW, 'needs_work', 'py.accumulate.case.no-points'),
        ('contrived: // that still prints a float', ROUNDS + SCORE + 'print(total)\nprint(empty)\nprint(float(total // rounds))\n', 'needs_work', 'py.accumulate.case.many-rounds'),
        ('contrived: reads only three rounds', ROUNDS + SCORE.replace('range(rounds)', 'range(min(rounds, 3))') + SHOW, 'needs_work', 'py.accumulate.case.many-rounds'),
        ('contrived: never counts past 1 in a longer game', ROUNDS + 'total = 0\nempty = 0\nfor game in range(rounds):\n    points = int(input())\n    total = total + points\n    if points == 0 and (empty == 0 or rounds < 3):\n        empty = empty + 1\n' + SHOW, 'needs_work', 'py.accumulate.case.more-empty'),
        ('divides by the empty rounds', ROUNDS + SCORE + 'print(total)\nprint(empty)\nprint(total / empty)\n', 'execution_error', ('error', 'ZeroDivisionError', 11)),
        ('asks for one round too many', ROUNDS + SCORE.replace('range(rounds)', 'range(rounds + 1)') + SHOW, 'needs_work', ('missing_input', 'EOFError', 5)),
        ('forgets int() on the points', ROUNDS + 'total = 0\nfor game in range(rounds):\n    points = input()\n    total = total + points\nprint(total)\n', 'execution_error', ('error', 'TypeError', 5)),
        ('a misspelt name', ROUNDS + 'for game in range(round):\n    points = int(input())\n', 'execution_error', ('error', 'TypeError', 2)),
        ('a total that was never started', ROUNDS + 'for game in range(rounds):\n    points = int(input())\n    total = total + points\n', 'execution_error', ('error', 'NameError', 4)),
        ('a loop line with no indent', ROUNDS + 'for game in range(rounds):\npoints = int(input())\n', 'execution_error', ('error', 'IndentationError', 3)),
        ('never moves on: prints for ever', ROUNDS + 'while rounds > 0:\n    print(rounds)\n', 'execution_error', ('output_limit', None, None)),
        ('never moves on, silently', ROUNDS + 'while rounds > 0:\n    rounds = rounds\n', 'execution_error', ('timeout', None, None)),
        ('a module the browser does not have', 'import pygame\n' + ROUNDS, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    'py.nested-loops': [
        ('the loops are the wrong way round', MAP + 'total = 0\nfor column in range(1, columns + 1):\n    for row in range(1, rows + 1):\n        print(row * column)\n        total = total + row * column\nprint(total)\n', 'needs_work', 'py.nested-loops.case.wide'),
        ('the inner counter does not start again', MAP + 'total = 0\nrow = 1\ncolumn = 1\nwhile row <= rows:\n    while column <= columns:\n        print(row * column)\n        total = total + row * column\n        column = column + 1\n    row = row + 1\nprint(total)\n', 'needs_work', 'py.nested-loops.case.wide'),
        ('the total goes back to 0 for each row', MAP + 'for row in range(1, rows + 1):\n    total = 0\n    for column in range(1, columns + 1):\n        print(row * column)\n        total = total + row * column\nprint(total)\n', 'needs_work', 'py.nested-loops.case.wide'),
        ('the inner range stops one early', MAP + WALK.replace('range(1, columns + 1)', 'range(1, columns)'), 'needs_work', 'py.nested-loops.case.wide'),
        ('counts from 0', MAP + WALK.replace('range(1, rows + 1)', 'range(rows)').replace('range(1, columns + 1)', 'range(columns)'), 'needs_work', 'py.nested-loops.case.wide'),
        ('adds instead of multiplying', MAP + WALK.replace('row * column', 'row + column'), 'needs_work', 'py.nested-loops.case.wide'),
        ('the total is printed after every row', MAP + 'total = 0\nfor row in range(1, rows + 1):\n    for column in range(1, columns + 1):\n        print(row * column)\n        total = total + row * column\n    print(total)\n', 'needs_work', 'py.nested-loops.case.wide'),
        ('no total line', MAP + 'for row in range(1, rows + 1):\n    for column in range(1, columns + 1):\n        print(row * column)\n', 'needs_work', 'py.nested-loops.case.wide'),
        ('two rows typed into the code', MAP + WALK.replace('range(1, rows + 1)', 'range(1, 3)'), 'needs_work', 'py.nested-loops.case.tall'),
        ('contrived: no total for one room', MAP + 'total = 0\nfor row in range(1, rows + 1):\n    for column in range(1, columns + 1):\n        print(row * column)\n        total = total + row * column\nif total > 1:\n    print(total)\n', 'needs_work', 'py.nested-loops.case.single'),
        ('contrived: never more than 3 rows', MAP + WALK.replace('range(1, rows + 1)', 'range(1, min(rows, 3) + 1)'), 'needs_work', 'py.nested-loops.case.more-rows'),
        ('contrived: never more than 3 columns', MAP + WALK.replace('range(1, columns + 1)', 'range(1, min(columns, 3) + 1)'), 'needs_work', 'py.nested-loops.case.more-columns'),
        ('asks for the columns in every row', 'rows = int(input())\ntotal = 0\nfor row in range(1, rows + 1):\n    columns = int(input())\n    for column in range(1, columns + 1):\n        total = total + row * column\nprint(total)\n', 'needs_work', ('missing_input', 'EOFError', 4)),
        ('forgets int()', 'rows = input()\ncolumns = int(input())\nfor row in range(1, rows + 1):\n    print(row)\n', 'execution_error', ('error', 'TypeError', 3)),
        ('a misspelt name', MAP + 'for row in range(1, rows + 1):\n    for column in range(1, colums + 1):\n        print(row * column)\n', 'execution_error', ('error', 'NameError', 4)),
        ('an inner loop with no indent', MAP + 'for row in range(1, rows + 1):\nfor column in range(1, columns + 1):\n    print(row * column)\n', 'execution_error', ('error', 'IndentationError', 4)),
        ('the inner counter never moves: prints for ever', MAP + 'for row in range(1, rows + 1):\n    column = 1\n    while column <= columns:\n        print(row * column)\n', 'execution_error', ('output_limit', None, None)),
        ('the inner counter never moves, silently', MAP + 'for row in range(1, rows + 1):\n    column = 1\n    while column <= columns:\n        column = column\n', 'execution_error', ('timeout', None, None)),
        ('a module the browser does not have', 'import pygame\n' + MAP, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
}


# The unit, complete

def test_unit_3_is_complete_with_five_lessons_in_order():
    py = next(c for c in helpers.CATALOG.courses if c.id == 'py')
    unit = next(u for u in py.units if u.id == 'py.u03')
    assert (unit.status, unit.lessons, unit.more_lessons_coming) == ('released', UNIT_3, False)
    assert 'come next' not in unit.summary and 'running totals' in unit.summary
    assert [u.id for u in py.units if u.status == 'released'] == ['py.u01', 'py.u02', 'py.u03']
    # No unit is still being written.
    assert [u.id for c in helpers.CATALOG.courses for u in c.units if u.more_lessons_coming] == []


def test_the_catalog_says_unit_3_is_complete():
    units = {u['id']: u for c in TestClient(app).get('/api/catalog').json()['courses'] for u in c['units']}
    assert units['py.u03']['complete'] is True
    assert [l['id'] for l in units['py.u03']['lessons']] == UNIT_3
    assert units['py.u04']['complete'] is False and units['py.u04']['lessons'] == []


def test_the_recommendation_rules_did_not_change():
    # Only the catalog's data changed: the rules already handle a complete unit and an unwritten next one.
    assert rules.RULES_VERSION == 2


@pytest.mark.parametrize('lesson_id', PART_2)
def test_each_lesson_is_a_browser_check_with_visible_and_hidden_cases(lesson_id):
    lesson = LESSONS[lesson_id]
    task = challenge(lesson_id)
    assert (lesson.course, lesson.unit, lesson.version) == ('py', 'py.u03', 1)
    assert (task.validator.id, task.validator.version, task.version) == ('browser-tests', 1, 1)
    assert task.check.time_limit_ms == 3000
    visible = [c for c in task.check.cases if c.visibility == 'visible']
    hidden = [c for c in task.check.cases if c.visibility == 'hidden']
    assert len(visible) == 3 and len(hidden) == 2
    assert task.messages == [] and task.check.require == [] and task.check.forbid == []
    assert len(task.hints) == 3 and task.similar_example and len(task.other_ways) == 2
    assert lesson.badge.category == 'practice' and lesson.badge.version == 1
    assert 'Print just the' in task.prompt


def test_correct_outputs_stay_far_below_the_output_limit():
    for lesson_id in PART_2:
        for case in challenge(lesson_id).check.cases:
            assert len(case.expected) < 200, (lesson_id, case.id)


def test_badges_are_new_and_one_per_lesson():
    badges = [LESSONS[i].badge.id for i in PART_2]
    assert badges == ['py.badge.tally-keeper', 'py.badge.map-reader']
    assert not {LESSONS[i].badge.id for i in LESSONS if i not in PART_2} & set(badges)


def test_support_stays_faded_to_one_comment():
    for lesson_id in PART_2:
        starter = challenge(lesson_id).starter
        assert len(starter.splitlines()) == 1 and starter.startswith('#')


def test_no_lesson_card_or_hint_uses_a_list_which_unit_4_teaches():
    for lesson_id in PART_2:
        task = challenge(lesson_id)
        shown = [LESSONS[lesson_id].task('example').code, task.similar_example.code, *task.hints, *(h.text for h in task.error_hints), *(w.code for w in task.other_ways)]
        assert not any('[' in text or 'append' in text for text in shown), lesson_id


# What the cards say is what Python does

@pytest.mark.parametrize('lesson_id', PART_2)
def test_every_worked_example_prints_what_its_card_shows(lesson_id):
    example = LESSONS[lesson_id].task('example')
    assert run_program(example.code, example.inputs) == (example.output + '\n', None)


EXAMPLE = {i: LESSONS[i].task('example') for i in PART_2}
RESET_INSIDE = EXAMPLE['py.accumulate'].code.replace('total = 0\n', '').replace('    coins = int', '    total = 0\n    coins = int')
SWAPPED = 'for seat in range(1, 4):\n    for row in range(1, 3):\n        print(row * 10 + seat)'

CLAIMS = [
    ('accumulate example note: the total grows', 'total = 0\nfor coins in (4, 0, 8):\n    total = total + coins\n    print(total)', [], '4\n4\n12'),
    ('accumulate predict: the start line inside the loop', RESET_INSIDE, ['4', '0', '8'], '8\n2.6666666666666665'),
    ('accumulate similar example', challenge('py.accumulate').similar_example.code, [], '8'),
    ('accumulate similar example note: doubling 0 stays 0', challenge('py.accumulate').similar_example.code.replace('gold = 1', 'gold = 0'), [], '0'),
    ('accumulate one-round hint', 'print(10 // 1)\nprint(10 / 1)', [], '10\n10.0'),
    ('nested discover: 2 turns of 3', 'runs = 0\nfor a in range(2):\n    for b in range(3):\n        runs = runs + 1\nprint(runs)', [], '6'),
    ('nested predict: the loops swapped', SWAPPED, [], '11\n21\n12\n22\n13\n23'),
    ('nested try it: three rows', 'for row in range(1, 4):\n    for seat in range(1, 4):\n        print(row * 10 + seat)', [], '11\n12\n13\n21\n22\n23\n31\n32\n33'),
    ('nested similar example', challenge('py.nested-loops').similar_example.code, [], '100\n130\n200\n230'),
]


@pytest.mark.parametrize('where,code,replies,shown', CLAIMS, ids=[c[0] for c in CLAIMS])
def test_what_the_cards_say_python_prints_is_what_it_prints(where, code, replies, shown):
    assert run_program(code, replies) == (shown + '\n', None)


def test_the_predict_answers_are_right():
    predict = LESSONS['py.accumulate'].task('predict')
    assert predict.options[predict.answer] == run_program(RESET_INSIDE, ['4', '0', '8'])[0].splitlines()[0]
    predict = LESSONS['py.nested-loops'].task('predict')
    first_three = run_program(SWAPPED, [])[0].splitlines()[:3]
    assert predict.options[predict.answer] == f'{first_three[0]}, {first_three[1]} and {first_three[2]}'


def test_the_error_hints_describe_real_errors():
    assert run_program('print(1 / 0)', [])[1] == 'ZeroDivisionError'
    assert run_program('total = 0\ntotal = total + input()', ['1'])[1] == 'TypeError'
    assert run_program('for row in range(1, input() + 1):\n    pass', ['1'])[1] == 'TypeError'


def test_the_example_is_not_the_challenge():
    for lesson_id in PART_2:
        code = EXAMPLE[lesson_id].code
        for program in (code, START[lesson_id] + code):
            assert judge(lesson_id, program)['result'] != 'passed'


# Correct programs pass, wrong ones fail with the right rule

@pytest.mark.parametrize('lesson_id', PART_2)
def test_reference_creative_and_other_ways_all_pass(lesson_id):
    programs = [REFERENCE[lesson_id], *CREATIVE[lesson_id], *(way.code for way in challenge(lesson_id).other_ways)]
    results = judge_all(lesson_id, programs)
    assert [r['result'] for r in results] == ['passed'] * len(programs), [r['feedback'] for r in results]


@pytest.mark.parametrize('lesson_id,label,code,result,expect', [(l, *w) for l in PART_2 for w in WRONG[l]],
                         ids=[f'{l}: {w[0]}' for l in PART_2 for w in WRONG[l]])
def test_wrong_programs_fail_with_the_right_rule(lesson_id, label, code, result, expect):
    answer = judge(lesson_id, code)
    assert answer['result'] == result, answer['feedback']
    if isinstance(expect, str):
        assert (answer['rule'], answer['failed']['reason']) == (expect, 'wrong_output')
        case = next(c for c in challenge(lesson_id).check.cases if expect.endswith('.case.' + c.id))
        assert case.description in answer['feedback']
    else:
        reason, error_type, line = expect
        assert (answer['rule'], answer['failed']['reason'], answer['failed']['error_type'], answer['failed']['line']) == (None, reason, error_type, line)


def test_one_loop_that_works_out_its_rows_passes_because_nesting_is_not_forced():
    # No construct rule: any correct program passes, and this one is shown under "Other ways".
    way = challenge('py.nested-loops').other_ways[1].code
    assert way.count('for ') == 1 and judge('py.nested-loops', way)['result'] == 'passed'


@pytest.mark.parametrize('lesson_id', PART_2)
def test_every_case_rule_has_a_wrong_sample_and_a_message(lesson_id):
    sampled = {expect for _, _, _, expect in WRONG[lesson_id] if isinstance(expect, str)}
    assert sampled == case_rules(lesson_id)
    for case in challenge(lesson_id).check.cases:
        assert case.description.strip() and len(case.description) <= 60


@pytest.mark.parametrize('lesson_id', PART_2)
def test_printing_the_expected_text_without_doing_the_work_fails(lesson_id):
    cases = challenge(lesson_id).check.cases
    visible = [c for c in cases if c.visibility == 'visible']
    fixed = [f'print({json.dumps(c.expected)})' for c in visible]
    table = {tuple(c.inputs): c.expected for c in visible}
    lookup = ('replies = []\nwhile True:\n    try:\n        replies.append(input())\n    except EOFError:\n        break\n'
              f'print({table!r}.get(tuple(replies), ""))')
    answers = judge_all(lesson_id, [*fixed, lookup])
    for answer in answers:
        assert answer['result'] == 'needs_work'
    assert answers[-1]['failed']['visibility'] == 'hidden' and answers[-1]['rule'] in case_rules(lesson_id)


@pytest.mark.parametrize('lesson_id', PART_2)
def test_every_tagged_hint_is_for_a_rule_or_error_this_lesson_can_report(lesson_id):
    tags = {tag for hint in challenge(lesson_id).error_hints for tag in hint.tags}
    errors = {expect[1] for _, _, _, expect in WRONG[lesson_id] if not isinstance(expect, str)}
    assert tags <= case_rules(lesson_id) | errors, tags - case_rules(lesson_id) - errors


# No hint, tagged hint or similar example, alone or together, passes the check

@pytest.mark.parametrize('lesson_id', PART_2)
def test_the_audit_finds_the_code_in_the_hints(lesson_id):
    pieces, _ = helpers.hint_pieces(lesson_id)
    expected = {
        'py.accumulate': {'distance = 0', 'distance = distance + miles'},
        'py.nested-loops': {'for shelf in range(1, shelves + 1):', 'for book in range(1, books + 1):'},
    }[lesson_id]
    assert expected <= set(pieces), pieces


def test_the_audit_builds_a_loop_inside_a_loop():
    program = helpers.assemble_nested(['for a in range(2):', 'for b in range(3):', 'print(a * b)', 'print(a)'])
    assert program == 'for a in range(2):\n    for b in range(3):\n        print(a * b)\n        print(a)'
    assert run_program(program, [])[1] is None
    # ... and a line can go below the loops, as a total's print does.
    assert helpers.assemble_nested(['for a in range(2):', 'print(a)', 'print(9)'], after=1) == 'for a in range(2):\n    print(a)\nprint(9)'


@pytest.mark.parametrize('lesson_id', PART_2)
def test_no_combination_of_hints_passes_the_check(lesson_id):
    programs = helpers.candidates(lesson_id)
    programs += [START[lesson_id] + p for p in programs]
    assert len(programs) > 10
    passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
    assert passing == []


RENAMED = {
    'py.accumulate': {'distance': 'total', 'miles': 'points', 'gold': 'total', 'day': 'game'},
    'py.nested-loops': {'shelf': 'row', 'shelves': 'rows', 'book': 'column', 'books': 'columns', 'hour': 'row', 'minute': 'column'},
}


@pytest.mark.parametrize('lesson_id', PART_2)
def test_the_hints_with_the_challenges_own_names_still_do_not_pass(lesson_id):
    task = challenge(lesson_id)
    names = RENAMED[lesson_id]
    pieces = [helpers.renamed(p, names) for text in [*task.hints, *(h.text for h in task.error_hints)] for p in helpers.fragments(text)]
    example = helpers.renamed(task.similar_example.code, names)
    start = START[lesson_id]
    programs = {start + example}
    for size in range(1, len(pieces) + 1):
        for chosen in itertools.combinations(pieces, size):
            for body in helpers.assemblies(chosen):
                programs.update({start + body, start + body + '\n' + example})
    programs = sorted(programs)
    passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
    assert passing == []


def test_the_audit_catches_a_hint_that_spells_out_the_nested_loops():
    # Control: a hint that writes the whole walk out is found, and it passes once the replies are read.
    leak = ('Write total = 0 then for row in range(1, rows + 1): then for column in range(1, columns + 1): '
            'then print(row * column) then total = total + row * column then print(total)')
    pieces = helpers.fragments(leak)
    programs = sorted(MAP + body for body in helpers.assemblies(pieces))
    assert any(r['result'] == 'passed' for r in judge_all('py.nested-loops', programs))


# Hidden expected output never reaches the browser

@pytest.mark.parametrize('lesson_id', PART_2)
def test_no_answer_holds_a_hidden_expected_output(lesson_id):
    client = TestClient(app)
    plan = client.get(f'/api/checks/{lesson_id}').json()
    assert all(('expected' in case) == (case['visibility'] == 'visible') for case in plan['cases'])
    answers = [client.get(path).text for path in ('/api/catalog', '/api/lessons', '/api/units/py.u03/lessons', f'/api/checks/{lesson_id}')]
    for _, code, _, _ in WRONG[lesson_id]:
        runs = [r.model_dump() for r in run(LESSONS[lesson_id], code)]
        answers.append(client.post('/api/check', json={'lesson_id': lesson_id, 'code': code, 'output': runs[0]['output'], 'runs': runs}, headers=HEADERS).text)
    visible = {json.dumps(c.expected) for c in challenge(lesson_id).check.cases if c.visibility == 'visible'}
    for case in challenge(lesson_id).check.cases:
        value = json.dumps(case.expected)
        if case.visibility == 'hidden' and value not in visible:
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
    client.cookies.set('session', helpers.sign_in_student(), domain='testserver.local', path='/')
    for lesson_id in PART_2:
        assert helpers.attempt(client, lesson_id, WRONG[lesson_id][0][1])['result'] != 'passed'
    assert client.get('/api/awards').json()['xp'] == 0
    for _ in range(2):
        for lesson_id in PART_2:
            assert helpers.attempt(client, lesson_id, REFERENCE[lesson_id])['result'] == 'passed'
    awards = client.get('/api/awards').json()
    assert awards['xp'] == 200 and awards['completed'] == PART_2
    assert [b['title'] for b in awards['badges']] == ['Tally keeper', 'Map reader']
    with Session(engine) as db:
        assert sorted((a.task_id, a.task_version, a.xp) for a in db.scalars(select(XpAward))) == sorted((f'{i}.challenge', 1, 100) for i in PART_2)
        assert db.scalar(select(func.count()).select_from(BadgeAward)) == 2


# The home page, once the unit is finished

ALL_RELEASED = [l for c in helpers.CATALOG.courses for u in c.units if u.status == 'released' for l in u.lessons]


def test_the_home_recommendation_after_unit_3_says_unit_4_is_not_written_yet():
    r = part1.recommendation_after(ALL_RELEASED)
    assert r['kind'] == 'caught_up' and r['lesson'] is None
    assert r['notes'][0] == 'Python Foundations unit 4, Keep track of a world, is next on your path. Its lessons are not written yet.'
    assert 'more lessons on the way' not in json.dumps(r)
    # Partway through unit 3: continue it.
    r = part1.recommendation_after([l for l in ALL_RELEASED if l != 'py.nested-loops'])
    assert (r['kind'], r['unit'], r['lesson']) == ('continue', 'py.u03', 'py.nested-loops')


# The answers the browser tests use are the real API's

def by_label(lesson_id, label):
    return next(w[1] for w in WRONG[lesson_id] if w[0] == label)


SCENARIOS = [
    ('accumulate passed', 'py.accumulate', REFERENCE['py.accumulate'], None),
    ('accumulate needs_work', 'py.accumulate', by_label('py.accumulate', 'the total goes back to 0 inside the loop'), None),
    ('accumulate counter from 1', 'py.accumulate', by_label('py.accumulate', 'the counter starts at 1'), None),
    ('accumulate hidden', 'py.accumulate', by_label('py.accumulate', 'contrived: // that still prints a float'), None),
    ('accumulate zero division', 'py.accumulate', by_label('py.accumulate', 'divides by the empty rounds'), None),
    ('accumulate out of replies', 'py.accumulate', by_label('py.accumulate', 'asks for one round too many'), None),
    ('accumulate endless loop', 'py.accumulate', ROUNDS + 'while True:\n    pass\n', 'timeout'),
    ('accumulate unsupported', 'py.accumulate', 'import turtle\n' + REFERENCE['py.accumulate'], 'unsupported'),
    ('nested passed', 'py.nested-loops', REFERENCE['py.nested-loops'], None),
    ('nested needs_work', 'py.nested-loops', by_label('py.nested-loops', 'the loops are the wrong way round'), None),
    ('nested inner not reset', 'py.nested-loops', by_label('py.nested-loops', 'the inner counter does not start again'), None),
    ('nested hidden', 'py.nested-loops', by_label('py.nested-loops', 'contrived: never more than 3 rows'), None),
    ('nested indentation error', 'py.nested-loops', by_label('py.nested-loops', 'an inner loop with no indent'), None),
    ('nested prints for ever', 'py.nested-loops', by_label('py.nested-loops', 'the inner counter never moves: prints for ever'), None),
    ('nested endless loop', 'py.nested-loops', MAP + 'while True:\n    pass\n', 'timeout'),
    ('nested unsupported', 'py.nested-loops', 'import turtle\n' + REFERENCE['py.nested-loops'], 'unsupported'),
]


def build_recordings():
    client = TestClient(app)
    recorded = {'catalog': client.get('/api/catalog').json(),
                'units': {'py.u03': client.get('/api/units/py.u03/lessons').json()},
                'plans': {i: client.get(f'/api/checks/{i}').json() for i in PART_2},
                'recommendation': part1.recommendation_after(ALL_RELEASED),
                'scenarios': []}
    for name, lesson_id, code, kind in SCENARIOS:
        runs = None
        if kind == 'timeout':
            runs = helpers.stopped(lesson_id, 'timeout')
        elif kind == 'unsupported':
            runs = helpers.stopped(lesson_id, 'error', 'error', error_type='ModuleNotFoundError', line=1)
        s = helpers.scenario(name, lesson_id, code, runs)
        s['response'] = client.post('/api/check', json=s['request'], headers=HEADERS).json()
        recorded['scenarios'].append(s)
    return recorded


def test_the_recorded_answers_are_the_real_apis():
    recorded = build_recordings()
    if os.environ.get('WRITE_UNIT3_RECORDINGS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded
    results = {s['name']: s['response'] for s in recorded['scenarios']}
    for lesson in ('accumulate', 'nested'):
        assert results[f'{lesson} passed']['result'] == 'passed' and results[f'{lesson} needs_work']['result'] == 'needs_work'
        assert results[f'{lesson} endless loop']['result'] == 'execution_error' and results[f'{lesson} unsupported']['result'] == 'unsupported'
    assert results['accumulate out of replies']['failed']['reason'] == 'missing_input'
    assert results['nested prints for ever']['failed']['reason'] == 'output_limit'

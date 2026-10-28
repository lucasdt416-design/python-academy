"""Python unit 2, part 1 (EDU-04): py.arithmetic, py.int-float and py.convert-input.

Each challenge is a browser check (ENG-03). The browser runs the learner's code once per case and the
API compares what it printed; here tests/case_runner.py plays the browser's part for the programs
written in this file and in the content files (samples, hints, reference solutions), and the real
judge (app.browser_checks.judge) decides. See docs/plan/browser-checks.md and lesson-feedback.md.

frontend/tests/fixtures/unit2-api.json holds the API's answers that the unit 2 browser tests mock;
test_the_recorded_answers_are_the_real_apis proves they are exactly what the API says. To rewrite it
after a deliberate content change: WRITE_UNIT2_RECORDINGS=1 python -m pytest -q tests/test_unit2_lessons.py
"""
import os
import tempfile
os.environ.setdefault('DATABASE_URL', 'sqlite:///' + tempfile.mktemp(suffix='.db'))
os.environ.setdefault('SESSION_SECRET', 'test-secret-that-is-at-least-thirty-two-characters')
import ast
import base64
import itertools
import json
import re
import secrets
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import browser_checks, content, sessions
from app.db import Base, BadgeAward, User, UserSession, XpAward
from app.main import app, engine
from case_runner import reports, run, run_program

CATALOG, LESSONS = content.load()
UNIT_2 = ['py.arithmetic', 'py.int-float', 'py.convert-input']
PART_2 = ['py.compare', 'py.boolean-logic', 'py.elif']  # the rest of py.u02 (part 2: tests/test_unit2_part2.py)
HEADERS = {'origin': 'http://localhost:3000'}
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/unit2-api.json'


def judge(lesson_id, code):
    lesson = LESSONS[lesson_id]
    return browser_checks.judge(lesson, code, run(lesson, code))


def judge_all(lesson_id, programs):
    lesson = LESSONS[lesson_id]
    programs = list(programs)
    return [browser_checks.judge(lesson, code, found) for code, found in zip(programs, reports(lesson, programs, timeout=120))]


def challenge(lesson_id):
    return LESSONS[lesson_id].task('challenge')


def case_rules(lesson_id):
    return {f'{lesson_id}.case.{case.id}' for case in challenge(lesson_id).check.cases}


# A trusted reference solution for each challenge (build.md section 12: "execute all trusted reference
# solutions in the intended runtime"). The content's "other ways" are checked too, below.
REFERENCE = {
    'py.arithmetic': 'coins = int(input("How many coins? "))\nfriends = int(input("How many friends? "))\nprint(coins // friends)\nprint(coins % friends)\n',
    'py.int-float': 'first = int(input("First score? "))\nsecond = int(input("Second score? "))\naverage = (first + second) / 2\nprint(average)\nprint(int(average))\n',
    'py.convert-input': 'score = int(input("Score? "))\npoints = input("Points? ")\nif points == "":\n    points = "0"\npoints = int(points)\nprint(score + points)\nprint(score - points)\n',
}

# Different, still correct programs a learner might write: a check must accept them (build.md section 4).
CREATIVE = {
    'py.arithmetic': [
        'coins = int(input())\nfriends = int(input())\nprint(int(coins / friends))\nprint(coins - friends * int(coins / friends))',
        'c = int(input("Coins? "))\nf = int(input("Friends? "))\nprint(c // f, c % f, sep="\\n")',
        '# my own names\ntreasure = int(input("How big is the chest? "))\nparty = int(input("How many in the party? "))\neach = treasure // party\nspare = treasure - each * party\nprint(each)\nprint(spare)',
    ],
    'py.int-float': [
        'first = int(input())\nsecond = int(input())\nprint(first / 2 + second / 2)\nprint(int(first / 2 + second / 2))',
        'a = int(input("A? "))\nb = int(input("B? "))\nmean = (a + b) / 2\nprint(mean)\nwhole = int(mean)\nprint(whole)',
        'first = float(input())\nsecond = float(input())\nprint((first + second) / 2)\nprint(int((first + second) / 2))',
    ],
    'py.convert-input': [
        'score = int(input())\nreply = input()\nif reply == "":\n    points = 0\nelse:\n    points = int(reply)\nprint(score + points)\nprint(score - points)',
        'score = int(input("Score? "))\npoints = input("Points? ")\nif points != "":\n    points = int(points)\nelse:\n    points = 0\nsolved = score + points\nmissed = score - points\nprint(solved)\nprint(missed)',
        'score = int(input())\npoints = int(input() or 0)\nprint(score + points)\nprint(score - points)',
    ],
}

STARTER_LINES = {
    'py.arithmetic': 'coins = int(input("How many coins? "))\nfriends = int(input("How many friends? "))\n',
    'py.int-float': 'first = int(input("First score? "))\nsecond = int(input("Second score? "))\n',
    'py.convert-input': '',
}

# Wrong programs, each with the result it must get and the rule (for wrong output) or the reason and
# error type. Together they give every case rule a sample, hidden cases included. Some are contrived on
# purpose ("contrived:"), to show that a particular hidden case really catches something.
WRONG = {
    'py.arithmetic': [
        ('uses / for the share', 'print(coins / friends)\nprint(coins % friends)', 'needs_work', 'py.arithmetic.case.even'),
        ('words on the line', 'print("Each friend gets", coins // friends)\nprint(coins % friends)', 'needs_work', 'py.arithmetic.case.even'),
        ('lines in the wrong order', 'print(coins % friends)\nprint(coins // friends)', 'needs_work', 'py.arithmetic.case.even'),
        ('hard-codes the first chest', 'print(3)\nprint(2)', 'needs_work', 'py.arithmetic.case.exact'),
        ('rounds the share', 'print(round(coins / friends))\nprint(coins % friends)', 'needs_work', 'py.arithmetic.case.fewer'),
        ('answers only the visible chests', 'if coins == 17:\n    print(3)\n    print(2)\nif coins == 20:\n    print(5)\n    print(0)\nif coins == 3:\n    print(0)\n    print(3)', 'needs_work', 'py.arithmetic.case.big'),
        ('contrived: one friend gets nothing', 'share = coins // friends\nif friends == 1:\n    share = 0\nprint(share)\nprint(coins % friends)', 'needs_work', 'py.arithmetic.case.one-friend'),
        ('a misspelt name', 'print(coin // friends)\nprint(coins % friends)', 'execution_error', ('error', 'NameError', 3)),
        ('a number joined to text', 'print("Share: " + coins // friends)', 'execution_error', ('error', 'TypeError', 3)),
        ('divides by zero', 'print(coins // (friends - friends))', 'execution_error', ('error', 'ZeroDivisionError', 3)),
        ('asks for a third reply', 'extra = input("And? ")\nprint(coins // friends)\nprint(coins % friends)', 'needs_work', ('missing_input', 'EOFError', 3)),
        ('a module the browser does not have', 'import pygame\nprint(coins // friends)\nprint(coins % friends)', 'unsupported', ('unsupported', 'ModuleNotFoundError', 3)),
    ],
    'py.int-float': [
        ('divides only the second score', 'average = first + second / 2\nprint(average)\nprint(int(average))', 'needs_work', 'py.int-float.case.half'),
        ('// on the first line', 'print((first + second) // 2)\nprint((first + second) // 2)', 'needs_work', 'py.int-float.case.half'),
        ('rounds instead of cutting off', 'average = (first + second) / 2\nprint(average)\nprint(round(average))', 'needs_work', 'py.int-float.case.half'),
        ('drops .0 from a whole average', 'average = (first + second) / 2\nif average == int(average):\n    print(int(average))\nelse:\n    print(average)\nprint(int(average))', 'needs_work', 'py.int-float.case.whole'),
        ('// for the whole part', 'average = (first + second) / 2\nprint(average)\nprint((first + second) // 2)', 'needs_work', 'py.int-float.case.negative'),
        ('answers only the visible scores', 'if first == 7:\n    print(7.5)\n    print(7)\nif first == 6:\n    print(7.0)\n    print(7)\nif first == -3:\n    print(-0.5)\n    print(0)', 'needs_work', 'py.int-float.case.high'),
        ('equal scores printed as they are', 'if first == second:\n    print(first)\n    print(first)\nelse:\n    print((first + second) / 2)\n    print(int((first + second) / 2))', 'needs_work', 'py.int-float.case.equal'),
        ('a number joined to text', 'print("Average: " + (first + second) / 2)', 'execution_error', ('error', 'TypeError', 3)),
        ('a misspelt name', 'average = (first + secnd) / 2\nprint(average)', 'execution_error', ('error', 'NameError', 3)),
    ],
    'py.convert-input': [
        ('replies left as text', 'score = input("Score? ")\npoints = input("Points? ")\nprint(score + points)\nprint(score - points)', 'execution_error', ('error', 'TypeError', 4)),
        ('no check for an empty reply', 'score = int(input("Score? "))\npoints = int(input("Points? "))\nprint(score + points)\nprint(score - points)', 'execution_error', ('error', 'ValueError', 2)),
        ('lines in the wrong order', 'score = int(input())\npoints = int(input() or "0")\nprint(score - points)\nprint(score + points)', 'needs_work', 'py.convert-input.case.solved-missed'),
        ('float() instead of int()', 'score = float(input())\npoints = float(input() or "0")\nprint(score + points)\nprint(score - points)', 'needs_work', 'py.convert-input.case.solved-missed'),
        ('stops the score at zero', 'score = int(input())\npoints = int(input() or "0")\nprint(score + points)\nmissed = score - points\nif missed < 0:\n    missed = 0\nprint(missed)', 'needs_work', 'py.convert-input.case.below-zero'),
        ('an empty reply counted as 1', 'score = int(input())\npoints = int(input() or "1")\nprint(score + points)\nprint(score - points)', 'needs_work', 'py.convert-input.case.no-points'),
        ('answers only the visible replies', 'score = input()\npoints = input()\nif score == "10":\n    print(13)\n    print(7)\nif score == "5":\n    print(13)\n    print(-3)\nif score == "6":\n    print(6)\n    print(6)', 'needs_work', 'py.convert-input.case.large'),
        ('contrived: a score of zero means no game', 'score = int(input())\npoints = int(input() or "0")\nif score == 0:\n    print(points)\n    print(points)\nelse:\n    print(score + points)\n    print(score - points)', 'needs_work', 'py.convert-input.case.from-zero'),
        ('asks for a third reply', 'score = int(input())\npoints = int(input() or "0")\nname = input()\nprint(score + points)\nprint(score - points)', 'needs_work', ('missing_input', 'EOFError', 3)),
        ('a misspelt name', 'score = int(input())\npoints = int(input() or "0")\nprint(scor + points)', 'execution_error', ('error', 'NameError', 3)),
    ],
}


def wrong_program(lesson_id, body):
    """Unit 2's first two starters already ask for the numbers, so those samples follow the starter's lines."""
    return STARTER_LINES[lesson_id] + body


# The unit and its lessons

def test_part_1_is_the_first_three_lessons_of_unit_2_in_order():
    py = next(c for c in CATALOG.courses if c.id == 'py')
    unit = next(u for u in py.units if u.id == 'py.u02')
    assert unit.status == 'released' and unit.lessons[:3] == UNIT_2 and unit.lessons[3:] == PART_2


@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_each_lesson_is_a_browser_check_with_visible_and_hidden_cases(lesson_id):
    lesson = LESSONS[lesson_id]
    task = challenge(lesson_id)
    assert (lesson.course, lesson.unit, lesson.version) == ('py', 'py.u02', 1)
    assert (task.validator.id, task.validator.version, task.version) == ('browser-tests', 1, 1)
    assert task.check.time_limit_ms == 3000  # the existing 3-second limit
    visible = [c for c in task.check.cases if c.visibility == 'visible']
    hidden = [c for c in task.check.cases if c.visibility == 'hidden']
    assert len(visible) >= 3 and len(hidden) >= 2
    # Browser checks name their rules by case; content messages belong to the unit 1 checker.
    assert task.messages == []
    assert len(task.hints) == 3 and task.similar_example and len(task.other_ways) >= 2
    assert lesson.badge.category == 'practice' and lesson.badge.version == 1
    # Exact-output checks: the prompt says to print just the numbers, so wording is never judged.
    assert 'Print just the two numbers.' in task.prompt


def test_badges_are_new_and_one_per_lesson():
    badges = [LESSONS[i].badge.id for i in UNIT_2]
    assert badges == ['py.badge.treasure-counter', 'py.badge.score-keeper', 'py.badge.riddle-scorer']
    unit_1 = {LESSONS[i].badge.id for i in content.LEGACY_LESSON_IDS}
    assert not unit_1 & set(badges)


def test_support_fades_across_the_three_lessons():
    # Lessons 1 and 2 hand over the input lines; lesson 3 leaves the learner a comment outline only.
    assert 'int(input(' in challenge('py.arithmetic').starter and 'int(input(' in challenge('py.int-float').starter
    starter = challenge('py.convert-input').starter
    assert all(line.startswith('#') for line in starter.splitlines()) and 'input(' not in starter


# What the cards say is what Python does

@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_every_worked_example_prints_what_its_card_shows(lesson_id):
    example = LESSONS[lesson_id].task('example')
    output, error = run_program(example.code, example.inputs)
    assert (output.rstrip('\n'), error) == (example.output, None)


CLAIMS = [
    # (where, code, replies, what the card says it prints)
    ('arithmetic discover', 'print(3 + 4)\nprint(17 // 5)\nprint(17 % 5)', [], '7\n3\n2'),
    ('arithmetic predict answer and why', 'coins = 14\nprint(coins % 5)\nprint(coins // 5)\nprint(coins / 5)', [], '4\n2\n2.8'),
    ('arithmetic example note', 'print(4 * 10 + 13)', [], '53'),
    ('arithmetic similar example', challenge('py.arithmetic').similar_example.code, [], '11'),
    ('int-float discover', 'print(6 / 3)\nprint(2 + 0.5)\nprint(int(3.9))\nprint(int(-2.5))\nprint(0.1 + 0.2)', [], '2.0\n2.5\n3\n-2\n0.30000000000000004'),
    ('int-float predict answer', 'print(int(7.9))', [], '7'),
    ('int-float guided', 'print(10 / 2)\nprint(8 // 2)', [], '5.0\n4'),
    ('int-float similar example', challenge('py.int-float').similar_example.code, [], '6.5'),
    ('int-float hint about -3 and 2', 'print((-3 + 2) / 2)\nprint(int((-3 + 2) / 2))\nprint((-3 + 2) // 2)', [], '-0.5\n0\n-1'),
    ('int-float hint about 11.0', 'print(7 + 8 / 2)', [], '11.0'),
    ('convert-input discover', 'print("5" + "5")\nprint(int("12"))\nprint(float("2.5"))', [], '55\n12\n2.5'),
    ('convert-input example, empty toll', LESSONS['py.convert-input'].task('example').code, ['20', ''], '20'),
    ('convert-input similar example, empty reply', challenge('py.convert-input').similar_example.code, [''], '2'),
]


@pytest.mark.parametrize('where,code,replies,shown', CLAIMS, ids=[c[0] for c in CLAIMS])
def test_what_the_cards_say_python_prints_is_what_it_prints(where, code, replies, shown):
    assert run_program(code, replies) == (shown + '\n', None)


def test_the_predict_answers_are_right():
    for lesson_id, code, replies in [('py.arithmetic', 'coins = 14\nprint(coins % 5)', []), ('py.int-float', 'print(int(7.9))', [])]:
        predict = LESSONS[lesson_id].task('predict')
        assert run_program(code, replies) == (predict.options[predict.answer] + '\n', None)
    # "ten" in letters stops int() with a ValueError on line 2 of the example.
    predict = LESSONS['py.convert-input'].task('predict')
    assert predict.options[predict.answer] == 'Python stops with a ValueError' and 'line 2' in predict.why
    lesson = LESSONS['py.convert-input']
    found = reports(lesson, [lesson.task('example').code])[0]
    assert found[0].status == 'ok'
    ten = run_program(lesson.task('example').code, ['ten', '5'])
    assert ten == ('', 'ValueError')


def test_the_example_is_not_the_challenge():
    # Worked examples use a different context from the challenge (lesson-feedback.md section 8, rule 2).
    for lesson_id in UNIT_2:
        example = LESSONS[lesson_id].task('example').code
        for program in (example, STARTER_LINES[lesson_id] + example):
            assert judge(lesson_id, program)['result'] != 'passed'


# Correct programs pass, wrong ones fail with the right rule

@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_reference_creative_and_other_ways_all_pass(lesson_id):
    programs = [REFERENCE[lesson_id], *CREATIVE[lesson_id], *(way.code for way in challenge(lesson_id).other_ways)]
    results = judge_all(lesson_id, programs)
    assert [r['result'] for r in results] == ['passed'] * len(programs), [r['feedback'] for r in results]
    hidden = sum(c.visibility == 'hidden' for c in challenge(lesson_id).check.cases)
    assert results[0]['feedback'].startswith(f'Your program printed the expected output for all 5 test cases, including {hidden} hidden cases.')


@pytest.mark.parametrize('lesson_id,label,body,result,expect', [(l, *w) for l in UNIT_2 for w in WRONG[l]],
                         ids=[f'{l}: {w[0]}' for l in UNIT_2 for w in WRONG[l]])
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


@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_every_case_rule_has_a_wrong_sample_and_a_message(lesson_id):
    sampled = {expect for _, _, _, expect in WRONG[lesson_id] if isinstance(expect, str)}
    assert sampled == case_rules(lesson_id)
    # The message for a case rule is the judge's sentence built from the case's description.
    for case in challenge(lesson_id).check.cases:
        assert case.description.strip() and len(case.description) <= 60


@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_printing_the_expected_text_without_doing_the_work_fails(lesson_id):
    cases = challenge(lesson_id).check.cases
    visible = [c for c in cases if c.visibility == 'visible']
    # Print one visible case's answer whatever the replies are.
    fixed = [f'print({json.dumps(c.expected)})' for c in visible]
    # Look up every visible case's answer by its replies: right on all of them, wrong on the hidden ones.
    table = {tuple(c.inputs): c.expected for c in visible}
    lookup = f'replies = tuple(input() for _ in range({len(visible[0].inputs)}))\nprint({table!r}.get(replies, ""))'
    for answer in judge_all(lesson_id, [*fixed, lookup]):
        assert answer['result'] == 'needs_work'
    assert answer['failed']['visibility'] == 'hidden' and answer['rule'] in case_rules(lesson_id)
    assert 'a hidden test case' in answer['feedback']


@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_every_tagged_hint_is_for_a_rule_or_error_this_lesson_can_report(lesson_id):
    tags = {tag for hint in challenge(lesson_id).error_hints for tag in hint.tags}
    errors = {expect[1] for _, _, _, expect in WRONG[lesson_id] if not isinstance(expect, str)}
    reported = case_rules(lesson_id) | errors
    assert tags <= reported, tags - reported


# No hint, tagged hint or similar example, alone or together, passes the check

def fragments(text):
    """Every piece of Python written out in a hint: the longest runs of words that parse as one assignment
    or call, and block headers such as `if reply == "":`."""
    tokens = [m for m in re.finditer(r'\S+', text)]
    found = []
    for i in range(len(tokens)):
        for j in range(len(tokens) - 1, i - 1, -1):
            piece = text[tokens[i].start():tokens[j].end()].rstrip('.,;')
            if piece.endswith(':'):
                # elif and else only parse after an if block.
                before = 'if True:\n    pass\n' if piece.startswith(('elif', 'else')) else ''
                try:
                    ast.parse(before + piece + '\n    pass')
                except SyntaxError:
                    continue
                found.append(piece)
                break
            if not re.search(r'[=(+\-*/%]', piece):
                continue
            try:
                tree = ast.parse(piece)
            except SyntaxError:
                continue
            # Only statements that do something: an assignment, or a call such as print(...). Prose can
            # parse too ("means / was", "print(coins). Joining", "names: total = …", "…, then").
            node = tree.body[0] if len(tree.body) == 1 else None
            value = getattr(node, 'value', None)
            if not (isinstance(node, ast.Assign) or isinstance(node, ast.Expr) and isinstance(value, ast.Call)) \
                    or isinstance(value, ast.Tuple) or any(isinstance(n, ast.Attribute) for n in ast.walk(tree)):
                continue
            found.append(piece)
            break
    # Keep the longest: drop a piece that sits inside another one.
    return [p for p in dict.fromkeys(found) if not any(p != q and p in q for q in found)]


def hint_pieces(lesson_id):
    task = challenge(lesson_id)
    texts = [*task.hints, *(h.text for h in task.error_hints)]
    return list(dict.fromkeys(p for text in texts for p in fragments(text))), task.similar_example.code.splitlines()


def assemble(chosen, greedy=False):
    """One program from hint pieces in order: a line after a block header is indented, except elif and
    else, which close the block above them (with pass if it was empty). greedy: every line after a header
    stays inside its block until the next header, so a loop body can have several lines (unit 3)."""
    lines, inside = [], False
    for piece in chosen:
        header_above = bool(lines) and lines[-1].endswith(':')
        if piece.startswith(('elif', 'else')):
            if header_above:
                lines.append('    pass')
            lines.append(piece)
            inside = True
        elif piece.endswith(':'):
            if header_above:
                lines.append('    pass')
            lines.append(piece)
            inside = True
        else:
            lines.append(('    ' if header_above or (greedy and inside) else '') + piece)
    if lines[-1].endswith(':'):
        lines.append('    pass')
    return '\n'.join(lines)


def candidates(lesson_id):
    """Programs made only from what the hints show, with and without the starter."""
    pieces, example = hint_pieces(lesson_id)
    starter = challenge(lesson_id).starter
    programs = set()
    for size in range(1, len(pieces) + 1):
        for chosen in itertools.combinations(pieces, size):
            for body in {assemble(chosen), assemble(chosen, greedy=True)}:
                programs.update({body, starter + body})
    whole = '\n'.join(example)
    programs.update({whole, starter + whole, starter + '\n'.join(pieces) + '\n' + whole})
    return sorted(programs)


@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_the_audit_finds_the_code_in_the_hints(lesson_id):
    pieces, _ = hint_pieces(lesson_id)
    expected = {
        'py.arithmetic': {'print(cookies // children)', 'print(coins)'},
        'py.int-float': {'total = low + high', 'print(total)'},
        'py.convert-input': {'reply = input("Coins? ")', 'if reply == "":', 'coins = int(reply)'},
    }[lesson_id]
    assert expected <= set(pieces), pieces


@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_no_combination_of_hints_passes_the_check(lesson_id):
    programs = candidates(lesson_id)
    assert len(programs) > 10
    passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
    assert passing == []


# The approach and the similar example use other names on purpose. With those names swapped for the
# challenge's own, they must still leave the learner something to do.
RENAMED = {
    'py.arithmetic': {'cookies': 'coins', 'children': 'friends', 'start': 'coins', 'later': 'coins', '12': 'friends', '14': '0'},
    'py.int-float': {'low': 'first', 'high': 'second', 'morning': 'first', 'evening': 'second', 'middle': 'average'},
    'py.convert-input': {'reply': 'points', 'coins': 'points', 'lanterns': 'points', 'Coins': 'Points', 'Lanterns': 'Points', '"1"': '"0"', '* 2': '+ 0'},
}


def renamed(text, names):
    return re.sub('|'.join(re.escape(k) if not k[0].isalpha() else rf'\b{re.escape(k)}\b' for k in sorted(names, key=len, reverse=True)), lambda m: names[m.group(0)], text)


@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_the_hints_with_the_challenges_own_names_still_do_not_pass(lesson_id):
    task = challenge(lesson_id)
    names = RENAMED[lesson_id]
    pieces = [renamed(p, names) for text in [*task.hints, *(h.text for h in task.error_hints)] for p in fragments(text)]
    example = renamed(task.similar_example.code, names)
    programs = {task.starter + example, STARTER_LINES[lesson_id] + example}
    for size in range(1, len(pieces) + 1):
        for chosen in itertools.combinations(pieces, size):
            for body in {assemble(chosen), assemble(chosen, greedy=True)}:
                programs.update({task.starter + body, task.starter + body + '\n' + example})
    programs = sorted(programs)
    passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
    assert passing == []


def test_the_audit_catches_a_hint_that_gives_the_answer():
    # Control: an approach hint that spells out the whole program is found and passes the check.
    leak = 'Write print(coins // friends) and then print(coins % friends).'
    pieces = fragments(leak)
    assert pieces == ['print(coins // friends)', 'print(coins % friends)']
    program = challenge('py.arithmetic').starter + '\n'.join(pieces)
    assert judge('py.arithmetic', program)['result'] == 'passed'


# Hidden expected output never reaches the browser

def hidden_values(lesson_id):
    """A hidden case's expected output as it would appear in a JSON answer, and its distinctive lines."""
    values = set()
    for case in challenge(lesson_id).check.cases:
        if case.visibility == 'hidden':
            values.add(json.dumps(case.expected))
            values.update(line for line in case.expected.splitlines() if len(line.strip('-')) >= 3)
    return values


@pytest.fixture
def client(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    test_client = TestClient(app)
    test_client.cookies.clear()
    return test_client


@pytest.mark.parametrize('lesson_id', UNIT_2)
def test_no_answer_holds_a_hidden_expected_output(client, lesson_id):
    plan = client.get(f'/api/checks/{lesson_id}').json()
    assert all(('expected' in case) == (case['visibility'] == 'visible') for case in plan['cases'])
    answers = [client.get(path).text for path in ('/api/catalog', '/api/lessons', '/api/units/py.u02/lessons', f'/api/checks/{lesson_id}')]
    for _, _, body, _, _ in [(lesson_id, *w) for w in WRONG[lesson_id]]:
        code = wrong_program(lesson_id, body)
        runs = [r.model_dump() for r in run(LESSONS[lesson_id], code)]
        answers.append(client.post('/api/check', json={'lesson_id': lesson_id, 'code': code, 'output': runs[0]['output'], 'runs': runs}, headers=HEADERS).text)
    for value in hidden_values(lesson_id):
        for answer in answers:
            assert value not in answer, value


# Lessons per unit, and unit 1 untouched

def test_unit_2_is_served_on_its_own_and_unit_1_is_unchanged(client):
    lessons = client.get('/api/units/py.u02/lessons').json()
    assert [(l['id'], l['course'], l['unit'], l['check']) for l in lessons] == [(i, 'py', 'py.u02', 'browser-tests') for i in UNIT_2 + PART_2]
    assert 'cases' not in json.dumps(lessons)
    legacy = json.loads((Path(__file__).with_name('fixtures') / 'legacy_lessons_v1.json').read_text())
    assert client.get('/api/lessons').json() == legacy
    assert [l['id'] for l in client.get('/api/units/py.u01/lessons').json()] == [l['id'] for l in legacy]


# XP and badges, once each

def sign_in_student():
    with Session(engine) as db:
        user = User(subject='u2', email='learner@example.com', role='student')
        db.add(user)
        db.flush()
        token, now = secrets.token_urlsafe(32), int(sessions.clock())
        db.add(UserSession(id=sessions.digest(token), user_id=user.id, created=now, last_seen=now, expires=now + sessions.ABSOLUTE))
        db.commit()
    return TimestampSigner(os.environ['SESSION_SECRET']).sign(base64.b64encode(json.dumps({'sid': token}).encode())).decode()


def attempt(client, lesson_id, code):
    runs = [r.model_dump() for r in run(LESSONS[lesson_id], code)]
    return client.post('/api/attempts', json={'lesson_id': lesson_id, 'code': code, 'output': runs[0]['output'], 'runs': runs}, headers=HEADERS).json()


def test_each_lesson_awards_100_xp_and_its_badge_once(client):
    client.cookies.set('session', sign_in_student(), domain='testserver.local', path='/')
    for lesson_id in UNIT_2:
        assert attempt(client, lesson_id, wrong_program(lesson_id, WRONG[lesson_id][0][1]))['result'] != 'passed'
    assert client.get('/api/awards').json() == {'xp': 0, 'completed': [], 'badges': []}
    for _ in range(2):
        for lesson_id in UNIT_2:
            assert attempt(client, lesson_id, REFERENCE[lesson_id])['result'] == 'passed'
    awards = client.get('/api/awards').json()
    assert awards['xp'] == 300 and awards['completed'] == UNIT_2
    assert [b['title'] for b in awards['badges']] == ['Treasure counter', 'Score keeper', 'Riddle scorer']
    with Session(engine) as db:
        assert sorted((a.task_id, a.task_version, a.xp) for a in db.scalars(select(XpAward))) == sorted((f'{i}.challenge', 1, 100) for i in UNIT_2)
        assert db.scalar(select(func.count()).select_from(BadgeAward)) == 3
    assert client.get('/api/progress').json() == UNIT_2


# The answers the browser tests use are the real API's

def scenario(name, lesson_id, code, runs=None):
    """One recorded judge request and answer. runs: given only for what a CPython run cannot show (a
    timeout, or a module Pyodide lacks); otherwise the program is run like the browser runs it."""
    runs = runs or [r.model_dump() for r in run(LESSONS[lesson_id], code)]
    return {'name': name, 'request': {'lesson_id': lesson_id, 'code': code, 'output': runs[0]['output'], 'inputs': [], 'runs': runs}}


def stopped(lesson_id, first, rest='not_run', **report):
    ids = [c.id for c in challenge(lesson_id).check.cases]
    return [{'id': ids[0], 'status': first, 'output': '', 'error_type': None, 'line': None, **report}] + \
           [{'id': i, 'status': rest, 'output': '', 'error_type': None, 'line': None, **(report if rest == first else {})} for i in ids[1:]]


SCENARIOS = [
    ('arithmetic passed', 'py.arithmetic', REFERENCE['py.arithmetic'], None),
    ('arithmetic needs_work', 'py.arithmetic', STARTER_LINES['py.arithmetic'] + 'print(coins / friends)\nprint(coins % friends)\n', None),
    ('arithmetic hidden', 'py.arithmetic', STARTER_LINES['py.arithmetic'] + WRONG['py.arithmetic'][5][1] + '\n', None),
    ('arithmetic name error', 'py.arithmetic', STARTER_LINES['py.arithmetic'] + 'print(coin // friends)\nprint(coins % friends)\n', None),
    ('arithmetic endless loop', 'py.arithmetic', STARTER_LINES['py.arithmetic'] + 'while True:\n    pass\n', 'timeout'),
    ('arithmetic unsupported', 'py.arithmetic', 'import turtle\n' + REFERENCE['py.arithmetic'], 'unsupported'),
    ('int-float passed', 'py.int-float', REFERENCE['py.int-float'], None),
    ('int-float needs_work', 'py.int-float', STARTER_LINES['py.int-float'] + 'average = first + second / 2\nprint(average)\nprint(int(average))\n', None),
    ('int-float negative', 'py.int-float', STARTER_LINES['py.int-float'] + 'average = (first + second) / 2\nprint(average)\nprint((first + second) // 2)\n', None),
    ('int-float type error', 'py.int-float', STARTER_LINES['py.int-float'] + 'print("Average: " + (first + second) / 2)\n', None),
    ('int-float endless loop', 'py.int-float', STARTER_LINES['py.int-float'] + 'while first > 0:\n    pass\n', 'timeout'),
    ('int-float unsupported', 'py.int-float', 'import turtle\n' + REFERENCE['py.int-float'], 'unsupported'),
    ('convert-input passed', 'py.convert-input', REFERENCE['py.convert-input'], None),
    ('convert-input needs_work', 'py.convert-input', 'score = int(input())\npoints = int(input() or "1")\nprint(score + points)\nprint(score - points)\n', None),
    ('convert-input value error', 'py.convert-input', 'score = int(input("Score? "))\npoints = int(input("Points? "))\nprint(score + points)\nprint(score - points)\n', None),
    ('convert-input endless loop', 'py.convert-input', 'score = int(input())\nwhile score:\n    pass\n', 'timeout'),
    ('convert-input unsupported', 'py.convert-input', 'import turtle\n' + REFERENCE['py.convert-input'], 'unsupported'),
]


def build_recordings():
    client = TestClient(app)
    recorded = {'catalog': client.get('/api/catalog').json(),
                'units': {'py.u02': client.get('/api/units/py.u02/lessons').json()},
                'plans': {i: client.get(f'/api/checks/{i}').json() for i in UNIT_2},
                'scenarios': []}
    for name, lesson_id, code, kind in SCENARIOS:
        runs = None
        if kind == 'timeout':
            # The browser stops the first case at 3 seconds and runs no more (the runner terminates the worker).
            runs = stopped(lesson_id, 'timeout')
        elif kind == 'unsupported':
            # Pyodide has no turtle module; every case stops on line 1.
            runs = stopped(lesson_id, 'error', 'error', error_type='ModuleNotFoundError', line=1)
        s = scenario(name, lesson_id, code, runs)
        s['response'] = client.post('/api/check', json=s['request'], headers=HEADERS).json()
        recorded['scenarios'].append(s)
    return recorded


def test_the_recorded_answers_are_the_real_apis(client):
    recorded = build_recordings()
    if os.environ.get('WRITE_UNIT2_RECORDINGS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded
    results = {s['name']: s['response']['result'] for s in recorded['scenarios']}
    for lesson in ('arithmetic', 'int-float', 'convert-input'):
        assert results[f'{lesson} passed'] == 'passed' and results[f'{lesson} needs_work'] == 'needs_work'
        assert results[f'{lesson} endless loop'] == 'execution_error' and results[f'{lesson} unsupported'] == 'unsupported'

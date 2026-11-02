"""Python unit 2, part 2 (EDU-04): py.compare, py.boolean-logic and py.elif, and the unit being complete.

The same checks as part 1 (tests/test_unit2_lessons.py, whose helpers this file reuses): the browser's
part is played by tests/case_runner.py for the programs written here and in the content files, and the
real judge decides. Each challenge forces the idea it teaches through behaviour, never a construct rule:
joining the "close" limits with or fails a guess 3 away, and separate ifs fail an exactly right guess,
which is also close.

frontend/tests/fixtures/unit2-part2-api.json holds the API's answers that the part 2 browser tests mock.
To rewrite it after a deliberate content change: WRITE_UNIT2_RECORDINGS=1 python -m pytest -q tests/test_unit2_part2.py
"""
import itertools
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import test_unit2_lessons as part1
from app import browser_checks, content
from app.main import app
from case_runner import reports, run, run_program

LESSONS = part1.LESSONS
UNIT_2 = part1.UNIT_2 + part1.PART_2
PART_2 = part1.PART_2
HEADERS = part1.HEADERS
RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/unit2-part2-api.json'
challenge, case_rules, judge, judge_all = part1.challenge, part1.case_rules, part1.judge, part1.judge_all

# The two replies, as lessons 5 and 6 leave the learner to ask for them.
ASK = 'secret = int(input("Secret number? "))\nguess = int(input("Your guess? "))\n'

REFERENCE = {
    'py.compare': ASK + 'print(guess > secret)\nprint(guess < secret)\nprint(guess == secret)\n',
    'py.boolean-logic': ASK + 'close = guess >= secret - 2 and guess <= secret + 2\nprint(close)\nprint(guess < 1 or guess > 100)\nprint(not close)\n',
    'py.elif': ASK + 'if guess == secret:\n    print(10)\nelif guess >= secret - 2 and guess <= secret + 2:\n    print(5)\nelif guess >= secret - 10 and guess <= secret + 10:\n    print(1)\nelse:\n    print(0)\n',
}

CREATIVE = {
    'py.compare': [
        ASK + 'print(not guess <= secret)\nprint(not guess >= secret)\nprint(not guess != secret)',
        'a = int(input())\nb = int(input())\ndifference = b - a\nprint(difference > 0)\nprint(difference < 0)\nprint(difference == 0)',
        ASK + 'if guess > secret:\n    print(True)\nelse:\n    print(False)\nif guess < secret:\n    print(True)\nelse:\n    print(False)\nprint(guess == secret)',
    ],
    'py.boolean-logic': [
        ASK + 'print(abs(guess - secret) <= 2)\nprint(not 1 <= guess <= 100)\nprint(abs(guess - secret) > 2)',
        'secret = int(input())\nguess = int(input())\nlow = secret - 2\nhigh = secret + 2\nclose = guess >= low and guess <= high\nprint(close)\nout = guess < 1 or guess > 100\nprint(out)\nprint(not close)',
        ASK + 'print(guess - secret in (-2, -1, 0, 1, 2))\nprint(guess not in range(1, 101))\nprint(not (secret - 2 <= guess <= secret + 2))',
    ],
    'py.elif': [
        ASK + 'distance = guess - secret\nif distance == 0:\n    print(10)\nelif -2 <= distance <= 2:\n    print(5)\nelif -10 <= distance <= 10:\n    print(1)\nelse:\n    print(0)',
        ASK + 'distance = abs(guess - secret)\nif distance > 10:\n    print(0)\nelif distance > 2:\n    print(1)\nelif distance > 0:\n    print(5)\nelse:\n    print(10)',
        ASK + 'if guess == secret:\n    print(10)\nelse:\n    if abs(guess - secret) <= 2:\n        print(5)\n    else:\n        if abs(guess - secret) <= 10:\n            print(1)\n        else:\n            print(0)',
    ],
}

# Lesson 4's starter asks for the two numbers; its samples follow those lines. Lessons 5 and 6 leave
# that to the learner, so their samples are whole programs.
STARTER_LINES = {'py.compare': ASK, 'py.boolean-logic': '', 'py.elif': ''}

WRONG = {
    'py.compare': [
        ('>= for too high', 'print(guess >= secret)\nprint(guess < secret)\nprint(guess == secret)', 'needs_work', 'py.compare.case.equal'),
        ('lines in the wrong order', 'print(guess < secret)\nprint(guess > secret)\nprint(guess == secret)', 'needs_work', 'py.compare.case.higher'),
        ('hard-codes the first guess', 'print(True)\nprint(False)\nprint(False)', 'needs_work', 'py.compare.case.lower'),
        ('contrived: off by one', 'print(guess > secret + 1)\nprint(guess < secret)\nprint(guess == secret)', 'needs_work', 'py.compare.case.one-above'),
        ('contrived: compares sizes without the sign', 'print(abs(guess) > abs(secret))\nprint(abs(guess) < abs(secret))\nprint(guess == secret)', 'needs_work', 'py.compare.case.below-zero'),
        ('compares with the visible secret', 'print(guess > 7)\nprint(guess < 7)\nprint(guess == 7)', 'needs_work', 'py.compare.case.large'),
        ('= inside print()', 'print(guess = secret)', 'execution_error', ('error', 'TypeError', 3)),
        ('a comparison written backwards', 'print(guess => secret)', 'execution_error', ('error', 'SyntaxError', 3)),
        ('a misspelt name', 'print(gues > secret)', 'execution_error', ('error', 'NameError', 3)),
        ('asks for a third reply', 'extra = input()\nprint(guess > secret)', 'needs_work', ('missing_input', 'EOFError', 3)),
        ('a module the browser does not have', 'import pygame\nprint(guess > secret)', 'unsupported', ('unsupported', 'ModuleNotFoundError', 3)),
    ],
    'py.boolean-logic': [
        ('or joins the close limits', ASK + 'print(guess >= secret - 2 or guess <= secret + 2)\nprint(guess < 1 or guess > 100)\nprint(not (guess >= secret - 2 or guess <= secret + 2))', 'needs_work', 'py.boolean-logic.case.just-outside'),
        ('< and > leave out the edges', ASK + 'close = guess > secret - 2 and guess < secret + 2\nprint(close)\nprint(guess < 1 or guess > 100)\nprint(not close)', 'needs_work', 'py.boolean-logic.case.edge-above'),
        ('contrived: lower limit off by one', ASK + 'close = guess >= secret - 1 and guess <= secret + 2\nprint(close)\nprint(guess < 1 or guess > 100)\nprint(not close)', 'needs_work', 'py.boolean-logic.case.edge-below'),
        ('and for out of range', ASK + 'close = guess >= secret - 2 and guess <= secret + 2\nprint(close)\nprint(guess < 1 and guess > 100)\nprint(not close)', 'needs_work', 'py.boolean-logic.case.below-range'),
        ('top limit off by one', ASK + 'close = guess >= secret - 2 and guess <= secret + 2\nprint(close)\nprint(guess < 1 or guess > 101)\nprint(not close)', 'needs_work', 'py.boolean-logic.case.above-range'),
        ('100 counted as out of range', ASK + 'close = guess >= secret - 2 and guess <= secret + 2\nprint(close)\nprint(guess < 1 or guess >= 100)\nprint(not close)', 'needs_work', 'py.boolean-logic.case.top-edge'),
        ('1 counted as out of range', ASK + 'close = guess >= secret - 2 and guess <= secret + 2\nprint(close)\nprint(guess <= 1 or guess > 100)\nprint(not close)', 'needs_work', 'py.boolean-logic.case.bottom-edge'),
        ('hard-codes the first guess', ASK + 'print(True)\nprint(False)\nprint(False)', 'needs_work', 'py.boolean-logic.case.just-outside'),
        ('a half comparison after and', ASK + 'print(guess >= 1 and <= 100)', 'execution_error', ('error', 'SyntaxError', 3)),
        ('a misspelt name', ASK + 'print(gues >= secret - 2)', 'execution_error', ('error', 'NameError', 3)),
    ],
    'py.elif': [
        ('separate ifs that each print', ASK + 'if guess == secret:\n    print(10)\nif guess >= secret - 2 and guess <= secret + 2:\n    print(5)\nif guess >= secret - 10 and guess <= secret + 10:\n    print(1)\nelse:\n    print(0)', 'needs_work', 'py.elif.case.exact'),
        ('separate ifs that each set the points', ASK + 'points = 0\nif guess == secret:\n    points = 10\nif guess >= secret - 2 and guess <= secret + 2:\n    points = 5\nif guess >= secret - 10 and guess <= secret + 10:\n    points = 1\nprint(points)', 'needs_work', 'py.elif.case.exact'),
        ('the widest check first', ASK + 'if guess >= secret - 10 and guess <= secret + 10:\n    print(1)\nelif guess >= secret - 2 and guess <= secret + 2:\n    print(5)\nelif guess == secret:\n    print(10)\nelse:\n    print(0)', 'needs_work', 'py.elif.case.exact'),
        ('no branch for close', ASK + 'if guess == secret:\n    print(10)\nelif guess >= secret - 10 and guess <= secret + 10:\n    print(1)\nelse:\n    print(0)', 'needs_work', 'py.elif.case.close'),
        ('contrived: within 10 only above', ASK + 'if guess == secret:\n    print(10)\nelif guess >= secret - 2 and guess <= secret + 2:\n    print(5)\nelif guess >= secret and guess <= secret + 10:\n    print(1)\nelse:\n    print(0)', 'needs_work', 'py.elif.case.near'),
        ('< leaves out 10 away', ASK + 'if guess == secret:\n    print(10)\nelif guess >= secret - 2 and guess <= secret + 2:\n    print(5)\nelif guess > secret - 10 and guess < secret + 10:\n    print(1)\nelse:\n    print(0)', 'needs_work', 'py.elif.case.near-edge'),
        ('11 away still scores', ASK + 'if guess == secret:\n    print(10)\nelif guess >= secret - 2 and guess <= secret + 2:\n    print(5)\nelif guess >= secret - 11 and guess <= secret + 11:\n    print(1)\nelse:\n    print(0)', 'needs_work', 'py.elif.case.far'),
        ('close only above the secret', ASK + 'if guess == secret:\n    print(10)\nelif guess >= secret and guess <= secret + 2:\n    print(5)\nelif guess >= secret - 10 and guess <= secret + 10:\n    print(1)\nelse:\n    print(0)', 'needs_work', 'py.elif.case.close-below'),
        ('within 10 with no lower limit', ASK + 'if guess == secret:\n    print(10)\nelif guess >= secret - 2 and guess <= secret + 2:\n    print(5)\nelif guess <= secret + 10:\n    print(1)\nelse:\n    print(0)', 'needs_work', 'py.elif.case.far-below'),
        ('answers only the visible guesses', ASK + 'if guess == 40:\n    print(10)\nelif guess == 42:\n    print(5)\nelif guess == 37 or guess == 50:\n    print(1)\nelif guess == 51:\n    print(0)', 'needs_work', 'py.elif.case.exact-again'),
        ('a missing colon', ASK + 'if guess == secret\n    print(10)', 'execution_error', ('error', 'SyntaxError', 3)),
        ('a block with no indent', ASK + 'if guess == secret:\nprint(10)', 'execution_error', ('error', 'IndentationError', 4)),
        ('a misspelt name', ASK + 'if gues == secret:\n    print(10)', 'execution_error', ('error', 'NameError', 3)),
    ],
}


def wrong_program(lesson_id, body):
    return STARTER_LINES[lesson_id] + body


# The unit, complete

def test_unit_2_is_complete_with_six_lessons_in_order():
    py = next(c for c in part1.CATALOG.courses if c.id == 'py')
    unit = next(u for u in py.units if u.id == 'py.u02')
    assert (unit.status, unit.lessons, unit.more_lessons_coming) == ('released', UNIT_2, False)
    assert 'come next' not in unit.summary and 'elif' in unit.summary
    # Unit 2 is not still being written (unit 3, released in parts, is: tests/test_unit3_lessons.py).
    assert [u.id for c in part1.CATALOG.courses for u in c.units if u.more_lessons_coming] == ['py.u03']


def test_the_catalog_says_which_units_are_complete():
    catalog = TestClient(app).get('/api/catalog').json()
    units = {u['id']: u['complete'] for c in catalog['courses'] for u in c['units']}
    assert units['py.u01'] is True and units['py.u02'] is True
    assert not any(complete for unit, complete in units.items() if unit not in ('py.u01', 'py.u02'))
    assert units['py.u03'] is False  # released, still being written


def test_more_lessons_coming_is_only_for_a_released_unit(tmp_path):
    root = tmp_path / 'content'
    import shutil
    shutil.copytree(content.CONTENT_DIR, root)
    data = json.loads((root / 'catalog.json').read_text())
    data['courses'][0]['units'][3]['more_lessons_coming'] = True  # py.u04, coming soon
    (root / 'catalog.json').write_text(json.dumps(data))
    with pytest.raises(content.ContentError, match='unit py.u04 is coming soon, so it cannot also have more lessons coming'):
        content.load(root)
    # On a released unit it is allowed, and the catalog then calls the unit not complete.
    data['courses'][0]['units'][3]['more_lessons_coming'] = False
    data['courses'][0]['units'][1]['more_lessons_coming'] = True
    (root / 'catalog.json').write_text(json.dumps(data))
    catalog, lessons = content.load(root)
    assert content.catalog_view(catalog, lessons)['courses'][0]['units'][1]['complete'] is False


@pytest.mark.parametrize('lesson_id', PART_2)
def test_each_lesson_is_a_browser_check_with_visible_and_hidden_cases(lesson_id):
    lesson = LESSONS[lesson_id]
    task = challenge(lesson_id)
    assert (lesson.course, lesson.unit, lesson.version) == ('py', 'py.u02', 1)
    assert (task.validator.id, task.validator.version, task.version) == ('browser-tests', 1, 1)
    assert task.check.time_limit_ms == 3000
    visible = [c for c in task.check.cases if c.visibility == 'visible']
    hidden = [c for c in task.check.cases if c.visibility == 'hidden']
    assert len(visible) >= 4 and len(hidden) >= 2
    assert task.messages == [] and task.check.require == [] and task.check.forbid == []
    assert len(task.hints) == 3 and task.similar_example and len(task.other_ways) >= 2
    assert lesson.badge.category == 'practice' and lesson.badge.version == 1
    # Output is True/False or a number, so wording is never judged.
    assert 'Print just the' in task.prompt


def test_badges_are_new_and_one_per_lesson():
    badges = [LESSONS[i].badge.id for i in PART_2]
    assert badges == ['py.badge.riddle-judge', 'py.badge.close-call', 'py.badge.fair-verdict']
    others = {LESSONS[i].badge.id for i in LESSONS if i not in PART_2}
    assert not others & set(badges)


def test_support_fades_across_the_three_lessons():
    assert 'int(input(' in challenge('py.compare').starter
    for lesson_id in ('py.boolean-logic', 'py.elif'):
        starter = challenge(lesson_id).starter
        assert all(line.startswith('#') for line in starter.splitlines()) and 'input(' not in starter
    assert len(challenge('py.elif').starter.splitlines()) <= len(challenge('py.boolean-logic').starter.splitlines())


# What the cards say is what Python does

@pytest.mark.parametrize('lesson_id', PART_2)
def test_every_worked_example_prints_what_its_card_shows(lesson_id):
    example = LESSONS[lesson_id].task('example')
    assert run_program(example.code, example.inputs) == (example.output + '\n', None)


def with_value(lesson_id, name, value):
    """The lesson's worked example with one variable changed, as the predict card asks."""
    code = LESSONS[lesson_id].task('example').code
    return code.replace(f'{name} = ', f'{name} = {value}  # was ', 1)


CLAIMS = [
    ('compare discover', 'print(7 > 5)\nprint(7 < 5)\nprint(5 <= 5)\nprint(5 < 5)', [], 'True\nFalse\nTrue\nFalse'),
    ('compare predict and why', 'oil = 3\nprint(oil >= 3)\nprint(oil > 3)', [], 'True\nFalse'),
    ('compare similar example', challenge('py.compare').similar_example.code, [], 'False\nTrue'),
    ('compare hint about 7 and 9', 'secret = 7\nguess = 9\nprint(guess > secret)\nprint(guess < secret)\nprint(guess == secret)', [], 'True\nFalse\nFalse'),
    ('boolean discover', 'print(True and False)\nprint(True or False)\nprint(not True)', [], 'False\nTrue\nFalse'),
    ('boolean predict', with_value('py.boolean-logic', 'travellers', 2), [], 'True\nFalse\nFalse'),
    ('boolean similar example', challenge('py.boolean-logic').similar_example.code, [], 'True\nTrue'),
    ('boolean hint: or is always True here', 'print(53 >= 48 or 53 <= 52)\nprint(abs(53 - 50), abs(52 - 50))', [], 'True\n3 2'),
    ('elif predict', with_value('py.elif', 'temperature', 30), [], 'light cloak'),
    ('elif example note with 30', with_value('py.elif', 'temperature', 30).replace('elif', 'if'), [], 'light cloak\nwool cloak'),
    ('elif similar example', challenge('py.elif').similar_example.code, [], '4'),
    ('elif hints: how far away', 'print(abs(42 - 40), abs(50 - 40), abs(51 - 40))', [], '2 10 11'),
]


@pytest.mark.parametrize('where,code,replies,shown', CLAIMS, ids=[c[0] for c in CLAIMS])
def test_what_the_cards_say_python_prints_is_what_it_prints(where, code, replies, shown):
    assert run_program(code, replies) == (shown + '\n', None)


def test_the_predict_answers_are_right():
    for lesson_id, name, value, line in [('py.compare', 'oil', 3, 0), ('py.boolean-logic', 'travellers', 2, 0), ('py.elif', 'temperature', 30, None)]:
        predict = LESSONS[lesson_id].task('predict')
        output, error = run_program(with_value(lesson_id, name, value), [])
        assert error is None
        shown = output.splitlines()[line] if line is not None else ', then '.join(output.splitlines())
        assert shown == predict.options[predict.answer], lesson_id


def test_the_error_hints_describe_real_errors():
    assert run_program('guess = 1\nsecret = 1\nprint(guess = secret)', [])[1] == 'TypeError'
    assert run_program('guess = 1\nprint(guess >= 1 and <= 100)', [])[1] == 'SyntaxError'
    assert run_program('guess = 1\nprint(guess => 1)', [])[1] == 'SyntaxError'


def test_the_example_is_not_the_challenge():
    for lesson_id in PART_2:
        example = LESSONS[lesson_id].task('example').code
        for program in (example, ASK + example):
            assert judge(lesson_id, program)['result'] != 'passed'


# Correct programs pass, wrong ones fail with the right rule

@pytest.mark.parametrize('lesson_id', PART_2)
def test_reference_creative_and_other_ways_all_pass(lesson_id):
    programs = [REFERENCE[lesson_id], *CREATIVE[lesson_id], *(way.code for way in challenge(lesson_id).other_ways)]
    results = judge_all(lesson_id, programs)
    assert [r['result'] for r in results] == ['passed'] * len(programs), [r['feedback'] for r in results]


@pytest.mark.parametrize('lesson_id,label,body,result,expect', [(l, *w) for l in PART_2 for w in WRONG[l]],
                         ids=[f'{l}: {w[0]}' for l in PART_2 for w in WRONG[l]])
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


def test_separate_ifs_fail_where_elif_is_taught_without_a_construct_rule():
    # The behaviour forces elif: an exactly right guess is also close and within 10.
    for label in ('separate ifs that each print', 'separate ifs that each set the points'):
        body = next(w[1] for w in WRONG['py.elif'] if w[0] == label)
        assert judge('py.elif', body)['rule'] == 'py.elif.case.exact'
    # ... but separate ifs written so that only one score is printed are a correct answer (other ways).
    assert judge('py.elif', challenge('py.elif').other_ways[1].code)['result'] == 'passed'


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
    lookup = f'replies = tuple(input() for _ in range({len(visible[0].inputs)}))\nprint({table!r}.get(replies, ""))'
    for answer in judge_all(lesson_id, [*fixed, lookup]):
        assert answer['result'] == 'needs_work'
    assert answer['failed']['visibility'] == 'hidden' and answer['rule'] in case_rules(lesson_id)


@pytest.mark.parametrize('lesson_id', PART_2)
def test_every_tagged_hint_is_for_a_rule_or_error_this_lesson_can_report(lesson_id):
    tags = {tag for hint in challenge(lesson_id).error_hints for tag in hint.tags}
    errors = {expect[1] for _, _, _, expect in WRONG[lesson_id] if not isinstance(expect, str)}
    assert tags <= case_rules(lesson_id) | errors, tags - case_rules(lesson_id) - errors


# No hint, tagged hint or similar example, alone or together, passes the check

@pytest.mark.parametrize('lesson_id', PART_2)
def test_the_audit_finds_the_code_in_the_hints(lesson_id):
    pieces, _ = part1.hint_pieces(lesson_id)
    expected = {
        'py.compare': {'print(height > limit)'},
        'py.boolean-logic': {'print(depth >= low and depth <= high)'},
        'py.elif': {'if age >= 18:', 'elif age >= 13:', 'else:'},
    }[lesson_id]
    assert expected <= set(pieces), pieces


@pytest.mark.parametrize('lesson_id', PART_2)
def test_no_combination_of_hints_passes_the_check(lesson_id):
    programs = part1.candidates(lesson_id)
    # Lessons 5 and 6 have no input lines in the starter: try the hints after the replies are read too.
    programs += [ASK + p for p in programs]
    assert len(programs) > 10
    passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
    assert passing == []


RENAMED = {
    'py.compare': {'height': 'guess', 'limit': 'secret', 'speed': 'guess'},
    'py.boolean-logic': {'depth': 'guess', 'low': 'secret - 2', 'high': 'secret + 2', 'temperature': 'guess', '15': 'secret - 2', '25': 'secret + 2'},
    'py.elif': {'age': 'guess', '18': 'secret', '13': 'secret - 2', '5': 'secret'},
}


@pytest.mark.parametrize('lesson_id', PART_2)
def test_the_hints_with_the_challenges_own_names_still_do_not_pass(lesson_id):
    task = challenge(lesson_id)
    names = RENAMED[lesson_id]
    pieces = [part1.renamed(p, names) for text in [*task.hints, *(h.text for h in task.error_hints)] for p in part1.fragments(text)]
    example = part1.renamed(task.similar_example.code, names)
    programs = {ASK + example}
    for size in range(1, len(pieces) + 1):
        for chosen in itertools.combinations(pieces, size):
            for body in {part1.assemble(chosen), part1.assemble(chosen, greedy=True)}:
                programs.update({ASK + body, ASK + body + '\n' + example})
    programs = sorted(programs)
    passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
    assert passing == []


# Hidden expected output never reaches the browser

@pytest.mark.parametrize('lesson_id', PART_2)
def test_no_answer_holds_a_hidden_expected_output(lesson_id):
    client = TestClient(app)
    plan = client.get(f'/api/checks/{lesson_id}').json()
    assert all(('expected' in case) == (case['visibility'] == 'visible') for case in plan['cases'])
    answers = [client.get(path).text for path in ('/api/catalog', '/api/lessons', '/api/units/py.u02/lessons', f'/api/checks/{lesson_id}')]
    for _, body, _, _ in WRONG[lesson_id]:
        code = wrong_program(lesson_id, body)
        runs = [r.model_dump() for r in run(LESSONS[lesson_id], code)]
        answers.append(client.post('/api/check', json={'lesson_id': lesson_id, 'code': code, 'output': runs[0]['output'], 'runs': runs}, headers=HEADERS).text)
    # Part 2's hidden outputs are short (True/False lines, small numbers): look for the whole output as JSON.
    hidden = [json.dumps(c.expected) for c in challenge(lesson_id).check.cases if c.visibility == 'hidden']
    visible = {json.dumps(c.expected) for c in challenge(lesson_id).check.cases if c.visibility == 'visible'}
    for value in hidden:
        if value in visible:
            continue  # the same output as a visible case is not a secret
        for answer in answers:
            assert value not in answer, value


def test_hidden_outputs_that_match_a_visible_one_are_still_not_sent_for_the_hidden_case():
    # Several hidden cases print the same as a visible one (for example True, False, False). The plan
    # still leaves out every hidden case's expected output.
    for lesson_id in PART_2:
        plan = TestClient(app).get(f'/api/checks/{lesson_id}').json()
        assert all('expected' not in c for c in plan['cases'] if c['visibility'] == 'hidden')


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
    for lesson_id in PART_2:
        assert part1.attempt(client, lesson_id, wrong_program(lesson_id, WRONG[lesson_id][0][1]))['result'] != 'passed'
    assert client.get('/api/awards').json()['xp'] == 0
    for _ in range(2):
        for lesson_id in PART_2:
            assert part1.attempt(client, lesson_id, REFERENCE[lesson_id])['result'] == 'passed'
    awards = client.get('/api/awards').json()
    assert awards['xp'] == 300 and awards['completed'] == PART_2
    assert [b['title'] for b in awards['badges']] == ['Riddle judge', 'Close call', 'Fair verdict']
    with Session(engine) as db:
        assert sorted((a.task_id, a.task_version, a.xp) for a in db.scalars(select(XpAward))) == sorted((f'{i}.challenge', 1, 100) for i in PART_2)
        assert db.scalar(select(func.count()).select_from(BadgeAward)) == 3


# The answers the browser tests use are the real API's

SCENARIOS = [
    ('compare passed', 'py.compare', REFERENCE['py.compare'], None),
    ('compare needs_work', 'py.compare', ASK + 'print(guess >= secret)\nprint(guess < secret)\nprint(guess == secret)\n', None),
    ('compare hidden', 'py.compare', ASK + 'print(guess > 7)\nprint(guess < 7)\nprint(guess == 7)\n', None),
    ('compare name error', 'py.compare', ASK + 'print(gues > secret)\n', None),
    ('compare endless loop', 'py.compare', ASK + 'while True:\n    pass\n', 'timeout'),
    ('compare unsupported', 'py.compare', 'import turtle\n' + REFERENCE['py.compare'], 'unsupported'),
    ('boolean passed', 'py.boolean-logic', REFERENCE['py.boolean-logic'], None),
    ('boolean needs_work', 'py.boolean-logic', WRONG['py.boolean-logic'][0][1] + '\n', None),
    ('boolean syntax error', 'py.boolean-logic', ASK + 'print(guess >= 1 and <= 100)\n', None),
    ('boolean endless loop', 'py.boolean-logic', ASK + 'while True:\n    pass\n', 'timeout'),
    ('boolean unsupported', 'py.boolean-logic', 'import turtle\n' + REFERENCE['py.boolean-logic'], 'unsupported'),
    ('elif passed', 'py.elif', REFERENCE['py.elif'], None),
    ('elif needs_work', 'py.elif', WRONG['py.elif'][0][1] + '\n', None),
    ('elif indentation error', 'py.elif', ASK + 'if guess == secret:\nprint(10)\n', None),
    ('elif endless loop', 'py.elif', ASK + 'while True:\n    pass\n', 'timeout'),
    ('elif unsupported', 'py.elif', 'import turtle\n' + REFERENCE['py.elif'], 'unsupported'),
]


def build_recordings():
    client = TestClient(app)
    recorded = {'catalog': client.get('/api/catalog').json(),
                'units': {'py.u02': client.get('/api/units/py.u02/lessons').json()},
                'plans': {i: client.get(f'/api/checks/{i}').json() for i in PART_2},
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


def test_the_recorded_answers_are_the_real_apis():
    recorded = build_recordings()
    if os.environ.get('WRITE_UNIT2_RECORDINGS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded
    results = {s['name']: s['response']['result'] for s in recorded['scenarios']}
    for lesson in ('compare', 'boolean', 'elif'):
        assert results[f'{lesson} passed'] == 'passed' and results[f'{lesson} needs_work'] == 'needs_work'
        assert results[f'{lesson} endless loop'] == 'execution_error' and results[f'{lesson} unsupported'] == 'unsupported'

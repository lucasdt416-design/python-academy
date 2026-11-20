"""The checks every browser-check lesson from unit 4 on gets (the lesson stage template, master run Part 7).

Units 2 and 3 wrote these tests out per unit (tests/test_unit2_lessons.py, test_unit3_*.py). From unit 4
there are many more lessons, so each unit's test file describes its lessons as data (a Spec) and
`make_tests` turns that into the same tests: what the cards say Python prints is what it prints; the
reference, creative programs and "Other ways" pass; wrong programs fail with the rule that names their
mistake; every case rule has a wrong sample; printing the visible answers without doing the work fails;
no hint, tagged hint or similar example, alone or combined, and with the challenge's own names, passes;
hidden expected output never reaches the browser; each lesson awards 100 XP and its badge once.

The hint audit uses fragments() from unit 2, extended here so a method call such as pack.append(item)
counts as code: unit 4 is where methods start.
"""
import ast
import itertools
import json
import re
from dataclasses import dataclass, field

import pytest
from fastapi.testclient import TestClient

import test_unit2_lessons as helpers
from app.main import app
from case_runner import reports, run, run_program

LESSONS, CATALOG = helpers.LESSONS, helpers.CATALOG
HEADERS = helpers.HEADERS
challenge, case_rules, judge, judge_all = helpers.challenge, helpers.case_rules, helpers.judge, helpers.judge_all


@dataclass
class Spec:
    start: str                      # the lines a learner writes first (replies read), used by the hint audit
    reference: str                  # a trusted correct program
    creative: list[str]             # other correct programs a learner might write
    wrong: list[tuple]              # (label, program, result, rule id or (reason, error type, line))
    renamed: dict[str, str]         # names in the hints and similar example -> the challenge's own names
    claims: list[tuple] = field(default_factory=list)  # (where, program, replies, what the card says it prints)
    modules: dict | None = None     # the learner's own files (ENG-08b) for the reference, creative and wrong programs


def fragments(text):
    """Unit 2's fragments(), plus method calls (pack.append(item), name.strip()) and lines that assign
    through an index or key (rooms["hall"] = "key")."""
    tokens = list(re.finditer(r'\S+', text))
    found = []
    for i in range(len(tokens)):
        for j in range(len(tokens) - 1, i - 1, -1):
            piece = text[tokens[i].start():tokens[j].end()].rstrip('.,;')
            if piece.endswith(':'):
                before = 'if True:\n    pass\n' if piece.startswith(('elif', 'else')) else 'try:\n    pass\n' if piece.startswith(('except', 'finally')) else ''
                try:
                    ast.parse(before + piece + '\n    pass')
                except SyntaxError:
                    continue
                found.append(piece)
                break
            if not re.search(r'[=(+\-*/%\[]', piece):
                continue
            try:
                tree = ast.parse(piece)
            except SyntaxError:
                continue
            node = tree.body[0] if len(tree.body) == 1 else None
            value = getattr(node, 'value', None)
            statement = isinstance(node, (ast.Assign, ast.AugAssign, ast.Return, ast.Raise, ast.Assert)) or isinstance(node, ast.Expr) and isinstance(value, ast.Call)
            if not statement or isinstance(value, ast.Tuple):
                continue
            # Prose such as "e.g." or "Note.Then" parses as an attribute; a real method call has a call.
            if any(isinstance(n, ast.Attribute) for n in ast.walk(tree)) and not re.search(r'\w\.\w+\(', piece):
                continue
            found.append(piece)
            break
    return [p for p in dict.fromkeys(found) if not any(p != q and p in q for q in found)]


def hint_pieces(lesson_id):
    task = challenge(lesson_id)
    texts = [*task.hints, *(h.text for h in task.error_hints)]
    return list(dict.fromkeys(p for text in texts for p in fragments(text))), task.similar_example.code


def programs_from(pieces, example, start):
    programs = {example, start + example}
    for size in range(1, min(len(pieces), 6) + 1):
        for chosen in itertools.combinations(pieces, size):
            for body in helpers.assemblies(list(chosen)):
                programs.update({body, start + body, start + body + '\n' + example})
    programs.add(start + '\n'.join(pieces) + '\n' + example)
    return sorted(programs)


def judge_with(lesson_id, programs, modules=None):
    """judge_all, with the learner's own files given (None: the challenge's starting files)."""
    lesson = LESSONS[lesson_id]
    programs = list(programs)
    from app import browser_checks
    return [browser_checks.judge(lesson, code, found) for code, found in zip(programs, reports(lesson, programs, timeout=120, modules=modules))]


def run_example(example):
    """The worked example, run as the Try it card runs it: its replies, files and the learner's own files."""
    from types import SimpleNamespace
    case = SimpleNamespace(id='once', inputs=list(example.inputs), seed=None, files=dict(example.files), reference=None, call=None)
    lesson = SimpleNamespace(task=lambda kind: SimpleNamespace(check=SimpleNamespace(cases=[case]), modules={}))
    report = reports(lesson, [example.code], modules=dict(example.modules))[0][0]
    return report.output, report.error_type


def sent(found):
    """Reports as the page sends them: returned is left out of a dump, so it is added back for call cases."""
    return [{**r.model_dump(), **({'returned': r.returned} if r.returned is not None else {})} for r in found]


def attempt(client, lesson_id, code, modules=None):
    runs = sent(reports(LESSONS[lesson_id], [code], modules=modules)[0])
    return client.post('/api/attempts', json={'lesson_id': lesson_id, 'code': code, 'output': runs[0]['output'], 'runs': runs}, headers=HEADERS).json()


def renamed(text, names):
    return helpers.renamed(text, names)


def released_unit(unit_id):
    py = next(c for c in CATALOG.courses if c.id == 'py')
    return next(u for u in py.units if u.id == unit_id)


def make_tests(unit_id, specs, badges):
    """The tests for these lessons, as module globals for pytest to collect. badges: the badge titles, in order."""
    ids = list(specs)

    def test_the_unit_is_released_with_these_lessons():
        unit = released_unit(unit_id)
        assert unit.status == 'released'
        assert unit.lessons[:len(ids)] == ids

    @pytest.mark.parametrize('lesson_id', ids)
    def test_each_lesson_is_a_browser_check_with_visible_and_hidden_cases(lesson_id):
        lesson, task = LESSONS[lesson_id], challenge(lesson_id)
        assert (lesson.course, lesson.unit) == ('py', unit_id)
        assert (task.validator.id, task.validator.version) == ('browser-tests', 1)
        visible = [c for c in task.check.cases if c.visibility == 'visible']
        hidden = [c for c in task.check.cases if c.visibility == 'hidden']
        assert len(visible) >= 2 and len(hidden) >= 1
        assert task.messages == [] and task.check.require == [] and task.check.forbid == []
        assert len(task.hints) == 3 and task.similar_example and len(task.other_ways) == 2
        assert lesson.badge.category == 'practice'
        for case in task.check.cases:
            assert case.description.strip() and len(case.description) <= 60

    def test_badges_are_new_and_one_per_lesson():
        assert [LESSONS[i].badge.title for i in ids] == badges
        others = {LESSONS[i].badge.id for i in LESSONS if i not in ids}
        assert not others & {LESSONS[i].badge.id for i in ids}
        assert len({LESSONS[i].badge.id for i in ids}) == len(ids)

    @pytest.mark.parametrize('lesson_id', ids)
    def test_the_worked_example_prints_what_its_card_shows(lesson_id):
        example = LESSONS[lesson_id].task('example')
        assert run_example(example) == (example.output + '\n', None)

    claims = [(i, *c) for i in ids for c in specs[i].claims]

    @pytest.mark.parametrize('lesson_id,where,code,replies,shown', claims, ids=[f'{c[0]}: {c[1]}' for c in claims])
    def test_what_the_cards_say_python_prints_is_what_it_prints(lesson_id, where, code, replies, shown):
        output, error = run_program(code, replies)
        if isinstance(shown, tuple):
            assert error == shown[0], output
        else:
            assert (output, error) == (shown + '\n' if shown else '', None)

    @pytest.mark.parametrize('lesson_id', ids)
    def test_the_predict_answer_is_one_of_its_options(lesson_id):
        predict = LESSONS[lesson_id].task('predict')
        assert 0 <= predict.answer < len(predict.options) and len(set(predict.options)) == len(predict.options)

    @pytest.mark.parametrize('lesson_id', ids)
    def test_the_example_is_not_the_challenge(lesson_id):
        code = LESSONS[lesson_id].task('example').code
        for program in (code, specs[lesson_id].start + code):
            assert judge(lesson_id, program)['result'] != 'passed'

    @pytest.mark.parametrize('lesson_id', ids)
    def test_reference_creative_and_other_ways_all_pass(lesson_id):
        mine = [specs[lesson_id].reference, *specs[lesson_id].creative]
        ways = [w.code for w in challenge(lesson_id).other_ways]
        programs = mine + ways
        results = judge_with(lesson_id, mine, specs[lesson_id].modules) + judge_all(lesson_id, ways)
        assert [r['result'] for r in results] == ['passed'] * len(programs), [(p, r['feedback']) for p, r in zip(programs, results) if r['result'] != 'passed']

    wrong = [(i, *w) for i in ids for w in specs[i].wrong]

    @pytest.mark.parametrize('lesson_id,label,code,result,expect', wrong, ids=[f'{w[0]}: {w[1]}' for w in wrong])
    def test_wrong_programs_fail_with_the_right_rule(lesson_id, label, code, result, expect):
        answer = judge_with(lesson_id, [code], specs[lesson_id].modules)[0]
        assert answer['result'] == result, answer['feedback']
        if isinstance(expect, str):
            assert answer['rule'] == expect, answer['feedback']
            case = next(c for c in challenge(lesson_id).check.cases if expect.endswith('.case.' + c.id))
            if not case.call:
                assert case.description in answer['feedback']
        else:
            reason, error_type, line = expect
            assert (answer['failed']['reason'], answer['failed'].get('error_type'), answer['failed'].get('line')) == (reason, error_type, line), answer

    @pytest.mark.parametrize('lesson_id', ids)
    def test_every_case_rule_has_a_wrong_sample(lesson_id):
        sampled = {e for _, _, _, e in specs[lesson_id].wrong if isinstance(e, str)}
        assert sampled == case_rules(lesson_id)

    @pytest.mark.parametrize('lesson_id', ids)
    def test_printing_the_visible_answers_without_doing_the_work_fails(lesson_id):
        cases = challenge(lesson_id).check.cases
        if any(c.call or c.reference for c in cases):
            pytest.skip('function and test cases: the call decides, not what the program prints')
        visible = [c for c in cases if c.visibility == 'visible']
        fixed = [f'print({json.dumps(c.expected)}, end="")' for c in visible]
        table = {tuple(c.inputs): c.expected for c in visible}
        lookup = ('replies = []\nwhile True:\n    try:\n        replies.append(input())\n    except EOFError:\n        break\n'
                  f'print({table!r}.get(tuple(replies), ""), end="")')
        for answer in judge_all(lesson_id, [*fixed, lookup]):
            assert answer['result'] == 'needs_work'

    @pytest.mark.parametrize('lesson_id', ids)
    def test_every_tagged_hint_is_for_a_rule_or_error_this_lesson_can_report(lesson_id):
        tags = {tag for hint in challenge(lesson_id).error_hints for tag in hint.tags}
        errors = {e[1] for _, _, _, e in specs[lesson_id].wrong if not isinstance(e, str)}
        assert tags <= case_rules(lesson_id) | errors, tags - case_rules(lesson_id) - errors

    @pytest.mark.parametrize('lesson_id', ids)
    def test_no_combination_of_hints_passes_the_check(lesson_id):
        pieces, example = hint_pieces(lesson_id)
        programs = programs_from(pieces, example, specs[lesson_id].start)
        assert len(programs) >= 3
        passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
        assert passing == []

    @pytest.mark.parametrize('lesson_id', ids)
    def test_the_hints_with_the_challenges_own_names_still_do_not_pass(lesson_id):
        pieces, example = hint_pieces(lesson_id)
        names = specs[lesson_id].renamed
        programs = programs_from([renamed(p, names) for p in pieces], renamed(example, names), specs[lesson_id].start)
        passing = [p for p, r in zip(programs, judge_all(lesson_id, programs)) if r['result'] == 'passed']
        assert passing == []

    @pytest.mark.parametrize('lesson_id', ids)
    def test_no_answer_holds_a_hidden_expected_output(lesson_id):
        client = TestClient(app)
        plan = client.get(f'/api/checks/{lesson_id}').json()
        for case in plan['cases']:
            if case['visibility'] == 'hidden':
                assert 'expected' not in case and 'returns' not in case and 'test_should' not in case
        answers = [client.get(p).text for p in ('/api/catalog', '/api/lessons', f'/api/units/{unit_id}/lessons', f'/api/checks/{lesson_id}')]
        for _, code, _, _ in specs[lesson_id].wrong[:8]:
            runs = sent(run(LESSONS[lesson_id], code))
            answers.append(client.post('/api/check', json={'lesson_id': lesson_id, 'code': code, 'output': runs[0]['output'], 'runs': runs}, headers=HEADERS).text)
        shown = {json.dumps(c.expected) for c in challenge(lesson_id).check.cases if c.visibility == 'visible'}
        for case in challenge(lesson_id).check.cases:
            if case.visibility == 'hidden' and case.expected and json.dumps(case.expected) not in shown and len(case.expected) > 3:
                for answer in answers:
                    assert json.dumps(case.expected) not in answer

    def test_each_lesson_awards_100_xp_and_its_badge_once(client):
        client.cookies.set('session', helpers.sign_in_student(), domain='testserver.local', path='/')
        for lesson_id in ids:
            assert attempt(client, lesson_id, specs[lesson_id].wrong[0][1])['result'] != 'passed'
        assert client.get('/api/awards').json()['xp'] == 0
        for _ in range(2):
            for lesson_id in ids:
                assert attempt(client, lesson_id, specs[lesson_id].reference, specs[lesson_id].modules)['result'] == 'passed', lesson_id
        awards = client.get('/api/awards').json()
        assert awards['xp'] == 100 * len(ids) and awards['completed'] == ids
        assert [b['title'] for b in awards['badges']] == badges

    return {name: fn for name, fn in locals().items() if name.startswith('test_')}

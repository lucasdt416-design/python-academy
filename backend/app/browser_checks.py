"""Judge browser behaviour checks (ENG-03, docs/plan/browser-checks.md).

The learner's browser runs their code in the Pyodide worker, once per check case, and reports what
each run printed or how it stopped. This module compares those reports with the content's expected
output and returns one of the result states. It parses the code to look for required or forbidden
constructs, but it never runs learner code.

Hidden cases: their expected output is only ever used here. Responses name a failing hidden case
by its description, which content validation keeps free of its inputs and expected output.
"""
import ast
from typing import Literal

from pydantic import BaseModel, Field

from .content import BROWSER_TESTS, CONSTRUCTS, OUTPUT_LIMIT
from .lesson_checks import SERVICE_ERROR

CALLS = {'input', 'print', 'int', 'float', 'str', 'range', 'len', 'eval', 'exec', 'open'}
# Errors that mean "this runtime cannot do that", not a learner mistake.
UNSUPPORTED = {'ModuleNotFoundError', 'ImportError'}


class CaseRun(BaseModel):
    """What the browser reports for one case. Python's error message is not sent: type and line are enough."""
    id: str = Field(max_length=80)
    # ok: finished. error: Python raised. timeout / output_limit: the page stopped it.
    # not_run: an earlier case was stopped. unavailable: Python could not start.
    status: Literal['ok', 'error', 'timeout', 'output_limit', 'not_run', 'unavailable']
    output: str = Field(default='', max_length=OUTPUT_LIMIT)
    error_type: str | None = Field(default=None, max_length=80, pattern=r'^[A-Za-z_][A-Za-z0-9_.]*$')
    line: int | None = Field(default=None, ge=1, le=100_000)


def applies(lesson):
    return lesson.task('challenge').validator.id == BROWSER_TESTS


def plan(lesson):
    """What the browser needs to run the check. Hidden cases come without their expected output."""
    challenge = lesson.task('challenge')
    return {
        'lesson_id': lesson.id, 'task_id': challenge.id, 'version': challenge.version,
        'time_limit_ms': challenge.check.time_limit_ms, 'output_limit': OUTPUT_LIMIT,
        'cases': [{'id': case.id, 'visibility': case.visibility, 'description': case.description, 'inputs': case.inputs,
                   **({'expected': case.expected} if case.visibility == 'visible' else {})}
                  for case in challenge.check.cases],
    }


def constructs(tree):
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.comprehension)):
            found.add('for')
        elif isinstance(node, ast.While):
            found.add('while')
        elif isinstance(node, ast.If):
            found.add('if')
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                found.add('elif')
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.add('def')
        elif isinstance(node, ast.Return):
            found.add('return')
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            found.add('import')
        elif isinstance(node, ast.JoinedStr):
            found.add('f-string')
        elif isinstance(node, (ast.List, ast.ListComp)):
            found.add('list')
        elif isinstance(node, (ast.Dict, ast.DictComp)):
            found.add('dict')
        elif isinstance(node, ast.Compare):
            found.add('comparison')
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in CALLS:
            found.add(node.func.id + '()')
    return found


def output_lines(text):
    """Lines as compared: Windows line endings, trailing spaces and trailing blank lines ignored."""
    lines = [line.rstrip() for line in text.replace('\r\n', '\n').split('\n')]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def first_difference(expected, actual):
    """(line number, expected line or None, actual line or None) of the first difference, or None."""
    want, got = output_lines(expected), output_lines(actual)
    for number in range(1, max(len(want), len(got)) + 1):
        a = want[number - 1] if number <= len(want) else None
        b = got[number - 1] if number <= len(got) else None
        if a != b:
            return number, a, b
    return None


def outcome(result, feedback, cases=(), failed=None, rule=None):
    # rule: for wrong output, <lesson>.case.<case id>, so the page can offer a hint tagged for it.
    return {'passed': result == 'passed', 'result': result, 'feedback': feedback, 'rule': rule,
            'assessment': 'browser_tests', 'cases': list(cases), 'failed': failed}


def judge(lesson, code, runs):
    """The result for the runs the browser reported. Never runs code."""
    check = lesson.task('challenge').check
    cases = {case.id: case for case in check.cases}
    runs = list(runs or [])
    if [run.id for run in runs] != list(cases) or any(run.status == 'unavailable' for run in runs):
        # Missing, extra or reordered cases: usually a page from before a content update.
        return outcome('service_error', SERVICE_ERROR)

    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return outcome('execution_error', f'Python cannot read line {error.lineno} yet. Check matching quotes, parentheses, colons and indentation.',
                       failed={'id': None, 'reason': 'error', 'error_type': type(error).__name__, 'line': error.lineno})
    used = constructs(tree)
    for name in check.forbid:
        if name in used:
            return outcome('needs_work', f'This task asks you not to use {CONSTRUCTS[name]} here.', failed={'id': None, 'reason': 'construct', 'construct': name})
    for name in check.require:
        if name not in used:
            return outcome('needs_work', f'This task asks you to use {CONSTRUCTS[name]}.', failed={'id': None, 'reason': 'construct', 'construct': name})

    statuses, problems = [], []
    for run in runs:
        case = cases[run.id]
        problem = None
        if run.status == 'ok':
            difference = first_difference(case.expected, run.output)
            if difference:
                problem = ('wrong_output', difference)
        elif run.status != 'not_run':
            problem = (run.status, None)
        statuses.append({'id': case.id, 'visibility': case.visibility,
                         'status': 'not_run' if run.status == 'not_run' else 'failed' if problem else 'passed'})
        if problem:
            problems.append((case, run, *problem))
    if not problems:
        if any(s['status'] == 'not_run' for s in statuses):
            return outcome('service_error', SERVICE_ERROR, statuses)
        hidden = sum(case.visibility == 'hidden' for case in check.cases)
        also = f', including {hidden} hidden {"case" if hidden == 1 else "cases"}' if hidden else ''
        return outcome('passed', f'Your program printed the expected output for all {len(runs)} test cases{also}. '
                                 'Read your code once more: could you explain each line to someone else?', statuses)

    # Report a visible case first when there is one: the learner can see its data.
    case, run, reason, difference = min(problems, key=lambda p: p[0].visibility == 'hidden')
    failed = {'id': case.id, 'visibility': case.visibility, 'description': case.description, 'reason': reason,
              'error_type': run.error_type, 'line': run.line}
    about = case.description
    if reason == 'wrong_output':
        if case.visibility == 'visible':
            number, want, got = difference
            failed.update(line_number=number, expected_line=want, actual_line=got)
            if got is None:
                message = f'For {about}, your program stopped printing before line {number}, which should be "{want}".'
            elif want is None:
                message = f'For {about}, your program printed an extra line {number}: "{got}".'
            else:
                message = f'For {about}, line {number} should be "{want}", but your program printed "{got}".'
        else:
            message = (f'Your program printed something different for {about} (a hidden test case). '
                       'Check that it works from the replies it is given, not from fixed values.')
        return outcome('needs_work', message, statuses, failed, rule=f'{lesson.id}.case.{case.id}')
    seconds = check.time_limit_ms / 1000
    if reason == 'timeout':
        return outcome('execution_error', f'Your program was still running after {seconds:g} seconds on {about}, so it was stopped. '
                                          'Check for a loop that never ends.', statuses, failed)
    if reason == 'output_limit':
        return outcome('execution_error', f'Your program printed more than {OUTPUT_LIMIT:,} characters on {about}, so it was stopped. '
                                          'Check for a loop that never ends.', statuses, failed)
    if run.error_type == 'EOFError':
        failed['reason'] = 'missing_input'
        return outcome('needs_work', f'Your program asked for more replies than {about} gives. Check how many times it calls input().', statuses, failed)
    if run.error_type in UNSUPPORTED:
        failed['reason'] = 'unsupported'
        return outcome('unsupported', "These checks run Python's built-in features only, so that import can't be used here.", statuses, failed)
    where = f' on line {run.line}' if run.line else ''
    return outcome('execution_error', f'Python stopped with {run.error_type or "an error"}{where} while running {about}. '
                                      'Read the error, change one thing, and run it again.', statuses, failed)

"""Versioned course content: catalog > course > unit > lesson > task.

Content lives in backend/content/ and is validated when the app starts, so a
broken reference or duplicate ID stops the service instead of reaching
learners. See backend/content/README.md for the format.
"""
import json
import keyword
import math
import re
import sys
from pathlib import Path
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError

CONTENT_DIR = Path(__file__).resolve().parent.parent / 'content'
ID = r'^[a-z0-9]+([.-][a-z0-9]+)*$'
# Lessons created before course-prefixed IDs. attempts.lesson_id stores these,
# so they are kept permanently without aliases.
LEGACY_LESSON_IDS = {'hello', 'variables', 'input', 'choices', 'adventure'}
# /api/lessons serves this unit in its original shape until the UI moves to the catalog.
LEGACY_UNIT = 'py.u01'
# Validator IDs and versions the platform can run for challenge tasks.
VALIDATORS = {'bounded-story': {2}}
# The current lesson page shows exactly these cards, in this order.
CARD_SEQUENCE = ['discover', 'example', 'predict', 'guided', 'challenge']
Status = Literal['released', 'coming_soon']


class ContentError(ValueError):
    pass


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)


class TaskBase(Strict):
    id: str = Field(pattern=ID)
    version: int = Field(default=1, ge=1)


class Discover(TaskBase):
    type: Literal['discover']
    title: str
    body: str
    detail: str


# ENG-08: at most this many files per case, each at most this many characters. Paths are relative, and
# each part starts with a letter or digit, so a path cannot leave the program's own folder.
FILES_PER_CASE = 10
FILE_LIMIT = 10_000
FILE_PATH = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]*(\.[A-Za-z0-9]+)*(/[A-Za-z0-9][A-Za-z0-9_-]*(\.[A-Za-z0-9]+)*)*$')


# Decision 30: no file a program gets, given or the learner's own, may be named like a module Python
# already has, so `import random` is always Python's random. The worker also puts these files after
# Python's own library on the import path, so this is a second line, not the only one.
PYTHON_MODULES = frozenset(sys.stdlib_module_names) | frozenset(sys.builtin_module_names) | {'js', 'pyodide', 'pyodide_js', 'micropip'}


def hides_a_module(path):
    return path.endswith('.py') and '/' not in path and path[:-3] in PYTHON_MODULES


def file_errors(owner, files):
    errors = [f'{owner} has more than {FILES_PER_CASE} files'] if len(files) > FILES_PER_CASE else []
    errors += [f'{owner} has an unsafe file path {path!r}' for path in files if len(path) > 100 or not FILE_PATH.match(path)]
    errors += [f"{owner} has a file {path!r} that would hide Python's own {path[:-3]} module" for path in files if hides_a_module(path)]
    return errors


# ENG-08b: the learner's own extra files, which they edit in their own tabs and import by name. At most
# this many per card. A name is short, lowercase and ends in .py, so it is also a module name.
MODULES_PER_TASK = 3
MODULE_NAME = re.compile(r'^[a-z][a-z0-9_]{0,30}\.py$')


def module_errors(owner, modules, given=()):
    errors = [f'{owner} has more than {MODULES_PER_TASK} learner files'] if len(modules) > MODULES_PER_TASK else []
    for name in modules:
        if not MODULE_NAME.match(name) or keyword.iskeyword(name[:-3]):
            errors.append(f'{owner}: a learner file {name!r} needs a short lowercase name that ends in .py')
        elif hides_a_module(name):
            errors.append(f"{owner}: a learner file {name!r} would hide Python's own {name[:-3]} module")
        if name in given:
            errors.append(f'{owner}: {name!r} is both a learner file and a given file')
    return errors


class Example(TaskBase):
    type: Literal['example']
    code: str
    output: str
    note: str
    inputs: list[str] = []
    # ENG-08: files the example's program finds in its folder, on the page and on the "Try it" card.
    files: dict[str, Annotated[str, Field(max_length=FILE_LIMIT)]] = {}
    # ENG-08b: the learner's own files on the "Try it" card, by name, with the code each starts with.
    modules: dict[str, Annotated[str, Field(max_length=FILE_LIMIT)]] = {}


class Predict(TaskBase):
    type: Literal['predict']
    question: str
    options: list[str] = Field(min_length=2)
    answer: int = Field(ge=0)
    why: str


class Guided(TaskBase):
    type: Literal['guided']
    prompt: str


class Validator(Strict):
    id: str
    version: int = Field(ge=1)


# Browser behaviour checks (ENG-03, docs/plan/browser-checks.md). The learner's browser runs the
# code against each case in the Pyodide worker and reports what it printed; the API compares that
# with `expected`. The API never runs learner code, and a hidden case's expected output never
# leaves the server.
BROWSER_TESTS = 'browser-tests'
# Most characters one case may print; the worker stops the program beyond this.
OUTPUT_LIMIT = 10_000
# Most characters one function-call case's arguments may take, as JSON.
CALL_LIMIT = 2_000
# Constructs a check can require or forbid, found by parsing the code, never by running it.
CONSTRUCTS = {
    'for': 'a for loop', 'while': 'a while loop', 'if': 'an if statement', 'elif': 'elif',
    'def': 'a function definition (def)', 'return': 'return', 'import': 'import',
    'f-string': 'an f-string', 'list': 'a list', 'dict': 'a dictionary', 'comparison': 'a comparison',
    'input()': 'input()', 'print()': 'print()', 'int()': 'int()', 'float()': 'float()', 'str()': 'str()',
    'range()': 'range()', 'len()': 'len()', 'eval()': 'eval()', 'exec()': 'exec()', 'open()': 'open()',
}


class CheckCall(Strict):
    """A function-call case (ENG-06): call this function, defined by the learner's program, with these values."""
    function: str = Field(pattern=r'^[A-Za-z_][A-Za-z0-9_]*$', max_length=80)
    args: list[Any] = Field(default=[], max_length=10)
    kwargs: dict[str, Any] = Field(default={}, max_length=10)


class CheckReturn(Strict):
    """The value a called function should return, compared by browser_checks.same_value."""
    value: Any
    # How far a number may be from the expected one. Needed when the expected value has a fraction.
    tolerance: float | None = Field(default=None, ge=0)


class CheckCase(Strict):
    """One run of the learner's program: replies fed to input(), and the output it should print.
    With `call`, the program runs and then the named function is called: `expected` is what the call
    prints, and `returns` is what it should return. Such a case has at least one of the two."""
    id: str = Field(pattern=ID)
    # Shown to the learner when this case fails, for hidden cases too, so it must not give away
    # their inputs or expected output (checked in validate()).
    description: str = Field(min_length=1, max_length=200)
    inputs: list[Annotated[str, Field(max_length=500)]] = Field(default=[], max_length=10)
    expected: str | None = Field(default=None, max_length=OUTPUT_LIMIT)
    visibility: Literal['visible', 'hidden'] = 'visible'
    # ENG-08: files this case's program finds in its folder, by path. Like inputs, a hidden case's files
    # reach the browser, because the program runs there.
    files: dict[str, Annotated[str, Field(max_length=FILE_LIMIT)]] = {}
    # ENG-10: the learner's program is a set of tests. This program is loaded first, and the tests should
    # pass or fail on it. Like inputs, a reference reaches the browser (decision 28). test_should is the
    # expected result, so a hidden case's is never sent.
    reference: str | None = Field(default=None, max_length=10_000)
    test_should: Literal['pass', 'fail'] | None = None
    # ENG-07: the number random is seeded with before this case runs. The worker uses 0 if it is not set.
    seed: int | None = Field(default=None, ge=0, le=2**31 - 1)
    call: CheckCall | None = None
    returns: CheckReturn | None = None


class BrowserCheck(Strict):
    cases: list[CheckCase] = Field(min_length=1, max_length=10)
    require: list[str] = []
    forbid: list[str] = []
    # Per case, after Python has loaded. The page stops the worker when it runs out.
    time_limit_ms: int = Field(default=3000, ge=500, le=10_000)


# Python errors a hint can be tagged with (docs/plan/lesson-feedback.md section 7). A hint can also
# be tagged with one of its own challenge's check rules.
ERROR_TAGS = {'SyntaxError', 'IndentationError', 'TabError', 'NameError', 'TypeError', 'ValueError', 'ZeroDivisionError', 'EOFError', 'FileNotFoundError'}


class CheckMessage(Strict):
    """What the learner reads when a named check rule fails, or when the check passes (section 6)."""
    id: str = Field(pattern=ID)
    message: str = Field(min_length=1, max_length=400)


class ErrorHint(Strict):
    """A hint offered first when one of its tags is the error or rule being shown (section 7)."""
    tags: list[str] = Field(min_length=1)
    text: str = Field(min_length=1, max_length=400)


class CodeSample(Strict):
    code: str = Field(min_length=1)
    note: str = Field(min_length=1, max_length=300)


class Challenge(TaskBase):
    type: Literal['challenge']
    prompt: str
    starter: str
    # The hint ladder, in order: a nudge, a bigger hint, the approach. Never a full solution.
    hints: list[str] = Field(default=[], max_length=3)
    error_hints: list[ErrorHint] = []
    # Offered after the last hint: the same idea in another context. It must not pass the check.
    similar_example: CodeSample | None = None
    # Shown only after passing: other valid solutions. Each must pass the check.
    other_ways: list[CodeSample] = []
    # Messages for the checker's named rules, by stable ID (bounded-story checks only).
    messages: list[CheckMessage] = []
    input_labels: list[str] = []
    # ENG-08b: the learner's own files, by name, with the code each starts with. They stay in the
    # browser: the page never sends them, so the API checks only what the program printed.
    modules: dict[str, Annotated[str, Field(max_length=FILE_LIMIT)]] = {}
    validator: Validator
    check: BrowserCheck | None = None

    def message(self, rule_id):
        return next(m.message for m in self.messages if m.id == rule_id)


Task = Annotated[Union[Discover, Example, Predict, Guided, Challenge], Field(discriminator='type')]


class Badge(Strict):
    id: str = Field(pattern=ID)
    version: int = Field(ge=1)
    title: str
    category: Literal['practice', 'skill', 'project', 'habit', 'collaboration', 'capstone']


class Lesson(Strict):
    id: str = Field(pattern=ID)
    version: int = Field(ge=1)
    course: str
    unit: str
    title: str
    concept: str
    description: str
    badge: Badge | None = None
    tasks: list[Task]

    def task(self, kind):
        return next(t for t in self.tasks if t.type == kind)


class Prerequisites(Strict):
    required: list[str] = []
    suggested: list[str] = []


class Unit(Strict):
    id: str = Field(pattern=ID)
    title: str
    summary: str
    status: Status
    lessons: list[str] = []
    # A released unit that is still being written: some of its planned lessons are out, more are
    # coming. The lesson page and the recommendation then say so instead of calling it complete.
    more_lessons_coming: bool = False


class Course(Strict):
    id: str = Field(pattern=ID)
    version: int = Field(ge=1)
    title: str
    summary: str
    status: Status
    prerequisites: Prerequisites = Prerequisites()
    units: list[Unit] = []


class Catalog(Strict):
    version: int = Field(ge=1)
    courses: list[Course]


def load(root: Path = CONTENT_DIR):
    """Read and validate all content under root. Returns (catalog, lessons by ID)."""
    errors = []
    try:
        catalog = Catalog.model_validate_json((root / 'catalog.json').read_text())
    except (OSError, ValidationError) as error:
        raise ContentError(f'catalog.json: {error}') from error
    lessons = {}
    for path in sorted(root.glob('*/u[0-9][0-9]/*.json')):
        name = path.relative_to(root)
        try:
            lesson = Lesson.model_validate_json(path.read_text())
        except ValidationError as error:
            errors.append(f'{name}: {error}')
            continue
        if path.stem != lesson.id or path.parent.parent.name != lesson.course or f'{lesson.course}.{path.parent.name}' != lesson.unit:
            errors.append(f'{name}: file must be at {lesson.course}/{lesson.unit.split(".")[-1]}/{lesson.id}.json')
        if lesson.id in lessons:
            errors.append(f'{name}: duplicate lesson ID {lesson.id}')
        lessons[lesson.id] = lesson
    errors += validate(catalog, lessons)
    if errors:
        raise ContentError('Invalid course content:\n- ' + '\n- '.join(errors))
    return catalog, lessons


def validate(catalog, lessons):
    errors = []
    courses = {}
    units = {}
    listed = {}
    for course in catalog.courses:
        if course.id in courses:
            errors.append(f'duplicate course ID {course.id}')
        courses[course.id] = course
        for unit in course.units:
            if not re.fullmatch(re.escape(course.id) + r'\.u\d\d', unit.id):
                errors.append(f'unit {unit.id} must be named {course.id}.uNN')
            if unit.id in units:
                errors.append(f'duplicate unit ID {unit.id}')
            units[unit.id] = course.id
            if unit.status == 'released' and not unit.lessons:
                errors.append(f'released unit {unit.id} has no lessons')
            if unit.status == 'coming_soon' and unit.lessons:
                errors.append(f'coming-soon unit {unit.id} lists lessons; release it or remove them')
            if unit.more_lessons_coming and unit.status != 'released':
                errors.append(f'unit {unit.id} is coming soon, so it cannot also have more lessons coming; that is only for a released unit')
            if course.status == 'coming_soon' and unit.status == 'released':
                errors.append(f'unit {unit.id} is released inside coming-soon course {course.id}')
            for lesson_id in unit.lessons:
                if lesson_id in listed:
                    errors.append(f'lesson {lesson_id} is listed in both {listed[lesson_id]} and {unit.id}')
                listed[lesson_id] = unit.id
                lesson = lessons.get(lesson_id)
                if not lesson:
                    errors.append(f'unit {unit.id} lists missing lesson {lesson_id}')
                elif (lesson.course, lesson.unit) != (course.id, unit.id):
                    errors.append(f'lesson {lesson_id} says {lesson.course}/{lesson.unit} but is listed in {unit.id}')
        if course.status == 'released' and not any(u.status == 'released' for u in course.units):
            errors.append(f'released course {course.id} has no released units')

    task_ids = set()
    rule_ids = set()
    badge_ids = set()
    for lesson in lessons.values():
        if lesson.id not in listed:
            errors.append(f'lesson {lesson.id} is not listed in any unit')
        if lesson.id not in LEGACY_LESSON_IDS and not lesson.id.startswith(lesson.course + '.'):
            errors.append(f'lesson {lesson.id} must start with its course ID, for example {lesson.course}.{lesson.id}')
        kinds = [t.type for t in lesson.tasks]
        if kinds != CARD_SEQUENCE:
            errors.append(f'lesson {lesson.id} tasks must be {", ".join(CARD_SEQUENCE)} in order, not {", ".join(kinds)}')
            continue
        for task in lesson.tasks:
            if not task.id.startswith(lesson.id + '.'):
                errors.append(f'task {task.id} must start with {lesson.id}.')
            if task.id in task_ids:
                errors.append(f'duplicate task ID {task.id}')
            task_ids.add(task.id)
        predict, example, challenge = lesson.task('predict'), lesson.task('example'), lesson.task('challenge')
        if predict.answer >= len(predict.options):
            errors.append(f'{predict.id} answer {predict.answer} is not one of its {len(predict.options)} options')
        if len(set(predict.options)) != len(predict.options):
            errors.append(f'{predict.id} has duplicate options')
        if len(challenge.input_labels) != len(example.inputs):
            errors.append(f'lesson {lesson.id} has {len(challenge.input_labels)} reply labels but {len(example.inputs)} example replies')
        if challenge.validator.version not in {**VALIDATORS, BROWSER_TESTS: {1}}.get(challenge.validator.id, set()):
            errors.append(f'{challenge.id} uses unknown validator {challenge.validator.id} v{challenge.validator.version}')
        errors += check_errors(challenge)
        errors += file_errors(example.id, example.files)
        errors += module_errors(example.id, example.modules, example.files)
        given = {path for case in (challenge.check.cases if challenge.check else []) for path in case.files}
        errors += module_errors(challenge.id, challenge.modules, given)
        if challenge.modules and challenge.validator.id != BROWSER_TESTS:
            errors.append(f'{challenge.id} has learner files, which only a browser check can run')
        errors += feedback_errors(lesson.id, challenge, rule_ids)
        if lesson.badge:
            if lesson.badge.id in badge_ids:
                errors.append(f'duplicate badge ID {lesson.badge.id}')
            badge_ids.add(lesson.badge.id)

    edges = {course_id: set() for course_id in courses}
    for course in catalog.courses:
        for ref in course.prerequisites.required + course.prerequisites.suggested:
            target = ref if ref in courses else units.get(ref)
            if target is None:
                errors.append(f'course {course.id} prerequisite {ref} is not a course or unit')
            elif target == course.id:
                errors.append(f'course {course.id} cannot require itself ({ref})')
            else:
                edges[course.id].add(target)
    errors += [f'prerequisite cycle: {" -> ".join(cycle)}' for cycle in _cycles(edges)]
    return errors


def feedback_errors(lesson_id, challenge, seen):
    """Problems with a challenge's check messages and hint tags. Whether the messages match the
    rules the checker really uses is checked by lesson_checks.rule_errors(), which knows them."""
    errors = []
    ids = [m.id for m in challenge.messages]
    for rule_id in ids:
        if not rule_id.startswith(lesson_id + '.'):
            errors.append(f'{challenge.id} rule {rule_id} must start with {lesson_id}.')
        if ids.count(rule_id) > 1 or rule_id in seen:
            errors.append(f'{challenge.id} has duplicate rule ID {rule_id}')
    seen.update(ids)
    rules = set(ids) - {lesson_id + '.passed'}
    if challenge.check:
        # A browser check's wrong-output result names its case as a rule: <lesson>.case.<case id>.
        rules |= {f'{lesson_id}.case.{case.id}' for case in challenge.check.cases}
    tagged = [tag for hint in challenge.error_hints for tag in hint.tags]
    for tag in tagged:
        if tag not in ERROR_TAGS | rules:
            errors.append(f'{challenge.id} hint tag {tag} is not a Python error ({", ".join(sorted(ERROR_TAGS))}) or one of its rules')
        if tagged.count(tag) > 1:
            errors.append(f'{challenge.id} has more than one hint tagged {tag}')
    return sorted(set(errors), key=errors.index)


def fractions_in(value):
    """Is there a number with a fraction anywhere in this value? Exact comparison of those is a trap."""
    if isinstance(value, float):
        return value != int(value) if math.isfinite(value) else True
    if isinstance(value, list):
        return any(map(fractions_in, value))
    if isinstance(value, dict):
        return any(map(fractions_in, value.values()))
    return False


def numbers_in(value):
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, list):
        return any(map(numbers_in, value))
    if isinstance(value, dict):
        return any(map(numbers_in, value.values()))
    return False


def json_size(value):
    """Characters as JSON, or None when it is not plain JSON (NaN and Infinity are not)."""
    try:
        return len(json.dumps(value, allow_nan=False))
    except ValueError:
        return None


def call_errors(challenge, case):
    """Problems with one case's function call and return value (ENG-06, browser-checks.md section 8)."""
    name = f'{challenge.id} case {case.id}'
    if (case.reference is None) != (case.test_should is None):
        return [f'{name} needs reference and test_should together']
    if case.reference is not None:
        if case.call or case.returns or case.expected is not None:
            return [f'{name}: a reference case compares nothing else, so it has no call, returns or expected']
        try:
            compile(case.reference, '<reference>', 'exec')
        except SyntaxError as error:
            return [f'{name}: its reference has a syntax error on line {error.lineno}']
        return []
    if case.call is None:
        if case.returns is not None:
            return [f'{name} has returns but no call']
        return [f'{name} needs expected output'] if case.expected is None else []
    errors = []
    if case.expected is None and case.returns is None:
        errors.append(f'{name} needs expected output, returns, or both')
    if keyword.iskeyword(case.call.function):
        errors.append(f'{name}: {case.call.function} cannot be a function name')
    for key in case.call.kwargs:
        if not key.isidentifier() or keyword.iskeyword(key):
            errors.append(f'{name}: {key} cannot be a keyword argument')
    size = json_size([case.call.args, case.call.kwargs])
    if size is None or size > CALL_LIMIT:
        errors.append(f'{name}: arguments must be plain JSON, up to {CALL_LIMIT} characters')
    if case.returns is not None:
        size = json_size(case.returns.value)
        if size is None or size > OUTPUT_LIMIT:
            errors.append(f'{name}: the return value must be plain JSON, up to {OUTPUT_LIMIT} characters')
        elif case.returns.tolerance is None and fractions_in(case.returns.value):
            errors.append(f'{name}: a return value with a fraction needs a tolerance')
        if case.returns.tolerance is not None and not numbers_in(case.returns.value):
            errors.append(f'{name}: a tolerance needs a number to apply to')
    return errors


def check_errors(challenge):
    """Problems with a challenge's browser check, if it has one."""
    check, errors = challenge.check, []
    if (challenge.validator.id == BROWSER_TESTS) != (check is not None):
        return [f'{challenge.id} needs a check exactly when its validator is {BROWSER_TESTS}']
    if check is None:
        return []
    ids = [case.id for case in check.cases]
    if len(set(ids)) != len(ids):
        errors.append(f'{challenge.id} has duplicate check case IDs')
    if not any(case.visibility == 'visible' for case in check.cases):
        errors.append(f'{challenge.id} needs at least one visible check case, so learners can see what is expected')
    for name in check.require + check.forbid:
        if name not in CONSTRUCTS:
            errors.append(f'{challenge.id} names unknown construct {name}; known: {", ".join(CONSTRUCTS)}')
    if set(check.require) & set(check.forbid):
        errors.append(f'{challenge.id} both requires and forbids {", ".join(sorted(set(check.require) & set(check.forbid)))}')
    testing = [case for case in check.cases if case.reference is not None]
    if testing:
        # Tests must be seen to pass on correct code first, or a typo would look like a bug caught.
        if len(testing) != len(check.cases):
            errors.append(f'{challenge.id}: if one case has a reference, all must')
        elif check.cases[0].test_should != 'pass' or check.cases[0].visibility != 'visible':
            errors.append(f'{challenge.id}: its first case must be visible, with a reference the tests should pass on')
        elif not any(case.test_should == 'fail' for case in check.cases):
            errors.append(f'{challenge.id} needs a broken reference, one that the tests should fail on')
    for case in check.cases:
        errors += call_errors(challenge, case)
        errors += file_errors(f'{challenge.id} case {case.id}', case.files)
        if case.visibility == 'hidden':
            lines = [line for text in case.files.values() for line in text.splitlines()]
            # Decision 28: a hidden call's arguments do reach the browser, but the page must not show them.
            call_values = [json.dumps(value) if not isinstance(value, str) else value for value in (case.call.args + list(case.call.kwargs.values()) if case.call else [])]
            answer = [json.dumps(case.returns.value)] if case.returns and case.returns.value is not None else []
            secrets = [value.strip() for value in case.inputs + lines + call_values + answer + (case.expected or '').splitlines() if value.strip()]
            if any(value.casefold() in case.description.casefold() for value in secrets):
                errors.append(f'{challenge.id} hidden case {case.id}: its description shows one of its inputs, file lines, call values or expected lines')
    return errors


def _cycles(edges):
    found, state = [], {}

    def visit(node, path):
        state[node] = 'open'
        for nxt in sorted(edges[node]):
            if state.get(nxt) == 'open':
                found.append(path[path.index(nxt):] + [nxt])
            elif nxt not in state:
                visit(nxt, path + [nxt])
        state[node] = 'done'

    for node in sorted(edges):
        if node not in state:
            visit(node, [node])
    return found


def sample_files(challenge):
    cases = challenge.check.cases if challenge.check else []
    return next((case.files for case in cases if case.visibility == 'visible' and case.files), None)


def lesson_view(lesson):
    """One lesson as the lesson page reads it (the original /api/lessons shape, plus later additions)."""
    discover, example, predict, guided, challenge = lesson.tasks
    return {
        'id': lesson.id, 'title': lesson.title, 'concept': lesson.concept,
        'badge': lesson.badge.title if lesson.badge else '', 'description': lesson.description,
        'learnTitle': discover.title, 'learn': discover.body, 'detail': discover.detail,
        'example': example.code, 'exampleOutput': example.output, 'exampleNote': example.note,
        'question': predict.question, 'options': predict.options, 'answer': predict.answer, 'why': predict.why,
        'guided': guided.prompt, 'starter': challenge.starter, 'challenge': challenge.prompt,
        'hints': challenge.hints, 'inputs': challenge.input_labels, 'exampleInputs': example.inputs,
        # Retired field, always null; kept so the response is unchanged.
        'expected': None,
        # Added for the feedback engine (ENG-04 part 2a). New fields only, so a page from before
        # them keeps working during a deploy.
        'errorHints': [{'tags': h.tags, 'text': h.text} for h in challenge.error_hints],
        'similarExample': challenge.similar_example.model_dump() if challenge.similar_example else None,
        'otherWays': [way.model_dump() for way in challenge.other_ways],
        # ENG-08, only for a lesson that has files. A challenge shows one visible case's files as a sample.
        **({'exampleFiles': example.files} if example.files else {}),
        **({'challengeFiles': sample} if (sample := sample_files(challenge)) else {}),
        # ENG-08b, only for a lesson with the learner's own files: each name and the code it starts with.
        **({'exampleModules': example.modules} if example.modules else {}),
        **({'challengeModules': challenge.modules} if challenge.modules else {}),
    }


def legacy_lessons(catalog, lessons):
    """The original /api/lessons shape, rebuilt from the content files for the current UI."""
    unit = next(u for c in catalog.courses for u in c.units if u.id == LEGACY_UNIT)
    return [lesson_view(lessons[i]) for i in unit.lessons]


def unit_lessons(catalog, lessons):
    """/api/units/<unit id>/lessons for every released unit (UI-05): each lesson as lesson_view()
    gives it, plus its course, its unit and which check its challenge uses. A browser check's cases
    are not here; the page asks /api/checks/<lesson id>, which leaves out hidden expected output."""
    return {unit.id: [{**lesson_view(lessons[i]), 'course': course.id, 'unit': unit.id, 'check': lessons[i].task('challenge').validator.id}
                      for i in unit.lessons]
            for course in catalog.courses for unit in course.units if unit.status == 'released'}


def lesson_order(catalog):
    """Lesson IDs in catalog order (course, then unit, then lesson)."""
    return [lesson_id for course in catalog.courses for unit in course.units for lesson_id in unit.lessons]


def catalog_view(catalog, lessons):
    """Public catalog for /api/catalog: every course and unit, with short lesson summaries."""
    def lesson_summary(lesson_id):
        lesson = lessons[lesson_id]
        return {'id': lesson.id, 'title': lesson.title, 'concept': lesson.concept, 'description': lesson.description,
                'badge': lesson.badge.title if lesson.badge else None}
    return {'version': catalog.version, 'courses': [{
        'id': course.id, 'title': course.title, 'summary': course.summary, 'status': course.status,
        'prerequisites': course.prerequisites.model_dump(),
        # complete: released with every planned lesson (added for EDU-04 part 2; a new field only).
        'units': [{'id': unit.id, 'title': unit.title, 'summary': unit.summary, 'status': unit.status,
                   'complete': unit.status == 'released' and not unit.more_lessons_coming,
                   'lessons': [lesson_summary(i) for i in unit.lessons]} for unit in course.units],
    } for course in catalog.courses]}

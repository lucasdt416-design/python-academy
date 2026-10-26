"""Versioned course content: catalog > course > unit > lesson > task.

Content lives in backend/content/ and is validated when the app starts, so a
broken reference or duplicate ID stops the service instead of reaching
learners. See backend/content/README.md for the format.
"""
import re
from pathlib import Path
from typing import Annotated, Literal, Union

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


class Example(TaskBase):
    type: Literal['example']
    code: str
    output: str
    note: str
    inputs: list[str] = []


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


class Challenge(TaskBase):
    type: Literal['challenge']
    prompt: str
    starter: str
    hints: list[str] = []
    input_labels: list[str] = []
    validator: Validator


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
        if challenge.validator.version not in VALIDATORS.get(challenge.validator.id, set()):
            errors.append(f'{challenge.id} uses unknown validator {challenge.validator.id} v{challenge.validator.version}')
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


def legacy_lessons(catalog, lessons):
    """The original /api/lessons shape, rebuilt from the content files for the current UI."""
    unit = next(u for c in catalog.courses for u in c.units if u.id == LEGACY_UNIT)
    result = []
    for lesson in (lessons[i] for i in unit.lessons):
        discover, example, predict, guided, challenge = lesson.tasks
        result.append({
            'id': lesson.id, 'title': lesson.title, 'concept': lesson.concept,
            'badge': lesson.badge.title if lesson.badge else '', 'description': lesson.description,
            'learnTitle': discover.title, 'learn': discover.body, 'detail': discover.detail,
            'example': example.code, 'exampleOutput': example.output, 'exampleNote': example.note,
            'question': predict.question, 'options': predict.options, 'answer': predict.answer, 'why': predict.why,
            'guided': guided.prompt, 'starter': challenge.starter, 'challenge': challenge.prompt,
            'hints': challenge.hints, 'inputs': challenge.input_labels, 'exampleInputs': example.inputs,
            # Retired field, always null; kept so the response is unchanged.
            'expected': None,
        })
    return result


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
        'units': [{'id': unit.id, 'title': unit.title, 'summary': unit.summary, 'status': unit.status,
                   'lessons': [lesson_summary(i) for i in unit.lessons]} for unit in course.units],
    } for course in catalog.courses]}

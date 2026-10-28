"""The rule-based recommendation (plan section 4) on the real catalog and on test catalogs
where later units and courses are released with placeholder lessons."""
from hypothesis import given, settings, strategies as st

from app import content
from app.content import Unit
from app.recommend import GOALS, RULES_VERSION, recommend

CATALOG, LESSONS = content.load()
UNIT1 = {'hello', 'variables', 'input', 'choices', 'adventure'}


def release(catalog, units, planned=None):
    """Return a copy of catalog with the given units released, each with placeholder lessons.

    units: unit IDs to release (py.u01 keeps its real lessons). planned: {course_id: n} gives
    courses without units n coming-soon units first, so they can be released too.
    """
    courses = []
    for course in catalog.courses:
        own = list(course.units)
        if not own and planned and course.id in planned:
            own = [Unit(id=f'{course.id}.u{n:02d}', title=f'{course.title} {n}', summary='', status='coming_soon')
                   for n in range(1, planned[course.id] + 1)]
        own = [u.model_copy(update={'status': 'released', 'lessons': u.lessons or [f'{u.id}.l1', f'{u.id}.l2']})
               if u.id in units else u for u in own]
        status = 'released' if any(u.status == 'released' for u in own) else course.status
        courses.append(course.model_copy(update={'units': own, 'status': status}))
    return catalog.model_copy(update={'courses': courses})


def lessons_of(catalog, *unit_ids):
    return {l for c in catalog.courses for u in c.units if u.id in unit_ids for l in u.lessons}


PY = [f'py.u{n:02d}' for n in range(1, 13)]


def test_new_student_starts_python_on_the_real_catalog():
    r = recommend('scratch', CATALOG, set())
    assert (r.kind, r.course, r.unit, r.lesson) == ('start', 'py', 'py.u01', 'hello')
    assert r.reason == 'Start of your Learn to code path.'
    assert r.rules_version == RULES_VERSION


def test_every_goal_starts_with_python_and_unknown_goals_use_the_default():
    for goal in GOALS:
        assert recommend(goal, CATALOG, set()).lesson == 'hello'
    assert recommend('nonsense', CATALOG, set()) == recommend('scratch', CATALOG, set())
    assert recommend(None, CATALOG, set()) == recommend('scratch', CATALOG, set())


def test_partway_through_a_course_continues_it():
    r = recommend('data', CATALOG, {'hello', 'variables'})
    assert (r.kind, r.lesson) == ('continue', 'input')
    assert r.reason == "You're partway through Python Foundations."


UNIT2_PART1 = {'py.arithmetic', 'py.int-float', 'py.convert-input'}
UNIT2 = UNIT2_PART1 | {'py.compare', 'py.boolean-logic', 'py.elif'}


def test_after_unit_1_python_continues_with_unit_2():
    r = recommend('hackathon', CATALOG, UNIT1)
    assert (r.kind, r.unit, r.lesson) == ('continue', 'py.u02', 'py.arithmetic')


def test_when_everything_released_is_done_the_coming_soon_courses_are_named():
    r = recommend('hackathon', CATALOG, UNIT1 | UNIT2)
    assert r.kind == 'caught_up' and r.lesson is None
    assert r.reason == "You've finished everything available on your path so far."
    assert r.notes[0] == 'Python Foundations unit 3, Repeat and explore, is next on your path. Its lessons are not written yet.'
    assert 'Hackathon Ready' in r.notes[1]


def test_part_of_unit_2_done_continues_unit_2():
    r = recommend('hackathon', CATALOG, UNIT1 | UNIT2_PART1)
    assert (r.kind, r.unit, r.lesson) == ('continue', 'py.u02', 'py.compare')


def test_a_unit_still_being_written_is_not_finished_and_says_more_lessons_are_coming():
    # A released unit marked more_lessons_coming (for example a unit released in parts, as unit 2 was).
    py = CATALOG.courses[0]
    partial = py.units[1].model_copy(update={'lessons': sorted(UNIT2_PART1, key=py.units[1].lessons.index), 'more_lessons_coming': True})
    catalog = CATALOG.model_copy(update={'courses': [py.model_copy(update={'units': [py.units[0], partial, *py.units[2:]]}), *CATALOG.courses[1:]]})
    r = recommend('scratch', catalog, UNIT1 | UNIT2_PART1)
    assert r.kind == 'caught_up' and r.lesson is None
    assert r.notes[0] == 'Python Foundations unit 2, Numbers and decisions, has more lessons on the way. You have finished every lesson in it so far.'
    # Unit 3 is never offered while unit 2 is still being written.
    assert 'unit 3' not in ' '.join(r.notes)


def test_worked_example_hackathon_moves_on_after_python_unit_seven():
    catalog = release(CATALOG, PY[:8] + ['hack.u01'])  # py units 1-8 and hack unit 1 released
    r = recommend('hackathon', catalog, lessons_of(catalog, *PY[:7]))
    assert (r.kind, r.course, r.lesson) == ('start', 'hack', 'hack.u01.l1')
    assert r.reason == "Next on your hackathon path, and you've finished Python Foundations units 1–7."


def test_worked_example_unreleased_hackathon_is_noted_and_the_next_released_course_follows():
    catalog = release(CATALOG, PY[:7] + ['git.u01'], planned={'git': 3})
    r = recommend('hackathon', catalog, lessons_of(catalog, *PY[:7]))
    assert r.notes == ('Hackathon Ready is next on your path and is coming soon.',)
    assert (r.kind, r.course, r.lesson) == ('start', 'git', 'git.u01.l1')
    assert r.reason == "Next on your hackathon path, and you've finished Python Foundations unit 1."


def test_worked_example_skills_check_moves_the_start_without_awarding_anything():
    catalog = release(CATALOG, PY[:2])
    completed = set()
    r = recommend('websites', catalog, completed, placed={'py.u01'})
    assert (r.kind, r.unit, r.lesson) == ('start', 'py.u02', 'py.arithmetic')
    assert r.reason == 'Next on your websites and apps path. Your skills check lets you start at unit 2.'
    assert completed == set()


def test_unmet_prerequisites_walk_back_to_one_that_is_ready():
    catalog = release(CATALOG, PY + ['web.u01', 'js.u01'], planned={'web': 2, 'js': 2})
    r = recommend('scratch', catalog, lessons_of(catalog, *PY), dismissed={'git', 'web'})
    assert (r.kind, r.course, r.lesson) == ('prerequisite', 'web', 'web.u01.l1')
    assert r.reason == 'JavaScript and the DOM needs Web Foundations: HTML and CSS first.'


def test_a_started_course_off_the_path_is_continued():
    catalog = release(CATALOG, PY + ['node.u01'], planned={'node': 2})
    started = lessons_of(catalog, *PY) | {'node.u01.l1'}
    r = recommend('data', catalog, started)
    assert (r.kind, r.course, r.lesson) == ('continue', 'node', 'node.u01.l2')


def test_dismissed_courses_are_skipped():
    catalog = release(CATALOG, PY + ['git.u01', 'cs.u01'], planned={'git': 1, 'cs': 1})
    done = lessons_of(catalog, *PY)
    assert recommend('university', catalog, done).course == 'git'
    assert recommend('university', catalog, done, dismissed={'git'}).course == 'cs'


def test_explore_offers_a_choice_after_the_first_unit():
    catalog = release(CATALOG, ['py.u01', 'git.u01'], planned={'git': 1})
    r = recommend('explore', catalog, UNIT1)
    assert (r.kind, r.options) == ('choose', ('git',))
    assert r.lesson is None


def test_a_finished_path_offers_other_ready_courses():
    path = ['py', 'git', 'web', 'js', 'sql']
    planned = {c: 1 for c in path[1:] + ['cs']}
    units = PY + [f'{c}.u01' for c in planned]
    catalog = release(CATALOG, units, planned=planned)
    r = recommend('scratch', catalog, lessons_of(catalog, *(PY + [f'{c}.u01' for c in path[1:]])))
    assert (r.kind, r.options) == ('choose', ('cs',))
    assert r.reason == "You've completed your Learn to code path."


def test_same_inputs_always_give_the_same_recommendation():
    assert recommend('hackathon', CATALOG, {'hello'}) == recommend('hackathon', CATALOG, {'hello'})


# Property tests: random release states, progress, placement, and dismissals.
UNIT_IDS = [u.id for c in CATALOG.courses for u in c.units]
PLANNED = {c.id: 2 for c in CATALOG.courses if not c.units}
ALL_UNITS = UNIT_IDS + [f'{c}.u{n:02d}' for c, k in PLANNED.items() for n in range(1, k + 1)]


@st.composite
def situations(draw):
    released = draw(st.sets(st.sampled_from(ALL_UNITS)))
    catalog = release(CATALOG, released, planned=PLANNED)
    all_lessons = sorted(lessons_of(catalog, *released))
    completed = draw(st.sets(st.sampled_from(all_lessons))) if all_lessons else set()
    placed = draw(st.sets(st.sampled_from(ALL_UNITS), max_size=3))
    dismissed = draw(st.sets(st.sampled_from([c.id for c in CATALOG.courses]), max_size=3))
    goal = draw(st.sampled_from(list(GOALS)))
    return goal, catalog, completed, placed, dismissed


@settings(max_examples=400, deadline=None)
@given(situations())
def test_recommendations_are_always_possible_and_explained(situation):
    goal, catalog, completed, placed, dismissed = situation
    r = recommend(goal, catalog, completed, placed, dismissed)
    assert r == recommend(goal, catalog, completed, placed, dismissed)
    assert r.kind in {'continue', 'start', 'prerequisite', 'choose', 'caught_up'} and r.reason
    courses = {c.id: c for c in catalog.courses}
    if r.lesson is None:
        assert r.kind in {'choose', 'caught_up'}
        assert all(courses[o].status == 'released' for o in r.options)
        return
    course = courses[r.course]
    unit = next(u for u in course.units if u.id == r.unit)
    # Never recommend something that cannot be started, or that is already done.
    assert course.status == 'released' and unit.status == 'released'
    assert r.lesson in unit.lessons and r.lesson not in completed and r.unit not in placed
    assert r.course not in dismissed or r.kind == 'prerequisite'

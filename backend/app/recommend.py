"""Rule-based "recommended next" (docs/plan/course-catalog.md section 4).

A pure function of its inputs: no database, no clock, no randomness, no AI service.
The same inputs always give the same recommendation and the same reason. It only
advises; learners can open any released course whatever it says.
"""
from dataclasses import asdict, dataclass

RULES_VERSION = 1


@dataclass(frozen=True)
class Step:
    """One stop on a goal path: a course, optionally only up to (and including) a unit."""
    course: str
    through: str | None = None


@dataclass(frozen=True)
class Goal:
    id: str
    label: str
    description: str
    path_name: str  # used in reasons: "Next on your <path_name> path"
    path: tuple[Step, ...]
    choose_after: bool = False  # "Just explore": after the path, offer a choice instead


# Plan section 2. "py through unit 7" stops are followed later by the rest of py.
GOALS = {goal.id: goal for goal in (
    Goal('scratch', 'Learn to code from scratch', 'Start with your first program and build up one small step at a time.',
         'Learn to code', (Step('py'), Step('git'), Step('web'), Step('js'), Step('sql'))),
    Goal('hackathon', 'Get ready for hackathons', 'Learn to scope, build, and demo a small working project with a team.',
         'hackathon', (Step('py', 'py.u07'), Step('hack'), Step('py'), Step('git'), Step('web'), Step('js'), Step('node'), Step('sql'))),
    Goal('university', 'Prepare for university CS or engineering', 'Build depth in programming, algorithms, and how computers work.',
         'university', (Step('py'), Step('git'), Step('cs'), Step('sql'), Step('ce'))),
    Goal('websites', 'Build websites and apps', 'Make things people can use in a browser, from pages to a full app.',
         'websites and apps', (Step('py', 'py.u07'), Step('web'), Step('py'), Step('js'), Step('git'), Step('sql'), Step('node'), Step('fullstack'))),
    Goal('data', 'Work with data', 'Ask questions of real data with Python and SQL.',
         'data', (Step('py'), Step('sql'), Step('data'), Step('git'))),
    Goal('explore', 'Just explore', 'No plan yet. Try the first unit, then pick whatever looks interesting.',
         'explore', (Step('py', 'py.u01'),), choose_after=True),
)}
DEFAULT_GOAL = 'scratch'


@dataclass(frozen=True)
class Recommendation:
    # continue: keep going in a course already started; start: next on the goal path;
    # prerequisite: something the next course needs first; choose: pick from options;
    # caught_up: nothing available is left for now.
    kind: str
    reason: str
    course: str | None = None
    unit: str | None = None
    lesson: str | None = None
    options: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    rules_version: int = RULES_VERSION

    def as_dict(self):
        return {**asdict(self), 'options': list(self.options), 'notes': list(self.notes)}


def recommend(goal_id, catalog, completed, placed=frozenset(), dismissed=frozenset()):
    """Recommend what a learner should do next.

    goal_id: the learner's goal (unknown or missing means the default).
    catalog: content.Catalog, including release status and prerequisites.
    completed: lesson IDs the learner has earned (from the XP ledger).
    placed: unit IDs the skills check showed as independently demonstrated (Issue #4).
            They satisfy prerequisites and move the starting point, never award anything.
    dismissed: course IDs the learner said "Not now" to.
    """
    goal = GOALS.get(goal_id) or GOALS[DEFAULT_GOAL]
    return _Rules(goal, catalog, set(completed), set(placed), set(dismissed)).run()


class _Rules:
    def __init__(self, goal, catalog, completed, placed, dismissed):
        self.goal, self.catalog, self.completed, self.placed, self.dismissed = goal, catalog, completed, placed, dismissed
        self.courses = {c.id: c for c in catalog.courses}
        self.units = {u.id: (c, u) for c in catalog.courses for u in c.units}
        steps = [s for s in goal.path if s.course in self.courses]
        # Each step covers only units no earlier step of the same course covered.
        self.own = {}
        covered = {}
        for step in steps:
            scope = self.scope(step)
            self.own[step] = [u for u in scope if u.id not in covered.get(step.course, set())]
            covered.setdefault(step.course, set()).update(u.id for u in scope)
        self.steps = steps

    def scope(self, step):
        units = self.courses[step.course].units
        if step.through:
            ids = [u.id for u in units]
            units = units[:ids.index(step.through) + 1] if step.through in ids else units
        return units

    def unit_done(self, unit):
        return unit.id in self.placed or (unit.status == 'released' and bool(unit.lessons) and all(l in self.completed for l in unit.lessons))

    def units_done(self, units):
        # A course with no units yet (still being planned) is never complete.
        return bool(units) and all(self.unit_done(u) for u in units)

    def satisfied(self, ref):
        if ref in self.courses:
            return self.units_done(self.courses[ref].units)
        return ref in self.units and self.unit_done(self.units[ref][1])

    def unmet(self, course):
        return [r for r in course.prerequisites.required if not self.satisfied(r)]

    def next_lesson(self, units):
        """(unit, lesson) to do next among units, or None if the next unit is not released yet."""
        for unit in units:
            if self.unit_done(unit):
                continue
            if unit.status != 'released':
                return None
            return unit, next(l for l in unit.lessons if l not in self.completed)
        return None

    def started(self, units):
        return any(l in self.completed for u in units for l in u.lessons)

    def describe(self, refs):
        parts = []
        for course in self.catalog.courses:
            if course.id in refs:
                parts.append(course.title)
                continue
            numbers = sorted(int(u.id.rsplit('.u', 1)[1]) for u in course.units if u.id in refs)
            if not numbers:
                continue
            ranges, start, end = [], numbers[0], numbers[0]
            for n in numbers[1:] + [None]:
                if n is not None and n == end + 1:
                    end = n
                    continue
                ranges.append(f'{start}' if start == end else f'{start}–{end}')
                start = end = n
            parts.append(f"{course.title} {'unit' if len(numbers) == 1 else 'units'} {', '.join(ranges)}")
        return parts[0] if len(parts) < 2 else ', '.join(parts[:-1]) + ' and ' + parts[-1] if parts else ''

    def coming_soon_note(self, step):
        course = self.courses[step.course]
        if course.status != 'released':
            return f'{course.title} is next on your path and is coming soon.'
        unit = next(u for u in self.own[step] if not self.unit_done(u))
        return f'{course.title} unit {int(unit.id.rsplit(".u", 1)[1])} is next on your path and is coming soon.'

    def recommendation(self, kind, reason, course, found, notes=()):
        unit, lesson = found
        return Recommendation(kind, reason, course.id, unit.id, lesson, notes=tuple(notes))

    def run(self):
        candidates = [s for s in self.steps if s.course not in self.dismissed and not self.units_done(self.own[s])]

        # Rule 1: keep going in a course already started (its current path stop first, then any other).
        for step in candidates:
            found = self.next_lesson(self.own[step])
            if found and self.started(self.own[step]):
                course = self.courses[step.course]
                return self.recommendation('continue', f"You're partway through {course.title}.", course, found)
        on_path = {s.course for s in self.steps}
        for course in self.catalog.courses:
            if course.id in on_path or course.id in self.dismissed or not self.started(course.units):
                continue
            found = self.next_lesson(course.units)
            if found:
                return self.recommendation('continue', f"You're partway through {course.title}.", course, found)

        # Rule 2: say so if the very next stop is not released yet.
        notes = []
        if candidates and not self.next_lesson(self.own[candidates[0]]):
            notes.append(self.coming_soon_note(candidates[0]))

        # Rule 3: the first released stop whose required prerequisites are met.
        blocked = None
        for step in candidates:
            found = self.next_lesson(self.own[step])
            if not found:
                continue
            course = self.courses[step.course]
            if self.unmet(course):
                blocked = blocked or (step, course)
                continue
            required = course.prerequisites.required
            if not self.completed and not self.placed:
                reason = f'Start of your {self.goal.path_name} path.'
            elif required:
                reason = f"Next on your {self.goal.path_name} path, and you've finished {self.describe(required)}."
            else:
                reason = f'Next on your {self.goal.path_name} path.'
            if any(u.id in self.placed for u in self.own[step]) and found[0] is not self.own[step][0]:
                reason += f' Your skills check lets you start at unit {int(found[0].id.rsplit(".u", 1)[1])}.'
            return self.recommendation('start', reason, course, found, notes)

        # Rule 4: walk back from the first released stop through its unmet prerequisites.
        if blocked:
            ready = self.ready_prerequisite(blocked[1], seen=set())
            if ready:
                needed, target, found = ready
                return self.recommendation('prerequisite', f'{needed.title} needs {self.describe([target])} first.', self.units[found[0].id][0], found, notes)

        # Rule 5: nothing on the path can be started now.
        options = tuple(c.id for c in self.catalog.courses
                        if c.id not in self.dismissed and not self.started(c.units) and not self.unmet(c) and self.next_lesson(c.units))
        if not candidates:
            if self.goal.choose_after:
                reason = 'You have tried the first unit. Pick whatever you would like to explore next.'
            else:
                reason = f"You've completed your {self.goal.path_name} path."
            return Recommendation('choose' if options else 'caught_up', reason if options else "You've finished everything available on your path so far.", options=options, notes=tuple(notes))
        coming = [self.courses[s.course].title for s in candidates if self.courses[s.course].status != 'released']
        if coming:
            notes.append('Coming soon on your path: ' + ', '.join(dict.fromkeys(coming)) + '.')
        return Recommendation('caught_up', "You've finished everything available on your path so far.", options=options, notes=tuple(dict.fromkeys(notes)))

    def ready_prerequisite(self, course, seen):
        """Depth-first through unmet required prerequisites; returns (course that needs it, ref, next lesson)."""
        for ref in self.unmet(course):
            if ref in seen:
                continue
            seen.add(ref)
            if ref in self.courses:
                target, units = self.courses[ref], self.courses[ref].units
            else:
                target = self.units[ref][0]
                ids = [u.id for u in target.units]
                units = target.units[:ids.index(ref) + 1]
            found = self.next_lesson(units)
            if found and not self.unmet(target):
                return course, ref, found
            deeper = self.ready_prerequisite(target, seen)
            if deeper:
                return deeper
        return None

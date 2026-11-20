"""Python unit 7, "Libraries and modules": py.import, py.random, py.math-module, py.datetime and py.own-modules.

The unit's sixth lesson, py.packages-local, is a local setup tutorial that needs the ENG-09 task type, so
the unit is released with more_lessons_coming. py.random's cases are seeded (ENG-07); py.own-modules runs
the program with the learner's own grader.py (ENG-08b), given here as the Spec's modules.
"""
from lesson_suite import Spec, make_tests, LESSONS, released_unit
from test_unit2_lessons import client  # noqa: F401

ex = lambda i: LESSONS[i].task('example').code  # noqa: E731
sim = lambda i: LESSONS[i].task('challenge').similar_example.code  # noqa: E731

I_REF = 'import math\nradius = int(input())\naround = 2 * math.pi * radius\nprint(round(around, 1))\nprint(round(math.pi * radius * radius, 1))\nprint(math.ceil(around))\n'
IMPORT = Spec(
    start='import math\nradius = int(input())\n',
    reference=I_REF,
    creative=[
        'from math import pi, ceil as up\nr = int(input())\nprint(round(2 * pi * r, 1), round(pi * r ** 2, 1), up(2 * pi * r), sep="\\n")',
        'import math as m\nradius = int(input())\nprint(round(m.tau * radius, 1))\nprint(round(m.pi * m.pow(radius, 2), 1))\nprint(m.ceil(m.tau * radius))',
    ],
    wrong=[
        ('int() instead of ceil()', I_REF.replace('math.ceil(around)', 'int(around)'), 'needs_work', 'py.import.case.one'),
        ('round() with no decimal places', I_REF.replace('round(around, 1)', 'round(around)'), 'needs_work', 'py.import.case.one'),
        ('pi as 3.14', I_REF.replace('math.pi', '3.14'), 'needs_work', 'py.import.case.ten'),
        ('always at least one step', I_REF.replace('print(math.ceil(around))', 'print(math.ceil(around) or 1)'), 'needs_work', 'py.import.case.zero'),
        ('contrived: rounds the steps down for a radius of 3', I_REF.replace('print(math.ceil(around))', 'print(int(around) if radius == 3 else math.ceil(around))'), 'needs_work', 'py.import.case.three'),
        ('contrived: a whole distance for bigger towers', I_REF.replace('print(round(around, 1))', 'print(round(around, 1) if radius < 5 or radius == 10 else int(around))'), 'needs_work', 'py.import.case.seven'),
        ('no import', 'radius = int(input())\nprint(round(2 * math.pi * radius, 1))\n', 'execution_error', ('error', 'NameError', 2)),
        ('forgets int()', 'import math\nradius = input()\nprint(2 * math.pi * radius)\n', 'execution_error', ('error', 'TypeError', 3)),
        ('a module the browser does not have', 'import pygame\n' + I_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'edge': 'around', 'side': 'radius'},
    claims=[
        ('predict: only import math', 'import math\nprint(sqrt(49))', [], ('NameError',)),
        ('discover: math.sqrt(16)', 'import math\nprint(math.sqrt(16))', [], '4.0'),
        ('similar example', sim('py.import'), [], '10.0\n4\n3.142'),
    ],
)

R_REF = 'import random\ndice = int(input())\nsides = int(input())\ntotal = 0\nfor n in range(dice):\n    roll = random.randint(1, sides)\n    print(roll)\n    total = total + roll\nprint(total)\n'
RANDOM = Spec(
    start='import random\ndice = int(input())\nsides = int(input())\n',
    reference=R_REF,
    creative=[
        'from random import randint\nn = int(input())\ns = int(input())\nrolls = [randint(1, s) for i in range(n)]\nprint(*rolls, sep="\\n")\nprint(sum(rolls))',
    ],
    wrong=[
        ('rolls from 0', R_REF.replace('randint(1, sides)', 'randint(0, sides)'), 'needs_work', 'py.random.case.two'),
        ('the total holds only the last roll', R_REF.replace('total = total + roll', 'total = roll'), 'needs_work', 'py.random.case.two'),
        ('calls random.seed(1) itself', R_REF.replace('import random\n', 'import random\nrandom.seed(1)\n'), 'needs_work', 'py.random.case.twenty'),
        ('contrived: never fewer than three sides', R_REF.replace('randint(1, sides)', 'randint(1, max(sides, 3))'), 'needs_work', 'py.random.case.coins'),
        ('contrived: rolls at most four dice', R_REF.replace('range(dice)', 'range(min(dice, 4))'), 'needs_work', 'py.random.case.many'),
        ('contrived: a one-sided die rolls 0', R_REF.replace('    roll = random.randint(1, sides)\n', '    roll = random.randint(1, sides) if sides > 1 else 0\n'), 'needs_work', 'py.random.case.one-side'),
        ('no import', 'dice = int(input())\nsides = int(input())\nprint(random.randint(1, sides))\n', 'execution_error', ('error', 'NameError', 3)),
        ('forgets int()', 'import random\ndice = input()\nfor n in range(dice):\n    pass\n', 'execution_error', ('error', 'TypeError', 3)),
        ('a module the browser does not have', 'import pygame\n' + R_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'coin': 'roll', 'heads': 'total', 'flip': 'n'},
    claims=[
        ('predict: the same seed gives the same lines', ex('py.random') + '\n' + ex('py.random'), [], LESSONS['py.random'].task('example').output + '\n' + LESSONS['py.random'].task('example').output),
        ('discover: randint includes both ends', 'import random\nrandom.seed(3)\nprint(sorted({random.randint(1, 6) for n in range(200)}))', [], '[1, 2, 3, 4, 5, 6]'),
        ('similar example', sim('py.random'), [], '1'),
    ],
)

M_REF = 'import math\neast = int(input())\nnorth = int(input())\ndistance = math.sqrt(east * east + north * north)\nprint(round(distance, 2))\nprint(east + north)\nprint(math.ceil(distance))\n'
MATH = Spec(
    start='import math\neast = int(input())\nnorth = int(input())\n',
    reference=M_REF,
    creative=['import math\ne = int(input())\nn = int(input())\nd = math.hypot(e, n)\nprint(round(d, 2))\nprint(e + n)\nprint(math.ceil(d))'],
    wrong=[
        ('adds instead of squaring', M_REF.replace('east * east + north * north', 'east + north'), 'needs_work', 'py.math-module.case.three-four'),
        ('rounds to a whole number', M_REF.replace('round(distance, 2)', 'round(distance)'), 'needs_work', 'py.math-module.case.three-four'),
        ('int() instead of ceil()', M_REF.replace('math.ceil(distance)', 'int(distance)'), 'needs_work', 'py.math-module.case.one-one'),
        ('contrived: straight north as a whole number', M_REF.replace('print(round(distance, 2))', 'print(round(distance, 2) if east else north)'), 'needs_work', 'py.math-module.case.north'),
        ('contrived: never more than 10 rounded up', M_REF.replace('math.ceil(distance)', 'min(math.ceil(distance), 10)'), 'needs_work', 'py.math-module.case.longer'),
        ('contrived: a walk of at least one square', M_REF.replace('print(east + north)', 'print(max(1, east + north))'), 'needs_work', 'py.math-module.case.start'),
        ('no import', 'east = int(input())\nnorth = int(input())\nprint(math.sqrt(east))\n', 'execution_error', ('error', 'NameError', 3)),
        ('forgets int()', 'import math\neast = input()\nprint(math.sqrt(east))\n', 'execution_error', ('error', 'TypeError', 3)),
        ('a module the browser does not have', 'import pygame\n' + M_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'side': 'distance', 'area': 'east', 'boxes': 'distance', 'items': 'north'},
    claims=[
        ('predict: 0.1 + 0.2 == 0.3', 'print(0.1 + 0.2 == 0.3)', [], 'False'),
        ('guided: halves round to the even neighbour', 'print(round(0.5), round(1.5))', [], '0 2'),
        ('discover: round(2.5)', 'print(round(2.5))', [], '2'),
        ('similar example', sim('py.math-module'), [], '7.1\n8'),
    ],
)

D_REF = ('from datetime import date, timedelta\nyear = int(input())\nmonth = int(input())\nday = int(input())\nsessions = int(input())\ngap = int(input())\n'
         'start = date(year, month, day)\nweekend = 0\nfor n in range(sessions):\n    when = start + timedelta(days=n * gap)\n    print(when.isoformat())\n    if when.weekday() >= 5:\n        weekend = weekend + 1\nprint(weekend)\n')
DATES = Spec(
    start='from datetime import date, timedelta\n',
    reference=D_REF,
    creative=[
        'import datetime\nparts = [int(input()) for i in range(3)]\nsessions, gap = int(input()), int(input())\nday = datetime.date(*parts)\ncount = 0\nfor i in range(sessions):\n    print(day)\n    count += day.strftime("%a") in ("Sat", "Sun")\n    day += datetime.timedelta(gap)\nprint(count)',
    ],
    wrong=[
        ('month and day swapped', D_REF.replace('date(year, month, day)', 'date(year, day, month)'), 'needs_work', 'py.datetime.case.weekly'),
        ('the gap counted from the second session', D_REF.replace('timedelta(days=n * gap)', 'timedelta(days=(n + 1) * gap)'), 'needs_work', 'py.datetime.case.weekly'),
        ('only Saturday counts as the weekend', D_REF.replace('when.weekday() >= 5', 'when.weekday() == 5'), 'needs_work', 'py.datetime.case.month-end'),
        ('contrived: one session prints no count', D_REF.replace('print(weekend)\n', 'if sessions > 1:\n    print(weekend)\n'), 'needs_work', 'py.datetime.case.single'),
        ('contrived: skips 29 February', D_REF.replace('    print(when.isoformat())\n', '    if when.month == 2 and when.day == 29:\n        when = when + timedelta(days=1)\n    print(when.isoformat())\n'), 'needs_work', 'py.datetime.case.leap'),
        ('only Sunday counts as the weekend', D_REF.replace('when.weekday() >= 5', 'when.weekday() >= 6'), 'needs_work', 'py.datetime.case.daily'),
        ('adds days to the day number', D_REF.replace('when = start + timedelta(days=n * gap)', 'when = date(year, month, day + n * gap)'), 'execution_error', ('error', 'ValueError', 10)),
        ('no import', 'year = int(input())\nstart = date(year, 1, 1)\n', 'execution_error', ('error', 'NameError', 2)),
        ('forgets int()', 'from datetime import date\nstart = date(input(), input(), input())\n', 'execution_error', ('error', 'TypeError', 2)),
        ('a module the browser does not have', 'import pygame\n' + D_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'lesson': 'when', 'first': 'start', 'week': 'n'},
    claims=[
        ('predict: 2028 is a leap year', 'from datetime import date\nprint((date(2028, 3, 6) - date(2028, 2, 20)).days)', [], '15'),
        ('discover: isoformat', 'from datetime import date\nprint(date(2026, 3, 1).isoformat())', [], '2026-03-01'),
        ('discover: weekday() of a Monday is 0', 'from datetime import date\nprint(date(2026, 3, 2).weekday())', [], '0'),
        ('similar example', sim('py.datetime'), [], '2026-09-07 False\n2026-09-14 False\n2026-09-21 False'),
    ],
)

GRADER = 'def grade(score, total):\n    percent = score * 100 / total\n    if percent >= 90:\n        return "A"\n    if percent >= 70:\n        return "B"\n    if percent >= 50:\n        return "C"\n    return "F"\n'
O_REF = 'from grader import grade\nquizzes = int(input())\ntop = 0\nfor n in range(quizzes):\n    letter = grade(int(input()), int(input()))\n    print(letter)\n    if letter == "A":\n        top = top + 1\nprint(top)\n'
SINGLE = GRADER + '\n' + O_REF.replace('from grader import grade\n', '')
OWN = Spec(
    start='from grader import grade\n',
    reference=O_REF,
    creative=[
        'import grader\nletters = []\nfor n in range(int(input())):\n    letters.append(grader.grade(int(input()), int(input())))\nfor x in letters:\n    print(x)\nprint(letters.count("A"))',
    ],
    wrong=[
        ('> 90 leaves out exactly 90 percent', SINGLE.replace('percent >= 90', 'percent > 90'), 'needs_work', 'py.own-modules.case.three'),
        ('counts the A grades from 1', O_REF.replace('top = 0', 'top = 1'), 'needs_work', 'py.own-modules.case.three'),
        ('a perfect score gets A+', SINGLE.replace('    percent = score * 100 / total\n', '    percent = score * 100 / total\n    if score == total:\n        return "A+"\n'), 'needs_work', 'py.own-modules.case.perfect'),
        ('contrived: says so when there are no quizzes', O_REF.replace('print(top)\n', 'if quizzes == 0:\n    print("no quizzes")\nelse:\n    print(top)\n'), 'needs_work', 'py.own-modules.case.none'),
        ('> 50 leaves out exactly 50 percent', SINGLE.replace('percent >= 50', 'percent > 50'), 'needs_work', 'py.own-modules.case.boundaries'),
        ('C starts at 49 percent', SINGLE.replace('percent >= 50', 'percent >= 49'), 'needs_work', 'py.own-modules.case.just-below'),
        ('grade() used without importing it', O_REF.replace('from grader import grade\n', ''), 'execution_error', ('error', 'NameError', 4)),
        ('the replies passed as text', 'from grader import grade\nquizzes = int(input())\nfor n in range(quizzes):\n    print(grade(input(), input()))\n', 'execution_error', ('error', 'TypeError', 4)),
        ('a module the browser does not have', 'import pygame\n' + O_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'size': 'grade', 'n': 'score', 'label': 'letter'},
    claims=[('similar example', sim('py.own-modules'), [], 'small\nbig')],
    modules={'grader.py': GRADER},
)

globals().update(make_tests('py.u07', {'py.import': IMPORT, 'py.random': RANDOM, 'py.math-module': MATH, 'py.datetime': DATES, 'py.own-modules': OWN},
                            ['Toolsmith', 'Dice roller', 'Navigator', 'Timekeeper', 'Librarian']))


def test_unit_7_says_more_lessons_are_coming_until_the_local_setup_lesson_exists():
    assert released_unit('py.u07').more_lessons_coming is True
    assert 'py.packages-local' not in LESSONS


def test_the_seeded_cases_send_their_seed_and_the_own_files_start_empty():
    from lesson_suite import challenge
    assert all(c.seed is not None for c in challenge('py.random').check.cases)
    assert challenge('py.own-modules').modules == {'grader.py': '# Write grade(score, total) here\n'}

"""Python unit 8, "Trust your changes": py.assert-tests, py.test-cases, py.boundaries, py.type-hints and py.refactor.

The first three are ENG-10 lessons: the learner writes tests, and each case loads a reference program
first (the correct one, where the tests must pass, then broken ones, where they must fail). Each broken
reference has a set of tests that misses it, so every case can be shown to matter.
"""
from lesson_suite import Spec, make_tests, LESSONS, challenge
from test_unit2_lessons import client  # noqa: F401

ex = lambda i: LESSONS[i].task('example').code  # noqa: E731
sim = lambda i: LESSONS[i].task('challenge').similar_example.code  # noqa: E731

A_REF = 'assert bonus(5, 0) == 5\nassert bonus(5, 2) == 5\nassert bonus(5, 3) == 10\nassert bonus(7, 4) == 14\n'
ASSERTS = Spec(
    start='',
    reference=A_REF,
    creative=['assert bonus(1, 3) == 2\nassert bonus(0, 5) == 0\nassert bonus(8, 1) == 8\nassert bonus(3, 99) == 6'],
    wrong=[
        ('a test that can never fail', 'assert True\n', 'needs_work', 'py.assert-tests.case.never'),
        ('defines its own bonus() and tests that', 'def bonus(p, s):\n    return p * 2 if s >= 3 else p\n\nassert bonus(5, 3) == 10\n', 'needs_work', 'py.assert-tests.case.never'),
        ('only a long streak tested', 'assert bonus(5, 5) == 10\n', 'needs_work', 'py.assert-tests.case.needs-four'),
        ('only a streak of exactly 3', 'assert bonus(10, 3) == 20\n', 'needs_work', 'py.assert-tests.case.always'),
        ('only 10 points tested', 'assert bonus(10, 3) == 20\nassert bonus(10, 1) == 10\n', 'needs_work', 'py.assert-tests.case.adds'),
        ('expects the wrong answer', 'assert bonus(5, 3) == 15\n', 'needs_work', 'py.assert-tests.case.correct'),
        ('calls bonus() with one value', 'assert bonus(5) == 5\n', 'execution_error', ('error', 'TypeError', 1)),
        ('a misspelt name', 'assert bonus(5, 3) == 10\nassert bonsu(5, 0) == 5\n', 'execution_error', ('error', 'NameError', 2)),
        ('a module the browser does not have', 'import pygame\n' + A_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'half': 'bonus'},
    claims=[
        ('predict: a wrong expected value', ex('py.assert-tests').replace('assert points(4, 4) == 10', 'assert points(4, 4) == 5'), [], ('AssertionError',)),
        ('discover: a true assert does nothing', 'assert 2 + 2 == 4', [], ''),
        ('similar example', sim('py.assert-tests'), [], 'half() passed'),
    ],
)

T_REF = 'assert average([]) == 0\nassert average([2, 4]) == 3\nassert average([3, 4]) == 3.5\nassert average([1, 2, 9]) == 4\n'
CASES = Spec(
    start='',
    reference=T_REF,
    creative=['import math\nassert average([]) == 0\nassert math.isclose(average([1, 2]), 1.5)\nassert average([5, 5, 2]) == 4\n'],
    wrong=[
        ('only a typical list', 'assert average([2, 4]) == 3\n', 'needs_work', 'py.test-cases.case.empty'),
        ('no decimal answers', 'assert average([]) == 0\nassert average([2, 4]) == 3\n', 'needs_work', 'py.test-cases.case.whole'),
        ('every list ends with 0', 'assert average([]) == 0\nassert average([6, 0]) == 3\nassert average([3, 0]) == 1.5\n', 'needs_work', 'py.test-cases.case.last'),
        ('only single scores', 'assert average([]) == 0\nassert average([5]) == 5\nassert average([2.5]) == 2.5\n', 'needs_work', 'py.test-cases.case.first'),
        ('expects a whole number', 'assert average([3, 4]) == 3\n', 'needs_work', 'py.test-cases.case.correct'),
        ('two numbers instead of a list', 'assert average(2, 4) == 3\n', 'execution_error', ('error', 'TypeError', 1)),
        ('a misspelt name', 'assert averge([]) == 0\n', 'execution_error', ('error', 'NameError', 1)),
        ('a module the browser does not have', 'import pygame\n' + T_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'total': 'average', 'prices': 'scores'},
    claims=[
        ('predict: best = 0 misses all-negative lists', ex('py.test-cases').replace('best = numbers[0]', 'best = 0'), [], ('AssertionError',)),
        ('guided: biggest([]) has no first item', 'def biggest(numbers):\n    return numbers[0]\n\nbiggest([])', [], ('IndexError',)),
        ('discover: 7 / 2', 'print(7 / 2)', [], '3.5'),
        ('similar example', sim('py.test-cases'), [], 'total() passed'),
    ],
)

B_REF = 'assert ticket_price(4) == 0\nassert ticket_price(5) == 5\nassert ticket_price(12) == 5\nassert ticket_price(13) == 10\nassert ticket_price(64) == 10\nassert ticket_price(65) == 6\n'
BOUNDARIES = Spec(
    start='',
    reference=B_REF,
    creative=['for age, price in [(0, 0), (4, 0), (5, 5), (12, 5), (13, 10), (64, 10), (65, 6), (90, 6)]:\n    assert ticket_price(age) == price'],
    wrong=[
        ('only ages in the middle of each band', 'assert ticket_price(2) == 0\nassert ticket_price(8) == 5\nassert ticket_price(30) == 10\nassert ticket_price(80) == 6\n', 'needs_work', 'py.boundaries.case.five'),
        ('tests 5 but not 12', 'assert ticket_price(4) == 0\nassert ticket_price(5) == 5\n', 'needs_work', 'py.boundaries.case.twelve'),
        ('the senior edge untested', B_REF.replace('assert ticket_price(64) == 10\nassert ticket_price(65) == 6\n', ''), 'needs_work', 'py.boundaries.case.senior'),
        ('13 untested', B_REF.replace('assert ticket_price(13) == 10\n', ''), 'needs_work', 'py.boundaries.case.teen'),
        ('thinks 12-year-olds pay full price', 'assert ticket_price(12) == 10\n', 'needs_work', 'py.boundaries.case.correct'),
        ('no age given', 'assert ticket_price() == 0\n', 'execution_error', ('error', 'TypeError', 1)),
        ('a misspelt name', 'assert ticket(4) == 0\n', 'execution_error', ('error', 'NameError', 1)),
        ('a module the browser does not have', 'import pygame\n' + B_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'can_ride': 'ticket_price', 'height': 'age'},
    claims=[
        ('predict: > misses the edge', 'def can_ride(height):\n    return height > 120\n\nassert can_ride(119) == False\nassert can_ride(120) == True', [], ('AssertionError',)),
        ('similar example', sim('py.boundaries'), [], 'edge tested'),
    ],
)

H_REF = 'def shares(coins: int, friends: int) -> list[int]:\n    result = []\n    for n in range(friends):\n        if n < coins % friends:\n            result.append(coins // friends + 1)\n        else:\n            result.append(coins // friends)\n    return result\n\nprint(shares.__annotations__)\n'
HINTS = Spec(
    start='',
    reference=H_REF,
    creative=['def shares(coins: int, friends: int) -> list[int]:\n    base, extra = divmod(coins, friends)\n    out = []\n    for i in range(friends):\n        out.append(base + (i < extra))\n    return out\n\nprint(shares.__annotations__)'],
    wrong=[
        ('no hints', H_REF.replace('(coins: int, friends: int) -> list[int]:', '(coins, friends):'), 'needs_work', 'py.type-hints.case.hints'),
        ('hints on the parameters only', H_REF.replace(' -> list[int]:', ':'), 'needs_work', 'py.type-hints.case.hints'),
        ('returns the shares as text', H_REF.replace('    return result\n', '    return str(result)\n'), 'needs_work', 'py.type-hints.case.even'),
        ('every friend gets the same', 'def shares(coins: int, friends: int) -> list[int]:\n    return [coins // friends] * friends\n\nprint(shares.__annotations__)\n', 'needs_work', 'py.type-hints.case.extra'),
        ('every friend gets at least one coin', H_REF.replace('result.append(coins // friends)\n', 'result.append(max(1, coins // friends))\n'), 'needs_work', 'py.type-hints.case.fewer'),
        ('contrived: a single friend keeps one coin back', H_REF.replace('    result = []\n', '    if friends == 1:\n        return [coins - 1]\n    result = []\n'), 'needs_work', 'py.type-hints.case.one'),
        ('tried with no friends', 'def shares(coins: int, friends: int) -> list[int]:\n    base = coins // friends\n    return [base] * friends\n\nprint(shares.__annotations__)\nprint(shares(5, 0))\n', 'execution_error', ('error', 'ZeroDivisionError', 2)),
        ('a hint with a capital letter', H_REF.replace('coins: int', 'coins: Int'), 'execution_error', ('error', 'NameError', 1)),
        ('a list passed to range()', H_REF.replace('range(friends)', 'range([friends])'), 'execution_error', ('error', 'TypeError', 3)),
        ('a module the browser does not have', 'import pygame\n' + H_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'split': 'shares', 'total': 'coins', 'parts': 'friends', 'base': 'share'},
    claims=[
        ('predict: hints are not checked', 'def twice(word: int) -> int:\n    return word * 2\n\nprint(twice("ha"))', [], 'haha'),
        ('guided: twice(3)', 'def twice(word: int) -> int:\n    return word * 2\n\nprint(twice(3))', [], '6'),
        ('similar example', sim('py.type-hints'), [], "Ada (15)\n{'name': <class 'str'>, 'age': <class 'int'>, 'return': <class 'str'>}"),
    ],
)

MESSY = challenge('py.refactor').starter
R_REF = ('PRICES = {"bread": 3, "milk": 2, "apple": 1}\n\ndef cost(item, amount):\n    return PRICES.get(item, 0) * amount\n\n'
         'orders = int(input("How many orders? "))\ntotal = 0\nfor n in range(orders):\n    item = input("Item? ")\n    amount = int(input("Amount? "))\n'
         '    price = cost(item, amount)\n    print(item, price)\n    total = total + price\nprint("total", total)\n')
REFACTOR = Spec(
    start='',
    reference=R_REF,
    creative=['def cost(item, amount):\n    prices = {"bread": 3, "milk": 2, "apple": 1}\n    if item not in prices:\n        return 0\n    return prices[item] * amount\n\ntotal = 0\nfor n in range(int(input())):\n    item, amount = input(), int(input())\n    print(item, cost(item, amount))\n    total += cost(item, amount)\nprint("total", total)'],
    wrong=[
        ('the starter as it is', MESSY, 'needs_work', 'py.refactor.case.cost'),
        ('a price changed while tidying', R_REF.replace('"bread": 3', '"bread": 4'), 'needs_work', 'py.refactor.case.orders'),
        ('stops printing what the shop does not sell', R_REF.replace('    print(item, price)\n', '    if price > 0:\n        print(item, price)\n'), 'needs_work', 'py.refactor.case.unknown'),
        ('cost() takes the amount first', R_REF.replace('def cost(item, amount):', 'def cost(amount, item):').replace('cost(item, amount)\n    print', 'cost(amount, item)\n    print'), 'needs_work', 'py.refactor.case.cost'),
        ('contrived: no total line for an empty day', R_REF.replace('print("total", total)\n', 'if orders:\n    print("total", total)\n'), 'needs_work', 'py.refactor.case.none'),
        ('cost() forgets its last return', R_REF.replace('    return PRICES.get(item, 0) * amount\n', '    if item in PRICES:\n        return PRICES[item] * amount\n').replace('    price = cost(item, amount)\n', '    price = cost(item, amount) if item in PRICES else 0\n'), 'needs_work', 'py.refactor.case.cost-unknown'),
        ('square brackets for an unknown item', R_REF.replace('PRICES.get(item, 0)', 'PRICES[item]'), 'execution_error', ('error', 'KeyError', 4)),
        ('a misspelt name', R_REF.replace('price = cost(item, amount)', 'price = cst(item, amount)'), 'execution_error', ('error', 'NameError', 11)),
        ('the amount left as text', R_REF.replace('amount = int(input("Amount? "))', 'amount = input("Amount? ")'), 'execution_error', ('error', 'TypeError', 13)),
        ('a module the browser does not have', 'import pygame\n' + R_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'rates': 'PRICES', 'fee': 'cost', 'kind': 'item', 'hours': 'amount'},
    claims=[
        ('predict: the rule changes in one place', ex('py.refactor').replace('pages * 3', 'pages * 4'), [], '18\n30\n38'),
        ('the starter prints what the tidy version prints', MESSY, ['3', 'bread', '2', 'milk', '1', 'apple', '5'], 'bread 6\nmilk 2\napple 5\ntotal 13'),
        ('similar example', sim('py.refactor'), [], '8\n0'),
    ],
)

globals().update(make_tests('py.u08', {'py.assert-tests': ASSERTS, 'py.test-cases': CASES, 'py.boundaries': BOUNDARIES, 'py.type-hints': HINTS, 'py.refactor': REFACTOR},
                            ['Tester', 'Case finder', 'Edge walker', 'Label maker', 'Tidy coder']))


def test_no_correct_reference_is_handed_out_as_the_answer():
    # browser-checks.md section 11: every reference reaches the browser, so the correct one must not be
    # the lesson's answer. In these three lessons the learner writes tests, never the function.
    for lesson_id in ('py.assert-tests', 'py.test-cases', 'py.boundaries'):
        assert 'Do not write' in challenge(lesson_id).prompt
        assert all(case.reference for case in challenge(lesson_id).check.cases)

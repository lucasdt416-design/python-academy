"""Python unit 6, "Recover and investigate": py.tracebacks, py.debug-strategy, py.try-except, py.raise and py.validate-input.

py.tracebacks and py.debug-strategy start from a broken program in the editor; the starter itself is
one of the wrong programs, so it is proven to fail with the error or case the lesson is about.
"""
from lesson_suite import Spec, make_tests, LESSONS, challenge
from test_unit2_lessons import client  # noqa: F401

ex = lambda i: LESSONS[i].task('example').code  # noqa: E731
sim = lambda i: LESSONS[i].task('challenge').similar_example.code  # noqa: E731

LEDGER = challenge('py.tracebacks').starter
T_REF = ('def total_cost(prices):\n    total = 0\n    for i in range(len(prices)):\n        total = total + prices[i]\n    return total\n\n'
         'count = int(input("How many items? "))\nprices = []\nfor n in range(count):\n    prices.append(int(input("Price? ")))\n'
         'print("Total: " + str(total_cost(prices)))\nprint("Most expensive: " + str(max(prices)))\n')
TRACEBACKS = Spec(
    start='',
    reference=T_REF,
    creative=[
        'count = int(input())\nprices = [int(input()) for n in range(count)]\nprint("Total:", sum(prices))\nprint("Most expensive:", max(prices))',
        LEDGER.replace('range(len(prices) + 1)', 'range(len(prices))').replace('prices.append(input("Price? "))', 'prices.append(int(input("Price? ")))').replace('"Total: " + total_cost(prices)', '"Total: " + str(total_cost(prices))'),
    ],
    wrong=[
        ('the starter as it is', LEDGER, 'execution_error', ('error', 'TypeError', 5)),
        ('only int() fixed', LEDGER.replace('prices.append(input("Price? "))', 'prices.append(int(input("Price? ")))'), 'execution_error', ('error', 'IndexError', 5)),
        ('int() and the range fixed', LEDGER.replace('prices.append(input("Price? "))', 'prices.append(int(input("Price? ")))').replace('range(len(prices) + 1)', 'range(len(prices))'), 'execution_error', ('error', 'TypeError', 12)),
        ('the total printed without its label', T_REF.replace('print("Total: " + str(total_cost(prices)))', 'print(total_cost(prices))'), 'needs_work', 'py.tracebacks.case.three'),
        ('contrived: one price counted twice', T_REF.replace('    return total\n', '    if len(prices) == 1:\n        return total * 2\n    return total\n'), 'needs_work', 'py.tracebacks.case.one'),
        ('compares the prices as text', T_REF.replace('prices.append(int(input("Price? ")))', 'prices.append(input("Price? "))').replace('total = total + prices[i]', 'total = total + int(prices[i])'), 'needs_work', 'py.tracebacks.case.digits'),
        ('contrived: adds only the first four prices', T_REF.replace('range(len(prices))', 'range(min(len(prices), 4))'), 'needs_work', 'py.tracebacks.case.longer'),
        ('contrived: equal prices counted once', T_REF.replace('print("Total: " + str(total_cost(prices)))', 'print("Total: " + str(sum(set(prices))))'), 'needs_work', 'py.tracebacks.case.same'),
        ('a misspelt name', T_REF.replace('str(max(prices))', 'str(max(price))'), 'execution_error', ('error', 'NameError', 12)),
        ('a module the browser does not have', 'import pygame\n' + T_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'ages': 'prices', 'age': 'price', 'sum': 'total', 'oldest': 'total'},
    claims=[
        ('example note: without int() the adding fails', 'prices = ["5", "12"]\ntotal = 0\nfor price in prices:\n    total = total + price', [], ('TypeError',)),
        ('predict: a misspelt total', 'total = 1\nprint(totl)', [], ('NameError',)),
        ('hint: text is compared as text', 'print(max(["9", "10"]))', [], '9'),
        ('similar example', sim('py.tracebacks'), [], 'Oldest: 15'),
    ],
)

TALLY = challenge('py.debug-strategy').starter
D_REF = ('rounds = int(input("Rounds? "))\nbest = None\nwins = 0\nfor r in range(rounds):\n    points = int(input("Points? "))\n'
         '    if best is None or points > best:\n        best = points\n    if points >= 10:\n        wins = wins + 1\nprint(best)\nprint(wins)\n')
FIXED_TWO = TALLY.replace('range(1, rounds)', 'range(rounds)').replace('points > 10', 'points >= 10')
DEBUG = Spec(
    start='rounds = int(input("Rounds? "))\n',
    reference=D_REF,
    creative=[
        'rounds = int(input())\nbest = int(input())\nwins = 1 if best >= 10 else 0\nfor r in range(rounds - 1):\n    points = int(input())\n    best = max(best, points)\n    if points >= 10:\n        wins += 1\nprint(best)\nprint(wins)',
        FIXED_TWO.replace('best = 0', 'best = -1000000'),
    ],
    wrong=[
        ('the starter as it is', TALLY, 'needs_work', 'py.debug-strategy.case.three'),
        ('only the range fixed', TALLY.replace('range(1, rounds)', 'range(rounds)'), 'needs_work', 'py.debug-strategy.case.three'),
        ('contrived: a single round is never a win', D_REF.replace('if points >= 10:', 'if points >= 10 and rounds > 1:'), 'needs_work', 'py.debug-strategy.case.single'),
        ('best still starts at 0', FIXED_TWO, 'needs_work', 'py.debug-strategy.case.lost'),
        ('contrived: never more than two wins', D_REF.replace('if points >= 10:', 'if points >= 10 and wins < 2:'), 'needs_work', 'py.debug-strategy.case.long'),
        ('contrived: 11 is not a win', D_REF.replace('if points >= 10:', 'if points >= 10 and points != 11:'), 'needs_work', 'py.debug-strategy.case.boundary'),
        ('a misspelt name', D_REF.replace('print(best)', 'print(bset)'), 'execution_error', ('error', 'NameError', 10)),
        ('None compared without a check', D_REF.replace('if best is None or points > best:', 'if points > best:'), 'execution_error', ('error', 'TypeError', 6)),
        ('reads one round too many', D_REF.replace('range(rounds)', 'range(rounds + 1)'), 'needs_work', ('missing_input', 'EOFError', 5)),
        ('a module the browser does not have', 'import pygame\n' + D_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'lowest': 'best', 'temp': 'points', 'temps': 'scores'},
    claims=[
        ('predict: range(1, 3) runs twice', 'n = 0\nfor r in range(1, 3):\n    n += 1\nprint(n)', [], '2'),
        ('guided: a step of -1', 'for n in range(5, 0, -1):\n    print("n is", n)', [], 'n is 5\nn is 4\nn is 3\nn is 2\nn is 1'),
        ('error hint: hint 1 on the starter, one round of 15', TALLY, ['1', '15'], '0\n0'),
        ('error hint: None > 5', 'print(None > 5)', [], ('TypeError',)),
        ('similar example', sim('py.debug-strategy'), [], 'checking 3 lowest so far None\nchecking -2 lowest so far 3\nchecking 5 lowest so far -2\n-2'),
    ],
)

E_REF = 'try:\n    coins = int(input("Coins? "))\n    friends = int(input("Friends? "))\n    print(coins // friends)\n    print(coins % friends)\nexcept ValueError:\n    print("not a number")\nexcept ZeroDivisionError:\n    print("nobody to share with")\n'
TRY = Spec(
    start='',
    reference=E_REF,
    creative=[
        'a = input()\nb = input()\ntry:\n    coins, friends = int(a), int(b)\n    share, left = divmod(coins, friends)\nexcept ValueError:\n    print("not a number")\nexcept ZeroDivisionError:\n    print("nobody to share with")\nelse:\n    print(share)\n    print(left)',
        'try:\n    coins = int(input())\n    friends = int(input())\n    if friends == 0:\n        print("nobody to share with")\n    else:\n        print(coins // friends, coins % friends, sep="\\n")\nexcept ValueError:\n    print("not a number")',
    ],
    wrong=[
        ('/ instead of //', E_REF.replace('coins // friends', 'coins / friends'), 'needs_work', 'py.try-except.case.share'),
        ('another message for a word', E_REF.replace('print("not a number")', 'print("not a whole number")'), 'needs_work', 'py.try-except.case.word'),
        ('prints 0 when there are no friends', E_REF.replace('print("nobody to share with")', 'print(0)'), 'needs_work', 'py.try-except.case.nobody'),
        ('contrived: friends that are not a number count as 1', 'try:\n    coins = int(input())\nexcept ValueError:\n    print("not a number")\nelse:\n    try:\n        friends = int(input())\n    except ValueError:\n        friends = 1\n    if friends == 0:\n        print("nobody to share with")\n    else:\n        print(coins // friends)\n        print(coins % friends)\n', 'needs_work', 'py.try-except.case.bad-friends'),
        ('turns a decimal into a whole number', E_REF.replace('coins = int(input("Coins? "))', 'coins = int(float(input("Coins? ")))'), 'needs_work', 'py.try-except.case.decimal'),
        ('only ValueError caught', E_REF.replace('except ZeroDivisionError:\n    print("nobody to share with")\n', ''), 'execution_error', ('error', 'ZeroDivisionError', 4)),
        ('only ZeroDivisionError caught', E_REF.replace('except ValueError:\n    print("not a number")\n', ''), 'execution_error', ('error', 'ValueError', 2)),
        ('a try block with no indent', 'try:\nprint(1)\n', 'execution_error', ('error', 'IndentationError', 2)),
        ('a module the browser does not have', 'import pygame\n' + E_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'reply': 'coins', 'n': 'coins'},
    claims=[
        ('predict: "4.5" is not a whole number', 'try:\n    int("4.5")\nexcept ValueError:\n    print("not a number")', [], 'not a number'),
        ('discover: int("seven")', 'int("seven")', [], ('ValueError',)),
        ('guided: without the ZeroDivisionError block', 'try:\n    print(60 // int("0"))\nexcept ValueError:\n    print("not a number")', [], ('ZeroDivisionError',)),
        ('similar example', sim('py.try-except'), [], '6\ntry again'),
    ],
)

R_FN = 'def set_lives(lives):\n    if lives < 1 or lives > 9:\n        raise ValueError("lives must be from 1 to 9")\n    return lives\n'
R_REF = R_FN + '\ntry:\n    print(set_lives(int(input("Lives? "))))\nexcept ValueError as error:\n    print("Refused:", error)\n'
RAISE = Spec(
    start='',
    reference=R_REF,
    creative=[
        'def set_lives(lives):\n    if 1 <= lives <= 9:\n        return lives\n    raise ValueError("lives must be from 1 to 9")\n\nwanted = int(input())\ntry:\n    got = set_lives(wanted)\n    print(got)\nexcept ValueError as problem:\n    print(f"Refused: {problem}")',
        R_FN + '\nreply = input()\ntry:\n    lives = set_lives(int(reply))\nexcept ValueError as e:\n    print("Refused: " + str(e))\nelse:\n    print(lives)',
    ],
    wrong=[
        ('a label before the lives', R_REF.replace('print(set_lives(int(input("Lives? "))))', 'print("Lives:", set_lives(int(input("Lives? "))))'), 'needs_work', 'py.raise.case.keep'),
        ('the message left out', R_REF.replace('print("Refused:", error)', 'print("Refused")'), 'needs_work', 'py.raise.case.too-many'),
        ('prints the refusal instead of raising', 'def set_lives(lives):\n    if lives < 1 or lives > 9:\n        print("Refused: lives must be from 1 to 9")\n    return lives\n\nprint(set_lives(int(input())))\n', 'needs_work', 'py.raise.case.too-many'),
        ('set_lives prints instead of returning', 'def set_lives(lives):\n    if lives < 1 or lives > 9:\n        raise ValueError("lives must be from 1 to 9")\n    print(lives)\n\ntry:\n    set_lives(int(input()))\nexcept ValueError as error:\n    print("Refused:", error)\n', 'needs_work', 'py.raise.case.function'),
        ('< 0 lets 0 lives through', R_REF.replace('lives < 1', 'lives < 0'), 'needs_work', 'py.raise.case.zero'),
        ('9 refused', R_REF.replace('lives > 9', 'lives >= 9'), 'needs_work', 'py.raise.case.edges'),
        ('contrived: only 0 and too many are refused', R_REF.replace('lives < 1 or lives > 9', 'lives == 0 or lives > 9'), 'needs_work', 'py.raise.case.negative'),
        ('raises the wrong kind of error', R_REF.replace('raise ValueError', 'raise TypeError'), 'execution_error', ('error', 'TypeError', 3)),
        ('set_lives called outside the try', R_FN + '\nlives = set_lives(int(input()))\nprint(lives)\n', 'execution_error', ('error', 'ValueError', 3)),
        ('the error named e but printed as error', R_REF.replace('except ValueError as error:', 'except ValueError as e:'), 'execution_error', ('error', 'NameError', 9)),
        ('a module the browser does not have', 'import pygame\n' + R_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'set_speed': 'set_lives', 'speed': 'lives'},
    claims=[
        ('predict: nothing catches it', R_FN.replace('lives', 'guess') + '\nset_guess(0)'.replace('set_guess', 'set_' + 'guess'), [], ('ValueError',)),
        ('guided: 100 is allowed', ex('py.raise').replace('[50, 200]', '[100]'), [], '100'),
        ('similar example', sim('py.raise'), [], 'Slow down: speed must be positive'),
    ],
)

V_REF = ('tries = 0\nwhile True:\n    tries = tries + 1\n    reply = input("Travellers? ")\n    try:\n        travellers = int(reply)\n    except ValueError:\n'
         '        print("not a number")\n        continue\n    if 1 <= travellers <= 8:\n        break\n    print("from 1 to 8 only")\nprint(tries)\nprint(travellers)\n')
VALIDATE = Spec(
    start='',
    reference=V_REF,
    creative=[
        'count = 0\ndone = False\nwhile not done:\n    count += 1\n    text = input()\n    try:\n        n = int(text)\n        if n < 1 or n > 8:\n            print("from 1 to 8 only")\n        else:\n            done = True\n    except ValueError:\n        print("not a number")\nprint(count)\nprint(n)',
    ],
    wrong=[
        ('tries counted only for numbers', V_REF.replace('    tries = tries + 1\n', '').replace('        travellers = int(reply)\n', '        travellers = int(reply)\n        tries = tries + 1\n'), 'needs_work', 'py.validate-input.case.mixed'),
        ('an empty reply skipped without a word', V_REF.replace('    tries = tries + 1\n    reply = input("Travellers? ")\n', '    reply = input("Travellers? ")\n    if reply == "":\n        continue\n    tries = tries + 1\n'), 'needs_work', 'py.validate-input.case.empty'),
        ('0 allowed', V_REF.replace('1 <= travellers <= 8', '0 <= travellers <= 8'), 'needs_work', 'py.validate-input.case.zero'),
        ('turns a decimal into a whole number', V_REF.replace('int(reply)', 'int(float(reply))'), 'needs_work', 'py.validate-input.case.decimal'),
        ('the travellers printed before the tries', V_REF.replace('print(tries)\nprint(travellers)\n', 'print(travellers)\nprint(tries)\n'), 'needs_work', 'py.validate-input.case.first-time'),
        ('8 refused', V_REF.replace('1 <= travellers <= 8', '1 <= travellers < 8'), 'needs_work', ('missing_input', 'EOFError', 4)),
        ('never asks again', 'tries = 1\nreply = input()\nwhile True:\n    try:\n        travellers = int(reply)\n        break\n    except ValueError:\n        print("not a number")\nprint(tries)\nprint(travellers)\n', 'execution_error', ('output_limit', None, None)),
        ('a misspelt name', V_REF.replace('print(travellers)', 'print(traveller)'), 'execution_error', ('error', 'NameError', 14)),
        ('no int() check in a try', 'tries = 0\nwhile True:\n    tries = tries + 1\n    travellers = int(input())\n    if 1 <= travellers <= 8:\n        break\nprint(tries)\nprint(travellers)\n', 'execution_error', ('error', 'ValueError', 4)),
        ('a module the browser does not have', 'import pygame\n' + V_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'age': 'travellers', 'replies': 'tries'},
    claims=[
        ('predict: an empty reply first', ex('py.validate-input'), ['', '3'], 'Type a number.\nYou open door 3'),
        ('discover: int("") is a ValueError', 'int("")', [], ('ValueError',)),
        ('similar example', sim('py.validate-input'), [], 'not a number\nout of range\nok 15'),
    ],
)

globals().update(make_tests('py.u06', {'py.tracebacks': TRACEBACKS, 'py.debug-strategy': DEBUG, 'py.try-except': TRY, 'py.raise': RAISE, 'py.validate-input': VALIDATE},
                            ['Crash reader', 'Bug hunter', 'Safety net', 'Rule maker', 'Gatekeeper']))


def test_the_broken_starters_really_are_broken_and_the_lesson_says_how_many_bugs():
    assert 'three bugs' in challenge('py.tracebacks').prompt and 'three bugs' in challenge('py.debug-strategy').prompt

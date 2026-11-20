"""Python unit 5, "Organize your code": py.functions, py.parameters, py.return-values, py.scope and py.decompose.

Most cases here call the learner's function (ENG-06): tests/case_runner.py now calls it the way the
worker's __academy_call does, and the reports go to the real judge with `returned`, as the page sends them.
"""
from lesson_suite import Spec, make_tests, LESSONS
from test_unit2_lessons import client  # noqa: F401

ex = lambda i: LESSONS[i].task('example').code  # noqa: E731
sim = lambda i: LESSONS[i].task('challenge').similar_example.code  # noqa: E731

CROSSING = 'def crossing():\n    print("Step on the stones.")\n    print("The water rushes past.")\n    print("You reach the far bank.")\n'
RIVER = '    print("Step on the stones.")\n    print("The water rushes past.")\n    print("You reach the far bank.")\n'
F_REF = CROSSING + '\ndef journey():\n    print("Day begins.")\n    crossing()\n    crossing()\n    print("Night falls.")\n\njourney()\n'
FUNCTIONS = Spec(
    start='',
    reference=F_REF,
    creative=[
        'def crossing():\n    print("Step on the stones.\\nThe water rushes past.\\nYou reach the far bank.")\n\ndef journey():\n    print("Day begins.")\n    times = 0\n    while times < 2:\n        crossing()\n        times += 1\n    print("Night falls.")\n\njourney()',
        CROSSING + '\ndef journey():\n    print("Day begins.")\n' + RIVER + RIVER + '    print("Night falls.")\n\njourney()',
    ],
    wrong=[
        ('defined but never called', F_REF.replace('\njourney()\n', '\n'), 'needs_work', 'py.functions.case.program'),
        ('the river crossed once', F_REF.replace('    crossing()\n    crossing()\n', '    crossing()\n'), 'needs_work', 'py.functions.case.program'),
        ('no crossing function: its lines written into journey', 'def journey():\n    print("Day begins.")\n' + RIVER + RIVER + '    print("Night falls.")\n\njourney()\n', 'needs_work', 'py.functions.case.crossing'),
        ('crossing prints the day too', F_REF.replace('def crossing():\n', 'def crossing():\n    print("Day begins.")\n').replace('    print("Day begins.")\n    crossing()', '    crossing()'), 'needs_work', 'py.functions.case.program'),
        ('journey written as plain lines, not a function', CROSSING + '\nprint("Day begins.")\ncrossing()\ncrossing()\nprint("Night falls.")\n', 'needs_work', 'py.functions.case.journey'),
        ('called above its definition', 'journey()\n' + F_REF.replace('\njourney()\n', '\n'), 'execution_error', ('error', 'NameError', 1)),
        ('a function body with no indent', 'def crossing():\nprint("Step on the stones.")\n', 'execution_error', ('error', 'IndentationError', 2)),
        ('a module the browser does not have', 'import pygame\n' + F_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'chorus': 'crossing', 'song': 'journey'},
    claims=[
        ('predict: no calls, so only Night falls.', ex('py.functions').replace('\ncampfire()\ncampfire()', ''), [], 'Night falls.'),
        ('discover: a name without brackets does not run it', 'def campfire():\n    print("The fire crackles.")\n\ncampfire', [], ''),
        ('similar example', sim('py.functions'), [], 'Verse one\nLa la la\nVerse two\nLa la la'),
    ],
)

P_REF = 'def scene(hero, place, mood="calm"):\n    print(hero + " is in " + place + ", feeling " + mood + ".")\n'
PARAMETERS = Spec(
    start='',
    reference=P_REF,
    creative=[
        'def scene(hero, place, mood="calm"):\n    print(hero, "is in", place + ",", "feeling", mood + ".")',
        'def scene(hero, place, mood="calm"):\n    line = "{} is in {}, feeling {}.".format(hero, place, mood)\n    print(line)',
        'def scene(hero, place, mood=None):\n    if mood is None:\n        mood = "calm"\n    print(f"{hero} is in {place}, feeling {mood}.")',
    ],
    wrong=[
        ('hero and place swapped in the def line', P_REF.replace('scene(hero, place,', 'scene(place, hero,'), 'needs_work', 'py.parameters.case.default'),
        ('no default for the mood', P_REF.replace('mood="calm"', 'mood'), 'needs_work', 'py.parameters.case.default'),
        ('the mood is always calm', P_REF.replace('", feeling " + mood + "."', '", feeling calm."'), 'needs_work', 'py.parameters.case.mood'),
        ('the mood parameter has another name', P_REF.replace('mood="calm"', 'feeling="calm"').replace('+ mood +', '+ feeling +'), 'needs_work', 'py.parameters.case.named'),
        ('contrived: only knows the example heroes', 'def scene(hero, place, mood="calm"):\n    if hero not in ["Nova", "Kai", "Ada", "Lin"]:\n        hero = "Someone"\n    print(hero + " is in " + place + ", feeling " + mood + ".")\n', 'needs_work', 'py.parameters.case.other'),
        ('other names for the hero and the place', 'def scene(name, where, mood="calm"):\n    print(name + " is in " + where + ", feeling " + mood + ".")\n', 'needs_work', 'py.parameters.case.named-all'),
        ('a misspelt parameter', 'def scene(hero, place, mood="calm"):\n    print(heroo)\n', 'execution_error', ('error', 'NameError', 2)),
        ('adds a number to the text', 'def scene(hero, place, mood="calm"):\n    print(hero + 1)\n', 'execution_error', ('error', 'TypeError', 2)),
        ('a module the browser does not have', 'import pygame\n' + P_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'order': 'scene', 'dish': 'hero', 'drink': 'mood'},
    claims=[
        ('predict: arguments in order', 'def arrive(hero, place="the harbour"):\n    print(hero + " arrives at " + place + ".")\n\narrive("the tower", "Kai")', [], 'the tower arrives at Kai.'),
        ('guided: a default for hero too', 'def arrive(hero="Someone", place="the harbour"):\n    print(hero + " arrives at " + place + ".")\n\narrive()', [], 'Someone arrives at the harbour.'),
        ('similar example', sim('py.parameters'), [], 'soup with water.\npie with milk.'),
    ],
)

R_REF = 'def score(secret, guess):\n    gap = abs(secret - guess)\n    if gap == 0:\n        return 10\n    if gap <= 2:\n        return 5\n    if gap <= 10:\n        return 1\n    return 0\n\ndef verdict(secret, guess):\n    return score(secret, guess), guess > secret\n'
R_VERDICT = '\ndef verdict(secret, guess):\n    return score(secret, guess), guess > secret\n'
RETURNS = Spec(
    start='',
    reference=R_REF,
    creative=[
        'def score(s, g):\n    if s == g:\n        return 10\n    elif g - 2 <= s <= g + 2:\n        return 5\n    elif -10 <= s - g <= 10:\n        return 1\n    return 0\n\ndef verdict(s, g):\n    return [score(s, g), g > s]',
        'def score(secret, guess):\n    d = max(secret, guess) - min(secret, guess)\n    result = 0\n    if d <= 10:\n        result = 1\n    if d <= 2:\n        result = 5\n    if d == 0:\n        result = 10\n    return result\n\ndef verdict(secret, guess):\n    high = False\n    if guess > secret:\n        high = True\n    return (score(secret, guess), high)',
    ],
    wrong=[
        ('prints instead of returning', 'def score(secret, guess):\n    gap = abs(secret - guess)\n    if gap == 0:\n        print(10)\n    elif gap <= 2:\n        print(5)\n    elif gap <= 10:\n        print(1)\n    else:\n        print(0)\n' + R_VERDICT, 'needs_work', 'py.return-values.case.right'),
        ('the bands checked from the bottom', 'def score(secret, guess):\n    gap = abs(secret - guess)\n    if gap <= 10:\n        return 1\n    if gap <= 2:\n        return 5\n    if gap == 0:\n        return 10\n    return 0\n' + R_VERDICT, 'needs_work', 'py.return-values.case.right'),
        ('< 2 leaves out a guess 2 away', R_REF.replace('gap <= 2', 'gap < 2'), 'needs_work', 'py.return-values.case.close'),
        ('verdict returns only the score', R_REF.replace('return score(secret, guess), guess > secret', 'return score(secret, guess)'), 'needs_work', 'py.return-values.case.verdict'),
        ('no verdict function', R_REF.split('\ndef verdict')[0], 'needs_work', 'py.return-values.case.verdict'),
        ('no return for the last band', R_REF.replace('    return 0\n', ''), 'needs_work', 'py.return-values.case.far'),
        ('too high measured with abs()', R_REF.replace('guess > secret', 'abs(guess - secret) > 0'), 'needs_work', 'py.return-values.case.verdict-low'),
        ('a misspelt parameter', 'def score(secret, guess):\n    return abs(secret - gues)\n', 'execution_error', ('error', 'NameError', 2)),
        ('adds text to a number', 'def score(secret, guess):\n    return secret - guess + "points"\n', 'execution_error', ('error', 'TypeError', 2)),
        ('a module the browser does not have', 'import pygame\n' + R_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'grade': 'score', 'mark': 'guess'},
    claims=[
        ('predict: print instead of return gives None + None', 'def points(tries):\n    if tries == 1:\n        print(10)\n    print(10 - tries * 2)\n\ntotal = points(1) + points(3)', [], ('TypeError',)),
        ('discover: double(4)', 'def double(n):\n    return n * 2\n\nx = double(4)\nprint(x)', [], '8'),
        ('discover: no return gives None', 'def nothing():\n    pass\n\nprint(nothing())', [], 'None'),
        ('guided: points(5)', ex('py.return-values') + '\nprint(points(5))', [], '14\n6\n0'),
        ('similar example', sim('py.return-values'), [], 'A\nB\nC'),
    ],
)

S_SPEND = '\ndef spend(coins, price):\n    if coins >= price:\n        return coins - price, True\n    return coins, False\n'
S_REF = 'def collect(coins, found):\n    return coins + found\n' + S_SPEND
SCOPE = Spec(
    start='',
    reference=S_REF,
    creative=[
        'def collect(coins, found):\n    coins = coins + found\n    return coins\n\ndef spend(coins, price):\n    paid = coins >= price\n    if paid:\n        coins -= price\n    return [coins, paid]',
        'def collect(a, b):\n    return sum([a, b])\n\ndef spend(purse, cost):\n    return (purse - cost, True) if purse >= cost else (purse, False)',
    ],
    wrong=[
        ('collect returns only what was found', 'def collect(coins, found):\n    return found\n' + S_SPEND, 'needs_work', 'py.scope.case.collect'),
        ('spend returns only the coins left', 'def collect(coins, found):\n    return coins + found\n\ndef spend(coins, price):\n    return coins - price\n', 'needs_work', 'py.scope.case.spend'),
        ('pays even when the price is too high', 'def collect(coins, found):\n    return coins + found\n\ndef spend(coins, price):\n    return coins - price, coins >= price\n', 'needs_work', 'py.scope.case.too-dear'),
        ('> leaves out spending every coin', S_REF.replace('coins >= price', 'coins > price'), 'needs_work', 'py.scope.case.exact'),
        ('collect uses the outer coins, not the parameter', 'coins = 10\n\ndef collect(purse, found):\n    return coins + found\n' + S_SPEND, 'needs_work', 'py.scope.case.collect-zero'),
        ('changes an outer name', 'coins = 0\n\ndef collect(c, found):\n    coins = coins + found\n    return coins\n', 'execution_error', ('error', 'UnboundLocalError', 4)),
        ('a misspelt parameter', 'def collect(coins, found):\n    return coin + found\n', 'execution_error', ('error', 'NameError', 2)),
        ('a module the browser does not have', 'import pygame\n' + S_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'eat': 'spend', 'food': 'coins', 'bite': 'price'},
    claims=[
        ('predict: assigning makes a name local', 'score = 0\n\ndef bonus():\n    score = score + 50\n\nbonus()', [], ('UnboundLocalError',)),
        ('guided: printing before assigning', 'score = 0\n\ndef bonus():\n    print(score)\n    score = 50\n\nbonus()', [], ('UnboundLocalError',)),
        ('discover: reading an outer name works', 'score = 3\n\ndef show():\n    print(score)\n\nshow()', [], '3'),
        ('similar example', sim('py.scope'), [], '5'),
    ],
)

D_DAMAGE = 'def damage(attack, armour):\n    return max(0, attack - armour)\n'
D_FIGHT = '\ndef fight(hero_hp, attack, armour):\n    return max(0, hero_hp - damage(attack, armour))\n'
D_SURVIVES = '\ndef survives(hero_hp, attacks, armour):\n    hp = hero_hp\n    for attack in attacks:\n        hp = fight(hp, attack, armour)\n    return hp > 0\n'
D_REF = D_DAMAGE + D_FIGHT + D_SURVIVES
DECOMPOSE = Spec(
    start='',
    reference=D_REF,
    creative=[
        'def damage(attack, armour):\n    d = attack - armour\n    return d if d > 0 else 0\n\ndef fight(hero_hp, attack, armour):\n    left = hero_hp - damage(attack, armour)\n    return left if left > 0 else 0\n\ndef survives(hero_hp, attacks, armour):\n    i = 0\n    while i < len(attacks) and hero_hp > 0:\n        hero_hp = fight(hero_hp, attacks[i], armour)\n        i += 1\n    return hero_hp > 0',
        'def survives(hero_hp, attacks, armour):\n    for a in attacks:\n        hero_hp = fight(hero_hp, a, armour)\n    return not hero_hp == 0\n\ndef fight(hero_hp, attack, armour):\n    return max(hero_hp - damage(attack, armour), 0)\n\ndef damage(attack, armour):\n    return max(attack - armour, 0)',
    ],
    wrong=[
        ('armour adds to the damage', D_REF.replace('attack - armour', 'attack + armour'), 'needs_work', 'py.decompose.case.damage'),
        ('damage can go below 0', D_REF.replace('max(0, attack - armour)', 'attack - armour'), 'needs_work', 'py.decompose.case.armour'),
        ('fight ignores the armour', D_REF.replace('hero_hp - damage(attack, armour)', 'hero_hp - attack'), 'needs_work', 'py.decompose.case.fight'),
        ('survives forgets the armour', D_REF.replace('fight(hp, attack, armour)', 'fight(hp, attack, 0)'), 'needs_work', 'py.decompose.case.survives'),
        ('survives counts 0 health as alive', D_REF.replace('return hp > 0', 'return hp >= 0'), 'needs_work', 'py.decompose.case.falls'),
        ('survives never stores the new health', D_REF.replace('        hp = fight(hp, attack, armour)', '        fight(hp, attack, armour)'), 'needs_work', 'py.decompose.case.falls'),
        ('fight can go below 0', D_REF.replace('max(0, hero_hp - damage(attack, armour))', 'hero_hp - damage(attack, armour)'), 'needs_work', 'py.decompose.case.heavy'),
        ('a misspelt function name', D_DAMAGE + '\ndef fight(hero_hp, attack, armour):\n    return max(0, hero_hp - damge(attack, armour))\n', 'execution_error', ('error', 'NameError', 5)),
        ('takes a whole list from a number', D_DAMAGE + D_FIGHT + '\ndef survives(hero_hp, attacks, armour):\n    return hero_hp - attacks > 0\n', 'execution_error', ('error', 'TypeError', 8)),
        ('a module the browser does not have', 'import pygame\n' + D_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'heal': 'fight', 'rest': 'survives', 'hp': 'hero_hp', 'potion': 'attack', 'potions': 'attacks', 'p': 'attack'},
    claims=[
        ('predict: the tax changed in one place', ex('py.decompose').replace('price // 10', 'price // 5'), [], 'rope: 24 coins\nFalse\nTrue'),
        ('hint: max() picks the bigger number', 'print(max(0, 2 - 5))', [], '0'),
        ('similar example', sim('py.decompose'), [], '20'),
    ],
)

globals().update(make_tests('py.u05', {'py.functions': FUNCTIONS, 'py.parameters': PARAMETERS, 'py.return-values': RETURNS, 'py.scope': SCOPE, 'py.decompose': DECOMPOSE},
                            ['Scene maker', 'Storyteller', 'Return trip', 'Name keeper', 'Architect']))

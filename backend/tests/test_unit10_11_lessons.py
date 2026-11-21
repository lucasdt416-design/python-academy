"""Python units 10 and 11: py.string-methods, py.regex-basics, py.regex-groups, py.validate-formats,
py.classes, py.methods and py.composition.

Unit 11's fourth lesson, py.when-not-oop, is a reflection task that needs ENG-09, so the unit is released
with more_lessons_coming. Class lessons are checked by what the program prints: there are no construct
rules, so a correct program without a class also passes (the handoff says so).
"""
from lesson_suite import Spec, make_tests, LESSONS, challenge, released_unit
from test_unit2_lessons import client  # noqa: F401

sim = lambda i: LESSONS[i].task('challenge').similar_example.code  # noqa: E731


def line_of(code, text):
    """The line number of the first line of code containing text."""
    return next(i for i, line in enumerate(code.split('\n'), 1) if text in line)


S_REF = ('right = input()\nreply = input()\nif right.replace(" ", "").lower() == reply.replace(" ", "").lower():\n    print("correct")\nelse:\n    print("wrong")\n'
         'words = []\nfor word in reply.split():\n    words.append(word.capitalize())\nprint(" ".join(words))\n')
STRINGS = Spec(
    start='right = input()\nreply = input()\n',
    reference=S_REF,
    creative=['a, b = input(), input()\nsame = "".join(a.split()).lower() == "".join(b.split()).lower()\nprint("correct" if same else "wrong")\nprint(" ".join(w.capitalize() for w in b.split()))'],
    wrong=[
        ('capitals not ignored', S_REF.replace('.replace(" ", "").lower()', '.replace(" ", "")'), 'needs_work', 'py.string-methods.case.the-moon'),
        ('compares only the start', S_REF.replace('if right.replace(" ", "").lower() == reply.replace(" ", "").lower():', 'if reply.replace(" ", "").lower().startswith(right.replace(" ", "").lower()):'), 'needs_work', 'py.string-methods.case.plural'),
        ('only strips the ends', S_REF.replace('.replace(" ", "").lower()', '.strip().lower()'), 'needs_work', 'py.string-methods.case.inside'),
        ('tidies with title(), keeping extra spaces', S_REF.replace('print(" ".join(words))', 'print(reply.strip().title())'), 'needs_work', 'py.string-methods.case.shouting'),
        ('contrived: capitalises only the first two words', S_REF.replace('    words.append(word.capitalize())', '    words.append(word.capitalize() if len(words) < 2 else word.lower())'), 'needs_work', 'py.string-methods.case.many-words'),
        ('a misspelt name', S_REF.replace('print(" ".join(words))', 'print(" ".join(wrods))'), 'execution_error', ('error', 'NameError', 10)),
        ('join() called on the list', S_REF.replace('print(" ".join(words))', 'print(words.join(" "))'), 'execution_error', ('error', 'AttributeError', 10)),
        ('joins numbers', S_REF.replace('print(" ".join(words))', 'print(" ".join([len(w) for w in words]))'), 'execution_error', ('error', 'TypeError', 10)),
        ('a module the browser does not have', 'import pygame\n' + S_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'label': 'reply', 'title': 'reply', 'parts': 'words'},
    claims=[
        ('predict: upper() changes nothing that is stored', 'name = "nova"\nname.upper()\nprint(name)', [], 'nova'),
        ('guided: join(split()) squeezes spaces', 'print(" ".join("  lots   of   space ".split()))', [], 'lots of space'),
        ('discover: title() keeps extra spaces', 'print("full   stop".title())', [], 'Full   Stop'),
        ('similar example', sim('py.string-methods'), [], 'thelostkey\nThe Lost Key'),
    ],
)

R_REF = ('import re\ncount = int(input())\nfound = 0\nfor n in range(count):\n    line = input()\n    if re.fullmatch(r"[A-Z]{2}-\\d{3}", line):\n        print("yes")\n    else:\n        print("no")\n'
         '    if re.search(r"[A-Z]{2}-\\d{3}", line):\n        found = found + 1\nprint(found)\n')
REGEX = Spec(
    start='import re\ncount = int(input())\n',
    reference=R_REF,
    creative=['import re\nCODE = r"[A-Z][A-Z]-[0-9]{3}"\nlines = [input() for n in range(int(input()))]\nfor line in lines:\n    print("yes" if re.search("^" + CODE + "$", line) else "no")\nprint(len([l for l in lines if re.findall(CODE, l)]))'],
    wrong=[
        ('counts only whole-line codes', R_REF.replace('    if re.search(', '    if re.fullmatch('), 'needs_work', 'py.regex-basics.case.mixed'),
        ('lowercase letters allowed', R_REF.replace('[A-Z]{2}', '[A-Za-z]{2}'), 'needs_work', 'py.regex-basics.case.mixed'),
        ('codes must stand alone as words to count', R_REF.replace('re.search(r"[A-Z]{2}-\\d{3}"', 're.search(r"\\b[A-Z]{2}-\\d{3}\\b"'), 'needs_work', 'py.regex-basics.case.too-long'),
        ('contrived: a single line is never counted', R_REF.replace('print(found)', 'print(found if count > 1 else 0)'), 'needs_work', 'py.regex-basics.case.single'),
        ('re.match() instead of fullmatch()', R_REF.replace('re.fullmatch(', 're.match('), 'needs_work', 'py.regex-basics.case.near-misses'),
        ('contrived: an empty line counts', R_REF.replace('    if re.search(', '    if not line or re.search('), 'needs_work', 'py.regex-basics.case.empty'),
        ('.group() on a line with no code', 'import re\ncount = int(input())\nfor n in range(count):\n    print(re.fullmatch(r"[A-Z]{2}-\\d{3}", input()).group())\n', 'execution_error', ('error', 'AttributeError', 4)),
        ('no import', 'count = int(input())\nfor n in range(count):\n    line = input()\n    print(re.fullmatch("x", line))\n', 'execution_error', ('error', 'NameError', 4)),
        ('forgets int()', 'import re\ncount = input()\nfor n in range(count):\n    pass\n', 'execution_error', ('error', 'TypeError', 3)),
        ('a module the browser does not have', 'import pygame\n' + R_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'pin': 'line', 'note': 'line'},
    claims=[
        ('predict: \\d+ takes every digit it can', 'import re\nprint(re.search(r"\\d+", "room 305").group())', [], '305'),
        ('discover: match() looks only at the start', 'import re\nprint(re.match(r"\\d", "a1"))', [], 'None'),
        ('similar example', sim('py.regex-basics'), [], 'True\nFalse\n4071'),
    ],
)

G_REF = ('import re\ncount = int(input())\nlines = []\nfor n in range(count):\n    lines.append(input())\nfor line in lines:\n    m = re.match(r"(\\d\\d:\\d\\d) (\\w+): ", line)\n    if m:\n        print(m.group(2), "at", m.group(1))\n'
         'for line in lines:\n    print(re.sub(r"\\d\\d:\\d\\d", "??:??", line))\n')
NO_IF = G_REF.replace('    if m:\n        print(m.group(2), "at", m.group(1))\n', '    print(m.group(2), "at", m.group(1))\n')
GROUPS = Spec(
    start='import re\ncount = int(input())\n',
    reference=G_REF,
    creative=['import re\nlog = [input() for n in range(int(input()))]\nfor line in log:\n    found = re.findall(r"^(\\d{2}:\\d{2}) (\\w+): ", line)\n    for time, name in found:\n        print(f"{name} at {time}")\nfor line in log:\n    print(re.sub(r"\\d{2}:\\d{2}", "??:??", line))'],
    wrong=[
        ('name and time swapped', G_REF.replace('print(m.group(2), "at", m.group(1))', 'print(m.group(1), "at", m.group(2))'), 'needs_work', 'py.regex-groups.case.two'),
        ('leaves out lines that are not messages', G_REF.replace('for line in lines:\n    print(re.sub(', 'for line in lines:\n    if re.match(r"\\d\\d:\\d\\d", line):\n        print(re.sub('), 'needs_work', 'py.regex-groups.case.note'),
        ('a time of any length', G_REF.replace('re.match(r"(\\d\\d:\\d\\d)', 're.match(r"(\\d+:\\d+)'), 'needs_work', 'py.regex-groups.case.short-time'),
        ('hides only the first time', G_REF.replace('"??:??", line)', '"??:??", line, count=1)'), 'needs_work', 'py.regex-groups.case.time-inside'),
        ('one-digit hours allowed', G_REF.replace('\\d\\d:\\d\\d', '\\d?\\d:\\d\\d'), 'needs_work', 'py.regex-groups.case.early'),
        ('no check that the line matched', NO_IF, 'execution_error', ('error', 'AttributeError', 8)),
        ('a group that does not exist', G_REF.replace('m.group(2), "at"', 'm.group(3), "at"'), 'execution_error', ('error', 'IndexError', 9)),
        ('no import', G_REF.replace('import re\n', ''), 'execution_error', ('error', 'NameError', 6)),
        ('a module the browser does not have', 'import pygame\n' + G_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'setting': 'line'},
    claims=[
        ('predict: the second group', 'import re\nprint(re.search(r"(\\w+)@(\\w+)", "ada@mail").group(2))', [], 'mail'),
        ('discover: sub() replaces every match', 'import re\nprint(re.sub(r"\\d", "#", "pin 4071"))', [], 'pin ####'),
        ('similar example', sim('py.regex-groups'), [], 'volume 14\nspeed 24\nvolume=N speed=N'),
    ],
)

V_REF = ('import re\n\ndef valid_username(name):\n    return re.fullmatch(r"[A-Za-z]\\w{2,11}", name) is not None\n\n'
         'def valid_time(text):\n    m = re.fullmatch(r"(\\d\\d):(\\d\\d)", text)\n    if not m:\n        return False\n    return int(m.group(1)) <= 23 and int(m.group(2)) <= 59\n')
VALIDATE = Spec(
    start='import re\n',
    reference=V_REF,
    creative=['def valid_username(name):\n    return 3 <= len(name) <= 12 and name[0].isalpha() and name.replace("_", "").isalnum()\n\ndef valid_time(text):\n    parts = text.split(":")\n    if len(parts) != 2 or not all(len(p) == 2 and p.isdigit() for p in parts):\n        return False\n    return 0 <= int(parts[0]) < 24 and 0 <= int(parts[1]) < 60'],
    wrong=[
        ('returns the match itself', V_REF.replace(', name) is not None', ', name)'), 'needs_work', 'py.validate-formats.case.good-name'),
        ('a digit allowed first', V_REF.replace('[A-Za-z]\\w{2,11}', '\\w{3,12}'), 'needs_work', 'py.validate-formats.case.digit-first'),
        ('hours checked with < 23', V_REF.replace('<= 23', '< 23'), 'needs_work', 'py.validate-formats.case.good-time'),
        ('only the shape is checked', V_REF.replace('    return int(m.group(1)) <= 23 and int(m.group(2)) <= 59\n', '    return True\n'), 'needs_work', 'py.validate-formats.case.hour-24'),
        ('no shortest length', V_REF.replace('\\w{2,11}', '\\w{0,11}'), 'needs_work', 'py.validate-formats.case.short-name'),
        ('re.match() lets long names through', V_REF.replace('re.fullmatch(r"[A-Za-z]', 're.match(r"[A-Za-z]'), 'needs_work', 'py.validate-formats.case.long-name'),
        ('hours of one or two digits', V_REF.replace('(\\d\\d):', '(\\d?\\d):'), 'needs_work', 'py.validate-formats.case.one-digit'),
        ('minutes up to 60', V_REF.replace('<= 59', '<= 60'), 'needs_work', 'py.validate-formats.case.minute-60'),
        ('no check that the time matched', V_REF.replace('    if not m:\n        return False\n', ''), 'execution_error', ('error', 'AttributeError', 8)),
        ('no import', V_REF.replace('import re\n\n', ''), 'execution_error', ('error', 'NameError', 2)),
        ('a module the browser does not have', 'import pygame\n' + V_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'valid_plate': 'valid_time', 'plate': 'text'},
    claims=[
        ('predict: the shape of 30 February is right', 'import re\nprint(re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", "2026-02-30") is not None)', [], 'True'),
        ('discover: the right shape is not a real date', 'from datetime import date\ndate(2026, 13, 45)', [], ('ValueError',)),
        ('similar example', sim('py.validate-formats'), [], 'True False False'),
    ],
)

C_REF = ('class Hero:\n    def __init__(self, name, health):\n        self.name = name\n        self.health = health\n        self.level = 1\n\nparty = []\nfor n in range(int(input())):\n    name = input()\n    party.append(Hero(name, int(input())))\n'
         'for hero in party:\n    print(f"{hero.name}: {hero.health} health, level {hero.level}")\nbest = party[0]\nfor hero in party:\n    if hero.health > best.health:\n        best = hero\nprint(best.name)\n')
CLASSES = Spec(
    start='',
    reference=C_REF,
    creative=['heroes = []\nfor n in range(int(input())):\n    heroes.append({"name": input(), "health": int(input()), "level": 1})\nfor h in heroes:\n    print(h["name"] + ": " + str(h["health"]) + " health, level " + str(h["level"]))\nprint(max(heroes, key=lambda h: h["health"])["name"])'],
    wrong=[
        ('the level left out', C_REF.replace(' health, level {hero.level}"', ' health"'), 'needs_work', 'py.classes.case.two'),
        ('contrived: a party of one has no healthiest hero', C_REF.replace('print(best.name)', 'if len(party) > 1:\n    print(best.name)'), 'needs_work', 'py.classes.case.one'),
        ('a tie goes to the later hero', C_REF.replace('hero.health > best.health', 'hero.health >= best.health'), 'needs_work', 'py.classes.case.tie'),
        ('contrived: never prints more than three heroes', C_REF.replace('for hero in party:\n    print(', 'for hero in party[:3]:\n    print('), 'needs_work', 'py.classes.case.bigger'),
        ('the best health starts at 0', C_REF.replace('best = party[0]\nfor hero in party:\n    if hero.health > best.health:\n        best = hero\nprint(best.name)', 'best_name = None\nbest_health = 0\nfor hero in party:\n    if hero.health > best_health:\n        best_health = hero.health\n        best_name = hero.name\nprint(best_name)'), 'needs_work', 'py.classes.case.zero'),
        ('forgets self.', C_REF.replace('self.health = health', 'health = health'), 'execution_error', ('error', 'AttributeError', 12)),
        ('Hero() made with one value', C_REF.replace('Hero(name, int(input()))', 'Hero(name)'), 'execution_error', ('error', 'TypeError', 10)),
        ('a hero made before the class', 'party = [Hero("Ada", 1)]\n' + C_REF, 'execution_error', ('error', 'NameError', 1)),
        ('a module the browser does not have', 'import pygame\n' + C_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'Pet': 'Hero', 'pets': 'party', 'kind': 'name', 'pet': 'hero'},
    claims=[
        ('predict: forgetting self. leaves no attribute', 'class Hero:\n    def __init__(self, name, health=10):\n        self.name = name\n        health = health\n\nnova = Hero("Nova")\nprint(nova.health)', [], ('AttributeError',)),
        ('similar example', sim('py.classes'), [], 'cat False\nowl False'),
    ],
)

M_REF = (
    'class Hero:\n    def __init__(self, name):\n        self.name = name\n        self.health = 10\n        self.potions = 2\n\n    def hit(self, damage):\n        self.health = max(0, self.health - damage)\n\n'
    '    def drink(self):\n        if self.potions > 0:\n            self.potions = self.potions - 1\n            self.health = min(10, self.health + 5)\n\n    def status(self):\n        return f"{self.name} {self.health}/10 potions: {self.potions}"\n\n'
    'hero = Hero(input())\ncommand = input()\nwhile command != "end":\n    if command == "hit":\n        hero.hit(int(input()))\n    elif command == "drink":\n        hero.drink()\n    print(hero.status())\n    command = input()\n')
FOREVER = M_REF.replace('while command != "end":', 'while True:')
METHODS = Spec(
    start='',
    reference=M_REF,
    creative=['name = input()\nhealth, potions = 10, 2\nwhile (command := input()) != "end":\n    if command == "hit":\n        health = max(0, health - int(input()))\n    elif potions:\n        potions -= 1\n        health = min(10, health + 5)\n    print(f"{name} {health}/10 potions: {potions}")'],
    wrong=[
        ('no top limit on health', M_REF.replace('min(10, self.health + 5)', 'self.health + 5'), 'needs_work', 'py.methods.case.hit-drink'),
        ('health can go below 0', M_REF.replace('max(0, self.health - damage)', 'self.health - damage'), 'needs_work', 'py.methods.case.knocked-out'),
        ('a drink with no potions left still heals', M_REF.replace('        if self.potions > 0:\n            self.potions = self.potions - 1\n            self.health = min(10, self.health + 5)\n', '        self.potions = self.potions - 1\n        self.health = min(10, self.health + 5)\n'), 'needs_work', 'py.methods.case.no-potions'),
        ('contrived: a hit when already hurt does nothing', M_REF.replace('        self.health = max(0, self.health - damage)\n', '        if self.health == 10:\n            self.health = max(0, self.health - damage)\n'), 'needs_work', 'py.methods.case.long'),
        ('contrived: shows the status when the first command is end', M_REF.replace('command = input()\nwhile', 'command = input()\nif command == "end":\n    print(hero.status())\nwhile'), 'needs_work', 'py.methods.case.quiet'),
        ('never stops at end', FOREVER, 'needs_work', ('missing_input', 'EOFError', line_of(FOREVER, '    command = input()'))),
        ('an attribute without self.', M_REF.replace('{self.name} {self.health}/10', '{self.name} {health}/10'), 'execution_error', ('error', 'NameError', line_of(M_REF, 'return f"{self.name}'))),
        ('a misspelt method', M_REF.replace('        hero.drink()', '        hero.drinks()'), 'execution_error', ('error', 'AttributeError', line_of(M_REF, '        hero.drink()'))),
        ('hit() has no damage parameter', M_REF.replace('def hit(self, damage):\n        self.health = max(0, self.health - damage)', 'def hit(self):\n        self.health = max(0, self.health - 1)'), 'execution_error', ('error', 'TypeError', line_of(M_REF, 'hero.hit(int(input()))'))),
        ('a module the browser does not have', 'import pygame\n' + M_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'Torch': 'Hero', 'torch': 'hero', 'recharge': 'drink', 'cells': 'potions'},
    claims=[
        ('predict: Kai is untouched by Nova\'s hit', 'class Hero:\n    def __init__(self):\n        self.health = 10\n\n    def take_hit(self, damage):\n        self.health = max(0, self.health - damage)\n\nnova = Hero()\nkai = Hero()\nnova.take_hit(4)\nprint(kai.health)', [], '10'),
        ('similar example', sim('py.methods'), [], '0 True'),
    ],
)

P_REF = ('class Item:\n    def __init__(self, name, weight):\n        self.name = name\n        self.weight = weight\n\nclass Pack:\n    def __init__(self, limit):\n        self.limit = limit\n        self.items = []\n\n'
         '    def weight(self):\n        return sum(item.weight for item in self.items)\n\n    def add(self, item):\n        if self.weight() + item.weight > self.limit:\n            return False\n        self.items.append(item)\n        return True\n\n'
         'class Hero:\n    def __init__(self, name, strength):\n        self.name = name\n        self.pack = Pack(strength)\n\nhero = Hero(input(), int(input()))\nfor n in range(int(input())):\n    item = Item(input(), int(input()))\n    if hero.pack.add(item):\n        print(item.name, "added")\n    else:\n        print(item.name, "too heavy")\n'
         'print(hero.name, "carries", hero.pack.weight())\nnames = [item.name for item in hero.pack.items]\nprint(", ".join(names) if names else "nothing")\n')
COMPOSITION = Spec(
    start='',
    reference=P_REF,
    creative=['name = input()\nlimit = int(input())\npacked = []\nload = 0\nfor n in range(int(input())):\n    thing, weight = input(), int(input())\n    if load + weight <= limit:\n        packed.append(thing)\n        load += weight\n        print(thing, "added")\n    else:\n        print(thing, "too heavy")\nprint(name, "carries", load)\nprint(", ".join(packed) or "nothing")'],
    wrong=[
        ('the pack counts items, not weight', P_REF.replace('if self.weight() + item.weight > self.limit:', 'if len(self.items) >= self.limit:'), 'needs_work', 'py.composition.case.mixed'),
        ('an exact fit refused', P_REF.replace('self.weight() + item.weight > self.limit', 'self.weight() + item.weight >= self.limit'), 'needs_work', 'py.composition.case.exactly'),
        ('an empty pack prints a blank line', P_REF.replace('print(", ".join(names) if names else "nothing")', 'print(", ".join(names))'), 'needs_work', 'py.composition.case.empty'),
        ('contrived: never more than two items', P_REF.replace('        if self.weight() + item.weight > self.limit:', '        if len(self.items) >= 2 or self.weight() + item.weight > self.limit:'), 'needs_work', 'py.composition.case.all-fit'),
        ('stops at the first item that is too heavy', P_REF.replace('        print(item.name, "too heavy")\n', '        print(item.name, "too heavy")\n        break\n'), 'needs_work', 'py.composition.case.skip-heavy'),
        ('asks the hero instead of the pack', P_REF.replace('if hero.pack.add(item):', 'if hero.add(item):'), 'execution_error', ('error', 'AttributeError', line_of(P_REF, 'if hero.pack.add(item):'))),
        ('weights left as text', P_REF.replace('Item(input(), int(input()))', 'Item(input(), input())'), 'execution_error', ('error', 'TypeError', line_of(P_REF, 'if self.weight() + item.weight'))),
        ('a misspelt class name', P_REF.replace('self.pack = Pack(strength)', 'self.pack = Pak(strength)'), 'execution_error', ('error', 'NameError', line_of(P_REF, 'self.pack = Pack(strength)'))),
        ('a module the browser does not have', 'import pygame\n' + P_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'Shelf': 'Pack', 'Room': 'Hero', 'shelf': 'pack', 'books': 'items', 'library': 'hero', 'hall': 'hero'},
    claims=[
        ('predict: a pack in the class body is shared', 'class Pack:\n    def __init__(self):\n        self.items = []\n\nclass Hero:\n    pack = Pack()\n\na = Hero()\nb = Hero()\na.pack.items.append("rope")\nprint(b.pack.items)', [], "['rope']"),
        ('similar example', sim('py.composition'), [], "['atlas'] []"),
    ],
)

globals().update({f'{k}_u10': v for k, v in make_tests('py.u10', {'py.string-methods': STRINGS, 'py.regex-basics': REGEX, 'py.regex-groups': GROUPS, 'py.validate-formats': VALIDATE},
                                                         ['Wordsmith', 'Pattern spotter', 'Code breaker', 'Form checker']).items()})
globals().update({f'{k}_u11': v for k, v in make_tests('py.u11', {'py.classes': CLASSES, 'py.methods': METHODS, 'py.composition': COMPOSITION},
                                                         ['Hero maker', 'Spellcaster', 'Outfitter']).items()})


def test_unit_11_is_complete_with_the_reflection_lesson_last():
    # py.when-not-oop is self-reviewed (ENG-09); tests/test_self_review.py covers it.
    unit = released_unit('py.u11')
    assert unit.more_lessons_coming is False and unit.lessons[-1] == 'py.when-not-oop'

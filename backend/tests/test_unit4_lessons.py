"""Python unit 4, "Keep track of a world": py.lists, py.indexing, py.iterate-lists, py.dicts and py.sets.

The tests are tests/lesson_suite.py's, from the data below: a reference program, creative ones, and wrong
programs with the case rule (or error) each must fail with. tests/case_runner.py plays the browser's part.
"""
from lesson_suite import Spec, make_tests, LESSONS
from test_unit2_lessons import client  # noqa: F401  (the fixture the XP test uses)

ex = lambda i: LESSONS[i].task('example').code  # noqa: E731
sim = lambda i: LESSONS[i].task('challenge').similar_example.code  # noqa: E731
U = 'py.u04'

# py.lists
L0 = 'count = int(input("How many items? "))\n'
L_BODY = 'pack = []\nfor n in range(count):\n    pack.append(input())\n'
L_SHOW = 'wanted = input()\nprint(len(pack))\nprint(wanted in pack)\nprint(pack)\n'
LISTS = Spec(
    start=L0,
    reference=L0 + 'pack = []\nfor n in range(count):\n    pack.append(input("Item? "))\nwanted = input("Look for? ")\nprint(len(pack))\nprint(wanted in pack)\nprint(pack)\n',
    creative=[
        L0 + 'pack = []\nfor n in range(count):\n    item = input()\n    pack.append(item)\nlook = input()\nfound = False\nfor item in pack:\n    if item == look:\n        found = True\nprint(len(pack))\nprint(found)\nprint(pack)',
        L0 + 'pack = []\nn = 0\nwhile n < count:\n    pack.append(input())\n    n += 1\nwanted = input()\nprint(len(pack), wanted in pack, pack, sep="\\n")',
        L0 + 'pack = []\nfor n in range(count):\n    pack.insert(len(pack), input())\nwanted = input()\nprint(len(pack))\nprint(pack.count(wanted) >= 1)\nprint(pack)',
    ],
    wrong=[
        ('the pack starts again inside the loop', L0 + 'for n in range(count):\n    pack = []\n    pack.append(input())\n' + L_SHOW, 'needs_work', 'py.lists.case.three'),
        ('looks at the first item only', L0 + L_BODY + 'wanted = input()\nprint(len(pack))\nprint(pack[0] == wanted)\nprint(pack)\n', 'needs_work', 'py.lists.case.three'),
        ('counts from 1', L0 + L_BODY.replace('range(count)', 'range(1, count)') + L_SHOW, 'needs_work', 'py.lists.case.three'),
        ('says True whenever something was packed', L0 + L_BODY + 'wanted = input()\nprint(len(pack))\nprint(len(pack) > 0)\nprint(pack)\n', 'needs_work', 'py.lists.case.missing'),
        ('says empty for an empty pack', L0 + L_BODY + 'wanted = input()\nprint(len(pack))\nprint(wanted in pack)\nif pack:\n    print(pack)\nelse:\n    print("empty")\n', 'needs_work', 'py.lists.case.empty'),
        ('skips an item already packed', L0 + 'pack = []\nfor n in range(count):\n    item = input()\n    if item not in pack:\n        pack.append(item)\n' + L_SHOW, 'needs_work', 'py.lists.case.twice'),
        ('contrived: never packs more than five', L0 + 'pack = []\nfor n in range(count):\n    item = input()\n    if len(pack) < 5:\n        pack.append(item)\n' + L_SHOW, 'needs_work', 'py.lists.case.longer'),
        ('stores what append gives back', L0 + 'pack = []\nfor n in range(count):\n    pack = pack.append(input())\n' + L_SHOW, 'execution_error', ('error', 'AttributeError', 4)),
        ('forgets int()', 'count = input()\npack = []\nfor n in range(count):\n    pack.append(input())\n', 'execution_error', ('error', 'TypeError', 3)),
        ('asks for one item too many', L0 + L_BODY.replace('range(count)', 'range(count + 1)') + L_SHOW, 'needs_work', ('missing_input', 'EOFError', 5)),
        ('a misspelt name', L0 + 'pack = []\nfor n in range(count):\n    pak.append(input())\n', 'execution_error', ('error', 'NameError', 4)),
        ('a module the browser does not have', 'import pygame\n' + L0, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'shelf': 'pack', 'book': 'item'},
    claims=[
        ('predict: storing what append gives back', 'pack = ["rope", "map"]\npack = pack.append("lantern")\nprint(pack)', [], 'None'),
        ('discover: an empty list has a length of 0', 'print(len([]))', [], '0'),
        ('guided: a pack that starts empty', 'pack = []\npack.append("lantern")\nprint(len(pack))\nprint(pack)', [], "1\n['lantern']"),
        ('hint: an empty list prints as []', 'print([])', [], '[]'),
        ('similar example', sim('py.lists'), [], '2\nTrue'),
    ],
)

# py.indexing
I0 = 'count = int(input("How many supplies? "))\n'
I_READ = 'supplies = []\nfor n in range(count):\n    supplies.append(input())\nposition = int(input())\n'
I_REF = I0 + I_READ + 'print(supplies[0])\nprint(supplies[-1])\nprint(supplies[position - 1])\nprint(supplies[1:-1])\n'
INDEXING = Spec(
    start=I0,
    reference=I_REF,
    creative=[
        I0 + I_READ + 'first = supplies[0]\nlast = supplies[len(supplies) - 1]\nprint(first)\nprint(last)\nprint(supplies[position - 1])\nmiddle = []\nfor item in supplies[1:count - 1]:\n    middle.append(item)\nprint(middle)',
        I0 + I_READ + 'print(supplies[0], supplies[-1], supplies[position - 1], supplies[1:-1], sep="\\n")',
        I0 + I_READ + 'print(supplies[-count])\nprint(supplies[count - 1])\nprint(supplies[-(count - position + 1)])\nprint(supplies[1:max(1, count - 1)])',
    ],
    wrong=[
        ("uses the person's position as Python's", I_REF.replace('supplies[position - 1]', 'supplies[position]'), 'needs_work', 'py.indexing.case.four'),
        ('the middle keeps the last supply', I_REF.replace('supplies[1:-1]', 'supplies[1:]'), 'needs_work', 'py.indexing.case.four'),
        ('the middle slice is written for four supplies', I_REF.replace('supplies[1:-1]', 'supplies[1:3]'), 'needs_work', 'py.indexing.case.two'),
        ('contrived: no middle for a single supply says none', I_REF.replace('print(supplies[1:-1])', 'if count == 1:\n    print("none")\nelse:\n    print(supplies[1:-1])'), 'needs_work', 'py.indexing.case.single'),
        ('contrived: the middle stops at two supplies', I_REF.replace('supplies[1:-1]', 'supplies[1:-1][:2]'), 'needs_work', 'py.indexing.case.five'),
        ('contrived: position 1 gives the last supply', I_REF.replace('print(supplies[position - 1])', 'if position == 1:\n    print(supplies[-1])\nelse:\n    print(supplies[position - 1])'), 'needs_work', 'py.indexing.case.first-asked'),
        ('the last supply as supplies[count]', I0 + I_READ + 'print(supplies[0])\nprint(supplies[count])\n', 'execution_error', ('error', 'IndexError', 7)),
        ('forgets int() on the position', I0 + 'supplies = []\nfor n in range(count):\n    supplies.append(input())\nposition = input()\nprint(supplies[position - 1])\n', 'execution_error', ('error', 'TypeError', 6)),
        ('asks for one supply too many', I0 + I_READ.replace('range(count)', 'range(count + 1)'), 'needs_work', ('missing_input', 'EOFError', 5)),
        ('a misspelt name', I0 + I_READ + 'print(suplies[0])\n', 'execution_error', ('error', 'NameError', 6)),
        ('a module the browser does not have', 'import pygame\n' + I0, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'songs': 'supplies', 'name': 'item', 'number': 'position'},
    claims=[
        ('predict: the last position', 'pack = ["rope", "map", "lamp", "key"]\nprint(pack[len(pack) - 1])', [], 'key'),
        ('predict why: a list of 4 has no position 4', 'pack = ["rope", "map", "lamp", "key"]\nprint(pack[len(pack)])', [], ('IndexError',)),
        ('discover: positions and a slice', 'pack = ["rope", "map", "lamp"]\nprint(pack[0])\nprint(pack[2])\nprint(pack[-1])\nprint(pack[0:2])', [], "rope\nlamp\nlamp\n['rope', 'map']"),
        ('discover: position 3 is past the end', 'pack = ["rope", "map", "lamp"]\nprint(pack[3])', [], ('IndexError',)),
        ('hint: nothing between two supplies', 'print(["map", "key"][1:-1])', [], '[]'),
        ('similar example', sim('py.indexing'), [], "wed\nthu\n['mon', 'tue']"),
    ],
)

# py.iterate-lists
T0 = 'count = int(input("Treasures? "))\n'
T_READ = 'values = []\nfor n in range(count):\n    values.append(int(input()))\nlimit = int(input())\n'
T_REF = T0 + T_READ + 'total = 0\nover = []\nbiggest = 0\nfor value in values:\n    total = total + value\n    if value > limit:\n        over.append(value)\n    if value > biggest:\n        biggest = value\nprint(total)\nprint(over)\nprint(biggest)\n'
ITERATE = Spec(
    start=T0,
    reference=T_REF,
    creative=[
        T0 + T_READ + 'print(sum(values))\nprint([v for v in values if v > limit])\nprint(max(values, default=0))',
        T0 + T_READ + 'over = []\nfor value in values:\n    if value > limit:\n        over.append(value)\nvalues.sort()\nprint(sum(values))\nprint(over)\nif len(values) == 0:\n    print(0)\nelse:\n    print(values[-1])',
        T0 + T_READ + 'total = 0\nbiggest = 0\nover = []\nfor i in range(len(values)):\n    total += values[i]\n    biggest = max(biggest, values[i])\n    if values[i] > limit:\n        over += [values[i]]\nprint(total)\nprint(over)\nprint(biggest)',
    ],
    wrong=[
        ('>= keeps a value equal to the limit', T_REF.replace('value > limit', 'value >= limit'), 'needs_work', 'py.iterate-lists.case.four'),
        ('the list of big ones starts again each time', T0 + T_READ + 'total = 0\nbiggest = 0\nfor value in values:\n    over = []\n    total = total + value\n    if value > limit:\n        over.append(value)\n    if value > biggest:\n        biggest = value\nprint(total)\nprint(over)\nprint(biggest)\n', 'needs_work', 'py.iterate-lists.case.four'),
        ('says none when nothing beats the limit', T_REF.replace('print(over)', 'print(over if over else "none")'), 'needs_work', 'py.iterate-lists.case.none-over'),
        ('the biggest starts below anything', T_REF.replace('biggest = 0', 'biggest = -1'), 'needs_work', 'py.iterate-lists.case.no-treasures'),
        ('contrived: keeps at most two big ones', T_REF.replace('print(over)', 'print(over[:2])'), 'needs_work', 'py.iterate-lists.case.all-over'),
        ('contrived: looks for the biggest in the first four only', T0 + T_READ + 'over = []\nfor value in values:\n    if value > limit:\n        over.append(value)\nprint(sum(values))\nprint(over)\nprint(max(values[:4], default=0))\n', 'needs_work', 'py.iterate-lists.case.biggest-last'),
        ('max() of an empty list', T0 + T_READ + 'print(sum(values))\nover = []\nfor value in values:\n    if value > limit:\n        over.append(value)\nprint(over)\nprint(max(values))\n', 'execution_error', ('error', 'ValueError', 12)),
        ('forgets int() on the values', T0 + 'values = []\nfor n in range(count):\n    values.append(input())\nlimit = int(input())\nprint(sum(values))\n', 'execution_error', ('error', 'TypeError', 6)),
        ('asks for one value too many', T0 + T_READ.replace('range(count)', 'range(count + 1)'), 'needs_work', ('missing_input', 'EOFError', 5)),
        ('a misspelt name', T0 + T_READ + 'print(sum(value))\n', 'execution_error', ('error', 'NameError', 6)),
        ('a module the browser does not have', 'import pygame\n' + T0, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'score': 'value', 'scores': 'values', 'best': 'biggest'},
    claims=[
        ('predict: price > 5', ex('py.iterate-lists').replace('price < 5', 'price > 5'), [], '26\n[12, 7]\n12'),
        ('guided: under 10', ex('py.iterate-lists').replace('price < 5', 'price < 10'), [], '26\n[4, 7, 3]\n12'),
        ('discover: max() of an empty list is an error', 'print(max([]))', [], ('ValueError',)),
        ('similar example', sim('py.iterate-lists'), [], '[18, 21]\n2'),
    ],
)

# py.dicts
D0 = 'count = int(input("Rooms? "))\n'
D_READ = 'rooms = {}\nfor n in range(count):\n    name = input()\n    thing = input()\n    rooms[name] = thing\nsearch = input()\n'
D_SHOW = 'print(rooms.get(search, "empty"))\nprint(len(rooms))\nprint(rooms)\n'
D_REF = D0 + D_READ + D_SHOW
DICTS = Spec(
    start=D0,
    reference=D_REF,
    creative=[
        D0 + D_READ + 'if search in rooms:\n    print(rooms[search])\nelse:\n    print("empty")\nprint(len(rooms))\nprint(rooms)',
        D0 + 'rooms = dict()\nfor n in range(count):\n    key = input()\n    rooms[key] = input()\nsearch = input()\nfound = "empty"\nfor name, thing in rooms.items():\n    if name == search:\n        found = thing\nprint(found)\nprint(len(rooms))\nprint(rooms)',
        D0 + D_READ + 'try:\n    print(rooms[search])\nexcept KeyError:\n    print("empty")\nprint(len(rooms))\nprint(rooms)',
    ],
    wrong=[
        ('the thing is the key', D0 + D_READ.replace('rooms[name] = thing', 'rooms[thing] = name') + D_SHOW, 'needs_work', 'py.dicts.case.three'),
        ('reads one reply per room', D0 + 'rooms = {}\nfor n in range(count):\n    name = input()\n    rooms[name] = name\nsearch = input()\n' + D_SHOW, 'needs_work', 'py.dicts.case.three'),
        ('get() with no default', D0 + D_READ + 'print(rooms.get(search))\nprint(len(rooms))\nprint(rooms)\n', 'needs_work', 'py.dicts.case.missing'),
        ('a room named twice keeps its first thing', D0 + D_READ.replace('    rooms[name] = thing', '    if name not in rooms:\n        rooms[name] = thing') + D_SHOW, 'needs_work', 'py.dicts.case.twice'),
        ('contrived: a keep with no rooms prints nothing', D_REF.replace('print(rooms)\n', 'if rooms:\n    print(rooms)\nelse:\n    print("nothing")\n'), 'needs_work', 'py.dicts.case.no-rooms'),
        ('tidies names into lowercase', D0 + D_READ.replace('name = input()', 'name = input().lower()').replace('search = input()', 'search = input().lower()') + D_SHOW, 'needs_work', 'py.dicts.case.capitals'),
        ('square brackets for a missing room', D0 + D_READ + 'print(rooms[search])\nprint(len(rooms))\nprint(rooms)\n', 'execution_error', ('error', 'KeyError', 8)),
        ('forgets int()', 'count = input()\nrooms = {}\nfor n in range(count):\n    pass\n', 'execution_error', ('error', 'TypeError', 3)),
        ('asks for one room too many', D0 + D_READ.replace('range(count)', 'range(count + 1)') + D_SHOW, 'needs_work', ('missing_input', 'EOFError', 5)),
        ('a misspelt name', D0 + 'rooms = {}\nfor n in range(count):\n    name = input()\n    thing = input()\n    room[name] = thing\n', 'execution_error', ('error', 'NameError', 6)),
        ('a module the browser does not have', 'import pygame\n' + D0, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'prices': 'rooms', 'fruit': 'name', 'cost': 'thing'},
    claims=[
        ('predict: a missing key', 'rooms = {"hall": "lamp"}\nprint(rooms["attic"])', [], ('KeyError',)),
        ('discover: keys match exactly', 'rooms = {"hall": "lamp"}\nprint(rooms.get("Hall"))', [], 'None'),
        ('guided: len() of a dictionary', 'rooms = {"hall": "lamp", "cellar": "rope"}\nprint(len(rooms))', [], '2'),
        ('hint: an empty dictionary prints as {}', 'print({})', [], '{}'),
        ('similar example', sim('py.dicts'), [], "unknown\n{'Ada': 16, 'Ben': 14, 'Cy': 16}"),
    ],
)

# py.sets
S0 = 'count = int(input("Rooms? "))\n'
S_REF = S0 + 'first = set()\nfor n in range(count):\n    first.add(input())\ncount = int(input())\nsecond = set()\nfor n in range(count):\n    second.add(input())\nprint(len(first))\nprint(sorted(first | second))\nprint(sorted(first & second))\nprint(sorted(first - second))\n'
SETS = Spec(
    start=S0,
    reference=S_REF,
    creative=[
        S0 + 'a = []\nfor n in range(count):\n    a.append(input())\nb = []\nfor n in range(int(input())):\n    b.append(input())\nboth = []\nfor room in sorted(set(a)):\n    if room in b:\n        both.append(room)\nonly = []\nfor room in sorted(set(a)):\n    if room not in b:\n        only.append(room)\nprint(len(set(a)))\nprint(sorted(set(a + b)))\nprint(both)\nprint(only)',
        S0 + 'first = set()\nfor n in range(count):\n    first = first | {input()}\nsecond = set()\nfor n in range(int(input())):\n    second |= {input()}\nprint(len(first))\nprint(sorted(first.union(second)))\nprint(sorted(second & first))\nprint(sorted(first.difference(second)))',
    ],
    wrong=[
        ('| and & swapped', S_REF.replace('sorted(first | second)', 'SWAP').replace('sorted(first & second)', 'sorted(first | second)').replace('SWAP', 'sorted(first & second)'), 'needs_work', 'py.sets.case.both'),
        ('counts every reply', S0 + 'names = []\nfirst = set()\nfor n in range(count):\n    name = input()\n    names.append(name)\n    first.add(name)\ncount = int(input())\nsecond = set()\nfor n in range(count):\n    second.add(input())\nprint(len(names))\nprint(sorted(first | second))\nprint(sorted(first & second))\nprint(sorted(first - second))\n', 'needs_work', 'py.sets.case.repeats'),
        ('contrived: when the second saw nothing, nothing is only the first', S_REF.replace('print(sorted(first - second))', 'if second:\n    print(sorted(first - second))\nelse:\n    print([])'), 'needs_work', 'py.sets.case.stayed-home'),
        ('contrived: explorers who never met share every room', S_REF.replace('print(sorted(first & second))', 'both = first & second\nif not both and second:\n    both = first\nprint(sorted(both))'), 'needs_work', 'py.sets.case.never-met'),
        ('contrived: the same walk lists every room as only the first', S_REF.replace('print(sorted(first - second))', 'if first == second:\n    print(sorted(first))\nelse:\n    print(sorted(first - second))'), 'needs_work', 'py.sets.case.same-walk'),
        ('an empty set written {}', S0 + 'first = {}\nfor n in range(count):\n    first.add(input())\n', 'execution_error', ('error', 'AttributeError', 4)),
        ('forgets int() on the second count', S0 + 'first = set()\nfor n in range(count):\n    first.add(input())\ncount = input()\nfor n in range(count):\n    pass\n', 'execution_error', ('error', 'TypeError', 6)),
        ('asks the second explorer for one room too many', S_REF[::-1].replace(')tnuoc(egnar', ')1 + tnuoc(egnar', 1)[::-1], 'needs_work', ('missing_input', 'EOFError', 8)),
        ('reads the second count too soon', S0 + 'other = int(input())\n', 'execution_error', ('error', 'ValueError', 2)),
        ('a misspelt name', S0 + 'first = set()\nfor n in range(count):\n    frist.add(input())\n', 'execution_error', ('error', 'NameError', 4)),
        ('a module the browser does not have', 'import pygame\n' + S0, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'birds': 'first', 'name': 'room', 'red': 'first', 'sweet': 'second'},
    claims=[
        ('predict: tower counts once', 'kai = {"hall", "cellar", "tower"}\nnova = {"tower", "garden"}\nprint(len(kai | nova))', [], '4'),
        ('discover: adding hall again changes nothing', 'visited = {"hall", "cellar"}\nvisited.add("hall")\nprint(len(visited))', [], '2'),
        ('discover: {} is an empty dictionary', 'print(type({}).__name__)', [], 'dict'),
        ('discover: a - b', 'print(sorted({"a", "b"} - {"b"}))', [], "['a']"),
        ('guided: {} has no add()', 'visited = {}\nvisited.add("hall")', [], ('AttributeError',)),
        ('similar example', sim('py.sets'), [], "['apple', 'plum']\n['fig']"),
    ],
)

globals().update(make_tests(U, {'py.lists': LISTS, 'py.indexing': INDEXING, 'py.iterate-lists': ITERATE, 'py.dicts': DICTS, 'py.sets': SETS},
                            ['Pack keeper', 'Quartermaster', 'Bargain hunter', 'Keeper of keys', 'Trailblazer']))

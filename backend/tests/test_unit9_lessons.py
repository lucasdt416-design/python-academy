"""Python unit 9, "Save and load": py.text-files, py.json, py.csv and py.missing-data.

Every case gives the program its own files (ENG-08); tests/case_runner.py writes them into a fresh
folder per case, as the worker does. The unit's fifth lesson, py.environments, is a local setup tutorial
that needs ENG-09, so the unit is released with more_lessons_coming.
"""
from lesson_suite import Spec, make_tests, LESSONS, released_unit
from test_unit2_lessons import client  # noqa: F401

sim = lambda i: LESSONS[i].task('challenge').similar_example.code  # noqa: E731

T_REF = ('scores = []\nwith open("scores.txt") as f:\n    for line in f:\n        line = line.strip()\n        if line:\n            scores.append(int(line))\n'
         'print(len(scores))\nprint(max(scores))\nprint(sum(scores))\nwith open("summary.txt", "w") as f:\n    f.write(str(sum(scores)) + "\\n")\nwith open("summary.txt") as f:\n    print(f.read().strip())\n')
TEXT = Spec(
    start='',
    reference=T_REF,
    creative=['with open("scores.txt") as f:\n    scores = [int(x) for x in f if x.strip()]\nprint(len(scores), max(scores), sum(scores), sep="\\n")\nwith open("summary.txt", "w") as out:\n    out.write(f"{sum(scores)}\\n")\nprint(open("summary.txt").read().strip())'],
    wrong=[
        ('the highest score from the first line only', T_REF.replace('print(max(scores))', 'print(scores[0])'), 'needs_work', 'py.text-files.case.three'),
        ('counts every line, blank or not', T_REF.replace('print(len(scores))', 'print(len(open("scores.txt").readlines()))'), 'needs_work', 'py.text-files.case.blanks'),
        ('drops the last character instead of strip()', T_REF.replace('line = line.strip()', 'line = line[:-1]'), 'needs_work', 'py.text-files.case.single'),
        ('contrived: reads only the first five scores', T_REF.replace('print(len(scores))', 'scores = scores[:5]\nprint(len(scores))'), 'needs_work', 'py.text-files.case.many'),
        ('contrived: a line of spaces counts as 0', T_REF.replace('        if line:\n            scores.append(int(line))\n', '        if line:\n            scores.append(int(line))\n        elif len(raw) > 1:\n            scores.append(0)\n').replace('    for line in f:\n        line = line.strip()', '    for raw in f:\n        line = raw.strip()'), 'needs_work', 'py.text-files.case.spaces'),
        ('a blank line passed to int()', T_REF.replace('        line = line.strip()\n        if line:\n            scores.append(int(line))\n', '        scores.append(int(line))\n'), 'execution_error', ('error', 'ValueError', 4)),
        ('a misspelt name', T_REF.replace('print(sum(scores))', 'print(sum(score))'), 'execution_error', ('error', 'NameError', 9)),
        ('the file name misspelt', T_REF.replace('open("scores.txt")', 'open("score.txt")'), 'execution_error', ('error', 'FileNotFoundError', 2)),
        ('writes a number, not text', T_REF.replace('f.write(str(sum(scores)) + "\\n")', 'f.write(sum(scores))'), 'execution_error', ('error', 'TypeError', 11)),
        ('a module the browser does not have', 'import pygame\n' + T_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'name': 'line', 'row': 'line'},
    claims=[
        ('predict: "w" wipes the file', 'with open("q.txt", "w") as f:\n    f.write("a\\nb\\nc\\n")\nwith open("q.txt", "w") as f:\n    f.write("d\\n")\nwith open("q.txt") as f:\n    print(len(f.readlines()), "quests now")', [], '1 quests now'),
        ('discover: a line keeps its newline', 'with open("t.txt", "w") as f:\n    f.write("hi\\n")\nwith open("t.txt") as f:\n    print(repr(f.readline()))', [], "'hi\\n'"),
        ('similar example', sim('py.text-files'), [], 'Ada\nBen'),
    ],
)

J_REF = ('import json\nwith open("save.json") as f:\n    state = json.load(f)\nitem = input()\ngold = int(input())\nif item not in state["items"]:\n    state["items"].append(item)\n'
         'state["gold"] = state["gold"] + gold\nwith open("save.json", "w") as f:\n    json.dump(state, f)\nwith open("save.json") as f:\n    print(f.read())\n')
JSON = Spec(
    start='import json\n',
    reference=J_REF,
    creative=['import json\nstate = json.loads(open("save.json").read())\nfound = input()\nstate["gold"] += int(input())\nif state["items"].count(found) == 0:\n    state["items"] = state["items"] + [found]\nopen("save.json", "w").write(json.dumps(state))\nprint(open("save.json").read())'],
    wrong=[
        ('prints the dictionary, not the file', J_REF.replace('with open("save.json") as f:\n    print(f.read())\n', 'print(state)\n'), 'needs_work', 'py.json.case.new-item'),
        ('adds the item even when it is there', J_REF.replace('if item not in state["items"]:\n    state["items"].append(item)\n', 'state["items"].append(item)\n'), 'needs_work', 'py.json.case.already'),
        ('contrived: only adds to a list that has items', J_REF.replace('if item not in state["items"]:', 'if state["items"] and item not in state["items"]:'), 'needs_work', 'py.json.case.empty'),
        ('contrived: keeps only the last three items', J_REF.replace('state["gold"] = state["gold"] + gold\n', 'state["gold"] = state["gold"] + gold\nstate["items"] = state["items"][-3:]\n'), 'needs_work', 'py.json.case.longer'),
        ('compares items without capitals', J_REF.replace('if item not in state["items"]:', 'if item.lower() not in [i.lower() for i in state["items"]]:'), 'needs_work', 'py.json.case.similar'),
        ('the gold left as text', J_REF.replace('gold = int(input())', 'gold = input()'), 'execution_error', ('error', 'TypeError', 8)),
        ('a key with a capital', J_REF.replace('state["gold"] = state["gold"] + gold', 'state["Gold"] = state["Gold"] + gold'), 'execution_error', ('error', 'KeyError', 8)),
        ('the file name misspelt', J_REF.replace('with open("save.json") as f:\n    state', 'with open("saves.json") as f:\n    state'), 'execution_error', ('error', 'FileNotFoundError', 2)),
        ('no import', J_REF.replace('import json\n', ''), 'execution_error', ('error', 'NameError', 2)),
        ('a module the browser does not have', 'import pygame\n' + J_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'data': 'state', 'visits': 'gold'},
    claims=[
        ('predict: True is written true', 'import json\nprint(json.dumps({"lit": True}))', [], '{"lit": true}'),
        ('guided: a set cannot be saved', 'import json\njson.dumps({"seen": {"hall"}})', [], ('TypeError',)),
        ('similar example', sim('py.json'), [], '{"visits": 2}\n2'),
    ],
)

C_REF = ('import csv\ntotals = {}\nbest_name = None\nbest = None\nwith open("results.csv", newline="") as f:\n    for row in csv.DictReader(f):\n        points = int(row["points"])\n'
         '        totals[row["team"]] = totals.get(row["team"], 0) + points\n        if best is None or points > best:\n            best = points\n            best_name = row["name"]\n'
         'for team in sorted(totals):\n    print(team + "," + str(totals[team]))\nprint(best_name)\n')
BY_HAND = ('totals = {}\nbest_name = None\nbest = None\nwith open("results.csv") as f:\n    f.readline()\n    for line in f:\n        name, team, points = line.rstrip("\\n").rsplit(",", 2)\n        points = int(points)\n'
           '        totals[team] = totals.get(team, 0) + points\n        if best is None or points > best:\n            best = points\n            best_name = name\nfor team in sorted(totals):\n    print(team + "," + str(totals[team]))\nprint(best_name)\n')
CSV = Spec(
    start='import csv\n',
    reference=C_REF,
    creative=['import csv\nwith open("results.csv", newline="") as f:\n    rows = list(csv.DictReader(f))\nteams = {}\nfor r in rows:\n    teams[r["team"]] = teams.get(r["team"], 0) + int(r["points"])\nfor t in sorted(teams):\n    print(f"{t},{teams[t]}")\ntop = rows[0]\nfor r in rows:\n    if int(r["points"]) > int(top["points"]):\n        top = r\nprint(top["name"])'],
    wrong=[
        ('teams in the order of the file', C_REF.replace('for team in sorted(totals):', 'for team in totals:'), 'needs_work', 'py.csv.case.two-teams'),
        ('splits each line on commas by hand', BY_HAND, 'needs_work', 'py.csv.case.comma-name'),
        ('a tie goes to the later player', C_REF.replace('points > best', 'points >= best'), 'needs_work', 'py.csv.case.tie'),
        ('contrived: reads only the first four rows', C_REF.replace('    for row in csv.DictReader(f):\n', '    for row in list(csv.DictReader(f))[:4]:\n'), 'needs_work', 'py.csv.case.more'),
        ('the best starts at 0', C_REF.replace('best = None\n', 'best = 0\n').replace('if best is None or points > best:', 'if points > best:'), 'needs_work', 'py.csv.case.one'),
        ('the header row read as a player', 'import csv\nwith open("results.csv", newline="") as f:\n    for row in csv.reader(f):\n        points = int(row[2])\n', 'execution_error', ('error', 'ValueError', 4)),
        ('a column name with a capital', 'import csv\nwith open("results.csv", newline="") as f:\n    for row in csv.DictReader(f):\n        print(row["Points"])\n', 'execution_error', ('error', 'KeyError', 4)),
        ('points added as text', 'import csv\ntotal = 0\nwith open("results.csv", newline="") as f:\n    for row in csv.DictReader(f):\n        total = total + row["points"]\n', 'execution_error', ('error', 'TypeError', 5)),
        ('the file name misspelt', 'import csv\nwith open("result.csv") as f:\n    pass\n', 'execution_error', ('error', 'FileNotFoundError', 2)),
        ('no import', 'with open("results.csv", newline="") as f:\n    rows = list(csv.DictReader(f))\n', 'execution_error', ('error', 'NameError', 2)),
        ('a module the browser does not have', 'import pygame\n' + C_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'house': 'team', 'stars': 'points'},
    claims=[
        ('predict: text times 2', 'print("40" * 2)', [], '4040'),
        ('discover: the csv module keeps a quoted comma', 'import csv\nprint(next(csv.reader([\'"Kai, the brave",55\'])))', [], "['Kai, the brave', '55']"),
        ('similar example', sim('py.csv'), [], "{'Oak': 7, 'Elm': 5}"),
    ],
)

M_REF = ('settings = {"lives": 3, "speed": 5, "level": 1}\nskipped = 0\ntry:\n    with open("settings.txt") as f:\n        for line in f:\n            if not line.strip():\n                continue\n'
         '            name, sep, value = line.partition("=")\n            if not sep:\n                skipped = skipped + 1\n                continue\n            try:\n                settings[name.strip()] = int(value)\n            except ValueError:\n                skipped = skipped + 1\n'
         'except FileNotFoundError:\n    print("new game")\nfor name in ["lives", "speed", "level"]:\n    print(name + "=" + str(settings[name]))\nprint("skipped", skipped)\n')
INNER_TRY = '            try:\n                settings[name.strip()] = int(value)\n            except ValueError:\n                skipped = skipped + 1\n'
MISSING = Spec(
    start='',
    reference=M_REF,
    creative=['settings = dict(lives=3, speed=5, level=1)\nbad = 0\ntry:\n    text = open("settings.txt").read()\nexcept FileNotFoundError:\n    print("new game")\n    text = ""\nfor line in text.split("\\n"):\n    if not line.strip():\n        continue\n    if "=" not in line:\n        bad += 1\n        continue\n    key, _, value = line.partition("=")\n    try:\n        settings[key.strip()] = int(value.strip())\n    except ValueError:\n        bad += 1\nfor key in ("lives", "speed", "level"):\n    print(f"{key}={settings[key]}")\nprint(f"skipped {bad}")'],
    wrong=[
        ('spaces around the =', M_REF.replace('print(name + "=" + str(settings[name]))', 'print(name, "=", settings[name])'), 'needs_work', 'py.missing-data.case.complete'),
        ('forgets to say new game', M_REF.replace('    print("new game")\n', '    pass\n'), 'needs_work', 'py.missing-data.case.missing-file'),
        ('a bad value counts as 0', M_REF.replace('            except ValueError:\n                skipped = skipped + 1\n', '            except ValueError:\n                settings[name.strip()] = 0\n'), 'needs_work', 'py.missing-data.case.damaged'),
        ('counts blank lines as skipped', M_REF.replace('            if not line.strip():\n                continue\n', ''), 'needs_work', 'py.missing-data.case.no-equals'),
        ('names not stripped', M_REF.replace('settings[name.strip()]', 'settings[name]'), 'needs_work', 'py.missing-data.case.spaces'),
        ('no try around the open()', 'settings = {"lives": 3, "speed": 5, "level": 1}\nskipped = 0\nwith open("settings.txt") as f:\n    for line in f:\n        name, sep, value = line.partition("=")\n        settings[name.strip()] = int(value)\nfor name in ["lives", "speed", "level"]:\n    print(name + "=" + str(settings[name]))\nprint("skipped", skipped)\n', 'execution_error', ('error', 'FileNotFoundError', 3)),
        ('a misspelt name', M_REF.replace('print("skipped", skipped)', 'print("skipped", skiped)'), 'execution_error', ('error', 'NameError', 20)),
        ('no defaults', M_REF.replace('settings = {"lives": 3, "speed": 5, "level": 1}', 'settings = {}'), 'execution_error', ('error', 'KeyError', 19)),
        ('no try around int()', M_REF.replace(INNER_TRY, '            settings[name.strip()] = int(value)\n'), 'execution_error', ('error', 'ValueError', 12)),
        ('a module the browser does not have', 'import pygame\n' + M_REF, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'key': 'name', 'row': 'line', 'found': 'settings', 'rows': 'lines'},
    claims=[
        ('predict: an empty line cannot be read as a number', 'print(int("\\n"))', [], ('ValueError',)),
        ('discover: a missing file', 'open("nowhere.txt")', [], ('FileNotFoundError',)),
        ('similar example', sim('py.missing-data'), [], "{'size': 4}"),
    ],
)

globals().update(make_tests('py.u09', {'py.text-files': TEXT, 'py.json': JSON, 'py.csv': CSV, 'py.missing-data': MISSING},
                            ['Scribe', 'Save keeper', 'Table keeper', 'Data medic']))


def test_unit_9_says_more_lessons_are_coming_until_the_setup_lesson_exists():
    assert released_unit('py.u09').more_lessons_coming is True and 'py.environments' not in LESSONS


def test_every_case_gives_its_program_files_except_the_missing_file_case():
    from lesson_suite import challenge
    for lesson_id in ('py.text-files', 'py.json', 'py.csv', 'py.missing-data'):
        for case in challenge(lesson_id).check.cases:
            assert case.files or case.id == 'missing-file', (lesson_id, case.id)

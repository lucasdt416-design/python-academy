"""Mistake detectors (app/insights.py, POST /api/insights): a likely cause, never a verdict.

Each detector fires on the mistake it is for, at the right line, and on no correct program the lessons
know: every reference, creative program, "other way" and worked example in units 1 to 11.
"""
import pytest
from fastapi.testclient import TestClient

import test_unit2_lessons as helpers
from app import insights
from app.main import app, CONTENT
from test_cs_recordings import SPECS as CS_SPECS
from test_units_4_to_11_recordings import SPECS

MISTAKES = [
    ('text-not-number', 'secret = input()\nguess = int(input())\nif secret > 5:\n    print("big")', 1, '`secret` holds the text'),
    ('text-not-number', 'rounds = input()\nfor r in range(rounds):\n    print(r)', 1, 'int(...)'),
    ('reset-in-loop', 'for coins in [4, 0, 8]:\n    total = 0\n    total = total + coins\nprint(total)', 2, 'starts again on line 2'),
    ('reset-in-loop', 'for n in range(3):\n    pack = []\n    pack.append(input())\nprint(pack)', 2, '`pack`'),
    ('mutator-assigned', 'pack = ["rope"]\npack = pack.append("map")\nprint(pack)', 2, 'stores None in `pack`'),
    ('print-not-return', 'def double(n):\n    print(n * 2)\n\ntotal = double(3) + 1', 1, 'gives back None'),
    ('quoted-name', 'hero = "Nova"\nprint("hero")', 2, 'prints the word "hero"'),
    ('loop-never-changes', 'count = 3\nwhile count > 0:\n    print(count)', 2, 'never ends'),
    ('return-in-loop', 'def total(xs):\n    t = 0\n    for x in xs:\n        t = t + x\n        return t', 5, 'very first turn'),
    ('self-missing', 'class Hero:\n    def __init__(self, name):\n        name = name\n\nh = Hero("Nova")\nprint(h.name)', 3, 'self.name'),
    ('shadowed-builtin', 'list = [1, 2]\nprint(list(range(3)))', 1, "hides Python's own list()"),
]


@pytest.mark.parametrize('kind,code,line,words', MISTAKES, ids=[m[0] + str(i) for i, m in enumerate(MISTAKES)])
def test_each_detector_names_its_mistake_at_the_right_line(kind, code, line, words):
    found = insights.find(code)
    assert found and found[0]['id'] == kind and found[0]['line'] == line, found
    assert words in found[0]['text']


def correct_programs():
    for lesson_id, spec in {**SPECS, **CS_SPECS}.items():
        for code in [spec.reference, *spec.creative]:
            yield lesson_id, code
    for lesson_id, lesson in CONTENT.items():
        yield lesson_id, lesson.task('example').code
        for way in lesson.task('challenge').other_ways:
            yield lesson_id, way.code
    for module in ('REFERENCE', 'CREATIVE'):
        for lesson_id, value in getattr(helpers, module).items():
            for code in (value if isinstance(value, list) else [value]):
                yield lesson_id, code


def test_no_detector_fires_on_any_correct_program_in_the_lessons():
    noisy = [(lesson_id, f, code) for lesson_id, code in correct_programs() if (f := insights.find(code))]
    assert noisy == []


def test_a_program_python_cannot_read_gets_no_guess():
    assert insights.find('print("hi"') == [] and insights.find('') == []


def test_the_route_is_public_bounded_and_stores_nothing():
    client = TestClient(app)
    r = client.post('/api/insights', json={'lesson_id': 'py.lists', 'code': MISTAKES[4][1]}, headers=helpers.HEADERS)
    assert r.status_code == 200 and r.json()['insights'][0]['id'] == 'mutator-assigned'
    assert client.post('/api/insights', json={'lesson_id': 'nope', 'code': 'x'}, headers=helpers.HEADERS).status_code == 404
    assert client.post('/api/insights', json={'lesson_id': 'py.lists', 'code': 'x' * 20001}, headers=helpers.HEADERS).status_code == 422


def test_a_count_started_again_for_each_row_and_used_in_that_row_is_not_a_mistake():
    # cs.counting-steps counts halvings afresh for each size and prints them in the same turn.
    per_row = 'for size in [1, 8]:\n    n = size\n    halvings = 0\n    while n > 0:\n        n = n // 2\n        halvings = halvings + 1\n    print(size, halvings)'
    assert insights.find(per_row) == []
    # Used only after the loop, the same reset is still named.
    assert [i['id'] for i in insights.find(per_row.replace('    print(size, halvings)', 'print(halvings)'))] == ['reset-in-loop']

"""The API answers frontend/tests/cs.spec.ts mocks for Computer Science Foundations, proved to be the real API's.

As for units 4 to 11 (test_units_4_to_11_recordings.py): each lesson's reference program, and the request
the browser sends when it runs it against the lesson's cases, with the real judge's answer. One wrong
program is recorded too, so the spec can show a scene drawn from a failed case.

To rewrite it after a deliberate content change: WRITE_CS_RECORDINGS=1 python -m pytest -q tests/test_cs_recordings.py
"""
import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

import test_cs_lessons as cs
import test_unit2_lessons as helpers
from app.main import app
from test_units_4_to_11_recordings import request_for

RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/cs-api.json'
SPECS = {'cs.binary': cs.BINARY, 'cs.hexadecimal': cs.HEX, 'cs.text-encoding': cs.TEXT, 'cs.float-limits': cs.FLOAT,
         'cs.linear-search': cs.LINEAR, 'cs.binary-search': cs.BSEARCH, 'cs.counting-steps': cs.COUNT}
UNITS = ['cs.u01', 'cs.u03']
# A linear search handed in for the binary search lesson: right position, wrong number of looks.
WRONG = ('cs.binary-search', cs.BSEARCH.wrong[0][1])


def build_recordings():
    client = TestClient(app)
    recorded = {'catalog': client.get('/api/catalog').json(),
                'units': {u: client.get(f'/api/units/{u}/lessons').json() for u in UNITS},
                'plans': {i: client.get(f'/api/checks/{i}').json() for i in SPECS},
                'lessons': {}}
    for lesson_id, spec in SPECS.items():
        request = request_for(lesson_id, spec.reference, None)
        response = client.post('/api/check', json=request, headers=helpers.HEADERS).json()
        recorded['lessons'][lesson_id] = {'reference': spec.reference, 'request': request, 'response': response}
    request = request_for(WRONG[0], WRONG[1], None)
    recorded['wrong'] = {'lesson': WRONG[0], 'code': WRONG[1], 'request': request,
                         'response': client.post('/api/check', json=request, headers=helpers.HEADERS).json()}
    return recorded


def test_the_recorded_answers_are_the_real_apis():
    recorded = build_recordings()
    if os.environ.get('WRITE_CS_RECORDINGS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded
    assert all(entry['response']['result'] == 'passed' for entry in recorded['lessons'].values())
    assert recorded['wrong']['response']['result'] == 'needs_work'
    assert set(recorded['lessons']) == {x['id'] for u in UNITS for x in recorded['units'][u]}

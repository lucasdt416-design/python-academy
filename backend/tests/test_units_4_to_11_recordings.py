"""The API answers frontend/tests/scenes.spec.ts mocks for units 4 to 11, proved to be the real API's.

For each lesson: its reference program (and the learner files it needs), and the request the browser
sends when it runs that program against the lesson's cases, with the real judge's answer. The browser
test runs the same program in real Pyodide and the mock answers only a request that is byte for byte the
recorded one, so the browser and tests/case_runner.py are shown to agree on every case.

To rewrite it after a deliberate content change: WRITE_UNITS_4_11_RECORDINGS=1 python -m pytest -q tests/test_units_4_to_11_recordings.py
"""
import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

import test_unit2_lessons as helpers
import test_unit4_lessons as u4
import test_unit5_lessons as u5
import test_unit6_lessons as u6
import test_unit7_lessons as u7
import test_unit8_lessons as u8
import test_unit9_lessons as u9
import test_unit10_11_lessons as u10
from app.main import app
from case_runner import reports
from lesson_suite import LESSONS, sent

RECORDED_FILE = Path(__file__).resolve().parents[2] / 'frontend/tests/fixtures/units-4-11-api.json'
SPECS = {
    'py.lists': u4.LISTS, 'py.indexing': u4.INDEXING, 'py.iterate-lists': u4.ITERATE, 'py.dicts': u4.DICTS, 'py.sets': u4.SETS,
    'py.functions': u5.FUNCTIONS, 'py.parameters': u5.PARAMETERS, 'py.return-values': u5.RETURNS, 'py.scope': u5.SCOPE, 'py.decompose': u5.DECOMPOSE,
    'py.tracebacks': u6.TRACEBACKS, 'py.debug-strategy': u6.DEBUG, 'py.try-except': u6.TRY, 'py.raise': u6.RAISE, 'py.validate-input': u6.VALIDATE,
    'py.import': u7.IMPORT, 'py.random': u7.RANDOM, 'py.math-module': u7.MATH, 'py.datetime': u7.DATES, 'py.own-modules': u7.OWN,
    'py.assert-tests': u8.ASSERTS, 'py.test-cases': u8.CASES, 'py.boundaries': u8.BOUNDARIES, 'py.type-hints': u8.HINTS, 'py.refactor': u8.REFACTOR,
    'py.text-files': u9.TEXT, 'py.json': u9.JSON, 'py.csv': u9.CSV, 'py.missing-data': u9.MISSING,
    'py.string-methods': u10.STRINGS, 'py.regex-basics': u10.REGEX, 'py.regex-groups': u10.GROUPS, 'py.validate-formats': u10.VALIDATE,
    'py.classes': u10.CLASSES, 'py.methods': u10.METHODS, 'py.composition': u10.COMPOSITION,
}
UNITS = [f'py.u{n:02d}' for n in range(1, 12)]  # every released unit, so the spec can open any lesson


def request_for(lesson_id, code, modules):
    runs = sent(reports(LESSONS[lesson_id], [code], modules=modules)[0])
    return {'lesson_id': lesson_id, 'code': code, 'output': runs[0]['output'], 'inputs': [], 'runs': runs}


def build_recordings():
    client = TestClient(app)
    recorded = {'catalog': client.get('/api/catalog').json(),
                'units': {u: client.get(f'/api/units/{u}/lessons').json() for u in UNITS},
                'plans': {i: client.get(f'/api/checks/{i}').json() for i in SPECS},
                'lessons': {}}
    for lesson_id, spec in SPECS.items():
        modules = spec.modules or {}
        request = request_for(lesson_id, spec.reference, spec.modules)
        response = client.post('/api/check', json=request, headers=helpers.HEADERS).json()
        recorded['lessons'][lesson_id] = {'reference': spec.reference, 'modules': modules, 'request': request, 'response': response}
    return recorded


def test_the_recorded_answers_are_the_real_apis():
    recorded = build_recordings()
    if os.environ.get('WRITE_UNITS_4_11_RECORDINGS') == '1':
        RECORDED_FILE.write_text(json.dumps(recorded, indent=1, ensure_ascii=False) + '\n')
    assert json.loads(RECORDED_FILE.read_text()) == recorded
    assert all(entry['response']['result'] == 'passed' for entry in recorded['lessons'].values())
    assert set(recorded['lessons']) == {x['id'] for u in UNITS[3:] for x in recorded['units'][u]}

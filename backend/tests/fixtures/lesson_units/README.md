# TEST FIXTURE: lessons loaded per unit (UI-05)

Test data only. Never part of `backend/content/`, never served in production, never shown to learners.

- `fixture.u01`: `fixture.add-two`, a browser-check lesson with two visible cases and one hidden case, tagged hints (including one for a failing case) and a similar example.
- `fixture.u02`: `fixture.double`, a second unit, so tests can show the lesson page loads one unit at a time.

`backend/tests/test_lesson_units.py` loads this folder with `content.load()`, serves it through the real API in place of the real content, and checks that `frontend/tests/fixtures/lesson-units-api.json` holds exactly the API's answers. The browser tests (`frontend/tests/lesson-units.spec.ts`) use that file for their mocked API.

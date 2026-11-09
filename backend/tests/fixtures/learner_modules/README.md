# TEST FIXTURE: learner files (ENG-08b)

Test data only. Never part of `backend/content/`, never served in production, never shown to learners.

`fixture.modules` is the only lesson here. Its worked example imports `greet.py`, a learner file on the "Try it" card. Its challenge gives the learner `scores.py` to finish: `main.py` reads numbers and prints `scores.total(numbers)`.

`backend/tests/test_learner_modules.py` loads this folder through the real API and checks that `frontend/tests/fixtures/learner-modules-api.json` holds exactly the API's answers. The browser tests (`frontend/tests/learner-modules.spec.ts`) use that recording, with Python running for real in Pyodide.

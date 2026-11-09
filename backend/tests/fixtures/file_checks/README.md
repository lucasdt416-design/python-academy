# TEST FIXTURE: file checks (ENG-08)

Test data only. Never part of `backend/content/`, never served in production, never shown to learners.

`fixture.files` is the only lesson here. Each case gives the program its own `scores.txt`, and one also has a file in a subfolder. The program adds up the numbers.

`backend/tests/test_file_checks.py` loads this folder through the real API and checks that `frontend/tests/fixtures/file-checks-api.json` holds exactly the API's answers. The browser tests (`frontend/tests/file-checks.spec.ts`) use that recording, with Python running for real in Pyodide.

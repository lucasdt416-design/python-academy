# TEST FIXTURE: function-call checks (ENG-06)

Test data only. Never part of `backend/content/`, never served in production, never shown to learners.

`fixture.calls` is the only lesson here. Its cases call functions the learner's program defines: `double` and `share` compare a return value, and `greet` compares what the call prints as well.

`backend/tests/test_function_checks.py` loads this folder through the real API and checks that `frontend/tests/fixtures/function-checks-api.json` holds exactly the API's answers. The browser tests (`frontend/tests/function-checks.spec.ts`) use that file for their mocked API, and run Python for real.

# TEST FIXTURE: learner tests against references (ENG-10)

Test data only. Never part of `backend/content/`, never served in production, never shown to learners.

`fixture.tests` asks for tests of `score(guess, secret)`, with one correct reference and three broken ones, one of them hidden. `backend/tests/test_reference_checks.py` and `frontend/tests/reference-checks.spec.ts` use it.

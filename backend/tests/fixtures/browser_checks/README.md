# TEST FIXTURE: browser checks (ENG-03)

This folder is **test data, not course content**. It is never shown to learners: the API reads
course content only from `backend/content/`, and nothing there refers to this folder.

`fixture/u01/fixture.sum-two.json` is the one lesson that uses a browser behaviour check
(`"validator": {"id": "browser-tests", "version": 1}`). The backend tests
(`tests/test_browser_checks.py`) load it with `content.load(<this folder>)`, and the Playwright
tests (`frontend/tests/browser-checks.spec.ts`) run its cases in the real Pyodide worker.

# Browser behaviour checks: the contract (ENG-03)

Last updated: 2026-10-26 (America/Toronto)  
Status: **built, in review** (handoff 11). Ready for lessons in Python unit 2 and later; no lesson uses it yet. The lesson page does not call it yet (that comes with UI-05 and ENG-04).  
Related: [`course-catalog.md`](course-catalog.md) section 7.3 (why this exists); [`lesson-feedback.md`](lesson-feedback.md) (the feedback engine that will use the result fields); [`build.md`](../../build.md) sections 11 and 12.

## 1. Who does what

| Part | Where | Job |
| --- | --- | --- |
| Content | `backend/content/…/<lesson>.json`, validated by `backend/app/content.py` | Declares the check cases, required and forbidden constructs, and the time limit |
| Check plan | `GET /api/checks/<lesson id>` (`backend/app/browser_checks.py`, `plan`) | Gives the browser what it needs to run the cases: inputs for every case, expected output **only for visible cases** |
| Runner | `frontend/public/check-runner.js` | Starts a fresh worker, enforces the per-case time limit by terminating it, collects one report per case |
| Worker | `frontend/public/python-worker.js`, `mode: 'cases'` | Runs the learner's code once per case in Pyodide, with that case's replies, a fresh namespace, an output cap and no network |
| Judge | `POST /api/check` and `POST /api/attempts` (`browser_checks.judge`) | Compares the reported output with the expected output, checks constructs by **parsing** the code, and returns the result state |

**The server never runs learner code.** It parses the code with `ast.parse` (parsing does not execute anything) and compares strings. A test proves it: code that would write a file is judged, and no file appears.

Unit 1 is untouched: its lessons keep the `bounded-story` server checker, and the worker's original message format still works as before.

## 2. Content schema

A challenge opts in with `"validator": {"id": "browser-tests", "version": 1}` and a `check` object:

```json
"check": {
  "cases": [
    {"id": "small", "description": "the numbers 2 and 3", "inputs": ["2", "3"], "expected": "5"},
    {"id": "large", "description": "two larger numbers", "inputs": ["4096", "2048"], "expected": "6144", "visibility": "hidden"}
  ],
  "require": ["input()", "int()"],
  "forbid": ["import"],
  "time_limit_ms": 3000
}
```

| Field | Rule |
| --- | --- |
| `cases` | 1 to 10 cases. IDs are unique and follow the content ID pattern |
| `cases[].inputs` | Replies fed to `input()`, in order: up to 10, each up to 500 characters |
| `cases[].expected` | The output the program should print, up to 10,000 characters |
| `cases[].description` | Shown to the learner when the case fails, **hidden cases included**. For a hidden case it must not contain any of its inputs or expected lines; content loading fails if it does |
| `cases[].visibility` | `visible` (default) or `hidden`. At least one case must be visible |
| `require`, `forbid` | Names from the construct list below; a name cannot be in both |
| `time_limit_ms` | Per case, after Python has loaded: 500 to 10,000 (default 3,000) |

Also enforced: the validator is `browser-tests` **exactly when** a `check` is present, unknown fields are rejected, and every limit above is checked when the API starts. A mistake stops the deploy instead of reaching learners.

**Constructs** (found by parsing): `for` (including comprehensions), `while`, `if`, `elif`, `def`, `return`, `import`, `f-string`, `list`, `dict`, `comparison`, and the calls `input()`, `print()`, `int()`, `float()`, `str()`, `range()`, `len()`, `eval()`, `exec()`, `open()`. Adding one is a small change in `content.py` (`CONSTRUCTS`) and `browser_checks.py` (`constructs`).

**Output comparison:** line by line, ignoring Windows line endings, spaces at the end of a line, and blank lines at the end. Everything else must match exactly.

## 3. The flow

1. The page fetches `GET /api/checks/<lesson id>`.
2. It calls `runCases(code, plan)` from `/check-runner.js`.
3. The runner starts a new worker and sends the code with each case's ID and inputs, **never any expected output**.
4. The worker loads Pyodide and posts `ready`. It then disables `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `importScripts` and `caches`. Then, for each case:
   - posts `start`
   - runs the code in a fresh `__main__` namespace with the case's replies
   - posts `case` with the status, the output (capped at 10,000 characters), and for errors the error type, line and message
5. The runner starts the time limit at each `start`. If a case is still running when it expires, the runner **terminates the worker**: that case is `timeout` and the rest are `not_run`. If Python cannot load within 30 seconds, every case is `unavailable`.
6. The page sends `forSubmission(reports)` as `runs` with `POST /api/check` (preview) or `POST /api/attempts` (signed-in student). Python's error message stays in the browser, because it can echo the learner's own text.
7. The API returns the result.

Each run status reported by the browser is one of: `ok`, `error`, `timeout`, `output_limit`, `not_run` or `unavailable`.

## 4. The result

```json
{
  "passed": false,
  "result": "needs_work",
  "feedback": "For the numbers 2 and 3, line 1 should be \"5\", but your program printed \"-1\".",
  "assessment": "browser_tests",
  "cases": [{"id": "small", "visibility": "visible", "status": "failed"}, {"id": "large", "visibility": "hidden", "status": "failed"}],
  "failed": {"id": "small", "visibility": "visible", "description": "the numbers 2 and 3", "reason": "wrong_output",
             "error_type": null, "line": null, "line_number": 1, "expected_line": "5", "actual_line": "-1"}
}
```

| Situation | `result` | `failed.reason` |
| --- | --- | --- |
| Every case printed its expected output | `passed` | (none; `failed` is null) |
| Output differs | `needs_work` | `wrong_output`; visible cases add `line_number`, `expected_line`, `actual_line` |
| A forbidden construct is used, or a required one is missing | `needs_work` | `construct`, with `construct` |
| The program asked for more replies than the case gives (`EOFError`) | `needs_work` | `missing_input` |
| The code does not parse (found by the server) | `execution_error` | `error`, with `error_type` and `line` |
| Python raised an error | `execution_error` | `error`, with `error_type` and `line` |
| Stopped at the time limit | `execution_error` | `timeout` |
| Printed more than 10,000 characters | `execution_error` | `output_limit` |
| An import the browser runtime does not have | `unsupported` | `unsupported` |
| Python could not start, or the reports do not match the plan (missing, extra or reordered cases, usually a page loaded before a content update) | `service_error` | (none) |

- When several cases fail, `failed` describes the first **visible** one, because the learner can see its data. Otherwise it describes the first hidden one.
- **For the feedback engine (ENG-04):** `failed.description`, `error_type`, `line`, and, for visible cases, the first different line. The runner's reports also carry Python's message for showing in the browser.
- Unit 1 responses keep their original shape, with `assessment: browser_practice` and no `cases` or `failed`.

## 5. What "hidden" means here

- **A hidden case's expected output never leaves the server.** It is not in the check plan, any lesson or catalog response, or any check or attempt result. A failing hidden case is named only by its description, which content validation keeps free of its inputs and expected lines. A test calls every GET route, signed out and as a student, and posts passing and failing reports to both check endpoints; the hidden expected output appears in none of the responses.
- **A hidden case's inputs do reach the browser,** in the check plan only (the test also confirms that). They have to: the code runs in the learner's browser, and it cannot run a case without its inputs. Knowing an input does not give away the answer; the learner would still have to work out the correct output, which is the task itself.
- **This is practice-level evidence, not tamper-proof** (`course-catalog.md` section 7.3). Someone who edits the reports their browser sends can claim any output. The same is true of unit 1 today. Checks that must resist that would need a separate, isolated hosted runner (deferred: cost, isolation and quotas).

## 6. Limits and safety

| Limit | Value | Enforced by |
| --- | --- | --- |
| Time per case | `time_limit_ms` (500 to 10,000; default 3,000), after Python loads | Runner terminates the worker |
| Python load | 30 seconds, then `unavailable` | Runner |
| Output per case | 10,000 characters | Worker stops the program; API rejects longer reports (422) |
| Cases per check | 10 | Content validation; API rejects more (422) |
| Network | None for learner code | Worker removes the network APIs after Pyodide loads; the worker's existing Content-Security-Policy only allows the Pyodide CDN in any case |
| State between cases | None | Fresh namespace per case. Imported modules stay loaded within one run, which is harmless |
| Request rate | Unchanged | The existing `check` and `attempts` rate limits |

## 7. Not done here

- **Lesson page:** it still uses the unit 1 flow. Calling the runner, and showing `failed` with highlighting and hints, is ENG-04 together with UI-05.
- **Unit 2 content** (EDU-04). The only lesson using this contract is the test fixture in `backend/tests/fixtures/browser_checks/`, which is never shown to learners.
- **Hosted runner:** a tamper-resistant evaluation service is out of scope (section 5).

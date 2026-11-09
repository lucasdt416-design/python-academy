# Browser behaviour checks: the contract (ENG-03)

Last updated: 2026-10-26 (America/Toronto)  
Status: **built** (merged, handoff 11). Used by all six lessons of Python unit 2 (EDU-04, handoffs 24 and 26) and all five of unit 3 (EDU-03, handoffs 27 and 32). Since UI-05 (handoff 22, in review), the lesson page runs it for any lesson whose challenge has a browser check.  
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
| `cases[].files` | Optional: files the program finds in its folder, by path (section 10) |
| `seed` | Optional, per case: the number `random` is seeded with (section 9) |
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
  "rule": "fixture.sum-two.case.small",
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
| An import that is refused (section 9), or a module the browser runtime does not have | `unsupported` | `unsupported` |
| Python could not start, or the reports do not match the plan (missing, extra or reordered cases, usually a page loaded before a content update) | `service_error` | (none) |

- When several cases fail, `failed` describes the first **visible** one, because the learner can see its data. Otherwise it describes the first hidden one.
- **For the feedback engine (ENG-04):** `failed.description`, `error_type`, `line`, and, for visible cases, the first different line. The runner's reports also carry Python's message for showing in the browser.
- Unit 1 responses keep their original shape, with `assessment: browser_practice` and no `cases` or `failed`.

## 5. What "hidden" means here

- **A hidden case's expected output never leaves the server.** It is not in the check plan, any lesson or catalog response, or any check or attempt result. A failing hidden case is named only by its description, which content validation keeps free of its inputs and expected lines. A test calls every GET route, signed out and as a student, and posts passing and failing reports to both check endpoints; the hidden expected output appears in none of the responses.
- **A hidden case's inputs do reach the browser,** in the check plan only (the test also confirms that). They have to: the code runs in the learner's browser, and it cannot run a case without its inputs. Knowing an input does not give away the answer; the learner would still have to work out the correct output, which is the task itself.
- **This is practice-level evidence, not tamper-proof** (`course-catalog.md` section 7.3). Someone who edits the reports their browser sends can claim any output. The same is true of unit 1 today. Checks that must resist that would need a separate, isolated hosted runner (deferred: cost, isolation and quotas).

**The rule (owner's decision 28, 2026-11-02): hidden inputs may reach the browser, because the worker has to run them, and hidden expected results never do.** It applies to every kind of hidden data: replies, function arguments, files and SQL rows. For ENG-10, broken reference programs may reach the browser, and a correct one may as long as it isn't the lesson's answer.

**The limit, stated honestly:** a learner who reads the hidden inputs could still hard-code the outputs. These checks are practice evidence, not a trusted grade. The leak tests stay, and they test the expected results.

## 6. Limits and safety

| Limit | Value | Enforced by |
| --- | --- | --- |
| Time per case | `time_limit_ms` (500 to 10,000; default 3,000), after Python loads | Runner terminates the worker |
| Python load | 30 seconds, then `unavailable` | Runner |
| Output per case | 10,000 characters | Worker stops the program; API rejects longer reports (422) |
| Cases per check | 10 | Content validation; API rejects more (422) |
| Imports | Only the modules in section 9 | The worker's import guard. A guide for learners, not a sandbox (section 9) |
| Network | None for learner code | Worker removes the network APIs after Pyodide loads; the worker's existing Content-Security-Policy only allows the Pyodide CDN in any case |
| State between cases | None | Fresh namespace and fresh files per case. Output a case left unflushed (for example one stopped at the output limit) is flushed and dropped before the next case starts (fixed in EDU-03 part 1, handoff 27). Imported modules stay loaded within one run, which is harmless |
| Request rate | Unchanged | The existing `check` and `attempts` rate limits |

## 7. Not done here

- **Lesson page:** done in UI-05 (handoff 22). The page loads lessons per unit (`GET /api/units/<unit id>/lessons`, where `check` says which checker a lesson uses), runs the cases with `runCases()`, and shows the result with the ENG-04 feedback: a Python error is explained in the browser and its line highlighted (`failed.line`; an output line number is never highlighted as a code line). Wrong output names its case as a rule, `<lesson>.case.<case id>` (the `rule` field), so a hint can be tagged for it.
- **Unit 2 content** (EDU-04): all six lessons use this contract (handoffs 24 and 26). None needs a required or forbidden construct: each check forces the idea through its cases.
- **Hosted runner:** a tamper-resistant evaluation service is out of scope (section 5).

## 8. Function-call checks (ENG-06)

A case can call a function the learner's program defined, instead of only reading what the program prints. Everything above still applies, and ordinary cases are unchanged: same plan, same reports, same results.

**No real lesson uses this yet.** It is tested with a TEST FIXTURE lesson (`backend/tests/fixtures/function_checks/`).

```json
{"id": "double-two", "description": "double(2)",
 "call": {"function": "double", "args": [2], "kwargs": {}},
 "returns": {"value": 4}}
```

| Field | Rule |
| --- | --- |
| `call.function` | The function's name: a valid Python name, not a keyword |
| `call.args`, `call.kwargs` | Plain JSON values: up to 10 of each, up to 2,000 characters together. `kwargs` keys are valid Python names |
| `returns.value` | What the function should return, as plain JSON (`null` is `None`), up to 10,000 characters |
| `returns.tolerance` | How far a number may be from the expected one. **Required** when the expected value holds a number with a fraction; content loading fails otherwise. Refused when there is no number for it to apply to |
| `expected` | Optional on a call: what the call should print. A call needs `expected`, `returns`, or both |
| `visibility` | `visible` or `hidden`. A hidden call's arguments reach the browser, and its answer never does (below) |

**What happens.** The worker runs the program as usual, with the case's replies, in a fresh namespace. It discards what the program printed so far, because a correct program may print other things first or call its own function. It then calls the function and reports what the call printed and returned. The per-case time limit and the output cap cover the program and the call together, and the worker is stopped the same way. `returned` is JSON text, sent only for a call that returned a value it can compare; the page also keeps Python's own display of the value, which stays in the browser.

**The equality rule** (`browser_checks.same_value`):

| Compared | Rule |
| --- | --- |
| `True`, `False` | Equal only to themselves. `True` is not `1`, and `False` is not `0` |
| Numbers | By value, so `4` equals `4.0`. With a tolerance, equal when the difference is at most the tolerance |
| Text | Exactly, including case and spaces |
| `None` | Only to `None` |
| Lists and tuples | A tuple is reported as a list, so `return 1, 2` and `return [1, 2]` both match `[1, 2]`. Same length and order, each item by these rules; the tolerance applies inside |
| Dictionaries with text keys | The same keys, each value by these rules |

**What can be returned.** Exactly `None`, `bool`, `int`, `float`, `str`, `list`, `tuple` and `dict` with text keys, nested up to 20 levels and up to 10,000 characters as JSON. Anything else, including sets, objects, subclasses, generators, `NaN` and infinity, is `not_comparable`, which names the type and asks for a simpler value. Sets are refused for now, because no return-value task needs them yet.

**Results added** (each `needs_work`, and the case's rule, `<lesson>.case.<case id>`, so a hint can be tagged for it):

| Browser reports | `failed.reason` | Message |
| --- | --- | --- |
| `status: no_function` | `no_function` | "Your program should define a function called double that takes 1 argument." |
| `status: bad_signature` | `wrong_arguments` | The same sentence, then "Yours cannot be called that way for double(2)." |
| `status: not_comparable` | `not_comparable` | "For double(2), your function returned a value this check cannot compare (set)…" |
| `status: ok`, a different value | `wrong_return`, with `expected_value` and `actual_value` | "For double(2), your function should return 4, but it returned 3." If it returned `None` and printed something, a sentence explains printing and returning |

Any function with a compatible signature passes, including one with defaults, `*args`, a `lambda` or a callable object. An error inside the function is an ordinary `execution_error`, with the line in the learner's code. A call case that reports `ok` with no usable `returned`, usually a page from before a content update, is `service_error`, as is a function-only status on an ordinary case.

**Hidden calls (decision 28).** A function runs in the browser, so a hidden call's arguments reach the browser, in the plan, like a hidden case's inputs. Its expected return value and output never do. A failing hidden call is named by its description only, and the description may not quote its arguments or answer (content loading refuses it). See section 5 for the limit: a learner who reads the arguments could hard-code answers. This is practice evidence.

## 9. Allowed imports and seeded random (ENG-07)

Status: **in review** (handoff 34).

**The list:** `math`, `random`, `datetime`, `json`, `csv`, `re`, and their submodules. It is `ALLOWED_MODULES` in `frontend/public/python-worker.js`, the only copy. Anything else is refused with `ModuleNotFoundError`, in Try it and in checks alike, which a check reports as `unsupported`.

**How it works.** Once Pyodide has loaded and the network APIs are gone, the worker replaces `__import__`. A module's own code imports what it needs as usual, because `random` needs `os`, for example. Only code that is not a module's own is limited: the learner's program, including `exec` and direct calls to `__import__`, and, since ENG-08b, the learner's own files too (section 12).

**This is a guide for learners, not a sandbox.** Python cannot sandbox itself. `random._os` reaches `os`, and from there other modules. The guard stops a learner reaching these by accident, and keeps lessons honest about what is available. **The security boundary is the worker:** no network APIs, its Content-Security-Policy unchanged, and nothing from the page. No new protection should ever be built on the assumption that the guard can't be bypassed.

**An allowed module does import blocked ones, inside itself.** `random` holds a reference to `os`, for example. That is expected, for the reason above.

**Seeded random.** Before each case the worker seeds `random` with the case's `seed`, or 0. An optional `seed` on a case, from 0 to 2,147,483,647, is sent to the browser in the plan only when set, like a hidden case's inputs. Pyodide's `random` gives the same numbers as CPython 3.12 (tested). Try it is not seeded, so a learner sees different numbers. A learner's own `random.seed()` still works.

**Adding a module.** Say why in a handoff, and check what it exposes. No lesson uses imports yet, so none of this changes what a learner meets in units 1 to 3, unless they import something.

## 10. File fixtures (ENG-08)

Status: **built** (#40, handoff 35).

A case can give its program files, and a worked example can give its "Try it" card files. They live only in Pyodide's in-memory filesystem, in the learner's browser.

| Rule | Value |
| --- | --- |
| Per case or example | Up to 10 files, each up to 10,000 characters |
| Paths | Relative, letters, digits, `-` and `_`, with `.` extensions and `/` folders. Each part starts with a letter or digit, so no `..`, and no absolute paths. Checked when content loads |
| Between cases | Before each case, the worker empties `/home/pyodide` and `/tmp`, goes back to `/home/pyodide`, and writes that case's files. Anything the program wrote before is gone |
| Saved? | **Never.** The page says "Files here are temporary" |
| Hidden cases | **A hidden case's files reach the browser,** in the plan, like its inputs: the program has to read them. The page never shows them, and a hidden description may not quote their lines. Hidden expected output still never leaves the server |
| What the page shows | The example's files, and one visible case's files as a sample |

**A given file can't stand in for one of Python's modules** (decision 30): content refuses a top-level file such as `random.py`, and the worker looks in the program's folder only after Python's own library. A learner's own second file is section 12.

## 11. Learner tests against reference programs (ENG-10)

Status: **built** (#46, handoff 41).

The learner's program is a set of tests, usually `assert` lines. Each case loads a **reference program** first, in the same fresh namespace, then runs the learner's tests. The result is judged by whether they ran to the end.

| A case's `test_should` | The tests ran to the end | A test stopped them |
| --- | --- | --- |
| `pass` (correct reference) | Good | `AssertionError`: "A test failed on …, which is correct". Any other error is a Python error, explained as usual |
| `fail` (broken reference) | "Your tests all passed on …, which has a bug" | Good, whatever the error, because the first case has shown that the tests run on correct code. A refused import is the exception: it is `unsupported` |

**Rules, checked when content loads:** every case has a `reference`, the first case is visible with `test_should: pass`, and at least one has `test_should: fail`. A reference case has no `call`, `returns` or `expected`. A reference must parse.

**What reaches the browser (decision 28).** Every reference, in the plan, because the tests run there. **So a correct reference must not be the lesson's answer.** Content validation can't check that; authors must. In unit 8 the learner writes tests, not the code under test, so this holds. A hidden case's `test_should` is its expected result and is not sent, and a hidden failure is named only by its description.

**Limits.** A learner who reads a broken reference could write a test aimed only at that bug, and these are practice evidence (section 5). Output is ignored. Imports in a reference follow the same list as the learner's.

## 12. The learner's own files (ENG-08b)

Status: **built** (#51, handoff 43).

A "Try it" card or a challenge can give the learner up to 3 files of their own, such as `helpers.py`, beside the program. Each has a tab above the editor, and the program imports it by name.

| Rule | Value |
| --- | --- |
| Content | `modules` on the example or the challenge: a name and the code it starts with, up to 10,000 characters. A challenge with learner files must use a browser check |
| Names | Short, lowercase, ending in `.py`, and a valid module name. **Never a name Python already has** (decision 30): `random.py`, `os.py`, `math.py` and every other standard library, built-in or Pyodide module are refused when content loads, and refused again by the worker |
| The import guard | **Applies inside the learner's files,** as in the program. A file of theirs may import the allowed modules and their other files, nothing else. The guard tells a learner's file from Python's own by where it lives: under `/home/pyodide` |
| Shadowing | The worker loads every allowed module before the learner's code runs, and puts the program's folder after Python's own library on the import path. So no file, given, the learner's own or written by the program while it runs, can replace a module Python has. Before this stage, a program could write `datetime.py`, import it, and import `os` from inside it |
| Between cases | Each case gets the files as they were when the learner pressed Run. Anything a case loaded or changed is forgotten before the next |
| What reaches the API | **Nothing of the learner's files.** The API gets the program, as before, and the reports. It checks what the program printed |
| Errors | An error inside a learner's file is reported at the program's line that called it, and "Go to line" opens `main.py` |

**Limits.** Construct rules (`require`, `forbid`) see only the program. The guard is still a guide, not a sandbox (section 9): `__import__("os", vars(random))` from a learner's file still gets past it, as `random._os` does. No real lesson uses learner files yet.

## 13. Pyodide pinned and checked (SEC-05)

Status: **in review** (handoff 44).

Pyodide still comes from the jsDelivr CDN, at version 0.27.7. **Every file it starts from is checked against a SHA-256 hash in `python-worker.js` before it is used**: `pyodide.js`, `pyodide.asm.js`, `pyodide.asm.wasm`, `python_stdlib.zip` and `pyodide-lock.json`. The hashes came from the CDN and match the official npm package `pyodide@0.27.7`, whose own integrity hash matches the npm registry.

| What | How |
| --- | --- |
| Checking | The worker fetches all five files first and checks each one. Only then does Pyodide start, from those bytes. **A changed or missing file means Python is unavailable,** in Try it and in checks, and nothing from it runs |
| Scripts | The two scripts are run from their checked bytes. `importScripts()` is no longer used, and the worker's policy no longer allows scripts from the CDN: `script-src 'unsafe-eval'` only. Connections still go only to the CDN |
| Other files | Anything else Pyodide asks the CDN for while it starts is refused. Today it asks for exactly these five (tested) |
| After loading | The worker drops its own copy of `fetch`, as well as removing the global ones, so learner code can't reach the network that way |
| Updating Pyodide | Change the version and all five hashes together, from the npm package, and run `pyodide-integrity.spec.ts`, which checks the hashes against the CDN |

**Why not self-host?** It would need the npm package as a dependency, and about 14 MB of files served by the app. Checked hashes give the same guarantee that the files are the ones reviewed, without either. Self-hosting is still an option if the CDN becomes unreliable.

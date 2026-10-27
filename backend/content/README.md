# Course content

All learner-facing course content lives here as JSON. `backend/app/content.py` defines the schema and validates everything when the API starts and in `python -m pytest`, so a mistake fails fast instead of reaching learners. The structure follows `docs/plan/course-catalog.md` section 3.

```text
content/
  catalog.json            every course and unit, in display order
  py/u01/hello.json       one file per lesson: <course>/<unit number>/<lesson id>.json
```

## Hierarchy

| Level | Where | ID rule | Example |
| --- | --- | --- | --- |
| Course | `catalog.json` | short slug | `py` |
| Unit | inside its course in `catalog.json` | `<course>.uNN` | `py.u01` |
| Lesson | its own file | `<course>.<slug>`; the five original lessons keep their old IDs | `hello`, `py.while-loops` |
| Task (card) | inside its lesson file | `<lesson id>.<card type>` | `hello.challenge` |

IDs are stable: never rename or reuse one for different content. For a wording or bug fix, increase `version` instead. Saved progress refers to these IDs.

## Status

Courses and units are `released` or `coming_soon`. A coming-soon course or unit has no lessons and cannot be started; the catalog shows it labelled "Coming soon". Release a unit by adding its lesson files, listing them in the unit, and changing its status.

## Lessons

Each lesson has exactly five tasks, in the order the lesson page shows them: `discover`, `example`, `predict`, `guided`, `challenge`. The challenge names the validator that checks it, for example `{"id": "bounded-story", "version": 1}`. Only validators the platform knows are accepted.

## Check messages and hints (unit 1 checker)

A `bounded-story` challenge lists the messages of its check rules in `messages`, each with a stable ID that starts with the lesson ID, for example `{"id": "hello.two-lines", "message": "…"}`, plus `<lesson>.passed` for a pass. The checker (`backend/app/lesson_checks.py`, `RULES`) reports these IDs; the API refuses to start if a rule has no message, a message has no rule, or an ID is used twice. To change what a learner reads, edit the message here and increase the challenge `version`.

Hints (`docs/plan/lesson-feedback.md` sections 7 and 8):

| Field | What it is |
| --- | --- |
| `hints` | The ladder, at most three, in order: a nudge, a bigger hint, the approach |
| `error_hints` | Hints with `tags`: Python error types (`NameError`, `SyntaxError`, `IndentationError`, `TabError`, `TypeError`, `ValueError`, `ZeroDivisionError`, `EOFError`) or this challenge's rule IDs. For a browser check, each case is also a rule, `<lesson>.case.<case id>`, reported when that case prints the wrong output. Offered first when that error or rule is shown. One hint per tag |
| `similar_example` | `code` and `note`: the same idea in another context, offered after the approach. It must not pass the check |
| `other_ways` | `code` and `note`: other valid solutions, shown only after passing. Each must pass the check |

No hint, tagged hint or similar example, alone or combined, may pass the check: `backend/tests/test_honest_checks.py` runs every combination through the real checker.

## Browser checks (unit 2 onwards)

A challenge can be checked by running the learner's code in their browser against test cases, instead of the unit 1 `bounded-story` checker. Set `"validator": {"id": "browser-tests", "version": 1}` and add a `check` with `cases` (`inputs`, `expected`, `description`, `visibility`), and optionally `require`, `forbid` and `time_limit_ms`. A hidden case's `description` is shown to learners, so it must not contain its inputs or expected output; loading fails if it does. The full contract, including the limits and what "hidden" guarantees, is in [`docs/plan/browser-checks.md`](../../docs/plan/browser-checks.md). The only lesson using it so far is a test fixture outside this folder (`backend/tests/fixtures/browser_checks/`), never shown to learners.

## Prerequisites

`prerequisites.required` and `prerequisites.suggested` list course or unit IDs. Every reference must exist, a course cannot require itself, and there can be no cycles.

## Checks

`cd backend && python -m pytest -q` validates this folder. It also checks that `/api/lessons` still returns exactly `tests/fixtures/legacy_lessons_v1.json`, the original unit 1 content. If you deliberately change unit 1 wording, update that fixture in the same pull request so the change is visible in review.

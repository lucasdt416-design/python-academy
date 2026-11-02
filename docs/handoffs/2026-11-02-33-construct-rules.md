# Handoff 33: Construct rule naming, a proposal (master run S26)

Date: 2026-11-02 (America/Toronto)  
Written by: Claude Code (implementer), in a separate git worktree  
For: the human maintainer, and ChatGPT or Claude chat (reviewer) without repository access  
Status: **in_review**: one pull request (#38), documentation only, not merged. No code changes, and nothing decided.

> **How to use this file:** upload it with `docs/plan/construct-rules.md`, `docs/plan/browser-checks.md` and handoffs 22 and 24. The pull request diff is the source of truth (`build.md` section 14).

## Starter prompt for the chat assistant

```text
You are reviewing a proposal for naming "construct rules" in Python Academy's
browser checks, docs/plan/construct-rules.md: rules that require or forbid a
piece of syntax. Check that each claim about today's code is true, that the IDs
fit the pattern, that the proposal would not fail a correct program unfairly,
and that nothing is presented as decided. Say whether section 4.4's test for
when a lesson may use a rule is the right one.
```

## Run plan details

| Field | Value |
| --- | --- |
| Stage | S26 |
| Base | `main`, at `59f8d0b`. No other PR needs to merge first |
| Part 2 boxes relied on | **None.** Every box is empty |
| Stages passed over to reach it | S16 to S25: each needs an empty box (B-E1, B-A1, B-I2 or B-P1), or a stage that does |

## 1. Step 0

`git fetch --all` and `gh pr list --state all`: #34 merged during the stage; #35 and #36 open, plus #37 (S02). No proposal for this on any branch. Worktree `../python-academy-construct`; the main folder was not switched.

## 2. Handoff record (build.md template)

| Field | Value |
| --- | --- |
| Task | Propose ID-safe names and the judge change for "uses elif, a loop or a function" rules, for Lucas to decide |
| Human goal | Decide once how construct rules work, and whether any lesson needs one |
| Non-goals | Any code; any change to a lesson; any decision |
| Data and compatibility | None |
| Deployment status | Not requested. Commits carry `[skip render]` |

### Files changed

`docs/plan/construct-rules.md` (new), `docs/run-log.md`, this handoff and its PDF.

## 3. What was found

| Finding | How it was checked |
| --- | --- |
| **No real lesson uses `require` or `forbid`** | A script over every lesson file in `backend/content/py/` |
| **`elif` is not detected reliably.** `else:` with an `if` inside gives the same parse tree as `elif`, apart from column numbers, so `constructs()` counts both as `elif`. Nothing is affected today, because no lesson requires it | Ran both in Python 3.12.14: `ast.dump` is equal, and the inner `if` is at column 4 or 0 |
| **The construct is checked before the cases,** so a wrong program lacking the construct hears only about the construct | Read `browser_checks.judge` |
| **A construct failure cannot have a tagged hint:** `rule` is null | Read `judge` and `content.feedback_errors` |
| **`if False:` with a `while` inside satisfies `require: ["while"]`** | Ran it: `ast.walk` finds the `While` |
| The proposed IDs fit the ID pattern, and `input()` does not | Ran the pattern from `content.py` |

## 4. Decisions and why

All proposals. Lucas decides.

| Decision | Options considered | Reason | Who decided |
| --- | --- | --- | --- |
| `<lesson>.require.<name>` and `<lesson>.forbid.<name>` | `<lesson>.uses-<name>`, as `variables.uses-variable` | Follows handoffs 22 and 24, mirrors the content fields, and keeps one name for both lists | Implementer (**assumption 1**) |
| `call-input` for calls | `uses-input`, `no-import` from handoff 22 | A name with "uses" inside `.require.` says it twice | Implementer (**assumption 2**) |
| New names `loop`, `nested-loop` and `called-function` | Only ID-safe versions of today's names | These are what S26 asks about, and today's names cannot express them | Implementer |
| Check `require` after the cases | Keep it first | A learner should first hear whether the program works | Implementer (**assumption 3**) |
| Recommend **not** building this yet | Build now | No lesson up to unit 5 needs it. Building it unused would be guesswork | Implementer |
| Did not edit `backlog.md` or `decision-log.md` | Add a row | The docs sync does that | Plan |

## 5. Bugs found and how they were fixed

No code was changed. **Not fixed, as this stage is documents only:** the `elif` detection in section 3. It affects no learner today.

Two slips in my first draft, found by re-reading it against the code: it said 14 lessons have browser checks (9 do on `main`), and it implied browser checks can already have per-rule messages (only bounded-story checks can).

## 6. How it was tested

| Check | Method | Result |
| --- | --- | --- |
| Links and tables | The script from handoff 28 | **2 local links and 84 table rows, 0 problems** |
| Claims about the code | Section 3's commands, and reading `content.py` and `browser_checks.py` at `59f8d0b` | All hold |

**Suites:** not run, as plan section 1.8 allows for a documentation stage; CI runs them. **Mocks:** none. **Deliberate-break controls:** none. **What this does not prove:** section 5 of the proposal is a reading of lesson plans that are not written yet.

## 7. Known limitations

- **Section 5's table is a judgement,** made before those lessons exist.
- **The proposal has never been tried.** The first lesson that needs it may show a gap.
- **The run log:** every open run branch carries an identical copy, so it should not conflict.

## 8. Live checks for you

None. Nothing a user can see has changed.

## 9. Questions for you

Section 7 of `construct-rules.md` has five, each **recommended, not yet confirmed**. The two to answer first:

1. **Build it now, or wait?** *Recommended: wait until a lesson needs it.*
2. **The naming.** *Recommended: `<lesson>.require.<name>` and `<lesson>.forbid.<name>`, with `call-input` for calls.*

## 10. For the docs sync

| Where | What |
| --- | --- |
| Backlog | A row for construct rule IDs (handoffs 22 and 24 asked for one), `proposed`, pointing at the document |
| Stage table | "33. Construct rules \| Naming proposal \| in_review (#38, handoff 33)" |
| Decision log | Replace "Construct rule IDs for browser checks" under "Open, awaiting the owner" with a link to the document's questions |

## 11. Next concrete action

Answer the questions, and merge this if you accept the document as a record of the proposal.

## 12. Removing the worktree safely

From the **main** folder, after this PR is merged:

```sh
cd /Users/DEV/Projects/python-academy
git -C ../python-academy-construct status --short   # expect nothing
git worktree remove ../python-academy-construct     # deletes only that folder; refuses if anything is uncommitted
git worktree prune
git branch -d docs/construct-rules                  # refuses if the branch is not merged
```

Don't delete the folder in the Finder or with `rm -rf`; Git would keep a stale record of it (`git worktree prune` fixes that).

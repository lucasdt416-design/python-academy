# Handoff 40: Hidden function calls (decision 28, follow-up to ENG-06)

Date: 2026-11-02 (America/Toronto)  
Written by: Claude Code (implementer), in a separate git worktree  
For: the human maintainer, and ChatGPT or Claude chat (reviewer) without repository access  
Status: **in_review**: one pull request (PR_NUMBER), not merged, not deployed. No migration, no new dependency, and no lesson uses it yet.

> **How to use this file:** upload it with `docs/plan/browser-checks.md` and handoff 29. The pull request diff is the source of truth (`build.md` section 14).

## Starter prompt for the chat assistant

```text
You are reviewing a change to Python Academy's browser checks: a check may now
call a learner's function with hidden arguments. Check that the expected value
and output can never reach the browser, that a failure message gives nothing
away, and that the docs say a learner could still read the arguments.
```

## Run plan details

| Field | Value |
| --- | --- |
| Stage | Follow-up to S05 (ENG-06), from the owner's decision 28. S05's text asked that hidden arguments never reach the browser; the decision replaces that |
| Base | `main`, at `1947f7a`. No other PR needs to merge first |
| Part 2 boxes relied on | **None** |

## 1. Step 0

`git fetch --all`, `gh pr list --state all`: #40, #43 and #44 open. Worktree `../python-academy-hidden`; the main folder was not switched.

## 2. Handoff record (build.md template)

| Field | Value |
| --- | --- |
| Task | Allow hidden function calls |
| Human goal | Unit 5 can catch a function that hard-codes the visible answers |
| Non-goals | Any lesson; ENG-10 |
| Data and compatibility | No migration. A content rule is loosened, and one is added. No API shape change |
| Deployment status | Not requested |

### Files changed

| File | Why |
| --- | --- |
| `backend/app/content.py` | Removes the refusal. A hidden description may not quote the call's arguments or answer |
| `backend/tests/test_function_checks.py` | The old refusal test becomes two new tests |
| `backend/tests/test_hidden_calls.py` (new, 6 tests), `frontend/tests/hidden-calls.spec.ts` (new, 3 tests), a fixture lesson and a recording | Section 5 |
| `docs/plan/browser-checks.md` | Section 8 |
| `docs/run-log.md`, this handoff and its PDF | The record |

## 3. Security note

**What now reaches the browser:** a hidden call's function name and arguments, in the plan. Someone reading network traffic can see them. **What does not:** its expected return value or output. They are not in the plan, a lesson or catalog response, or a result. **The limit:** a learner who reads the arguments could hard-code answers. These checks are practice evidence, not a trusted grade, as `browser-checks.md` section 5 says.

**The judge needed no change.** Handoff 29 had already kept a hidden case's answer on the server, and that test stays. The output panel already lists visible cases only.

## 4. Decisions and why

| Decision | Options considered | Reason | Who decided |
| --- | --- | --- | --- |
| Allow hidden calls | Keep refusing | Decision 28 | Owner |
| A hidden description may not quote arguments or the answer | Rely on authors | The description is shown to learners. It's the same rule as for inputs | Implementer |
| A separate fixture lesson | Add to `fixture.calls` | That would re-record every scenario of an unrelated PR's tests | Implementer |
| A return value of `None` isn't treated as a secret | Check it too | The word "null" would never fairly appear in a description | Implementer |

## 5. How it was tested

| Command | Result |
| --- | --- |
| Backend on SQLite | **813 passed, 11 skipped** |
| Backend on PostgreSQL | **824 passed** |
| `npx tsc --noEmit && npm run build` | OK |
| `CI=1 npx playwright test` | **282 passed** |

Covered in real Pyodide: a correct function passes both calls; a hard-coded one fails on the hidden call, named by its description, with its tagged hint, and with neither 57 nor 171 anywhere on the page. Every request must exactly match its recording. The backend proves the answer is in no response.

| Deliberate break (each undone) | Tests that failed |
| --- | --- |
| B1. A hidden description may quote arguments or the answer | **2** |
| B2. The plan sends a hidden call's answer | **5** |
| B3. The output panel lists hidden cases too | **1** |

**Mocks:** page tests use recorded real answers. Python, the worker and the page are real.

## 6. Bugs found and how they were fixed

None. Reading the judge and the page first found them already safe.

## 7. Known limitations

- **No lesson uses this yet.** Unit 5 (S08) still needs B-R2.
- **A short argument may clash with a description,** such as an argument of 2 and the words "2 numbers". Content loading then refuses it, and the author rewords.

## 8. Live checks for you

None: no real lesson uses it.

## 9. Questions for you

None.

## 10. For the docs sync

| Where | What |
| --- | --- |
| Backlog ENG-06 | Remove "Hidden calls are refused until the follow-up" |
| Stage table | "40. ENG-06 follow-up \| Hidden function calls \| in_review (PR_NUMBER, handoff 40)" |

## 11. Next concrete action

Review and merge.

## 12. Removing the worktree safely

From the **main** folder, after this PR is merged:

```sh
cd /Users/DEV/Projects/python-academy
git -C ../python-academy-hidden status --short   # expect nothing, or only ?? frontend/AGENTS.md
rm -f ../python-academy-hidden/frontend/AGENTS.md   # generated by Next.js, not part of the project
git worktree remove ../python-academy-hidden     # deletes only that folder; refuses if anything is uncommitted
git worktree prune
git branch -d eng/hidden-calls                   # refuses if the branch is not merged
```

Don't delete the folder in the Finder or with `rm -rf`; Git would keep a stale record of it (`git worktree prune` fixes that).

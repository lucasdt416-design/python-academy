# Handoff 30: Design documents for ten courses (master run S10)

Date: 2026-11-02 (America/Toronto)  
Written by: Claude Code (implementer), in a separate git worktree  
For: the human maintainer, and ChatGPT or Claude chat (reviewer) without repository access  
Status: **in_review**: one pull request (PR_NUMBER), documentation only, not merged. No code, no catalog change, nothing decided.

> **How to use this file:** upload it with `docs/plan/courses/` and `docs/plan/teaching-design.md`. The pull request diff is the source of truth (`build.md` section 14).

## Starter prompt for the chat assistant

```text
You are reviewing proposed course designs for Python Academy, in
docs/plan/courses/. Look hardest at the safety analysis in js.md and sql.md,
and the age and cost table in ai.md. Check that no learner code would run on
the server, that no hidden expected result reaches the browser, that every
fact has a source or says it is unconfirmed, and that nothing is presented as
decided.
```

## Run plan details

| Field | Value |
| --- | --- |
| Stage | S10 |
| Base | `main`, at `4b70a28`. No other PR needs to merge first |
| Part 2 boxes relied on | **None.** B-D1 is empty, so `sql` stays a design |

## 1. Step 0

`git fetch --all` and `gh pr list --state all`: #32, #33 and #34 open. No `docs/plan/courses/` on any branch. Worktree `../python-academy-courses`; the main folder was not switched.

## 2. Handoff record (build.md template)

| Field | Value |
| --- | --- |
| Task | For each of `git`, `web`, `js`, `sql`, `data`, `cs`, `node`, `fullstack`, `ce` and `ai`, a design document, as S10 lists |
| Human goal | Lucas can review each course's shape and risks before any of it is built |
| Non-goals | Code; catalog changes; `hack`, which S10 does not list; any decision |
| Data and compatibility | None |
| Deployment status | Not requested. Commits carry `[skip render]` |

### Files changed

`docs/plan/courses/README.md` and one file per course; `docs/run-log.md`; this handoff and its PDF.

## 3. The findings that matter

| Course | Finding |
| --- | --- |
| `ai` | **Claude's terms require 18** (Consumer Terms section 2, effective 2025-10-08), and Claude Code is not on the free plan (Pro is USD 20 a month, or USD 17 billed yearly). So the draft units "Setting up Claude" and "Claude Code in a practice repository" cannot be hands-on for students aged 13 to 17, and "parent-led setup" in `teaching-design.md` section 6.6 does not fix it. The design makes those units simulated for everyone, with hands-on labelled 18 or older |
| `js` | **An endless loop in a DOM lesson may freeze the whole page,** and nothing in the plain design can stop it. This is unsolved, and needs a decision before building |
| `js` | JavaScript in a worker has the app's origin, so it could call the API with the learner's cookies unless blocked. A `connect-src 'none'` worker policy is the real barrier |
| `sql` | `teaching-design.md` asks for a hidden dataset, whose rows would have to reach the browser. This is the same conflict as handoff 29 question 1 |
| `cs` | Telling binary from linear search by behaviour needs test objects that ENG-06's plain JSON cannot pass. This is a gap |
| `node`, `fullstack`, `ce` (C) | These cannot run in the product, and must never run on the server. Evidence is self-reported, and labelled so |
| `ai` | It is in `course-catalog.md` but not in `catalog.json` |

## 4. Decisions and why

All proposals. Lucas decides.

| Decision | Options considered | Reason | Who decided |
| --- | --- | --- | --- |
| `sql.js` 1.15.2 as the candidate | `@sqlite.org/sqlite-wasm`; `wa-sqlite` | MIT, small, and simple in-memory use. Sizes measured from the package. `wa-sqlite` was set aside because npm listed no licence | Implementer (**assumption 1**) |
| Git simulation is a small data model | A real Git library in the browser | Enough for what is taught; no dependency; never a shell | Implementer |
| Text charts first in `data` | `matplotlib` | No new download | Implementer |
| Numerical methods as the first `ce` elective | C first | No new runtime | Implementer |
| Added lessons and renamed `ai.u03`, `ai.u04` | Keep `teaching-design.md`'s titles | Those titles assume hands-on setup that the terms rule out for most students | Implementer (**assumption 2**) |
| `ai` prerequisites proposed | None | The catalog lists none, and a learner needs to run code to test an answer | Implementer (**assumption 3**) |

## 5. Bugs found and how they were fixed

No code. Near-miss: my first course index said "the other ten" courses are in `catalog.json`. There are nine others among these ten, found while checking the IDs against the file. Fixed.

## 6. How it was tested

| Check | Method | Result |
| --- | --- | --- |
| Links and tables | The script from handoff 28 over all 11 files | **10 local links and 191 table rows, 0 problems** |
| Required sections | A script looks for each of the 8 sections in each course document | 0 missing |
| Proposed IDs | A script collects every unit and lesson ID | **257 IDs, no duplicates, none clashes with `catalog.json`** |
| Outside links | `curl` on the pages read directly | Anthropic terms, Claude pricing, Google help and GitHub terms: 200 |
| Package facts | `npm view` and `npm pack`, measured 2026-11-02 | As in `sql.md` |

**Suites:** not run, as plan section 1.8 allows for a documentation stage, because no code or content changed. CI runs them on the PR. **Mocks:** none. **Deliberate-break controls:** none.

## 7. Known limitations

- **Outlines are first drafts** by the implementer, not reviewed by a teacher or subject expert.
- **ChatGPT's terms were read only through search results,** because the page refused a direct fetch. Gemini's age in Canada, and Copilot Free's age rule, are not confirmed.
- **Not legal advice.** Terms change, and `ai.md` says to re-check.
- **The browser claims in `web.md` and `js.md` are analysis, not tests.** Nothing was run on real browsers, and each says what to test.
- **The run log conflicts** with #33 and #34: keep the copy with the most rows.

## 8. Live checks for you

None. Nothing a user can see has changed.

## 9. Questions for you

Each course document ends with its own questions, and `courses/README.md` lists three that cut across them. Each is **recommended, not yet confirmed**. The three most important:

1. **One rule for hidden data, across courses:** may hidden data reach the browser, if hidden expected results never do? *Recommended: yes.*
2. **`ai`:** hands-on units for 18 or older only, with a simulated path and the same badge rules for everyone else? *Recommended: yes.*
3. **`js`:** test a separate-origin preview on real browsers before deciding how to handle endless loops in DOM lessons? *Recommended: yes. It may need a new Render service, which would be yours to make.*

## 10. For the docs sync

| Where | What |
| --- | --- |
| Stage table | "30. Course designs \| Ten course design documents \| in_review (PR_NUMBER, handoff 30)" |
| Backlog WEB-01, DATA-01, NODE-01, CE-01, TOOL-03 | Point to the documents; remain `proposed` |
| `teaching-design.md` section 6.6 | The age finding, once question 2 is answered |
| Decision log | A chapter from sections 3 and 4 |

## 11. Next concrete action

Read `ai.md`, `js.md` and `sql.md` first. WE12 stays blocked per course until you have reviewed that course's document.

## 12. Removing the worktree safely

From the **main** folder, after this PR is merged:

```sh
cd /Users/DEV/Projects/python-academy
git -C ../python-academy-courses status --short   # expect nothing
git worktree remove ../python-academy-courses     # deletes only that folder; refuses if anything is uncommitted
git worktree prune
git branch -d docs/course-designs                 # refuses if the branch is not merged
```

Don't delete the folder in the Finder or with `rm -rf`; Git would keep a stale record of it (`git worktree prune` fixes that).

## Sources

[Anthropic Consumer Terms](https://www.anthropic.com/legal/consumer-terms), [Claude pricing](https://claude.com/pricing), [OpenAI Terms of Use](https://openai.com/policies/row-terms-of-use/), [OpenAI help](https://help.openai.com/en/articles/8313401-is-chatgpt-safe-for-all-ages), [Gemini help](https://support.google.com/gemini/answer/13278668?hl=en-CA), [GitHub terms](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service), [Copilot plans](https://docs.github.com/en/enterprise-cloud%40latest/copilot/get-started/plans-for-github-copilot).

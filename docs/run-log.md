# Master run log

The plan is [`docs/plan/master-run.md`](plan/master-run.md). A new session reads this file on the newest run branch, checks that each `done` row has a PR and a pushed branch, and continues at the first stage that is not `done` (plan section 1.7).

## Stages

| Stage | Branch | Base | PR | Handoff | Status | Date | Tests (one line) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S00 | none | none | none | none | done | 2026-11-02 | State check; differences below |
| S01 | `docs/backlog-sync-3` | `main` | #33 | 28 | done | 2026-11-02 | Docs checks 0 problems; backend 541 and 552; build OK; Playwright 173 |
| S02 | `content/py-u03-part2` | `main` | #37 | 32 | done | 2026-11-02 | Backend 785 and 796; types and build OK; Playwright 255; axe 0 once animations finish; 6 deliberate breaks caught |
| S03 | none | none | none | none | blocked: waiting for B-S1 | 2026-11-02 | |
| S04 | none | none | none | none | blocked: waiting for B-I5 | 2026-11-02 | |
| S05 | `eng/function-checks` | `main` | #34 | 29 | done | 2026-11-02 | Backend 611 and 622; types and build OK; Playwright 200; axe 0; 9 deliberate breaks caught. Hidden calls refused: owner question |
| S06 | none | none | none | none | blocked: waiting for B-R1 and B-R2 | 2026-11-02 | Releases a unit in parts, on top of unit 3 |
| S07 | none | none | none | none | blocked: dependency S06 | 2026-11-02 | |
| S08 | none | none | none | none | blocked: waiting for B-R1 and B-R2 | 2026-11-02 | Also needs the earlier units, and an answer on hidden calls (handoff 29 question 1) |
| S09 | none | none | none | none | blocked: dependency S08 | 2026-11-02 | |
| S10 | `docs/course-designs` | `main` | #35 | 30 | done | 2026-11-02 | Docs checks 0 problems; 257 proposed IDs, no clashes |
| S11 | none | none | none | none | blocked: waiting for B-I8 and B-S2 | 2026-11-02 | |
| S12 | none | none | none | none | blocked: waiting for B-I6 and B-I7 | 2026-11-02 | |
| S13 | none | none | none | none | blocked: waiting for B-I2, B-I3 and B-I4 | 2026-11-02 | Also needs S04, S11 and S12 |
| S14 | none | none | none | none | blocked: waiting for B-E1 | 2026-11-02 | |
| S15 | `docs/retention` | `main` | #36 | 31 | done | 2026-11-02 | Docs checks 0 problems; every table in `db.py` covered |
| S16 to S18 | none | none | none | none | blocked: waiting for B-E1 | 2026-11-02 | |
| S19, S20, S22 to S24 | none | none | none | none | blocked: waiting for B-A1 | 2026-11-02 | |
| S21 | none | none | none | none | blocked: waiting for B-I2 | 2026-11-02 | |
| S25 | none | none | none | none | blocked: waiting for B-P1 | 2026-11-02 | |
| S26 | `docs/construct-rules` | `main` | #38 | 33 | done | 2026-11-02 | Docs checks 0 problems |
| WWD1 | none | none | none | none | blocked: dependency S09 | 2026-11-02 | |
| WD2 | `eng/allowlisted-imports` | `main` | #39 | 34 | done | 2026-11-02 | On `ac167e3`: backend 802 and 813; types and build OK; Playwright 275; 9 deliberate breaks, one gap closed. One earlier run failed many Pyodide tests, cause not established |
| WD3 | none | none | none | none | blocked: dependency WD2 and WD4 | 2026-11-02 | Both unmerged; chaining needs B-R1 |
| WD4 | `eng/file-fixtures` | `main` | #40 | 35 | done | 2026-11-02 | Backend 813 and 824; types and build OK; Playwright 272; axe 0; 8 deliberate breaks caught. Text conflicts with #39; the combination was tested |
| WD5 | `eng/reference-tests` | `main` | #46 | 41 | done | 2026-11-02 | Backend 828 and 839; types and build OK; Playwright 287 three times; 7 deliberate breaks, one gap closed. One earlier run failed one test, cause not established |
| WD6 | none | none | none | none | blocked: dependency WD5 | 2026-11-02 | Unmerged; also needs B-R2 |
| WD7 | none | none | none | none | blocked: dependency WD4 | 2026-11-02 | Unmerged; also needs B-R2 to release in parts |
| WD8 | none | none | none | none | blocked: waiting for B-R2 | 2026-11-02 | Five lessons, and needs WD2 |
| WD9 | none | none | none | none | blocked: dependency WD10 | 2026-11-02 | Its third lesson needs ENG-09 |
| WD10 to WD12 | none | none | none | none | blocked: dependency S23 | 2026-11-02 | S23 needs B-A1 |
| WE1 to WE4 | none | none | none | none | blocked: waiting for B-W1 | 2026-11-02 | |
| WE5, UI-01 | `ui/cosmetic-fixes` | `main` | #41 | 36 | done | 2026-11-02 | Backend 785 and 796; types and build OK; Playwright 259; 3 deliberate breaks caught |
| WE5, UI-02 to UI-04 | none | none | none | none | skipped: owner said wait (decision 29) | 2026-11-02 | |
| WE7, SEC-08 | `sec/pin-ci-actions` | `main` | #42 | 37 | done | 2026-11-02 | Backend 788 on SQLite; 3 deliberate breaks caught; CI proves the workflow. Out of queue order: see handoff 37 |
| Docs sync 4 | `docs/backlog-sync-4` | `main` | #43 | 38 | done | 2026-11-02 | Docs checks 0 problems. Records decisions 28 to 31 |
| SEC-08, Dependabot | `sec/dependabot-actions` | `main` | #44 | 39 | done | 2026-11-02 | Test passes; 3 deliberate breaks caught; only GitHub can show it runs |
| ENG-06 follow-up | `eng/hidden-calls` | `main` | #45 | 40 | done | 2026-11-02 | Backend 813 and 824; types and build OK; Playwright 282; 3 deliberate breaks caught |
| ENG-08b | none | none | none | none | blocked: dependency WD4 | 2026-11-02 | #40 unmerged; chaining needs B-R1. Must keep the guard on inside learner modules (decision 30) |

Owner merged #32 to #39, #41 and #42 on 2026-11-02. The run stopped at the cap of 5 open PRs. Not reached: WE6, the rest of WE7, WE8 and later.

**Keeping this file mergeable:** every open run branch carries an identical copy of this file, so they merge in any order. If one conflicts after a merge, keep the copy with the most rows.

## S00: state check, 2026-11-02

**Part 2 boxes:** none is ticked in `MASTER-RUN.md`, and the copy in `~/Downloads` is byte-identical. Nothing that needs a box was done. An unticked B-R1 means no chained PRs in this run, so each stage either starts from `origin/main` or is blocked. The plan's estimate that a first run does "S01, S02, S05, S06 and S07" assumes chaining is allowed.

**Open-PR cap:** the default of 5 applies. #32 is open, which leaves room for 4 more.

**Confirmed against the repository:** PR #32 is open and unmerged, targeting `main`. All PRs named as merged in Part 3 are merged, including #17 and #18. The newest migration on `main` is 0008. No handoff 21 exists. The highest handoff number on any branch is 27, on #32's branch, so the next free number is 28. `course-catalog.md` section 6.2 and the README are stale as described.

**Differences from Parts 3 and 4 of the plan:**

| Plan says | What the repository shows |
| --- | --- |
| Stage table lacks rows 20 to 27 | It stops at 15, so rows 16 to 19 are missing too. They were added in S01 |
| Decision log lacks chapters from handoffs 22, 26 and 27 | Handoff 24 also has no chapter, and its section 11 asks for one. It was added in S01. Handoff 25's owner answers were already in the plan's list |
| FB-02 and ENG-04 part 2a statuses are not listed as wrong | Both rows, and ASSESS-08, still said `proposed` although merged. Fixed in S01 |
| README-01 row exists to update | The backlog has no such row. One was added in S01 |
| `DOC-03`, `EDU-11` and `PORT-01` are IDs with no rows yet | Handoff 16 found no such items, and handoff 18 notes EDU-11 was a discarded draft ID. Not in Part 9, so not added; listed as a question |
| S21 names "ASSESS-06 and ID-01e learner level" | `independent-learners.md` section 10 says ID-01e is the invited group and that the learner level is ASSESS-06 alone. `build.md` and that plan win; the master run file is unchanged |
| S18 says FB-05 must never ship before FB-06 | The backlog's FB-06 row depends on FB-05. Left as it is, and listed as a question |
| Part 6 stage WD1 | Written "WWD1", a typing slip |
| Worktree `../python-academy-sync3` may exist | It did not; this run created it for S01 |
| About 30 remote branches | 33 lines in `git branch -r`, including `origin/HEAD` |

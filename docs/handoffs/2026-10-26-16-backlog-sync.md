# Handoff 16: Backlog sync (BACKLOG-SYNC)

Date: 2026-10-26 (America/Toronto)  
Written by: Claude Code (implementer)  
For: the human maintainer, and ChatGPT or Claude chat (reviewer) without repository access  
Status: **in_review**: one pull request, not merged. **Documentation only**: `docs/plan/backlog.md` is the only file changed besides this handoff. No application code, content, tests, settings or deployment changed.

> **How to use this file:** read it with the diff of `docs/plan/backlog.md`. The pull request diff is the source of truth (`build.md` section 14).

## Starter prompt for the chat assistant

```text
You are reviewing a documentation-only Python Academy PR that brings
docs/plan/backlog.md up to date with handoffs 09 to 14. I'm attaching the
backlog diff and this handoff. Check that every added row matches the
handoff it came from word for word, that statuses match what git and the
PR list show (merged, in review with a PR number, or proposed), that no
item was invented, and that build.md's status words were respected.
```

## 1. Handoff record (build.md template)

| Field | Value |
| --- | --- |
| Task | BACKLOG-SYNC: apply the backlog and stage-row changes that handoffs 09, 10, 11, 13 and 14 listed but did not make; set statuses from git and the PR list; add "Live checks still owed" |
| Human goal | One backlog that matches reality, without merge conflicts between open PRs |
| Repository and branch | `torontojohn/python-academy`, branch `docs/backlog-sync`, branched from `origin/main` |
| Base commit | `27ab31b` (`main` after PR #16) |
| Implementer / reviewer | Claude Code / owner |
| Deployment status | Not applicable (documentation only); not merged |

### What was read

- `docs/handoffs/` on `main` (handoffs 01 to 10).
- The three open branches via `git show`: handoff 11 (`eng/browser-checks`, PR #17), handoff 14 (`docs/decision-log`, PR #18) and handoff 13 (`docs/site-design`, PR #19).
- `gh pr list --state all`: PRs #1 to #16 are merged; #17, #18 and #19 are open. No closed-unmerged PRs. No other remote branches carry handoffs.

### Files changed

| File | Change |
| --- | --- |
| `docs/plan/backlog.md` | **Stage table:** 10 updated; rows 11, 13 and 14 added; a note that there is no stage 12. **New section "Live checks still owed".** Statuses updated for SEC-03, SEC-09, ASSESS-07 and ENG-03. Notes added to ENG-04 and UI-05 (from handoff 11). New groups "Documentation" (DOC-01, DOC-02) and "Public website" (SITE-01 to SITE-04), copied word for word from handoffs 14 and 13. Suggested-order item 6 notes ASSESS-07 merged and ENG-03 in review |
| `docs/handoffs/2026-10-26-16-backlog-sync.md` and `.pdf` | This handoff |

### Statuses set

From `git log origin/main` and `gh pr list`, 2026-10-26:

| Item | Status now | Evidence |
| --- | --- | --- |
| SEC-03 | in_review: merged (PR #13); live check owed (a) | PR #13 merged |
| SEC-09 | in_review: merged (PR #14), Report-Only; live check owed; enforce after a week of clean consoles | PR #14 merged |
| ASSESS-07 | in_review: merged (PR #16); live check owed (b) | PR #16 merged |
| ENG-03 | in_review (PR #17, handoff 11) | PR #17 open |
| ENG-04 | proposed (unchanged), plus the handoff 11 note | No PR |
| DOC-01, DOC-02 | in_review (PR #18, handoff 14) | PR #18 open |
| SITE-01 | in_review (PR #19, handoff 13) | PR #19 open |
| SITE-02, SITE-03, SITE-04 | proposed | No PR |
| FB-01 to FB-07, FB-09, PILOT-01 (admin, testers, feedback) | proposed (unchanged); FB-08 stays deferred | No PRs or branches exist for them |
| UI-05 | proposed (unchanged), plus the handoff 11 note | No PR |

## 2. Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Merged items are written `in_review: merged (PR #N); live check owed` instead of a new status "merged" | Writing a bare "merged" status, as the task listed | `build.md` section 18 and the backlog header allow only proposed, ready, in_progress, in_review, verified, blocked and deferred, and "verified" needs a live check. The backlog already used this form for stages 7 and 8. ASSESS-07 is therefore shown as merged, not as `verified`, until check (b) is recorded |
| Did **not** edit `build.md` | Adding a stage table there | `build.md` has no work-stage status table. Its only "Stage" table is the curriculum map in section 5, and the work-stage table lives in `docs/plan/backlog.md` section 1. Adding one to `build.md` would duplicate it. The new IDs follow `build.md` section 13's prefixes (DOC, SITE), which the backlog already allows for IDs not listed in `build.md` (as with SEC and FB) |
| Copy the DOC and SITE rows word for word from handoffs 14 and 13, and only update their status to name the PR | Rewording them | "Do not invent new items" |
| Paths to documents that exist only on open branches (`browser-checks.md`, `decision-log.md`, `site-design.md`, `engineering-book-outline.md`) are written as code, not links | Markdown links | A link to a file not yet on `main` would be broken. These become real files when their PRs merge |
| Added a third line under "Live checks still owed": stage 8, SEC-09, is also unrecorded | Only (a) and (b), as asked | It is a fact from the stage table, not a new item. Remove it if you prefer only the two |

## 3. Things I was unsure about, or could not find

**Please read.** The task named several items and handoffs that **do not exist** anywhere I can see: not on `main`, not on any remote branch, and not in any PR or commit message. Following "do not invent new items", **none of them were added**:

| Named in the task | What I found |
| --- | --- |
| **The admin/tester handoff** | No such handoff, branch or PR. The admin, tester and feedback work exists only as backlog items FB-01 to FB-09 and PILOT-01 (from stage 5), all proposed. Their statuses are unchanged |
| **The ENG-04 handoff** | No such handoff, branch or PR. ENG-04 exists as a proposed backlog item (added by PR #15); only handoff 11's note was added to it |
| **DOC-03** | Not found anywhere; only DOC-01 and DOC-02 exist (handoff 14) |
| **EDU-11** | Not found. Video scripts are **EDU-10** (PR #15). EDU-11 was a draft ID renamed before that PR merged. EDU-10 is unchanged |
| **PORT-01 (parked)** | Not found anywhere |

If these come from another session or machine, push their branches or handoffs, and a follow-up sync can add them exactly.

**Also:**
- **Stage numbering:** handoffs 13 and 14 were numbered as asked, and no handoff 12 exists. The stage table says so, rather than renumbering.
- **Handoff 11's change to `course-catalog.md` section 7.3** ("browser behaviour checks are built") was not applied. The task limited edits to the backlog and `build.md`, and ENG-03 is not merged yet.

## 4. Bugs found and how they were fixed

None.

## 5. How it was tested

- **Source check:** each added or changed row was compared with the handoff section it came from: handoff 11 section 6, handoff 13 section 6, handoff 14 section 6, and handoff 10's status. Each status was compared with `gh pr list --state all`.
- **Link check:** every relative link in `docs/plan/backlog.md` resolves (`../../build.md`, `course-catalog.md`, `feedback-security.md`). No new links were added.
- **Conflict check:** none of the open PRs (#17, #18, #19) edits `docs/plan/backlog.md`; each edits only `build.md`, which this PR does not touch. `git merge-tree` shows this branch merges cleanly with all three.
- **Full test suites,** run although nothing executable changed:

  | Command | Result |
  | --- | --- |
  | `cd backend && .venv/bin/python -m pytest -q` | `213 passed, 9 skipped` (the 9 need PostgreSQL) |
  | `cd frontend && npm run build` | Compiled successfully |
  | `cd frontend && CI=1 npm run test:e2e` | `30 passed` |

- **Mocks:** none.
- **Deliberate-break controls:** not applicable; no code.

## 6. Live checks for you

- [ ] **Read the diff** of `docs/plan/backlog.md`. Nothing is deployed.
- [ ] Tell me whether the missing items in section 3 exist somewhere I cannot see.

## 7. Next concrete action

The owner reviews and merges this PR. When PRs #17, #18 and #19 merge, their rows move to `verified` (documentation) or to "merged; live check owed" (ENG-03). The owed live checks (a) and (b) are recorded in section 1 of the backlog.

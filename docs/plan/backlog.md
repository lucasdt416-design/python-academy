# Python Academy backlog

Last updated: 2026-10-25 (America/Toronto)  
Status: **proposed**; decisions 11, 12, 13, 16, 18, 19, 21, 22 and 23 answered by the owner on 2026-10-25. Status words follow `build.md` section 18: proposed, ready, in_progress, in_review, verified, blocked, deferred. Priorities: **Now**, **Next**, **Later**, plus the timing words `build.md` section 13 already uses (for example "Before broader use").  
Related: [`build.md`](../../build.md), [`docs/plan/course-catalog.md`](course-catalog.md), [`docs/plan/feedback-security.md`](feedback-security.md).

**This file is the source of truth for the order of work.** IDs and what they mean follow `build.md` section 13; where this file and `build.md` disagree on an ID, its meaning, or its priority, `build.md` wins until one is deliberately updated (section 8 lists the differences found when this file was added). A backlog item becomes `verified` only with linked evidence (PR, commit, test results, live check).

Decision numbers continue the sequence in `docs/plan/course-catalog.md` section 9 (decisions 1–10 there), so "decision 13" means the same thing in both files.

## 1. Where we are

| Stage | What | Status |
| --- | --- | --- |
| Plan | `docs/plan/course-catalog.md` | verified (PR #6) |
| 1. ENG-01 | Content format and result states | verified live (PR #5) |
| 2. ENG-02 | Migrations, XP and badge ledgers | verified live (PR #7) for this stage; the rest of ENG-02 is open (section 5) |
| 3. Catalog UI | Catalog, course pages, lesson sidebar | verified live (PR #8) |
| 4. Goals and recommendations | Goal card, rule-based recommendation | in_review: merged (PR #9, 2026-10-25); owner's live check not yet recorded |
| 5. Backlog and feature plans | This file, feature specs, feedback security | verified (PR #10, documentation only) |
| 6. SEC-01 and SEC-04 | Rate limits; security headers with the page CSP in Report-Only mode | in_review (handoff 06) |

## 2. Suggested order

1. Record the stage 4 live check.
2. **SEC-01 and SEC-04** (rate limits, security headers). Feedback adds a new place where users can send text, so limits come first. In review (stage 6); after the owner's live check, switch the page CSP to enforce mode (handoff 06 section 4).
3. **FB-01 to FB-07**: admin, testers, feedback button, admin inbox (security plan: `docs/plan/feedback-security.md`).
4. **PILOT-01**: invite the first learner and collect feedback through the new button.
5. **ENG-03**: browser behaviour checks, then **EDU-04** (Python unit 2) with its first **unit check**.
6. **OPS-05**: cost review (the owner has set a reminder for 2026-11-08).

## 3. Feature spec: testers, feedback, admin inbox

Recorded in the plan as section 11 of `docs/plan/course-catalog.md`; threats and controls in `docs/plan/feedback-security.md`.

**Goal.** The maintainer can mark chosen students as testers. Testers press a button anywhere in the app to report a problem or idea. The maintainer signs in as admin, reads the feedback in one place, and turns it into fixes.

**Proposed behaviour**

- **Admin.** One admin to start (the owner). Admin is decided on the server only, from a list of verified Google account emails kept in a server setting, never in source code and never from anything the browser sends. Every admin request is checked again on the server. Nobody can make themselves admin (decision 14, proposed).
- **Tester.** A flag on a student account, set only by the admin from an admin page. **Testers are students only (decision 23).** Testers see a "Send feedback" button on every page and lesson card. **Only testers and the admin get the button; parents never do (decisions 11 and 23).**
- **Form.** Type (confusing, bug, wrong grading, idea, other) and a message with a length limit. The app attaches context automatically: page, lesson and task ID, content version, browser type, time. Learner code is **not** attached by default; an optional "Include my code" checkbox shows exactly what will be sent (decision 17, proposed). No screenshots in the first version.
- **Inbox (admin).** List with filters (status, type, lesson). Statuses: new, triaged, in_progress, fixed, wont_fix. Internal notes. A field for a GitHub issue link. A "Copy digest" button that produces plain text for pasting into Claude Code or ChatGPT, with IDs and no email addresses.
- **Safety.** Plain text only and escaped on display. Server-side length limits. Sign-in required. Rate limited per user. Existing origin (CSRF) checks apply. A short notice in the form: do not include passwords or personal details.
- **Anonymous but signed in (decision 12).** Sign-in is required only to stop bots. The stored feedback has **no user ID, name or email**, so the admin cannot see who sent it. Per-user rate limits use a separate counter table that holds no message text and expires within a day. Trade-off: the admin cannot reply to or follow up with a tester, and testers cannot see the status of their own items (FB-08 dropped).
- **Privacy.** Only the admin sees feedback. Parents never see it (decision 19, answered 2026-10-25, following decision 23). Because optional code and free text could still identify someone, the form warns not to include names or personal details, and the admin view never shows account data.
- **Retention and cap (decision 18).** Items are deleted 50 days after creation at the latest, and the inbox holds at most 90 items at a time. When it is full, the oldest resolved items are deleted first; if none are resolved, the new item is rejected with a clear message. "Resolved" means status `fixed` or `wont_fix` (decision 18).

**Acceptance tests (real accounts, not mocks, per `build.md` section 12):** a non-admin gets 403 on every admin route; only an admin can set the tester flag, and only on student accounts; parents never see the button or can send feedback; emoji and unusual characters are stored and shown safely; over-length and over-rate submissions are rejected; optional code is only sent when the box is checked; a full inbox drops the oldest resolved item, or rejects the new one when nothing is resolved.

## 4. Feature spec: end-of-unit skill checks

Recorded in the plan as section 12 of `docs/plan/course-catalog.md`.

**Goal.** Every unit ends with a short check where learners put the unit's skills to use, so finishing cards is not mistaken for understanding (`build.md` section 3).

**Proposed behaviour**

- **Shape.** Four to six tasks, one card at a time, untimed: predict the output, spot the bug, and one or two short write-the-code tasks that reuse the unit's project. Roughly 10 to 15 minutes. **Variants by learner level (decision 21):** each check has versions for a self-chosen level (high school or university) that change the context, difficulty and examples, not the skills tested. The level is chosen by the learner; it is never derived from a birthdate, and the check never asks for one.
- **Fairness.** Multiple correct solutions accepted. Hints allowed and recorded as support data, not penalties. Retakes use different variants. Technical failures show "Unable to assess" and keep the draft; they never count as a failed attempt.
- **Rewards (decision 16).** Passing the check awards the unit's **skill badge** and **no extra XP**; the unit project keeps its 200 XP (plan section 6.1). The check is the "later, different variation" that skill badges need (plan section 6.2). It is practice evidence, not certification.
- **Needs first:** the browser behaviour-check contract (ENG-03), because the current server checker only handles unit 1.
- **Decided:** passing is required to complete a unit, and learners can retake it (decision 13). A unit is complete when both its project and its check are done; the check does not replace the project (decision 16). Learners who already completed unit 1 keep it as complete; the unit 1 check is optional for them and earns the badge (decision 22). **Open:** the exact pass rule (decision 15).

## 5. Backlog

### Planning and foundations (from `build.md` section 13)

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| PLAN-01 | Now | Review the plan and select a milestone owner | None | verified: plan reviewed and decisions recorded (PR #6); milestone owner is Lucas, the maintainer (owner answer 2026-10-25) |
| PLAN-02 | Now | Give the continuing maintainer appropriate repo access | Owner | verified: maintainer account has push access (GitHub API check, 2026-10-24) |
| ENG-01 | Next | Typed content and result-state contracts | None | verified (PR #5, live check 2026-10-25) |
| ENG-02 | Next | Versioned evidence/progress and schema migrations | ENG-01 | in_progress: migrations and award ledgers verified (PR #7); versioned skill evidence, progress records and retention not yet done |

### Safety and operations

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| SEC-01 | Now | Rate limits and quotas on write endpoints: `/api/check`, invitations, attempts, enrolment, goal changes and sign-in (done in stage 6; counters in memory, see handoff 06), and the future feedback endpoint (its own database counters, `feedback-security.md` section 7) | None | in_review |
| SEC-02 | Next | Make the API a private Render service with no public URL; confirm the frontend proxy still works | None | proposed |
| SEC-03 | Next | Logout revokes the session on the server (today a stolen cookie works up to 24 hours); required before the admin inbox (FB-06) ships, see `feedback-security.md` | Migration | proposed |
| SEC-04 | Now | Security headers: Content-Security-Policy and HSTS on the main app. Stage 6 adds HSTS, `frame-ancestors 'none'` (enforced) and the page CSP in Report-Only mode; the item is verified once the CSP is switched to enforce mode after a clean live check | None | in_review |
| SEC-05 | Later | Pyodide and CDN integrity: self-host or pin with integrity checks where possible | None | proposed |
| SEC-06 | Later | Keep invitation tokens out of URLs and request logs | None | proposed |
| SEC-07 | Next | Branch protection on `main` requiring passing checks (owner action; may need a paid GitHub plan, otherwise merge only on all-green) | Owner | proposed |
| SEC-08 | Later | Pin CI actions to commit SHAs; routine dependency updates | None | proposed |
| SEC-09 | Next | Replace `'unsafe-inline'` in the page CSP's `script-src` with per-request nonces (a Next.js proxy file and dynamic rendering), so injected inline script is blocked; proposed as a dependency of the admin inbox (FB-06), owner to confirm | SEC-04 | proposed |
| OPS-01 | Before broad rollout | Confirm staging, recovery, privacy, quotas and alerts (umbrella item; OPS-02 to OPS-04 are parts of it) | OPS-02, OPS-03, OPS-04 | proposed |
| OPS-02 | Next | Part of OPS-01: confirm backups and a restore drill; add staging | None | proposed |
| OPS-03 | Later | Part of OPS-01: operational alerts | OPS-02 | proposed |
| OPS-04 | Next | Part of OPS-01: data retention policy: feedback 50 days max and 90 items max (decision 18); goals and placement data to be decided | Before FB-05 ships | proposed |
| OPS-05 | Next | Reduce Render costs: review billing, workspace plan, 15 GB database storage; later consider one combined service or a free-tier database (reminder set by the owner for 2026-11-08) | Billing screenshot | proposed |

### Testers, feedback and admin

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| FB-01 | Next | Decide admin identity (email allowlist) and record it in the plan; tester rules (students only, decision 23) and parents' access (none, decision 19) are decided | Decisions 14, 17; ID-01 | proposed |
| FB-02 | Next | Migration: anonymous `feedback` table (no user ID), tester flag, short-lived rate-limit counters, 50-day cleanup, 90-item cap | FB-01 | proposed |
| FB-03 | Next | Admin role and server-side guard, with tests for 403 on every admin route | FB-01 | proposed |
| FB-04 | Next | Admin page to mark students as testers (student accounts only) | FB-03 | proposed |
| FB-05 | Next | Feedback button and form (testers and the admin; never parents) with auto-attached context and optional code | FB-02, SEC-01, OPS-04 | proposed |
| FB-06 | Next | Admin inbox: list, filters, statuses, notes, GitHub issue link | FB-03, FB-05, SEC-03 | proposed |
| FB-07 | Next | "Copy digest" export for pasting into an assistant, with no emails and no code by default | FB-06 | proposed |
| FB-08 | — | Testers see status of their own items (dropped: not possible with anonymous feedback) | None | deferred |
| FB-09 | Later | Create GitHub issues from feedback automatically (needs a token and review; manual links first) | FB-06 | deferred |
| PILOT-01 | Next | Invite the first learner, watch a 10-minute session, collect feedback through the button | FB-05 | proposed |

### Assessment

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| ENG-03 | Next | Browser behaviour-check contract: the Pyodide worker runs learner code against test cases from the content file, with limits and result states including `execution_error` | None | proposed |
| ASSESS-01 | Next | Decide the remaining unit-check rule (the pass rule, decision 15) and record it in the plan | None | proposed |
| ASSESS-02 | Next | Content schema: `unit_check` task type, level variants (high school, university) and validation | ENG-03 | proposed |
| ASSESS-06 | Next | Learner level setting (self-chosen, never a birthdate; decision 21) used to pick the check variant | ASSESS-02 | proposed |
| ASSESS-03 | Next | Unit check interface (cards, retake with new variants, "Unable to assess" handling) | ASSESS-02 | proposed |
| ASSESS-04 | Next | Unit check for unit 1 using the existing bounded checker; optional for learners who already completed unit 1, and earns the badge (decision 22) | ASSESS-02 | proposed |
| ASSESS-05 | Next | Award the unit's skill badge (no XP) from the check through the existing ledgers; the unit project keeps its 200 XP (decision 16) | ASSESS-03 | proposed |
| EDU-01 | Next | Write placement question and task examples for the current four skills (Issue #4) | None | proposed |
| EDU-02 | After design | Pilot placement (the optional skills check) on one skill before all four | EDU-01, ENG-03 | proposed |

### Curriculum

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| EDU-04 | Next | Python unit 2, Numbers and decisions, with its unit check | ENG-03, ASSESS-02 | proposed |
| EDU-03 | After checker design | Python unit 3, Repeat and explore (loops that always end), with a project extension | EDU-04 | proposed |
| EDU-05 | — | Not used: this ID was briefly unit 3, which is EDU-03 in `build.md` | — | deferred |
| EDU-06 | Next | Unit 4, Keep track of a world (lists, dicts, sets) | EDU-03 | proposed |
| EDU-07 | Next | Unit 5, Organize your code (functions); project Adventure v2 | EDU-06 | proposed |
| EDU-08 | Later | Units 6 to 12: errors, libraries, tests, files, regex, classes, final project | EDU-07 | proposed |
| EDU-09 | Later | Hackathon Ready course (7 units) | Python units 1 to 7 | proposed |
| TOOL-01 | Alongside projects | Draft "Git versus GitHub" and "first commit" lessons with a safe practice repo | Python unit 1 | proposed |
| TOOL-02 | Later | The full Git and GitHub Essentials course, including a real first pull request | TOOL-01 | proposed |
| WEB-01 | Later | Design the website project track and isolated previews | Earlier courses | proposed |
| DATA-01 | Later | Design the SQL runtime and first investigation project | Earlier courses | proposed |
| NODE-01 | Later | Plan the Node.js/SQL capstone | WEB-01, DATA-01 | proposed |
| CE-01 | Later | Map university courses to optional deep-dive units | Actual course outlines | proposed |

### Interface and accounts

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| UI-01 | Next | Cosmetic fixes: stacked chips on the Python course card; small "Goal:" text in the parent view | None | proposed |
| UI-02 | Later | "Not now" button and storage for dismissed recommendations | None | proposed |
| UI-03 | Later | Record when a learner overrides a recommendation (plan 4.4) | None | proposed |
| UI-04 | Later | Pause a course (plan 4.2) | None | proposed |
| UI-05 | Next | Lesson page reads lessons per unit instead of the legacy shape (needed once unit 2 exists) | None | proposed |
| UI-06 | Later | Show a goal-specific capstone when a path is finished (proposed mapping: scratch to Python final project, hackathons to Hackathon Ready, university to Engineering Depth, websites to Full-Stack Builder, data to Data Investigation) | Decision 20 | proposed |
| ID-01 | Next | Decide independent adult learner onboarding and visibility: account lifecycle, adult control, parent boundaries, migration | Product decision | proposed |
| QA-01 | Before broader use | Audit core lesson accessibility and grading reports: real screen reader, Safari and Firefox, reproducible defects and retest evidence | None | proposed |
| QA-02 | Before broader use | Part of QA-01: report on incorrect grading rejections (uses feedback data) | FB-06 | proposed |

## 6. Decisions

Numbers continue from `docs/plan/course-catalog.md` section 9.

| # | Decision | Answer |
| --- | --- | --- |
| 11 | Who gets the feedback button? | Testers only (answered 2026-10-25); the admin also sees it (decision 23) |
| 12 | Is feedback tied to an account? | Sign-in required only to stop bots; stored anonymously with no user ID, name or email (answered 2026-10-25) |
| 13 | Is passing the unit check required to complete a unit? | Yes, and learners can retake it (answered 2026-10-25) |
| 14 | How is the admin identified? | Server-side list of verified Google emails; owner only (proposed, confirm) |
| 15 | What counts as passing a unit check? | All core tasks pass; hints allowed. Pilot and adjust (proposed) |
| 16 | Does the check replace the unit project milestone? | No. The unit project keeps its 200 XP; passing the check awards a skill badge and no extra XP; a unit is complete when both the project and the check are done (answered 2026-10-25) |
| 17 | Does feedback include the learner's code? | Only with an opt-in checkbox (proposed) |
| 18 | Feedback retention | Delete after 50 days; at most 90 items. When full, delete the oldest resolved items first (resolved means `fixed` or `wont_fix`); if none are resolved, reject the new item with a clear message (answered 2026-10-25) |
| 19 | Do parents see feedback? | No. Parents never see the feedback button or any feedback, which follows from decision 23 (answered 2026-10-25) |
| 20 | Capstone for each goal | As proposed in UI-06 (proposed) |
| 21 | How is the unit-check variant chosen? | Variants by a self-chosen learner level (high school, university). The level is never derived from, and never asks for, a birthdate. The enrolment age gate is unchanged (answered 2026-10-25) |
| 22 | What happens to learners who already completed unit 1? | They keep unit 1 as complete. The unit 1 check is optional for them and earns the badge (answered 2026-10-25) |
| 23 | Who can be a tester, and who sees the feedback button? | Testers are students only. The admin account also sees the button. Parents never do (answered 2026-10-25) |

The questions raised when this file was added (handoff 05) were answered by the owner on 2026-10-25 and are recorded above as decisions 16, 18, 21, 22 and 23, and in items SEC-03, OPS-05 and PLAN-01.

## 7. Maintenance

Move an item to `in_progress` when a branch exists, `in_review` when a pull request is open, and `verified` only after the live check. Record decisions with date, reason and consequence. Split items into linked GitHub issues when work starts.

## 8. Reconciliation with `build.md` (2026-10-25)

When this file was added, every ID was checked against `build.md` section 13 and `docs/plan/course-catalog.md`. Where they differed, `build.md` was followed:

| # | What differed | Resolution |
| --- | --- | --- |
| 1 | **OPS-01** meant "reduce Render costs" here, but "confirm staging, recovery, privacy, quotas and alerts" in `build.md` | OPS-01 keeps the `build.md` meaning and priority (Before broad rollout); OPS-02 to OPS-04 are marked as parts of it; the cost review moved to a new ID, **OPS-05** |
| 2 | **EDU-01** was "optional skills check for placement", Later, depending on ENG-03; `build.md` has "write placement question/task examples for the current four skills", Next | EDU-01 takes the `build.md` wording and priority; building the skills check is **EDU-02**, as in `build.md` |
| 3 | **EDU-02** and **EDU-03** were missing; this file's **EDU-05** (unit 3 loops) is what `build.md` and the plan call EDU-03 | EDU-02 added; unit 3 renamed **EDU-03** with the `build.md` priority (After checker design); EDU-05 marked unused; EDU-06 now depends on EDU-03 |
| 4 | **TOOL-01** was the full Git course, Later; `build.md` has "draft Git versus GitHub and first commit lessons", Alongside projects | TOOL-01 takes the `build.md` wording and priority; the full course is a new ID, **TOOL-02**, Later |
| 5 | **ID-01** was Later; `build.md` has Next | Priority set to Next |
| 6 | **QA-01** was only accessibility; `build.md` includes grading reports | QA-01 takes the `build.md` scope; QA-02 is marked as part of QA-01 |
| 7 | **WEB-01, DATA-01, NODE-01, CE-01** were one row meaning "build the courses"; `build.md` has separate design and planning tasks | Split into four rows with the `build.md` meanings |
| 8 | **PLAN-01, PLAN-02, ENG-01, ENG-02** were missing | Added with their status and evidence |
| 9 | **ENG-02**: the stage table said verified, but `build.md`'s ENG-02 also covers versioned skill evidence, progress records and retention | Stage 2 stays verified; ENG-02 itself is in_progress |
| 10 | **Decisions 1–10** here reused the numbers of the plan's decisions 1–10, which mean different things (for example plan decision 3 is "build Python unit 2 next") | Renumbered 11–20 and references updated; the new level decision is 21 |
| 11 | **FB-08** used "Dropped" as a priority, which is not a `build.md` priority or status word | Priority "—", status deferred, with "dropped" explained in the item |
| 12 | **Stage 4** was in_review "confirm merge" | PR #9 is merged; it stays in_review until the owner's live check is recorded |

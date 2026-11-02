# Python Academy master run plan

Written 2026-11-02 (America/Toronto) by the planning chat, for Lucas (owner) and Claude Code (implementer).
Status: **proposed**. This is a work queue, not a decision record. Where it says "recommended", that is the planning chat's opinion, and nothing recommended is decided until Lucas ticks it in Part 2.

**This file does not replace `build.md`.** `build.md` is the plan and the rules of work (ID rules in section 13, the handoff template in section 14, status words in section 18). This file is a queue of stages to run under those rules. If this file and `build.md` disagree, `build.md` wins and you say so in the handoff.

Where to put it: copy it unchanged into `docs/plan/master-run.md` in the first PR (commit it unchanged first, then correct it in later commits so the diff shows what changed).

---

## Part 0. What this run is

Lucas is in midterms this week and cannot review or merge between stages. He wants as much of the roadmap built as is safe, in one long run. That changes only one thing about the usual workflow: stages are **chained** (section 1.3) instead of each waiting for a merge. It changes nothing about quality, tests, handoffs or safety.

The run is **resumable**. It will not finish in one session: Claude Code has hit usage limits before. Section 1.7 says how to stop cleanly and how to resume.

Nothing here deploys anything, changes Render or Google settings, or spends money. Those are human tasks (Part 5).

---

## Part 1. Rules of the run (non-negotiable)

### 1.1 Safety first, always

1. Learner code runs only in the browser (Pyodide worker). Never on the server. Never relax the worker CSP, the 3-second stop, the output limit or the "unsupported import" state without a stage that says so and a security note in its handoff.
2. Hidden expected output never reaches the browser. The API judges reported output and never runs learner code.
3. No secrets in the repository. Never write a real key, token, password or email list into any file.
4. Database changes are Alembic migrations that are **additive** and safe while the previous version still runs during a deploy. Each has a test on SQLite and PostgreSQL, up and down. Never drop or rename a column in use.
5. API changes are additive only. Do not change an existing response shape or route meaning.
6. No new dependencies unless the stage text says so. If a stage needs one, stop that stage and ask (section 1.6).
7. No `style="..."` attributes. 0 axe violations at desktop and phone widths. Honour `prefers-reduced-motion`.
8. Honest wording everywhere: a message may only claim what was checked. Practice evidence is never described as certification.
9. Never copy lesson wording, exercises, datasets or images from outside sources. Pointers to outside courses are links only, with terms checked first.
10. Do not touch Lucas's data. No production calls, no sign-ins, no scripts against the live site. Tests use local servers and mocks of the API with recorded real answers, as in handoffs 24, 26 and 27.

### 1.2 One stage = one branch = one PR = one handoff

Every stage follows `build.md` section 14: a step 0 check, work, tests, a handoff in `docs/handoffs/` as `.md` and `.pdf`, a PR that names itself in the handoff ("Name PR #N in handoff NN"). Use the next free handoff number at the time (the highest number in `docs/handoffs/` plus one; the gap at 21 is deliberate and stays empty). Write handoffs exactly as handoffs 24, 26 and 27 do: every card, hint and check case word for word in an appendix for lesson stages; decisions and why with assumptions marked; bugs found; how it was tested; limits; live checks for Lucas; questions for Lucas with a recommendation beside each, marked "recommended, not yet confirmed"; and how to remove the worktree safely.

Use a separate git worktree per stage (`git worktree add ../python-academy-<slug> -b <branch> <base>`). Never switch branches in the main folder `/Users/DEV/Projects/python-academy`. Other sessions may use it.

Do not merge anything. Do not enable auto-merge. Do not push to `main`.

### 1.3 Chaining (the one change for this run)

Normally a stage branches from `origin/main` after the previous PR merges. During this run Lucas will not merge until later, so:

- A stage that **depends on an unmerged stage** branches from that stage's branch, and its PR targets that branch (`gh pr create --base <previous-branch>`). Say "merge #N first" at the top of the PR description and the handoff.
- A stage that **does not depend on anything unmerged** branches from `origin/main` and targets `main`. Prefer this whenever possible (documentation, safety and independent engineering stages), so one failed review does not block everything.
- **Never more than 5 unmerged PRs open at once** (counting open PRs from earlier work). When 5 are open, stop (section 1.7). Lucas merges bottom-up; GitHub re-targets the next PR to `main` when its base branch is deleted after merge.
- Before starting each stage, re-run `git fetch --all` and `gh pr list --state all`. If something Lucas merged or closed changes the base, rebase the chain with `git rebase --onto` and say so in the handoff. If a PR in the chain is closed unmerged, stop and report.
- If review later finds a problem in a lower PR, the stages above it will need a rebase. That is accepted. Keep each stage's commits small and clean so rebasing is easy.

### 1.4 Gates

Every stage in Part 6 has a **Gate**:

- **none**: do it.
- **needs [box]**: do it only if Lucas ticked that box in Part 2. If the box is empty, **skip the stage**, record it as `blocked: waiting for owner decision` in the run log, and go on to the next stage that has no gate. Do not guess an answer. Do not tick boxes yourself.
- **human**: Claude Code cannot do it (Part 5). Skip, and list it in the final report.

### 1.5 Decisions

Only an item marked "decided" in `docs/plan/backlog.md` section 6, or ticked in Part 2, is decided. Everything else is a proposal. When you must make a small choice inside a stage (a name, a wording), make the smallest one, mark it **assumption** in the handoff, and ask. Never record your own recommendation as "owner decided". If a stage needs a new ID, take it from the "proposed IDs" list in Part 9 and check it against `build.md` section 13 for clashes first.

### 1.6 When to stop a stage and ask

Stop that stage (leave the branch pushed and the work described in the handoff) and move on or end the run if:

- a stage needs a new dependency, a paid service, a new Render or Google setting, or a new environment variable that is not already documented;
- a lesson cannot be checked fairly without a construct rule (a check that requires the learner to use a particular syntax). Do not invent construct rule naming. Build the lessons that can be checked, and list exactly what is needed (ID-safe names, the judge change, the tag acceptance) as a question;
- a test fails and you cannot explain why after two honest attempts;
- a change would alter unit 1 behaviour (the frozen snapshot tests must pass unchanged);
- you find a security problem (a leak, an unchecked route, a log with personal data). Write it up in the handoff first. If it is serious, stop the whole run and report it at the top of the final report.

### 1.7 Stopping cleanly and resuming

Keep a run log, `docs/run-log.md`, updated in every PR (it accumulates along the chain). One row per stage: stage ID, branch, base, PR number, handoff number, status (`done`, `blocked: <why>`, `skipped: <why>`, `in_progress`), date, tests result in one line. Update it **before** you start a stage (`in_progress`) and after you finish it.

If you are running low on usage, finish the current commit, push, write what is left into the handoff and the run log, and stop. Never leave a half-written handoff or an unpushed commit.

**Resume protocol:** a new session starts with `git fetch --all`, `gh pr list --state all`, reads `docs/run-log.md` on the newest branch in the chain, checks that every `done` row has a PR and a pushed branch, then continues at the first stage that is not `done`.

### 1.8 Tests (every stage)

Run the full backend suite (SQLite and PostgreSQL), `tsc`, the production build and the full Playwright suite, **alone, not alongside other jobs**. Add tests for what you built. Run **at least three deliberate-break checks** per code stage (break something the tests should catch, see tests fail, undo it, report which failed). Documentation-only stages need link/table/ID checks (as in handoffs 23 and 25) instead. Never mark a stage done with a red suite.

### 1.9 The final report

When the run ends (finished, blocked or out of usage), reply with: what was built (PR numbers in merge order), what was skipped and why, what Lucas must do (merges, live checks, decisions), and the first line "SECURITY: none" or the problem. Keep it short. The handoffs hold the detail.

---

## Part 2. Owner pre-approvals (Lucas fills this in before sending)

Box names start with `B-` so they cannot be confused with stage names. Change `[ ]` to `[x]` only for answers you accept. Leave the rest empty. An empty box means "do not do the stages that need it". These are the planning chat's recommendations, not decisions. Each is explained in the handoff or plan named beside it.

**Run rules**
- [ ] **B-R1.** Chained PRs are allowed as described in section 1.3. Maximum unmerged PRs open at once (default 5; write a different number if you want): ____
- [ ] **B-R2.** Lesson stages may release a unit in parts, using `more_lessons_coming` on the unit until its last part.

**Unit 2 (handoff 26, questions 1 to 4)**
- [ ] **B-U1.** Field names `more_lessons_coming` (content) and `complete` (API) are fine.
- [ ] **B-U2.** "Its lessons are not written yet" for a planned unit, and "is coming soon" for a planned course.
- [ ] **B-U3.** One practice badge per lesson stays; update `course-catalog.md` section 6.2 to say so. (Allows the docs sync to edit 6.2.)

**Unit 3 part 1 (handoff 27)**
- [ ] **B-U4.** I read handoff 27 and accept its recommendations as written. (Do not tick unless you read it. If unticked, the stages that build on unit 3 still run, but treat its open questions as open.)

**Unit checks and projects**
- [ ] **B-A1.** Decision 15: a unit check is passed when all core tasks pass; hints are allowed and recorded as support data, not penalties. (Unlocks ASSESS-02 onward.)

**Independent learners (ID-01 plan, section 11)**
- [ ] **B-I2.** An independent learner is a `student` with no parent (option A).
- [ ] **B-I3.** A parent who also wants to learn uses a second Google account for now.
- [ ] **B-I4.** Keep storing the full date of birth; revisit in the enrolment stage.
- [ ] **B-I5.** Daily cap on new accounts starts at 20.
- [ ] **B-I6.** Inactive accounts are deleted after 24 months without sign-in, and the notice says so.
- [ ] **B-I7.** Both the student and the parent may ask to delete an invited student's account.
- [ ] **B-I8.** Contact address for the privacy notice (write it here, or leave blank): ______________________
- [ ] **B-I9.** Check the Google console before deciding whether a custom domain must come first.
- [ ] **B-S1.** SEC-11: filter query strings out of the API access log (keep request lines, drop `?state=...&code=...`).
- [ ] **B-S2.** Write a short terms of service page with the privacy notice.
- [ ] **B-S3.** SEC-10 result: I checked with a Google account that is not on my list. (Write what happened: ______ ) This changes the stage order, so say it.

**Security enforcement**
- [ ] **B-E1.** I did the SEC-09 console checks (handoff 08 section 10) and saw no CSP reports. Claude Code may prepare the enforce-mode PR (it stays a one-line change, and Lucas merges it).

**Public site (SITE-02, `docs/plan/site-design.md`)**
- [ ] **B-W1.** Accept the planning chat's seven recommendations for the public site: story concept B with a small map; a separate static site; hand-written SVG art; keep the current name and no custom domain yet; launch after unit 2 (now true); a short intro; the teams page later. (Claude Code: open `site-design.md` and confirm these match the questions it lists before building; if they do not match, skip and ask.)

**Teaching design**
- [ ] **B-T1.** Decision 24 revisit (friendly message first versus Python's own message) happens inside unit 6, as a small choice shown to learners in `py.tracebacks`. If unticked, keep the friendly message first and skip the revisit.

**Measurements**
- [ ] **B-P1.** Predict-first and support-data measurements (ENG-04c) may be built: a small table of counts per lesson and rule, no user ID, no code, with stated retention.

**Dependencies**
- [ ] **B-D1.** A SQL engine that runs in the browser (a WebAssembly SQLite) may be added as a dependency for the SQL course, after a design PR that names the exact package, size, licence and integrity check. (Unticked: the SQL course stays a design document only.)

---

## Part 3. What is done (as of 2026-11-02)

This list comes from `docs/plan/backlog.md` (last updated 2026-10-27, so it is behind), the handoffs and the merge history. Step 0 must re-check it (Part 6, S00). Statuses use `build.md` section 18. "Merged" is not "verified": verified needs a recorded live check.

### 3.1 Platform and safety

| Stage | What | PR | State |
| --- | --- | --- | --- |
| ENG-01 | Content format and result states (passed, needs_work, execution_error, unsupported, service_error) | #5 | verified |
| Plan | Course catalog plan | #6 | verified |
| ENG-02 | Migrations; XP and badge ledgers | #7 | ledgers verified; versioned skill evidence, progress records, retention still open |
| Catalog UI | Catalog, course pages, lesson sidebar | #8 | verified |
| Goals | Goal card and rule-based recommendation | #9 | verified |
| Plans | Backlog, feature specs, feedback security plan | #10 | verified |
| SEC-01 | Rate limits (in memory) with `CLIENT_IP_HEADER=cf-connecting-ip` | #11, #12 | verified live |
| SEC-04 | HSTS, nosniff, no-referrer, frame-ancestors none; page CSP in Report-Only | #12 | in_review: enforce mode not switched |
| SEC-03 | Server-side sessions (migration 0006) | #13 | merged; live check owed |
| SEC-09 | Nonce-based page CSP, Report-Only | #14 | merged; live check owed; enforce later |
| Teaching design | `teaching-design.md`, `lesson-feedback.md`, `ai-helper.md` | #15 | verified (docs) |
| ASSESS-07 | Honest unit 1 checks | #16 | merged; live check owed |
| ENG-03 | Browser behaviour checks (Pyodide worker runs cases; judge uses reported output) | #17 | in_review in the stale backlog; later stages depend on it, so almost certainly merged; S00 checks. Live check owed |
| DOC-01/02 | Decision log and handoff template | #18 | in_review in the stale backlog; S00 checks |
| SITE-01 | Site and product design direction (docs) | #19 | merged |
| FB-01/FB-03 | Admin (`ADMIN_EMAILS`), tester flag, route guards (migration 0007) | #21 | merged; live check owed |
| ENG-04 part 1 | Friendly error translations, line highlight, hint ladder, honest result labels | #22 | merged; live check owed |
| FB-02 | Anonymous feedback storage and `POST /api/feedback` (migration 0008) | #24 | merged; live check owed |
| ENG-04 part 2a | Tagged hints, similar example, "Other ways to do it", hint-button outline | #25 | merged; live check owed |
| FB-04 | Testers page at `/admin/testers` | #26 | merged; live check owed |
| UI-05 | Lessons per unit (`GET /api/units/{unit}/lessons`); lesson page runs browser checks | #27 | merged; live check owed |
| README-01 | README with banner, screenshots, feature table, diagram | #28 | merged |

(Numbers not listed, such as #1 to #4, #20 and #23, are earlier setup or documentation syncs; `git log` has them.)

### 3.2 Content

| Stage | What | PR | State |
| --- | --- | --- | --- |
| Unit 1 | Build Your Own Adventure: `hello`, `variables`, `input`, `choices`, `adventure` | earlier | live (bounded checker) |
| EDU-04 part 1 | Unit 2: `py.arithmetic`, `py.int-float`, `py.convert-input` | #29 | merged; live check owed |
| ID-01 plan | Independent learner plan (documentation) | #30 | merged |
| EDU-04 part 2 | Unit 2: `py.compare`, `py.boolean-logic`, `py.elif`; `more_lessons_coming` and `complete` | #31 | merged; live check owed. Unit 2 is complete in lessons only: no unit project, no unit check |
| EDU-03 part 1 | Unit 3: `py.while-loops`, `py.loop-termination`, `py.for-range`; a worker fix so output cannot leak between cases | #32 | **open when last seen (2026-10-28), not reviewed by the planning chat**. Step 0 checks |

What learners have today: 2 complete units (11 lessons, counting the 5 in unit 1), 3 more lessons in unit 3 if #32 is merged. Everything else in the catalog is "Coming soon".

---

## Part 4. What is missing or stale on GitHub right now

These are the known gaps. S00 verifies each.

1. **The docs sync never ran.** `docs/plan/backlog.md` and the stage table stop at 2026-10-27 morning: no rows for stages 20 to 27, no ID-01 rows (ID-01a to f, SEC-10, SEC-11), no ASSESS-06 addition, statuses of FB-04, UI-05, README-01, EDU-04 and EDU-03 are wrong. The decision log lacks chapters from handoffs 22, 26 and 27 (chapters 16 and 17 came with #26). Handoff 21 was reserved and does not exist.
2. **README is stale.** It says only unit 1 is released and lists unit 2 as upcoming.
3. **`course-catalog.md` section 6.2** still says new lessons earn no per-lesson badge, but units 2 and 3 award one (box B-U3).
4. **Live checks owed and not recorded:** SEC-03, ASSESS-07, SEC-09 (console), ENG-03, FB-01, ENG-04 part 1 and 2a, FB-02, FB-04, UI-05, unit 2 parts 1 and 2, unit 3 part 1. Nothing is `verified` until Lucas records results.
5. **About 30 remote branches**, most merged long ago. Cleanup is a docs stage plus Lucas's commands (deleting remote branches is his call).
6. **Worktrees** on Lucas's Mac to remove after merges: `../python-academy-readme`, `-ui05`, `-u02`, `-u02b`, `-id01`, `-u03`, `-sync3` if it exists. Folder `.review-shots/` in the main folder (untracked).
7. **Not built yet** (the rest of this file): the feedback inbox and button (FB-05 to FB-07), PILOT-01, unit projects, all unit checks (ASSESS-01 to 06), `ENG-04c` (predict-first and support measurements), construct rule IDs, `py` units 3 (part 2) to 12, `hack` and 10 other courses, the public site (SITE-02 to 04), independent learner accounts (ID-01a to f), privacy notice, export and delete, sign-ups switch, SEC-02, SEC-05 to SEC-08, SEC-10/11, OPS-01 to 05, QA-01/02, UI-01 to 04 and UI-06, EDU-01/02, TOOL-01 to 03, EDU-10 video scripts, DOC-03/EDU-11 (a book and course from the decision log; no rows yet), PORT-01 (a parked portfolio page).
8. **Known weak points to keep honest in the docs:** browser checks are practice evidence and can be faked; rate limits reset on restart; no screen reader, Safari or Firefox testing; no privacy notice, retention or deletion workflow; Google sign-in may already be open to any Google account (SEC-10, unconfirmed).

---

## Part 5. Human-only tasks (Claude Code skips these and lists them)

| Task | Who | Why it can't be automated |
| --- | --- | --- |
| Merge PRs, one at a time bottom-up, wait for Render "Live" | Lucas | Deploys; review |
| Run the live checks in each handoff and report results | Lucas | Needs the live site and a student account |
| SEC-10: sign in with a Google account not on the list; or read Google Auth Platform, Audience (Publishing status; Test users) | Lucas | Google console |
| Set Render env vars (`ADMIN_EMAILS` exists; any new one named in a handoff) | Lucas | Secrets live in Render only |
| SEC-02 private API service; OPS-02 backups and a restore drill; OPS-03 alerts | Lucas, with a prepared checklist | Render settings |
| SEC-07 branch protection on `main` | Lucas | GitHub settings; may need a paid plan |
| OPS-05 cost review, **2026-11-08** (baseline about USD 20 a month) | Lucas | Billing |
| SITE-04 custom domain and name | Lucas | Paid, owner decision |
| Real screen reader, Safari and Firefox testing (QA-01) | Lucas and testers | Real devices |
| Sister's lesson trial; PILOT-01 | Lucas | People |
| Delete merged remote branches and remove worktrees | Lucas | His machine |
| Read the PIPEDA material and ask someone about the privacy notice before inviting strangers | Lucas | Not legal advice from Claude |

---

## Part 6. The queue

Process stages **top to bottom**. Skip a stage whose Gate is not met, or whose dependency was skipped, and record why in the run log. Stop when the open-PR cap (section 1.3) is reached. "Base" says where the branch starts: `main`, or `prev` (the previous stage's branch in the chain). A "shared lesson template" is Part 7; the lesson lists are Part 8.

**Order override (read box B-S3 in Part 2):** if Lucas reports that a Google account outside his list can already sign in, move S04 (ID-01c) to directly after S01. Real strangers' data is the biggest risk in the project, and the switch must exist before anything else is built on open sign-in.

### Wave A: record the truth, then keep content going

**S00. State check (no PR).** `git fetch --all`, `gh pr list --state all`, read `docs/run-log.md` if it exists. Verify Part 3 and Part 4 against the repository and report differences in the run log. Confirm PR #32's state (merged, open or closed). Create the run log. Gate: none.

**S01. DOCS-SYNC** (handoff: next free; branch `docs/backlog-sync-3`; base `main`).
Make `backlog.md`, `decision-log.md`, the stage table and the README match reality. Facts only.
- Stage table rows 20 to 27 (FB-04 #26; this sync; UI-05 #27; README #28; EDU-04 part 1 #29; ID-01 plan #30; EDU-04 part 2 #31; EDU-03 part 1 #32 with its real state).
- Update FB-04, UI-05, README-01, EDU-04, EDU-03 and ID-01 rows. Add ID-01a to ID-01f, SEC-10, SEC-11 exactly as `docs/plan/independent-learners.md` section 10 names them, and the ASSESS-06 addition. Add every ID from Part 9 below as `proposed`, after checking `build.md` section 13 for clashes.
- Status words from `build.md` section 18 only. Nothing is `verified` unless Lucas recorded a live check. For merged items keep `in_review` with "merged, live check pending". Add a "Live checks owed" list naming each check and its PR.
- Decision log: add the missing chapters from handoffs 22, 26 and 27 (sections "Decisions and why", "Bugs", "How it was tested"), and the three ID-01 owner answers of 2026-10-27 (16 or older, self-declared; anyone with a Google account once published; level-based recommendations later). Record as decided **only** what a handoff marks as decided by the owner or what Lucas ticked in Part 2 (cite the box). Everything else is "open, awaiting owner" with the recommendation beside it.
- README: update the "what you can do today" and "what is coming" parts to the true state of `main` (units released; near-term work). Keep the honest-early-days note. Re-run the README link check from handoff 23.
- If box B-U3 is ticked, update `course-catalog.md` section 6.2 (one practice badge per lesson). Otherwise do not touch it.
- Add `docs/plan/master-run.md` (this file) unchanged as its own first commit.
Gate: none (parts are gated as written). Tests: link, anchor, table and ID checks as in handoffs 23 and 25; backend and frontend suites unchanged.

**S02. EDU-03 part 2** (branch `content/py-u03-part2`; base: the `#32` branch if unmerged, else `main`; depends on EDU-03 part 1).
Lessons `py.accumulate` and `py.nested-loops`; unit 3 is then complete (`more_lessons_coming` becomes false or is removed, and the page, the home recommendation and the catalog summary say so correctly). Use the shared lesson template and Part 8 table "u03". Gate: none (box B-U4 recommended).

**S03. SEC-11 Google code out of the access log** (branch `sec/access-log-query`; base `main`). Gate: needs **B-S1**.
Stop the API's access log from recording query strings (the Google `state` and `code` on `/auth/google/callback`), while keeping method, path, status. Do it in application code (a logging filter on `uvicorn.access`); do **not** edit `render.yaml` start commands or any Render setting. Tests: a request with a query string produces a log line without it; other log lines unchanged; the tests from handoff 20/17 that no email, code or message text is logged still pass. Three deliberate breaks.

**S04. ID-01c sign-ups switch, daily cap, admin disable or delete** (branch `feat/signups-switch`; base `main`). Gate: needs **B-I5**.
Plan: `docs/plan/independent-learners.md` sections 4, 6.3 and 9 (stage C). Additive migration `0009` creating `app_settings` (one row per setting; default "open" so nothing changes at deploy). Enrolment checks the switch and a daily cap counted from today's `enrolled` events. New admin routes (all behind the existing admin guard, 401 signed out and 403 non-admin, with a route-enumeration test): set the switch, read today's count, disable an account by ID with a reason, delete an account by ID with a reason. A deletion or disable record holds **no personal data**. A small admin page for these (no link in the public navigation, like `/admin/testers`). Closed sign-ups show a plain page message; existing accounts are unaffected. Tests: what the switch does if its setting cannot be read (mark as an assumption; recommended: block new enrolments, keep existing sessions working); cap boundary (19, 20, 21); role and 401/403 tests on every route; migration up and down on both databases; deletion order respects foreign keys (the app sets no SQLite `foreign_keys` pragma; only `sessions.user_id` cascades). Live check for Lucas: flip the switch off and on, confirm a second Google account is blocked while off.

**S05. ENG-06 function-call checks** (branch `eng/function-checks`; base `prev` or `main`).
Extend the ENG-03 contract, **additively**, so a check can call a function the learner defined, with arguments, and compare the return value or printed output (needed by unit 5; also useful in units 4, 6, 8 and 11). Update `docs/plan/browser-checks.md`. Design rules: hidden cases' arguments and expected values never reach the browser; the learner's function is called inside the worker with the same time and output limits; a missing function, a wrong name or wrong parameter count gives a clear tagged result ("your program should define a function called X that takes N arguments"); results are compared by value with a documented equality rule (no float equality traps: use a tolerance field when needed); the 3-second stop applies per case. No new dependency. Tests: sample correct and wrong functions, a missing function, an exception inside the function (friendly explanation with the line), an endless loop, hidden values never sent, unit 1 to 3 snapshots unchanged. Three deliberate breaks. Gate: none.

**S06. EDU-06 part 1: unit 4, lessons 1 to 3** (branch `content/py-u04-part1`; base `prev`). Shared lesson template; Part 8 table "u04": `py.lists`, `py.indexing`, `py.iterate-lists`. Release `py.u04` with `more_lessons_coming`. Gate: none.

**S07. EDU-06 part 2: unit 4, lessons 4 and 5** (branch `content/py-u04-part2`; base `prev`): `py.dicts`, `py.sets`; unit complete. Gate: none.

**S08. EDU-07 part 1: unit 5, lessons 1 to 3** (branch `content/py-u05-part1`; base `prev`; depends on S05): `py.functions`, `py.parameters`, `py.return-values`. Gate: S05 done.

**S09. EDU-07 part 2: unit 5, lessons 4 and 5** (branch `content/py-u05-part2`; base `prev`): `py.scope`, `py.decompose`; unit complete. The unit's project (Adventure v2) is S23. Gate: none.

**S10. Course design documents** (one PR, branch `docs/course-designs`, base `main`; docs only). For each of `git`, `web`, `js`, `sql`, `data`, `cs`, `node`, `fullstack`, `ce` and `ai`, write `docs/plan/courses/<id>.md`: audience and prerequisites (from `course-catalog.md` section 3.4), unit and lesson outline with proposed IDs in the catalog's style, the projects and what counts as evidence, **the runtime each needs and its safety analysis** (for example a sandboxed HTML preview, a JavaScript worker, a browser SQL engine, no server-side execution of learner code), any dependency it would need (name, size, licence, integrity), the checker features required, risks, and open questions for Lucas. No code, no catalog change. For `ai`, check each provider's minimum age and cost before writing setup units and keep a no-cost path (`teaching-design.md` section 6.6). Gate: none.

(With a cap of 5 and no gated stages ticked, a first run does S01, S02, S05, S06 and S07, then stops. Ticked boxes pull gated stages in at their place in the order. The rest follow in later runs.)

### Wave B: opening up safely (independent learners, privacy, feedback)

**S11. ID-01a privacy notice and data inventory** (branch `docs/privacy-notice`; base `main`). Gate: needs **B-I8** and **B-S2**.
A page `/privacy` in plain language covering exactly the contents list in plan section 5.5, plus a short terms page. Every sentence must be true: verify each against the code and say where in the handoff (as in handoff 25). Use the contact address from B-I8. State retention exactly as ticked in B-I6; do not describe a deletion feature that does not exist yet (say "to be added" or link it only after S12 exists). Add a data inventory document `docs/plan/data-inventory.md`. Link the page from sign-in and the footer. Tests: page renders signed out; axe clean; no personal data in the page; links resolve. Not legal advice; say so in the handoff.

**S12. ID-01b export and delete my account** (branch `feat/account-export-delete`; base `prev` or `main`). Gate: needs **B-I6** and **B-I7**.
Plan section 5.3. Export: one JSON file (account row without other people's IDs, history events, attempts with code and output, XP, badges, goal), rate-limited, signed-in only. Delete: confirmation step; deletes the user's `attempts`, `xp_awards`, `badge_awards`, `learner_goals`, `events`, `sessions`, then the `users` row, in a foreign-key-safe order, on SQLite and PostgreSQL. Parent with students: refused until the students are released or deleted (state the rule in the UI). Deletion record has no personal data. Tests: nothing left behind (query every table); a parent cannot delete or export another account; rate limits; 401/403. Three deliberate breaks, including one that forgets a table.

**S13. ID-01d independent enrolment, 16 or older** (branch `feat/independent-enrolment`; base `prev`). Gate: needs **B-I2**, **B-I3**, **B-I4**, and S04, S11, S12 done.
Plan sections 2.3, 2.5 and 3. Owner-decided: 16 or older, self-declared; anyone with a Google account. New enrolment question; independent learner = `student` with `parent_id` null; 13 to 15 without an invitation is refused with the explanation from the plan; under 13 refused; existing parents and students unchanged. Tests: age boundaries (12, 13, 15, 16, 17, 25, 26) with and without an invitation; a parent can never see an independent learner (assert in the family view); an under-16 cannot slip through; no code assumes a student has a parent (grep every `parent_id` use); the sign-ups switch and daily cap apply. Live check for Lucas with a spare Google account.

**S14. SEC-09 enforce mode** (branch `sec/csp-enforce`; base `main`). Gate: needs **B-E1**.
Switch the nonce page CSP to enforce (the one-line change in handoff 08 section 5), keep Report-Only for any remaining policy, update tests and `DEPLOYMENT.md`. Complete SEC-04. Handoff lists exactly what Lucas must look for on the live site (console CSP errors on every page type, sign-in, lesson run, admin pages) and how to revert in one line.

**S15. OPS-04 retention policy** (docs only; branch `docs/retention`; base `main`). Write the retention table for every data kind (feedback 50 days and 90 items, goals, placement, attempts, events, sessions, invitations, export/delete) from decisions 18 and 19, plus ticked B-I6. Gate: none.

**S16. FB-06 admin inbox** (branch `feat/feedback-inbox`; base `prev`). Gate: needs **B-E1**, and S14 done.
Per `docs/plan/feedback-security.md` and backlog section 3: list, filters (status, type, lesson), statuses (new, triaged, in_progress, fixed, wont_fix), internal notes, a GitHub issue link field. Admin-only (401/403 on every route, route-enumeration test). Plain text, escaped on display. **Anonymous: no user data anywhere in the view.** The 90-item cap and 50-day cleanup are already in FB-02; verify they run. Tests including emoji and long text, XSS strings rendered inert, status transitions.

**S17. FB-07 "Copy digest"** (branch `feat/feedback-digest`; base `prev`). Plain text for pasting into an assistant: IDs, types, lesson, message; no emails, no code by default. Gate: S16 done.

**S18. FB-05 feedback button and form** (branch `feat/feedback-button`; base `prev`). Gate: S16, S15 done. **Never ship before FB-06.**
Button on every page and lesson card for testers and the admin only (never parents; never non-testers). Form per backlog section 3: type, message with a length limit, auto-attached context (page, lesson and task ID, content version, browser type, time), opt-in "Include my code" showing exactly what will be sent, a plain notice not to include personal details. Uses the existing `POST /api/feedback`. Tests: non-testers do not see the button; the request holds no user ID; over-length and over-rate rejected; accessibility; keyboard use.

### Wave C: unit checks, projects, measurement

**S19. ASSESS-02 `unit_check` task type, level variants, validation** (branch `feat/unit-check-schema`; base `prev` or `main`). Gate: needs **B-A1**. Content schema only (plan section 12.4): four to six tasks, level variants `high_school` and `university`, validation at load; no UI yet.

**S20. ASSESS-03 unit check interface** (branch `feat/unit-check-ui`). Gate: B-A1, S19. One card at a time, untimed; retakes with different variants; "Unable to assess" never counts as failure and keeps the draft; hints allowed and recorded as support data; honest labels.

**S21. ASSESS-06 and ID-01e learner level** (branch `feat/learner-level`). Gate: needs **B-I2**, S19. Self-chosen `high_school` or `university`, **never derived from or asking for a birthdate**; optional; changes recorded as history events; used to pick the check variant. Additive migration.

**S22. ASSESS-04 unit 1 check; ASSESS-05 award** (two PRs). Gate: B-A1, S20. The unit 1 check is optional for learners who completed unit 1 (decision 22) and awards the skill badge (no XP) once, through the existing ledgers (decision 16).

**S23. PROJ-01 unit projects** (branch `feat/unit-projects`). Gate: B-A1. First check what exists for unit 1's `adventure` lesson and how 200 XP is awarded. Design and build the unit project milestone mechanism in three versions (guided build, independent brief, stretch extensions; `build.md` section 7) with one award per unit (200 XP, plan section 6.1). A unit is complete when its project and its check are done (decision 16). Rubric-assessed projects use the self-review task type from ENG-09; automated checks only where behaviour is deterministic.

**S24. Unit checks for units 2, 3, 4 and 5** (four PRs, each from the lesson template section for `unit_check`). Gate: B-A1, S19, S20, the unit's lessons.

**S25. ENG-04c predict-first and support-data measurements** (branch `feat/support-measures`). Gate: needs **B-P1** and S11 done. Database change with a privacy review in the handoff: counts per lesson and rule only, no user ID, no code, retention stated.

**S26. Construct rule naming proposal** (docs only). Propose ID-safe names and the judge change for "uses elif / uses a loop / uses a function" style rules, for Lucas to decide. No code. Gate: none.

### Wave D: the rest of Python (units 6 to 12) and its engineering

Each Python unit follows the lesson template (Part 7) in parts of at most 3 lessons, plus its runtime stage first when one is listed. Part 8 has the lessons.

| Order | Stage | Depends on | Gate |
| --- | --- | --- | --- |
| WWD1 | EDU-08 unit 6 part 1 and 2 (errors) | S09 | B-T1 for the friendly-message revisit |
| WD2 | ENG-07 allowlisted standard-library imports, seeded `random` | none | none; **security stage**, see its text |
| WD3 | EDU-08 unit 7 parts 1 and 2 (libraries) | WD2, WD4 | none |
| WD4 | ENG-08 virtual filesystem fixtures, several files | none | none |
| WD5 | ENG-10 learner tests run against correct and broken reference code | S05 | none |
| WD6 | EDU-08 unit 8 (tests) | WD5 | none |
| WD7 | EDU-08 unit 9 (files) | WD4 | none |
| WD8 | EDU-08 unit 10 (text patterns) | none | none |
| WD9 | EDU-08 unit 11 (classes) | S05 | none |
| WD10 | ENG-09 rubric, self-review and local-tutorial task types | S23 | none |
| WD11 | EDU-08 unit 12 (final project) | WD10 | none |
| WD12 | EDU-09 Hackathon Ready, units 1 to 7 | WD10, py units 1 to 7 | none |

Runtime stages (Part 9 has the specs) are separate PRs with their own security notes; the lesson stages that need them stay `blocked` until they are done.

### Wave E: public site, polish, hardening, future courses

| Stage | What | Gate |
| --- | --- | --- |
| WE1 | SITE-02 skeleton: still scenes, strict headers, separate static site, 0 axe violations, within the performance budget in `site-design.md` section 3 | needs **B-W1** |
| WE2 | SITE-02 scroll motion, reduced-motion, pause button | WE1 |
| WE3 | SITE-02 interactive moments | WE2 |
| WE4 | SITE-03 product polish to match the story | WE1 |
| WE5 | UI-01 cosmetic fixes; UI-02 "Not now"; UI-03 override record; UI-04 pause a course; UI-06 goal capstone | none (UI-06 needs decision 20: its mapping is proposed in the backlog, ask) |
| WE6 | QA-01a accessibility audit script, keyboard-only Playwright tests, a manual test sheet for real screen readers; QA-03 add Firefox and WebKit to CI as non-blocking projects first | none (CI time increase: say so) |
| WE7 | SEC-05 pin or self-host Pyodide with integrity checks; SEC-06 invitation tokens out of URLs and logs; SEC-08 pin CI actions to commit SHAs; ENG-11 move rate-limit counters to the database (migration) | none |
| WE8 | EDU-01 placement examples; EDU-02 placement pilot on one skill (placement never grants XP, badges or completion) | none |
| WE9 | TOOL-01 "Git versus GitHub" and "first commit" lessons with a safe practice repository (evidence label per `build.md` section 8; simulation alone is a lower label) | S10 reviewed by Lucas |
| WE10 | EDU-10 video scripts (scripts only, under 6 minutes, captions and transcripts; lessons work without them) | none |
| WE11 | DOC-03 book and course outline expanded from the decision log | none |
| WE12 | Each future course's content (`git`, `web`, `js`, `sql`, ...) | its design document reviewed by Lucas, and box **B-D1** for SQL |
| WE99 | Final DOCS-SYNC: backlog, decision log, README, run log summary | none |

---

## Part 7. The shared lesson stage template

Use this for every content stage (a part of a unit: at most 3 lessons per PR). It is the prompt that produced units 2 and 3, generalised. Fill the angle-bracket items from Part 8.

```text
Task: <EDU id> part <n>, Python unit <u> "<unit title>", lessons <list>. One PR. Do step 0 first.

Step 0, check only: git fetch --all and gh pr list --state all. Confirm every stage this one depends on is merged or is the base branch. Confirm none of these lesson files already exists on any branch. Create a separate worktree for this stage (never switch branches in the main folder).

Read first: build.md, docs/plan/teaching-design.md, docs/plan/lesson-feedback.md, docs/plan/browser-checks.md, docs/plan/course-catalog.md (the unit row and project spine), backend/content/README.md, the two newest lesson handoffs (decisions, questions, appendix), and the newest lesson files in backend/content/py/. Match their structure, tone, hint style, check design and tests exactly.

Scope: build ONLY <lesson IDs, in order>, with the IDs exactly as in the plan. Learner: grade 9 beginner who finished the previous units; calm, short, one idea per card, original wording; five cards each (discover, worked example, predict, try it, challenge); predict-then-run and fix-the-bug as far as five cards allow; support fades across the unit; browser checks with visible and hidden cases that measure the skill, not the exact wording, so any correct solution passes and hard-coded or visible-only output fails; rule IDs <lesson>.case.<case id>; tagged hints first, a three-level ladder (nudge, bigger hint, approach) that never gives the answer, a similar example from another context, and "Other ways to do it" after passing; 100 XP and one practice badge per lesson challenge, awarded once. No unit project and no unit check in this PR. Do not change earlier units or lessons.

Story and context: <from Part 8>. Concept notes and traps: <from Part 8>. Runtime needs: <from Part 8>.

Construct rules: do NOT invent construct rule naming. Try to design cases so the intended construct is forced by behaviour; accept every correct program. If a lesson truly cannot be checked fairly without a construct rule, build the others, stop on that one, and list exactly what is needed as a question.

Unit state: if lessons remain, set the unit's more_lessons_coming to true and check the lesson page ends with the "released so far" wording, the home recommendation says the unit has more lessons on the way and never names the unit after it, and the catalog summary is true. If this part finishes the unit, set it complete and check the "Unit complete" ending, the home note and the recommendation. Additive API changes only. RULES_VERSION changes only if the recommendation rules actually change (explain either way).

Rules: no new dependencies; learner code never leaves the browser except the reported output the ENG-03 contract defines; hidden expected output never reaches the browser; no style="..." attributes; 0 axe violations; do not edit docs/plan/backlog.md or docs/plan/decision-log.md (the docs sync does); never copy lesson wording from outside sources.

Tests (required), following the newest lesson handoffs: content validation; every claim on a card and every worked-example output run in Python; correct programs, creative solutions and the other ways pass; wrong programs fail with the right rule (including endless, off-by-one, hard-coded and visible-only answers); the hint audit (code in hints, tagged hints and similar example, alone and in every combination, with and without the starter, plus the version with the hints' names swapped for the challenge's names; extend the audit's parser if new syntax needs it); every rule has a message and a sample; hidden output never sent; end to end with real Pyodide per lesson (a pass, needs_work with the tagged hint first, a Python error with the friendly explanation, an endless loop stopped at 3 seconds, an unsupported import); XP and badges once; earlier units' snapshots unchanged; the unit-state ending; axe at desktop and phone. At least three deliberate-break checks (for example a hint that spells out an answer, a check that accepts the wrong construct, a leak of hidden output), each undone afterwards, reporting which tests failed. Run backend (SQLite and PostgreSQL), build and Playwright suites alone.

Deliver the handoff as md and pdf with every card, hint and check case word for word in an appendix, decisions and why (assumptions marked), bugs, tests, limits, live checks for Lucas (one test account; a sister will try it), questions with a recommendation beside each marked not yet confirmed, and how to remove the worktree safely. Open the PR (base per the run plan). Do not merge it.
```

### 7.1 The unit check template (for stages in S24)

Same as above, except: scope is `<unit>.check`, one `unit_check` task of four to six tasks (predict the output, spot the bug, one or two short write-the-code tasks reusing the unit's project), two level variants (`high_school`, `university`) that change context and difficulty and not the skills tested, retake variants, hints allowed and recorded as support data, "Unable to assess" on technical failure, and the pass rule ticked in box B-A1. Awards the unit's skill badge once and **no XP**.

### 7.2 Checking that a lesson is good (the reviewer's questions)

Claude Code asks these of its own lessons and answers them in the handoff:

1. Could a learner pass by copying a hint? (The audit says no. Say what it tried.)
2. Could a learner fail with a correct program? (List the creative solutions that pass.)
3. Does every failing case give a message that names the idea and not the answer?
4. Is every sentence on every card true Python 3.12 (run it)?
5. Is there one idea per card, and a first sentence a grade 9 reader can follow?
6. Does the story continue the unit's project, and does the last lesson end the unit in a way that is true?

---

## Part 8. Every lesson, by unit

IDs are the plan's (`course-catalog.md` section 5.2). **Context** is a suggested story thread; change it if a better one fits, and say why. **Trap** is what the check must catch. **Runtime** is what must already exist. Each row is one lesson stage input for Part 7.

### Unit 3 "Repeat and explore" (`py.u03`), project: replay a scene until the player quits; repeat a quiz

| Lesson | Concept | Context | Trap the cases must catch | Runtime |
| --- | --- | --- | --- | --- |
| `py.while-loops` | repeat while a condition is true | built in #32; see handoff 27 | a loop that runs once, or never | exists |
| `py.loop-termination` | make sure a loop ends; reading `while True` bugs | built in #32; see handoff 27 | endless loop, off by one | exists |
| `py.for-range` | `for` and `range`, start/stop/step | built in #32; see handoff 27 | stops one early; wrong step | exists |
| `py.accumulate` | running totals, counters, simple averages | add up points across rounds | total reset inside the loop; counting from the wrong value | exists |
| `py.nested-loops` | a loop inside a loop | rooms in a row-and-column map; a times-table | inner loop not reset; swapped loop order; output bound under the output limit | exists |

### Unit 4 "Keep track of a world" (`py.u04`), project: inventory, rooms, scores

| Lesson | Concept | Context | Trap | Runtime |
| --- | --- | --- | --- | --- |
| `py.lists` | create, `append`, `len`, `in` | the hero's pack | forgetting a list is changed in place; an empty list | exists |
| `py.indexing` | index from 0, negative index, `IndexError`, simple slices | picking the first and last item | off-by-one; last item; empty list | exists; friendly translation for `IndexError` |
| `py.iterate-lists` | `for item in items`, sum, max, filtering with `if` | shopping for the pack, treasure values | modifying while looping; empty, single and many cases | exists |
| `py.dicts` | key-value pairs, `get`, add/update, loop over `items()` | rooms and what is in them | `KeyError`; missing key with `get`; keys that look alike | exists; friendly translation for `KeyError` |
| `py.sets` | unique values, membership, `add`, set operations (union, intersection) | rooms already visited | duplicates; order is not guaranteed so outputs must be sorted in the check | exists |

### Unit 5 "Organize your code" (`py.u05`), project: **Adventure v2**, replayable, data-driven scenes using functions (course midpoint)

| Lesson | Concept | Context | Trap | Runtime |
| --- | --- | --- | --- | --- |
| `py.functions` | `def`, calling, reuse | a scene function | defining without calling; wrong indent | ENG-06 |
| `py.parameters` | parameters, arguments, defaults, keyword arguments | a scene that takes the hero's name | wrong argument order; hard-coded value | ENG-06 |
| `py.return-values` | `return` versus `print`, returning several values, `None` | scoring a guess | printing instead of returning; returning too early | ENG-06 |
| `py.scope` | local versus global names, shadowing | a score that must change | a global that is never updated; unexpected shadowing | ENG-06 |
| `py.decompose` | splitting a program into small functions | refactor the adventure | one huge function; functions that depend on globals | ENG-06 |

### Unit 6 "Recover and investigate" (`py.u06`), project: validate player input; diagnose and repair a broken adventure

| Lesson | Concept | Context | Trap | Runtime |
| --- | --- | --- | --- | --- |
| `py.tracebacks` | read a traceback from bottom to top; where the error is | a crash report; decision 24 revisit if box B-T1 is ticked | confusing the type with the line | exists |
| `py.debug-strategy` | print debugging, isolate, binary search, rubber duck | a program that is wrong by one | changing several things at once | exists |
| `py.try-except` | `try`, `except ValueError/ZeroDivisionError`, `else`, `finally` | a safe number reader | bare `except` hiding bugs; catching too much | exists |
| `py.raise` | `raise` your own error, messages | rules of the riddle | wrong exception type; lost message | exists |
| `py.validate-input` | loop until valid input | ask until a whole number | endless loop on bad input; accepting empty reply | exists (replies list; end of input handled) |

### Unit 7 "Libraries and modules" (`py.u07`), project: quiz and spaced-practice tool v1

| Lesson | Concept | Context | Trap | Runtime |
| --- | --- | --- | --- | --- |
| `py.import` | `import`, `from ... import`, dotted names | a toolbox | importing something not allowed | **ENG-07** allowlist |
| `py.random` | `random` with a seed, `choice`, `randint`, shuffle | the riddle keeper's secret number | non-seeded results; checks must use a seed fixed by the harness | ENG-07 |
| `py.math-module` | `math` functions, constants, rounding | distance and rounding | floating-point output; use tolerance | ENG-07 |
| `py.datetime` | `datetime` and `timedelta` basics (no clock reads in checks) | a study schedule | time-dependent output; fixed dates only | ENG-07 |
| `py.own-modules` | write and import your own module | a helper file | single-file worker | **ENG-08** several files |
| `py.packages-local` | local setup tutorial: virtual environments, `pip` (not run in the browser) | working on your own machine | cannot be auto-checked | **ENG-09** local tutorial type |

### Unit 8 "Trust your changes" (`py.u08`), project: tests that catch an intentionally broken quiz tool

| Lesson | Concept | Context | Trap | Runtime |
| --- | --- | --- | --- | --- |
| `py.assert-tests` | `assert`, reading a failing assert | testing the scorer | tests that always pass | **ENG-10** |
| `py.test-cases` | choosing cases: typical, edge, wrong | table of cases | only happy-path cases | ENG-10 |
| `py.boundaries` | boundary values | the 0, 1, 2 and 10 limits again | missing the edge | ENG-10 |
| `py.type-hints` | annotations as documentation (not enforced) | a typed function | claiming hints are checked at runtime | exists |
| `py.refactor` | change structure without changing behaviour; tests as a safety net | tidy a messy scorer | refactor that changes behaviour | ENG-10 |

### Unit 9 "Save and load" (`py.u09`), project: save and load the game or a study tracker

| Lesson | Concept | Context | Trap | Runtime |
| --- | --- | --- | --- | --- |
| `py.text-files` | `open`, `with`, read/write text | a save file | forgetting to close; file in the wrong place | **ENG-08** virtual filesystem, explained limits |
| `py.json` | `json.dump/load` | the game state | non-serialisable values | ENG-08 |
| `py.csv` | `csv` module reading/writing | a score table | quoting; header row | ENG-08 |
| `py.missing-data` | missing files, bad rows, defaults | corrupt save | crash instead of recover | ENG-08 |
| `py.environments` | local setup tutorial: environments and requirements | on your machine | cannot be auto-checked | ENG-09 |

### Unit 10 "Patterns in text" (`py.u10`), core but skippable by placement (plan decision 7)

| Lesson | Concept | Context | Trap | Runtime |
| --- | --- | --- | --- | --- |
| `py.string-methods` | `split`, `strip`, `replace`, `find`, f-strings | clean up player answers | immutability; case | exists |
| `py.regex-basics` | `re.search`, `match`, character classes, quantifiers | recognise a code | greedy matches | ENG-07 allows `re` |
| `py.regex-groups` | groups, `findall`, `sub` | pull out parts | wrong group number | ENG-07 |
| `py.validate-formats` | validate course codes, emails (simple), dates | form checking | over-trusting a pattern; say regex is not full validation | ENG-07 |

### Unit 11 "Model a larger program" (`py.u11`), project: inventory or simulation model

| Lesson | Concept | Context | Trap | Runtime |
| --- | --- | --- | --- | --- |
| `py.classes` | `class`, `__init__`, attributes | a hero | forgetting `self` | ENG-06 (call constructors) |
| `py.methods` | methods and state | actions that change a hero | shared state between objects | ENG-06 |
| `py.composition` | objects that hold objects | a hero with a pack | inheritance used too early | ENG-06 |
| `py.when-not-oop` | when a function or dict is better | compare designs | OOP for its own sake | rubric/reflection (ENG-09) |

### Unit 12 "Final project" (`py.u12`)

| Lesson | Concept | Evidence | Runtime |
| --- | --- | --- | --- |
| `py.final-brief` | choose, scope and plan a project | brief checked against a rubric | ENG-09 |
| `py.final-milestones` | milestones, README, tests | milestone checklist | ENG-09 |
| `py.final-review` | demo, explanation, trade-offs | rubric self-review with honest evidence label (`build.md` section 7); never an automated pass on its own | ENG-09 |

### Hackathon Ready (`hack`), requires `py.u01` to `py.u07`

Evidence is rubric or self-review, not auto pass/fail (`course-catalog.md` section 5.5). Tasks use ENG-09 types. Public API exercises use saved fixtures, never a live API. No hosting spend, no real hackathon attendance required for badges.

| Unit | Title | Lessons to design (propose IDs `hack.<slug>`) |
| --- | --- | --- |
| `hack.u01` | Idea to MVP | pick a problem and user; cut to an MVP; scope statement with a "not doing" list |
| `hack.u02` | Time-boxing | break into time blocks; decide what to drop |
| `hack.u03` | Teamwork with Git branches | one branch per feature; small PRs; review a diff; resolve a small conflict (simulation is a lower evidence label) |
| `hack.u04` | Using public APIs safely | read docs, rate limits and terms; keys never in browser or source; keyless APIs or a server-side proxy; fixtures offline |
| `hack.u05` | Quick UI prototyping | paper sketch, then a command-line flow or a simple page; accessibility basics |
| `hack.u06` | Demo and pitching | a two-minute script; backup recording |
| `hack.u07` | Judging criteria | how criteria are applied; honest self-assessment against a rubric |

### Other courses

Design documents only until Lucas approves them (stage S10). When approved, each course gets lesson stages from the same template, gated on its runtime stage:

| Course | Runtime/engineering it needs first |
| --- | --- |
| `git` | a safe practice repository workflow; simulation is a lower evidence label than a real PR |
| `web` | an isolated HTML/CSS preview (sandboxed iframe, no script, strict CSP) |
| `js` | a JavaScript execution worker with the same limits as Pyodide's; DOM exercises inside the isolated preview |
| `sql` | a browser SQL engine (box B-D1; new dependency) |
| `data` | CSV fixtures (ENG-08); no network |
| `cs` | mostly reasoning tasks; algorithm traces; reuse Python runtime |
| `node` | cannot run on the server; design a browser-simulated or local-tutorial approach |
| `fullstack` | capstone: rubric review of a project the learner builds on their own machine |
| `ce` | C and memory, discrete foundations, numerical methods, embedded simulation: each needs its own design and safety analysis; later |
| `ai` | no provider calls from the product; lessons teach verification, asking well, setting up tools on the learner's own machine; check each provider's age and cost; keep a no-cost path |

---

## Part 9. Engineering stages and proposed IDs

New IDs are **proposed**. Check `build.md` section 13 before adding any; the docs sync adds them to the backlog.

| ID | What | Notes for the implementer |
| --- | --- | --- |
| ENG-06 | Function-call checks (S05) | Additive extension of the ENG-03 contract |
| ENG-07 | Allowlisted standard-library imports and seeded `random` | **Security stage.** Today any import is `unsupported`. Allowlist exactly the modules the lessons need (`math`, `random`, `datetime`, `json`, `csv`, `re`, ...). Block `os`, `sys`, `subprocess`, `socket`, `urllib`, `requests`, `pyodide`, `js`, `ctypes`, `importlib` and anything that reaches the network or the host page. Check Pyodide's packages and that no allowed module can import a blocked one. Seed `random` from the harness; checks fix the seed. Tests: each blocked module is refused with the `unsupported` state; the allowlist is one list in one place; a deliberate break that adds `os` must fail tests. Worker CSP unchanged |
| ENG-08 | Virtual filesystem fixtures and several files | Pyodide's in-memory filesystem only; fixtures loaded by the harness per case; learner files are not persisted unless a stage says so; explain limits to learners ("files here are temporary") |
| ENG-09 | Rubric, self-review and local-tutorial task types | Evidence labelled honestly as self-reported; never awards a skill badge alone; project badges follow published rubrics (`build.md` section 10); a local tutorial is "read and confirm", worth practice evidence only |
| ENG-10 | Run learner tests against correct and broken reference implementations | Learner tests pass on the correct reference and fail on each broken one; references stay server-side; tests run in the worker with limits |
| ENG-11 | Move rate-limit counters from memory to the database | Migration; behaviour identical to today; needed before more than one API instance |
| PROJ-01 | Unit project mechanism | S23 |
| QA-03 | Cross-browser CI (Firefox, WebKit), non-blocking first | CI time increase must be stated |
| (OPS-02 prep) | A checklist document for backups and a restore drill | Docs only; Lucas performs it |

---

## Part 10. Handoff and run-log formats

### 10.1 Run log row (`docs/run-log.md`)

```text
| Stage | Branch | Base | PR | Handoff | Status | Date | Tests (one line) |
```

Statuses: `done`, `in_progress`, `blocked: waiting for B-<box>`, `blocked: dependency <stage>`, `skipped: human task`, `stopped: <reason>`.

### 10.2 What every handoff includes

Everything in `build.md` section 14, plus: **the stage ID from this plan**, **which Part 2 boxes it relied on** (quoted), the base branch and "merge #N first" line, and a "For the docs sync" table (rows to add or change in the backlog, stage table and decision log).

---

## Part 11. Launcher prompt (what Lucas pastes into Claude Code)

```text
Read MASTER-RUN.md in the main folder (or docs/plan/master-run.md on the newest run branch) completely before doing anything. It is the plan and the rules. Then run it: step S00 first, then the queue in Part 6 from the top, obeying Part 1 (safety, chaining, gates, stopping and resuming) and only acting on boxes ticked in Part 2. Do not merge anything. Do not edit Render, Google or GitHub settings. If you run low on usage, finish and push the current commit, update docs/run-log.md, and stop; the same prompt resumes the run. When you stop for any reason, reply with the final report from section 1.9.
```

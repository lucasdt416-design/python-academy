# Python Academy backlog

Last updated: 2026-11-09 (America/Toronto)  
Status: **proposed**; decisions 11, 12, 13, 16, 18, 19, 21, 22 and 23 answered by the owner on 2026-10-25, decision 14 on 2026-10-26, decisions 24 to 27 on 2026-10-27, and the three ID-01 answers on 2026-10-27 (`independent-learners.md` section 0). Status words follow `build.md` section 18: proposed, ready, in_progress, in_review, verified, blocked, deferred. Priorities: **Now**, **Next**, **Later**, plus the timing words `build.md` section 13 already uses (for example "Before broader use").  
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
| 4. Goals and recommendations | Goal card, rule-based recommendation | verified live (PR #9; owner's live check 2026-10-25: goal card, Change goal then Cancel, `migration 0005` in the API logs) |
| 5. Backlog and feature plans | This file, feature specs, feedback security | verified (PR #10, documentation only) |
| 6. SEC-01 and SEC-04 | Rate limits; security headers with the page CSP in Report-Only mode | verified live (PRs #11 and #12; owner's live checks 2026-10-25, handoff 06 section 13.7). SEC-04 stays in_review only until the page CSP is switched to enforce mode |
| 7. SEC-03 | Server-side sessions: logout ends the session at once | in_review: merged (PR #13); owner's live check (handoff 07 section 10) not yet recorded |
| 8. SEC-09 | Nonce-based page CSP, in Report-Only mode | in_review: merged (PR #14); owner's live check (handoff 08 section 10) not yet recorded |
| 9. Teaching design and lesson feedback | `teaching-design.md`, `lesson-feedback.md`, `ai-helper.md`, new backlog items | verified (PR #15, documentation only) |
| 10. ASSESS-07 | Honest unit 1 checks and hints | in_review: merged (PR #16); live check owed (see below) |
| 11. ENG-03 | Browser behaviour checks | in_review: merged (PR #17, handoff 11); live check owed (see below) |
| 12. FB-01 | Admin and tester roles | in_review: merged (PR #21, handoff 12); live check owed (see below) |
| 13. SITE-01 | Site and product design direction | in_review: merged (PR #19, handoff 13; documentation only) |
| 14. DOC-01 and DOC-02 | Decision log and handoff template | in_review: merged (PR #18, handoff 14; documentation only) |
| 15. ENG-04 part 1 | Lesson feedback engine: error translations, line highlight, hint ladder, honest result states | in_review: merged (PR #22, handoff 15); live check owed (see below) |
| 16. BACKLOG-SYNC | Backlog synced with handoffs 09 to 14 | in_review: merged (PR #20, handoff 16; documentation only) |
| 17. FB-02 | Anonymous feedback storage and `POST /api/feedback` (migration 0008) | in_review: merged (PR #24, handoff 17); live check owed (see below) |
| 18. BACKLOG-SYNC-2 | Backlog synced with PRs #19 to #22 | in_review: merged (PR #23, handoff 18; documentation only) |
| 19. ENG-04 part 2a | Check rules in content, tagged hints, similar examples, "Other ways to do it", hint-button outline | in_review: merged (PR #25, handoff 19); live check owed (see below) |
| 20. FB-04 | Testers page at `/admin/testers` | in_review: merged (PR #26, handoff 20); live check owed (see below) |
| 21. Docs sync | Reserved for a sync that never ran. The number stays empty, and no handoff 21 exists; that sync is stage 28 | — |
| 22. UI-05 | Lessons per unit; browser checks on the lesson page | in_review: merged (PR #27, handoff 22); live check owed (see below) |
| 23. README-01 | README with banner, screenshots, feature table and diagram | in_review: merged (PR #28, handoff 23; documentation only) |
| 24. EDU-04 part 1 | Unit 2 lessons 1 to 3 | in_review: merged (PR #29, handoff 24); live check owed (see below) |
| 25. ID-01 plan | Independent learner accounts, checked against the code | in_review: merged (PR #30, handoff 25; documentation only) |
| 26. EDU-04 part 2 | Unit 2 lessons 4 to 6; unit lessons complete, with no unit project and no unit check | in_review: merged (PR #31, handoff 26); live check owed (see below) |
| 27. EDU-03 part 1 | Unit 3 lessons 1 to 3 | in_review: merged (PR #32, handoff 27); live check owed (see below) |
| 28. DOCS-SYNC | Docs sync (master run S01) | in_review: merged (PR #33, handoff 28; documentation only) |
| 29. ENG-06 | Function-call checks | in_review: merged (PR #34, handoff 29); no lesson uses them yet |
| 30. Course designs | Ten course design documents | in_review: merged (PR #35, handoff 30; documentation only) |
| 31. OPS-04 | Data retention policy | in_review: merged (PR #36, handoff 31; documentation only) |
| 32. EDU-03 part 2 | Unit 3 lessons 4 and 5; unit lessons complete, with no unit project and no unit check | in_review: merged (PR #37, handoff 32); live check owed (see below) |
| 33. Construct rules | Naming proposal | in_review: merged (PR #38, handoff 33; documentation only) |
| 34. ENG-07 | Allowed imports and seeded random | in_review: merged (PR #39, handoff 34); live check owed (see below) |
| 35. ENG-08 | File fixtures; each check case starts clean | in_review: merged (PR #40, handoff 35); live check owed (see below) |
| 36. UI-01 | Two cosmetic fixes | in_review: merged (PR #41, handoff 36); live check owed (see below) |
| 37. SEC-08 | CI actions pinned to commits | in_review: merged (PR #42, handoff 37) |
| 38. DOCS-SYNC | Docs sync, with the owner's answers of 2026-11-02 | in_review: merged (PR #43, handoff 38; documentation only) |
| 39. Dependabot | GitHub Actions only, monthly (decision 31) | in_review: merged (PR #44, handoff 39); its first PRs, #47 to #49, are merged too |
| 40. Hidden calls | A hidden case may call a function; its arguments reach the browser, its result never does (decision 28) | in_review: merged (PR #45, handoff 40); no lesson uses it yet |
| 41. ENG-10 | Learner tests against correct and broken reference programs | in_review: merged (PR #46, handoff 41); no lesson uses it yet |
| 42. QA-01a, QA-03 | Keyboard fix in the editor (Esc, then Tab), keyboard-only tests, axe audit, screen reader sheet, Firefox and WebKit report | in_review: merged (PR #50, handoff 42); live check owed (see below) |
| 43. ENG-08b | The learner's own files; no file can stand in for a Python module (decision 30) | in_review: merged (PR #51, handoff 43); no lesson uses it yet |
| 44. SEC-05 | Pyodide pinned, every file checked against a SHA-256 hash | in_review: merged (PR #52, handoff 44) |
| 45. SEC-06 | Invitation tokens after `#`, out of addresses and logs | in_review: merged (PR #53, handoff 45) |
| 46. ENG-11 | Rate-limit counters in the database (migration 0010) | in_review: merged (PR #54, handoff 46) |
| 47. QA-03 follow-up | Tests that failed only in Firefox or WebKit | in_review: merged (PR #55, handoff 47) |
| 48. EDU-01 | Placement questions and tasks for unit 1 | in_review: merged (PR #56, handoff 48; documentation only) |
| 49. EDU-10 | Video scripts for unit 1 | in_review: merged (PR #57, handoff 49; documentation only) |
| 50. DOC-03 | Book and course outline, expanded | in_review: merged (PR #58, handoff 50; documentation only) |
| 51. DOCS-SYNC | Docs sync after handoffs 38 to 50 | in_review: merged (PR #59, handoff 51; documentation only) |
| 52. Visual redesign | The owner's prototype built into the app: design tokens and one stylesheet, 16 lesson pictures with a fallback, the lesson page (card-type tabs, five-stop path, worked-example markers, a challenge ticket with visible cases and locked hidden ones), signed-out and student home, course page; `docs/design/art-style.md`. No backend change, no CSP change. Three open questions (decision log) | in_review: merged (PR #60, handoff 52); live check owed (see below) |
| 53. Public-history scan | Secrets and personal data in every commit on every branch, after the repository went public: nothing to rotate | in_review (PR #61, handoff 53; documentation only) |
| 54. DOCS-SYNC | This sync | in_review (PR #62, handoff 54) |

### Live checks still owed

Merged work whose live check has not been recorded yet. Record the result here (date and what was seen), then move the item to `verified`.

**Every check still owed, with its PR.** None has a recorded result, so none of these is `verified`.

- **(a) Stage 7, SEC-03 sessions, PR #13** (handoff 07 section 10): a copied `session` cookie makes `curl … /api/me` print `200`; after **Sign out** the same command prints `401`; another device that was signed in stays signed in.
- **(b) ASSESS-07, honest unit 1 checks, PR #16** (handoff 10 section 9): on `/preview?lesson=hello&card=5`, printing the same line twice (`print("hi")` twice) no longer passes; it says "Both lines say the same thing".
- Also unrecorded: **stage 8, SEC-09, PR #14** (handoff 08 section 10), the nonce headers and the console checks.
- **(c) Stage 12, FB-01 admin and tester roles, PR #21** (handoff 12 section 9; `ADMIN_EMAILS` must be set in Render first):
  - Render → python-academy-api → Logs shows `Database schema is at migration 0007`.
  - Signed out, `/api/admin/students` gives `401`.
  - Signed in as a normal student, `/api/admin/students` gives `403`.
  - The admin session is short: after more than 1 hour unused, `/api/admin/students` gives `401` and you sign in again.
- **(d) Stage 15, ENG-04 part 1 lesson feedback, PR #22** (handoff 15 section 10):
  - **NameError:** on "Create your hero", card 5, `hero = "Kai"`, `tool = "map"`, `print(heor)` shows "Python stopped", "Python does not know heor", "Line 3", "Did you mean hero?"; line 3 is marked with ▶ and tinted; "Go to line 3" puts the cursor at the start of line 3.
  - **Python's message:** "Show Python's message" shows a short traceback for line 3, with no `/lib/python312.zip` lines.
  - **Syntax error:** on "Choose a path", card 5, removing the `:` after an `if` shows "This line needs a colon" and "On or just before line N", with that line marked.
  - **The highlight clears** when the marked line is changed; the message stays until the next run.
  - **Honest pass:** on "Open the story", card 5, `print("hi")` then `print("woah")` shows "Check passed" and a message ending "That part is your call."
  - **Not a pass on "Try it":** a run on card 4 shows "Ran · not checked" in a grey box, not green.
  - **Hints:** three clicks show "A nudge", "A bigger hint", "The approach" in order, then "That is every hint" and no answer button.
  - **Nothing new is sent:** in DevTools → Network, a run with an error makes no request to `/api/check` or `/api/attempts`.
  - **No CSP reports** in DevTools → Console during these checks.
  - **Phone:** the NameError check on a phone, with no sideways scrolling.
- **(e) Stage 11, ENG-03 browser checks, PR #17:** handoff 11 section 8.
- **(f) Stage 17, FB-02 feedback storage, PR #24:** handoff 17 section 9.
- **(g) Stage 19, ENG-04 part 2a, PR #25:** handoff 19 section 9.
- **(h) Stage 20, FB-04 testers page, PR #26:** handoff 20 section 8.
- **(i) Stage 22, UI-05 lessons per unit, PR #27:** handoff 22 section 8. Its note that the browser-check path cannot be checked live no longer holds: unit 2 uses it.
- **(j) Stage 24, unit 2 part 1, PR #29:** handoff 24 section 8.
- **(k) Stage 26, unit 2 part 2, PR #31:** handoff 26 section 8.
- **(l) Stage 27, unit 3 part 1, PR #32:** handoff 27 section 8.
- **(m) Stage 32, unit 3 part 2, PR #37:** handoff 32 section 9.
- **(n) Stage 34, allowed imports, PR #39:** handoff 34 section 8.
- **(o) Stage 36, cosmetic fixes, PR #41:** handoff 36 section 8.
- **(p) Stage 35, file fixtures, PR #40:** handoff 35 section 9: units 2 and 3 work as before, with no CSP reports.
- **(q) Stage 39, Dependabot, PR #44:** handoff 39 section 8. Seen: PRs #47 to #49 appeared and were merged on 2026-11-02.
- **(r) Stage 42, keyboard and accessibility, PR #50:** handoff 42 section 8: in a challenge, Tab adds four spaces, then Esc and Tab moves to "Run & check challenge".
- **(s) Stage 43, learner files, PR #51:** handoff 43 section 9: units 2 and 3 work as before, with no CSP reports.
- **(t) Stage 44, Pyodide pinned and checked, PR #52:** handoff 44 section 8.
- **(u) Stage 45, invitation tokens, PR #53:** handoff 45 section 8.
- **(v) Stage 46, rate-limit counters in the database, PR #54:** handoff 46 section 8.
- **(w) Stage 52, visual redesign, PR #60:** handoff 52 section 10: the home page playground loads no Python; a student sees the next lesson with its picture; a unit 2 challenge ticket marks a wrong answer "not yet"; no CSP reports. Also a real phone and Safari, which were not tried.

## 2. Suggested order

1. ~~Record the stage 4 live check.~~ Done 2026-10-25.
2. **SEC-01 and SEC-04** (rate limits, security headers): live and checked 2026-10-25. Still to do: switch the page CSP to enforce mode after a week of clean consoles (handoff 06 section 4).
3. **SEC-03** (server-side sessions): merged (stage 7); record its live check. **SEC-09** (CSP nonces): in review (stage 8); after a week of clean consoles, enforce the nonce policy (handoff 08 section 5), which also completes SEC-04. Both come before the admin inbox.
4. **FB-01 to FB-07**: admin, testers, feedback button, admin inbox (security plan: `docs/plan/feedback-security.md`).
5. **PILOT-01**: invite the first learner and collect feedback through the new button.
6. **ENG-04** (lesson feedback engine) and **ASSESS-07** (honest unit 1 "Open the story" check; merged in PR #16), then **ENG-03** (browser behaviour checks; in review, PR #17), then **EDU-04** (Python unit 2) with its first **unit check**. PLAN-03 (review of `teaching-design.md`) can run alongside and should finish before unit 2 content is written.
7. **OPS-05**: cost review (the owner has set a reminder for 2026-11-08).

**State on 2026-11-02:** items 3, 4 and 6 above were written before stages 16 to 27. Since then FB-02, FB-04, ENG-04 part 2a, UI-05 and unit 2's lessons have merged, and unit 3 is merged in full (PRs #32 and #37). Unit 2 shipped without its unit check. `docs/plan/master-run.md` holds a proposed queue for the remaining work; it decides nothing, and an item in it is decided only when the owner says so.

**State on 2026-11-09:** PRs #43 to #60 are merged, including the visual redesign (#60), and the repository is public. Every Part 2 box of the master run is still empty, so the rest of its queue waits on them.

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
| PLAN-03 | Next | Review the teaching design (`docs/plan/teaching-design.md`): owner reads it, a second assistant checks it against `build.md` sections 3, 4 and 12, decisions recorded; pilot one new task type in unit 2 before adding the rest | None | proposed (stage 9, handoff 09) |

### Safety and operations

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| SEC-01 | Now | Rate limits and quotas on write endpoints: `/api/check`, invitations, attempts, enrolment, goal changes and sign-in (done in stage 6; counters in memory, see handoff 06). The first live check found that a made-up `X-Forwarded-For` header chose a new counter; PR #12 trusts only a configured source. Production uses `CLIENT_IP_HEADER=cf-connecting-ip` (now in `render.yaml`); without it all signed-out visitors share one counter. The future feedback endpoint gets its own database counters (`feedback-security.md` section 7) | None | verified: live checks passed 2026-10-25 (spoof tests, `Retry-After`, separate counters for phone and Mac; handoff 06 section 13.7) |
| SEC-02 | Next | Make the API a private Render service with no public URL; confirm the frontend proxy still works | None | proposed |
| SEC-03 | Next | Logout revokes the session on the server. Before stage 7 a copied cookie kept working after logout, and for as long as it was used at least once a day. Stage 7: the cookie holds only a random session ID, the `sessions` table (migration 0006) holds the session, logout deletes it; 7-day absolute and 24-hour idle limits. Required before the admin inbox (FB-06) ships, see `feedback-security.md` | Migration | in_review: merged (PR #13); live check owed, section 1 (a) |
| SEC-04 | Now | Security headers: Content-Security-Policy and HSTS on the main app. Stage 6 adds HSTS, `frame-ancestors 'none'` (enforced) and the page CSP in Report-Only mode; the item is verified once the CSP is switched to enforce mode after a clean live check | None | in_review: headers live and checked 2026-10-25 (handoff 06 section 13.7); enforce mode not yet switched |
| SEC-10 | Now | Check whether any Google account can sign in today (`independent-learners.md` section 6.1); if so, record it and bring ID-01c forward | Owner check | proposed |
| SEC-11 | Next | Keep Google's one-time sign-in code out of the API access log (`independent-learners.md` section 5.1): turn off uvicorn's access log or filter query strings, and confirm what Render's own request logs keep. Related to SEC-06 (invitation tokens) | None | proposed |
| SEC-05 | Later | Pyodide and CDN integrity: self-host or pin with integrity checks where possible. Pinned with SHA-256 checks of every file, without self-hosting (PR #52, handoff 44) | None | in_review: merged; live check owed, section 1 (t) |
| SEC-06 | Later | Keep invitation tokens out of URLs and request logs. Links carry the token after `#`; older links still work (PR #53, handoff 45) | None | in_review: merged; live check owed, section 1 (u) |
| SEC-07 | Next | Branch protection on `main` requiring passing checks (owner action; may need a paid GitHub plan, otherwise merge only on all-green) | Owner | proposed |
| SEC-08 | Later | Pin CI actions to commit SHAs (merged, PR #42, handoff 37); routine updates by Dependabot for GitHub Actions only, monthly (decision 31) | None | in_review |
| SEC-09 | Next | Replace `'unsafe-inline'` in the page CSP's `script-src` with per-request nonces (a Next.js proxy file and dynamic rendering), so injected inline script is blocked. Stage 8: `frontend/proxy.ts` makes a nonce per page request; every page now renders per request; the nonce policy is sent in Report-Only mode next to handoff 06's policy; enforcing it is one line (handoff 08 section 5). Proposed as a dependency of the admin inbox (FB-06), owner to confirm | SEC-04 | in_review: merged (PR #14), Report-Only; live check owed (handoff 08 section 10); enforce after a week of clean consoles |
| ENG-11 | — | Proposed by the master run: Move rate-limit counters from memory to the database, with behaviour identical to today; needed before more than one API instance. Built with migration 0010, as decision 29 keeps 0009 for S04; feedback's per-tester counters stay in memory (PR #54, handoff 46) | Migration | in_review: merged; live check owed, section 1 (v) |
| OPS-01 | Before broad rollout | Confirm staging, recovery, privacy, quotas and alerts (umbrella item; OPS-02 to OPS-04 are parts of it) | OPS-02, OPS-03, OPS-04 | proposed |
| OPS-02 | Next | Part of OPS-01: confirm backups and a restore drill; add staging | None | proposed |
| OPS-03 | Later | Part of OPS-01: operational alerts | OPS-02 | proposed |
| OPS-04 | Next | Part of OPS-01: data retention policy (`retention.md`, merged, PR #36, handoff 31). Its questions are open, and nothing in it is built | Before FB-05 ships | in_review |
| OPS-05 | Next | Reduce Render costs: review billing, workspace plan, 15 GB database storage; later consider one combined service or a free-tier database (reminder set by the owner for 2026-11-08) | Billing screenshot | proposed |

### Documentation (handoff 14)

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| DOC-01 | Next | Every handoff includes "Decisions and why", "Bugs found and how they were fixed" and "How it was tested" (`build.md` section 14) | None | in_review: merged (PR #18, handoff 14) |
| DOC-02 | Later | Decision log (`docs/plan/decision-log.md`), kept up to date each stage, and a book and course built from it (`docs/plan/engineering-book-outline.md`) | DOC-01 | in_review: merged (PR #18, handoff 14): log backfilled and outline proposed; book and course not written |
| DOC-03 | Later | Proposed by the master run (stage WE11): expand the book and course outline from the decision log. Expanded (PR #58, handoff 50); no chapter written | DOC-02 | in_review |
| README-01 | Next | README with banner, screenshots, feature table and diagram, each claim checked against the code. Kept up to date by each docs sync | None | in_review: merged (PR #28, handoff 23) |

### Public website (handoff 13)

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| SITE-01 | Next | Design direction for the public story site and the product's look (`docs/plan/site-design.md`): three story concepts, illustration approach, motion and performance budget, architecture, accessibility, staged plan. The visual redesign (PR #60) follows the owner's prototype where it differs from section 2 (code text in pictures; flat shapes, no gradients). Whether to update `site-design.md` is open question 2 of handoff 52 | None | in_review: merged (PR #19, handoff 13) |
| SITE-02 | Next | Public landing story site: the chosen concept as a separate static site (proposed), built in three PRs: skeleton with still scenes and strict headers; scroll motion with reduced motion and a pause button; interactive moments. Within the section 3 budget, 0 axe violations. **Not decided:** since PR #60 the signed-out home works as a landing page, so whether SITE-02 is still wanted, and if so whether it shares the product's new stylesheet, are open questions (decision log). Master run box B-W1 is still empty | SITE-01 decisions (concept, architecture); the open questions | proposed |
| SITE-03 | Later | Product polish, rescoped after the visual redesign (PR #60, handoff 52 section 7). **Done by PR #60:** colour and spacing tokens, one stylesheet, a picture for every lesson, the course page header and rows. **Left:** course emblems in the catalog, a short lesson celebration, and refreshed README screenshots; calm and fast. Was "to match the story"; it no longer waits on SITE-02 | Visual redesign (PR #60, merged) | proposed |
| SITE-04 | Later | Custom domain and possible rename: choose a name, buy a domain (paid, owner decision), DNS, `APP_ORIGIN` and `API_ORIGIN`, Google OAuth settings, redirects, one-time sign-in again | Owner decision on name and cost; `build.md` section 16 (brand) | proposed |

### Testers, feedback and admin

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| FB-01 | Next | Decide admin identity (email allowlist) and record it in the plan; tester rules (students only, decision 23) and parents' access (none, decision 19) are decided. Built in stage 12: `ADMIN_EMAILS`, short admin sessions, the tester flag (migration 0007) | Decisions 14, 17; ID-01 | in_review: merged (PR #21, handoff 12); live check owed, section 1 (c) |
| FB-02 | Next | Migration: anonymous `feedback` table (no user ID), tester flag, short-lived rate-limit counters, 50-day cleanup, 90-item cap. Built in stage 17: migration 0008 and `POST /api/feedback` | FB-01 | in_review: merged (PR #24, handoff 17); live check owed, section 1 (f) |
| FB-03 | Next | Admin role and server-side guard, with tests for 403 on every admin route. Handoff 12 section 8: the guard and the route-enumeration tests are delivered in PR #21; the inbox routes remain | FB-01 | in_review: merged (PR #21) |
| FB-04 | Next | Admin page to mark students as testers (student accounts only). The API came with PR #21 (`GET /api/admin/students`, `POST /api/admin/testers`); the page at `/admin/testers` came with PR #26 | FB-03 | in_review: merged (PR #26, handoff 20); live check owed, section 1 (h) |
| FB-05 | Next | Feedback button and form (testers and the admin; never parents) with auto-attached context and optional code | FB-02, SEC-01, OPS-04 | proposed |
| FB-06 | Next | Admin inbox: list, filters, statuses, notes, GitHub issue link | FB-03, FB-05, SEC-03 | proposed |
| FB-07 | Next | "Copy digest" export for pasting into an assistant, with no emails and no code by default | FB-06 | proposed |
| FB-08 | — | Testers see status of their own items (dropped: not possible with anonymous feedback) | None | deferred |
| FB-09 | Later | Create GitHub issues from feedback automatically (needs a token and review; manual links first) | FB-06 | deferred |
| PILOT-01 | Next | Invite the first learner, watch a 10-minute session, collect feedback through the button | FB-05 | proposed |

### Assessment

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| ENG-04 | Next | Lesson feedback engine (`docs/plan/lesson-feedback.md`): friendly translations of common Python errors, the offending line highlighted in the editor, check-specific messages that only claim what was checked, progressive hints beside the error, predict-first tasks; tests that no hint, example or message adds up to a full solution. Before unit 2. Uses the `failed` fields of the ENG-03 result (`docs/plan/browser-checks.md` section 4, added by PR #17). Part 1 (stage 15): translations, line highlight, hint ladder, honest result states | None | in_review: merged (PR #22, handoff 15); live check owed, section 1 (d) |
| ENG-04b | Next | Part 2: named check rules and message IDs in content; hints tagged to errors and rules; a similar example after hint 3; "Other ways to do it" after passing; predict-first; support-data measurements. Also the hint-button outline after two failed runs (decision 25). Part 2a: rules, tagged hints, similar example, other ways, outline. Predict-first and measurements moved to ENG-04c (handoff 19) | ENG-04 | in_review: merged (PR #25, handoff 19); live check owed, section 1 (g) |
| ENG-04c | Next | Part 2b: predict-first tasks, measurements and support data. Measurements need a privacy review (no user ID, no code, stated retention) | ENG-04b | proposed |
| ASSESS-07 | Next | Make the unit 1 "Open the story" (`hello`) check honest: the success message says only what was checked; the two lines must differ, contain letters and not copy the worked example or a hint; reword the prompt; replace hint 3 with a partial pattern; also rewrite the `input` hints, which combined into a passing answer, and the `variables` hints, which spelled out the whole `print` line (`lesson-feedback.md` appendix A and section 8). New task version; learners who passed keep it; no XP change. Before unit 2 | ENG-01 | in_review: merged (PR #16); live check owed, section 1 (b) |
| ASSESS-08 | Next | Reword unit 1 hints to fit "a nudge, a bigger hint, the approach", still with no hint passing the check (handoff 15 section 11). Done as part of ENG-04b (decision 27) | ENG-04b | in_review: merged (PR #25, handoff 19); live check owed, section 1 (g) |
| ENG-03 | Next | Browser behaviour-check contract: the Pyodide worker runs learner code against test cases from the content file, with limits and result states including `execution_error` | None | in_review: merged (PR #17, handoff 11); live check owed, section 1 (e) |
| ASSESS-01 | Next | Decide the remaining unit-check rule (the pass rule, decision 15) and record it in the plan | None | proposed |
| ASSESS-02 | Next | Content schema: `unit_check` task type, level variants (high school, university) and validation | ENG-03 | proposed |
| ASSESS-06 | Next | Learner level setting (self-chosen, never a birthdate; decision 21) used to pick the check variant. Also asked once at onboarding (ID-01 stage E), still self-chosen and never from a birthdate | ASSESS-02; for onboarding, ID-01d | proposed |
| ASSESS-03 | Next | Unit check interface (cards, retake with new variants, "Unable to assess" handling) | ASSESS-02 | proposed |
| ASSESS-04 | Next | Unit check for unit 1 using the existing bounded checker; optional for learners who already completed unit 1, and earns the badge (decision 22) | ASSESS-02 | proposed |
| ASSESS-05 | Next | Award the unit's skill badge (no XP) from the check through the existing ledgers; the unit project keeps its 200 XP (decision 16) | ASSESS-03 | proposed |
| ENG-06 | — | Function-call checks: an additive extension of the ENG-03 contract, so a check can call a function the learner defined. Merged (PR #34, handoff 29). Hidden calls, under decision 28, merged too (PR #45, handoff 40) | ENG-03 | in_review |
| ENG-07 | — | Allowed imports and seeded `random` (a security stage). Merged (PR #39, handoff 34); live check pending | None | in_review |
| ENG-08 | — | File fixtures in Pyodide's in-memory filesystem. Merged (PR #40, handoff 35). A learner's own second file is ENG-08b | None | in_review |
| ENG-08b | Before unit 7 | A learner's own second file, for `py.own-modules`. A file named `random.py` or `os.py` must not shadow or get past the import guard, and the guard applies inside learner modules too (decision 30). Merged (PR #51, handoff 43); it also closed a way round the guard (a program writing `datetime.py`) | ENG-07, ENG-08 | in_review |
| ENG-09 | — | Proposed by the master run: Rubric, self-review and local-tutorial task types, with evidence labelled as self-reported | PROJ-01 | proposed |
| ENG-10 | — | Run learner tests against correct and broken reference implementations, in the worker. Broken references may reach the browser, and a correct one may where it isn't the lesson's answer (decision 28). Merged (PR #46, handoff 41) | ENG-06 | in_review |
| PROJ-01 | — | Proposed by the master run: Unit project mechanism: three versions and one award per unit (200 XP) | Decision 15 | proposed |
| ENG-05 | Later | Optional AI helper, "Explain my error" (`docs/plan/ai-helper.md`): server-side key only, off by default, per-user and global daily caps, a hard provider spending limit, never grades or writes solutions. Design note only; not to be built until the owner decides section 9 of that note (cost, provider terms for 13 to 17 year olds, consent) | ENG-04, owner decisions | deferred |
| EDU-01 | Next | Write placement question and task examples for the current four skills (Issue #4). Proposed in `placement.md` (PR #56, handoff 48) | None | in_review |
| EDU-02 | After design | Pilot placement (the optional skills check) on one skill before all four. Waits for EDU-01's review and the placement storage decision (`retention.md`) | EDU-01, ENG-03 | proposed |

### Curriculum

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| EDU-04 | Next | Python unit 2, Numbers and decisions, with its unit check. Part 1 (lessons 1 to 3) and part 2 (lessons 4 to 6) are merged; the unit check is not built, and neither is the unit project | ENG-03, ASSESS-02, ENG-04, ASSESS-07 | in_review: lessons merged (PRs #29 and #31, handoffs 24 and 26); live checks owed, section 1 (j) and (k) |
| EDU-03 | After checker design | Python unit 3, Repeat and explore (loops that always end). All five lessons merged (PRs #32 and #37, handoffs 27 and 32); live checks pending. Its project and check are still to do | EDU-04 | in_review |
| EDU-05 | — | Not used: this ID was briefly unit 3, which is EDU-03 in `build.md` | — | deferred |
| EDU-06 | Next | Unit 4, Keep track of a world (lists, dicts, sets) | EDU-03 | proposed |
| EDU-07 | Next | Unit 5, Organize your code (functions); project Adventure v2 | EDU-06 | proposed |
| EDU-08 | Later | Units 6 to 12: errors, libraries, tests, files, regex, classes, final project | EDU-07 | proposed |
| EDU-09 | Later | Hackathon Ready course (7 units) | Python units 1 to 7 | proposed |
| TOOL-01 | Alongside projects | Draft "Git versus GitHub" and "first commit" lessons with a safe practice repo | Python unit 1 | proposed |
| TOOL-02 | Later | The full Git and GitHub Essentials course, including a real first pull request | TOOL-01 | proposed |
| TOOL-03 | Later | "Working with AI" course (`ai`): verifying AI answers, asking well, setting up Claude and Claude Code in a practice repository, AI with GitHub, connecting tools safely, handoffs (`teaching-design.md` section 6.6). Before writing the setup units: check each provider's minimum age and cost, and keep a no-cost path | TOOL-01, PLAN-03 | proposed |
| EDU-10 | Later | Video scripts for lessons: short (under about 6 minutes), one idea each, pause-and-predict moments, captions and transcripts, lessons still work without them (`teaching-design.md` section 7). Scripts only; recording and hosting are separate decisions Unit 1 scripts drafted (PR #57, handoff 49). | PLAN-03 | in_review |
| WEB-01 | Later | Design the website project track and isolated previews | Earlier courses | proposed |
| DATA-01 | Later | Design the SQL runtime and first investigation project | Earlier courses | proposed |
| NODE-01 | Later | Plan the Node.js/SQL capstone | WEB-01, DATA-01 | proposed |
| CE-01 | Later | Map university courses to optional deep-dive units | Actual course outlines | proposed |

### Interface and accounts

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| UI-01 | Next | Cosmetic fixes: stacked chips on the Python course card; small "Goal:" text in the parent view. Merged (PR #41, handoff 36); live check pending | None | in_review |
| UI-02 | Later | "Not now" button and storage for dismissed recommendations. **Wait** (decision 29) | Decision 29 | proposed |
| UI-03 | Later | Record when a learner overrides a recommendation (plan 4.4). **Wait** (decision 29) | Decision 29 | proposed |
| UI-04 | Later | Pause a course (plan 4.2). **Wait** (decision 29) | Decision 29 | proposed |
| UI-05 | Next | Lesson page reads lessons per unit instead of the legacy shape (needed once unit 2 exists). With ENG-04, this is the step that connects the lesson page to the ENG-03 browser-check contract (handoff 11): it must call `check-runner.js` from the lesson page for lessons with browser checks (handoff 15 section 11) | None | in_review: merged (PR #27, handoff 22); live check owed, section 1 (i) |
| UI-06 | Later | Show a goal-specific capstone when a path is finished (proposed mapping: scratch to Python final project, hackathons to Hackathon Ready, university to Engineering Depth, websites to Full-Stack Builder, data to Data Investigation) | Decision 20 | proposed |
| ID-01 | Next | Independent learner accounts: the plan (`independent-learners.md`). Decided 2026-10-27: 16 or older, self-declared; anyone with a Google account; level-based recommendations later. Split into ID-01a to ID-01f and ASSESS-06 | Product decision (made) | in_review: plan merged (PR #30, handoff 25; documentation only) |
| ID-01a | Next | Privacy notice and data inventory (stage A) | ID-01 | proposed |
| ID-01b | Next | Export and delete my account (stage B) | ID-01a | proposed |
| ID-01c | Next | Sign-ups switch, daily cap, admin disable or delete (stage C) | None | proposed |
| ID-01d | Next | Independent enrolment, 16 or older (stage D) | ID-01a, ID-01b, ID-01c | proposed |
| ID-01e | Next | Invited group first, then publishing the Google app and, if needed, a custom domain (stage F) | ID-01a to ID-01d, ASSESS-06, OPS-02, SEC-09, SEC-11 | proposed |
| ID-01f | Later | Level-based recommendations (stage G) | ASSESS-06 | proposed |
| QA-01 | Before broader use | Audit core lesson accessibility and grading reports: real screen reader, Safari and Firefox, reproducible defects and retest evidence Part a built: keyboard-only tests, an axe audit, a manual screen reader sheet (PR #50, handoff 42). The manual checks need people and are not run. | None | in_review |
| QA-02 | Before broader use | Part of QA-01: report on incorrect grading rejections (uses feedback data) | FB-06 | proposed |
| QA-03 | — | Proposed by the master run: Cross-browser CI (Firefox, WebKit), non-blocking first; increases CI time Built as a non-blocking weekly report (PR #50, handoff 42); test-only fixes after its first run (PR #55, handoff 47). | None | in_review |

## 6. Decisions

Numbers continue from `docs/plan/course-catalog.md` section 9.

| # | Decision | Answer |
| --- | --- | --- |
| 11 | Who gets the feedback button? | Testers only (answered 2026-10-25); the admin also sees it (decision 23) |
| 12 | Is feedback tied to an account? | Sign-in required only to stop bots; stored anonymously with no user ID, name or email (answered 2026-10-25) |
| 13 | Is passing the unit check required to complete a unit? | Yes, and learners can retake it (answered 2026-10-25) |
| 14 | How is the admin identified? | `ADMIN_EMAILS`, a server-side list of verified Google emails; admin is decided at sign-in and re-checked on every request (answered 2026-10-26; built in FB-01, PR #21; `course-catalog.md` section 9) |
| 15 | What counts as passing a unit check? | All core tasks pass; hints allowed. Pilot and adjust (proposed) |
| 16 | Does the check replace the unit project milestone? | No. The unit project keeps its 200 XP; passing the check awards a skill badge and no extra XP; a unit is complete when both the project and the check are done (answered 2026-10-25) |
| 17 | Does feedback include the learner's code? | Only with an opt-in checkbox (proposed) |
| 18 | Feedback retention | Delete after 50 days; at most 90 items. When full, delete the oldest resolved items first (resolved means `fixed` or `wont_fix`); if none are resolved, reject the new item with a clear message (answered 2026-10-25) |
| 19 | Do parents see feedback? | No. Parents never see the feedback button or any feedback, which follows from decision 23 (answered 2026-10-25) |
| 20 | Capstone for each goal | As proposed in UI-06 (proposed) |
| 21 | How is the unit-check variant chosen? | Variants by a self-chosen learner level (high school, university). The level is never derived from, and never asks for, a birthdate. The enrolment age gate is unchanged (answered 2026-10-25) |
| 22 | What happens to learners who already completed unit 1? | They keep unit 1 as complete. The unit 1 check is optional for them and earns the badge (answered 2026-10-25) |
| 23 | Who can be a tester, and who sees the feedback button? | Testers are students only. The admin account also sees the button. Parents never do (answered 2026-10-25) |
| 24 | Lesson feedback: friendly message or Python's message first? (`lesson-feedback.md` section 11, decision 2) | The friendly message first in every unit; revisit around unit 6 (answered 2026-10-27) |
| 25 | Highlight the hint button after two failed runs? (`lesson-feedback.md` section 11, decision 3) | Yes, as a gentle outline, in ENG-04b (answered 2026-10-27) |
| 26 | ENG-04 part 1 assumptions 1 to 3 (handoff 15 section 5): the timeout message in every unit; the indent message also for `else` and `elif`; naming the real built-in in the case-sensitivity message | Accepted (answered 2026-10-27) |
| 27 | Reword the unit 1 hints to fit the hint ladder? | Yes, in ENG-04b (ASSESS-08) (answered 2026-10-27) |
| 28 | May hidden data reach the browser? | Yes, with one rule: hidden inputs reach the browser, because the worker has to run them, and hidden expected results never do. For ENG-10, broken reference programs may reach the browser, and a correct one may as long as it isn't the lesson's answer. `browser-checks.md` section 5 states the rule and its limit, and the leak tests stay (answered 2026-11-02) |
| 29 | Build UI-02 to UI-04 now? | Wait. Dismissing the only released course leaves nothing to recommend, they would store personal data the retention policy doesn't cover yet, and they would take migration 0009, planned for the sign-ups switch (answered 2026-11-02) |
| 30 | A learner's own second file? | Its own stage before unit 7 (ENG-08b). A learner file named `random.py` or `os.py` must not shadow or get past the import guard, and the guard applies inside learner modules too (answered 2026-11-02) |
| 31 | Automatic updates for pinned CI actions? | Yes: Dependabot for GitHub Actions only, monthly. It only opens PRs for review (answered 2026-11-02) |

The questions raised when this file was added (handoff 05) were answered by the owner on 2026-10-25 and are recorded above as decisions 16, 18, 21, 22 and 23, and in items SEC-03, OPS-05 and PLAN-01.

**Answered on 2026-10-27 (`independent-learners.md` section 0), not numbered:** an independent learner account is for people 16 or older, self-declared; anyone with a Google account may sign up once the Google app is published; level-based recommendations come later.

Questions from handoffs 22 to 27 that are still open, with their recommendations, are listed in `decision-log.md`, in the section "Open, awaiting the owner". Handoff 22 also asks for a row for construct rule IDs in browser checks. It has no ID yet, so it is listed there and not here.

**Open, not decided (handoff 52, questions 1 to 3):** the lesson stage names "Worked example" and "Challenge", code text inside lesson pictures, and the parents' attempt count. Each has a recommendation in `decision-log.md`, "Open, awaiting the owner"; none is a decision.

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

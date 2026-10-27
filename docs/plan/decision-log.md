# Decision log: how Python Academy was built

Last updated: 2026-10-26 (America/Toronto)  
Status: **backfilled** from handoffs 01 to 11, the merged pull request descriptions (#1 to #16, plus #17, which was still open) and the commit history up to `27ab31b`. From handoff 14 on, each handoff adds its own chapter (`build.md` section 14, "Handoff template").  
Backlog: DOC-01 (decision sections in every handoff) and DOC-02 (this log); proposed in handoff 14.  
Related: [`engineering-book-outline.md`](engineering-book-outline.md) (the book and course this log feeds); [`docs/handoffs/`](../handoffs/).

## How to read this log

Each chapter is one stage of work and has the same three sections:

- **Decisions and why:** what was chosen, the other options that were considered, and the reason.
- **Bugs found and how they were fixed:** including near-misses, meaning problems caught by a test, a review or a live check before they hurt anyone.
- **How it was tested:** what each kind of test proves, what was mocked, and what the deliberate-break controls showed.

**Rules used when backfilling:**
- Every statement comes from a handoff, a pull request (PR) description or a commit message, named in **Sources** at the start of each chapter.
- Where the reason for a choice was never written down, the entry says **reasoning not recorded**. Where only one option was ever written down, it says **other options not recorded**. Nothing was invented to fill the gaps.
- A few small bugs were fixed while tests were being written and never made it into a handoff. They are included, labelled **(implementer's session notes)**, because handoffs before handoff 14 had no section for them. That gap is why the template changed.

Terms in **bold** the first time they appear are explained in the [glossary](#glossary) at the end.

| Chapter | Stage | Pull requests | Status at the time of writing |
| --- | --- | --- | --- |
| [0](#chapter-0-the-first-version-2026-10-24) | First version, deployment and first lessons | #1, #2, #3 and direct commits | Live |
| [1](#chapter-1-a-roadmap-and-a-plan-2026-10-24) | Roadmap and catalog plan | #6 and direct commits | Merged (documentation) |
| [2](#chapter-2-content-as-data-eng-01) | ENG-01 content format and result states | #5 | Verified live |
| [3](#chapter-3-changing-the-database-safely-eng-02) | ENG-02 migrations and award ledgers | #7 | Verified live |
| [4](#chapter-4-the-course-catalog-interface) | Catalog interface | #8 | Verified live |
| [5](#chapter-5-goals-and-recommendations) | Learner goals and recommendations | #9 | Verified live |
| [6](#chapter-6-one-ordered-backlog-and-a-threat-model) | Backlog, feature plans, feedback threat model | #10 | Merged (documentation) |
| [7](#chapter-7-rate-limits-and-security-headers-sec-01-sec-04) | SEC-01 rate limits, SEC-04 security headers | #11, #12 | Verified live (page policy still Report-Only) |
| [8](#chapter-8-logout-that-really-logs-out-sec-03) | SEC-03 server-side sessions | #13 | Merged; live check not yet recorded |
| [9](#chapter-9-a-content-security-policy-with-nonces-sec-09) | SEC-09 nonce-based CSP | #14 | Merged; live check not yet recorded |
| [10](#chapter-10-how-we-teach-and-how-feedback-should-work) | Teaching design and lesson feedback | #15 | Merged (documentation) |
| [11](#chapter-11-honest-checks-assess-07) | ASSESS-07 honest unit 1 checks | #16 | Merged; live check not yet recorded |
| [12](#chapter-12-checking-code-in-the-browser-eng-03) | ENG-03 browser behaviour checks | #17 | In review when this log was written |
| [13](#chapter-13-patterns-that-kept-coming-back) | Patterns that kept coming back | — | — |
| [14](#chapter-14-feedback-a-beginner-can-act-on-eng-04-part-1) | ENG-04 lesson feedback engine, part 1 | #22 | In review when this chapter was written |
| [15](#chapter-15-feedback-nobody-can-trace-fb-02) | FB-02 anonymous feedback storage | (handoff 17) | In review when this chapter was written |

---

## Chapter 0. The first version (2026-10-24)

**Sources:** commits `0f5c904` to `4241efb`; PRs #1, #2 and #3; `DEPLOYMENT.md`; handoff 01 section 4 (the security review).

**What was built:**
- A web app with a **Next.js** and **React** frontend in **TypeScript**, and a **FastAPI** backend on **PostgreSQL**, deployed on **Render**.
- **Google sign-in**: parents create a family account and invite learners.
- One chapter of lessons, "Build Your Own Adventure".
- Learners' Python runs in their own browser with **Pyodide** in a **web worker**.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| The technology stack (Next.js, FastAPI, PostgreSQL, Render) | Other options not recorded | Reasoning not recorded. `build.md` later says to keep this stack "unless a separately justified architecture decision changes it" |
| Learner code runs only in the browser; the server never runs it. It checks a small part of Python by reading the code's **abstract syntax tree (AST)** | Other options not recorded | PR #1: "without running learner code on the server". Running untrusted code on a server is a major security risk; this became a standing rule for every later stage |
| Parents must be over 25 and students at least 13; students join by invitation | Other options not recorded | Reasoning not recorded. Later stages were told never to change these rules |
| Parents can try the lessons in a preview that saves nothing (PR #2) | Other options not recorded | PR #2: let parents "try lessons from their dashboard"; "preview practice is not saved" |
| One card at a time: explanation, worked example, prediction, guided coding, challenge (PR #3) | A long single page (the previous design) | PR #3 replaced "the long lesson page". The detailed reasoning is in the later teaching design (chapter 10); at the time it was not recorded |
| Checks accept creative story text, but test different names and both paths (PR #3) | Other options not recorded | PR #3: "test different names and both paths while accepting creative story text" |

### Bugs found and how they were fixed

- **The first frontend build on Render failed.** Render's production build skipped development dependencies, which TypeScript needed. Fixed by changing the build command to `npm ci --include=dev` (commit `30b2416`; `DEPLOYMENT.md`). Found by: the deploy itself.
- **Browser tests could not run locally for PR #1:** "Chromium is absent and its download returned a corrupt archive." They ran in CI instead (PR #1 description).
- **Security gaps found in a review before stage 1** (handoff 01 section 4). They are not bugs in behaviour, but risks:
  - no rate limits
  - logout could not revoke a stolen cookie
  - the API had its own public URL
  - no Content-Security-Policy or HSTS
  - Pyodide loaded from a CDN without integrity checks
  - invitation tokens appeared in URLs

  Chapters 7, 8 and 9 fix several of these.

### How it was tested

- **Backend tests** (pytest): 25 in PR #1, 42 by PR #3. **Browser tests** (Playwright): 14 by PR #3, covering card navigation, account flows, real Pyodide for all five lessons, stop and timeout, mobile layout and reduced motion.
- **Live checks:** the first production deploy and a real Google sign-in were verified and recorded in `DEPLOYMENT.md` (commits `b738545`, `4241efb`).
- **Mocks:** the browser tests faked the account and check API answers; Python itself ran for real.
- **Deliberate-break controls:** none recorded.

---

## Chapter 1. A roadmap and a plan (2026-10-24)

**Sources:** commits `a293798`, `5466166`, `46e9559`, `7d3ed9f`; PR #6; handoff 01 section 2.

**What was written:**
- `build.md`, the roadmap, shared by the maintainer, ChatGPT and Claude.
- `docs/plan/course-catalog.md`, the catalog plan.
- The handoff system: one Markdown and PDF summary per stage, for chat assistants that cannot see the repository.

### Decisions and why

The maintainer's ten decisions, from `course-catalog.md` section 9, which records the alternatives considered and the consequence of each. Where no separate reason was written, the recorded consequence is given.

| # | Decision | Options considered | Reason or recorded consequence |
| --- | --- | --- | --- |
| 1 | One primary learner goal for the pilot | Primary plus secondary goals | Simpler recommendation rules; revisit after the pilot |
| 2 | Parents see a learner's goal and completed courses, not placement answers | Full visibility; no visibility | Reasoning not recorded; to be finalized with ID-01 before adult learners exist |
| 3 | Python unit 2 (numbers and decisions) next, after the groundwork | Unit 3 (loops) first | Unit 3 builds on unit 2's arithmetic and comparison |
| 4 | Units 2 and later are checked in the browser against test cases; the bounded checker stays for unit 1 | Extend the bounded interpreter; a hosted evaluation service | Practice-level evidence only, and no learner code on the server. Plan section 7.3 adds that `build.md` says not to grow the checker into a pretend Python, and that a hosted service needs its own isolation, network rules, quotas and cost review |
| 5 | The five existing lesson IDs stay forever, with no aliases | Add `py.hello`-style aliases | No migration of saved attempts' lesson IDs needed |
| 6 | XP: 100 per lesson challenge, 200 per unit project, 500 per course final project; stretch work earns a badge only | Other amounts; XP for stretch work | Pilot values, to be revisited with evidence |
| 7 | Regular expressions are a core Python unit, skippable through placement | An optional elective | The course covers CS50P-level breadth |
| 8 | Unreleased courses appear as "Coming soon" and cannot be started | Show only Python; hide unreleased courses | The catalog shows the whole plan without implying the content exists |
| 9 | Hackathon path: Python units 1 to 7, then Hackathon Ready, then branch | The full Python course first | Reasoning not recorded; consequence: a new course was added |
| 10 | A new course, Hackathon Ready (`hack`) | Teach hackathon skills inside the Git and web courses | Reasoning not recorded; noted as not yet in `build.md` section 5 |

Process decisions, which every later stage followed:
- **One branch and one PR per stage; never merge to `main` or deploy without the owner; stop for review.** Reason: merging `main` deploys to production (`build.md` section 14).
- **A handoff per stage, as Markdown and PDF.** Reason (PR #6): chat assistants "without repository access" need the evidence in one file.
- **Documentation-only commits are marked `[skip render]`,** so they do not redeploy the site.

### Bugs found and how they were fixed

None recorded. It was a documentation stage.

### How it was tested

Documentation only. CI ran the existing tests unchanged (PR #6).

---

## Chapter 2. Content as data (ENG-01)

**Sources:** handoff 01; PR #5; commits `bd592f4`, `4a86973`.

**What was built:**
- Every lesson moved from one hard-coded file into versioned **JSON** files: course, then unit, then lesson, then task.
- A **schema** that checks the content when the app starts.
- **Result states**, so a learner's mistake, a checker limit and a broken checker are told apart.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Validate all content when the API starts, and refuse to start if anything is wrong | Validate only in tests | A broken reference or a duplicate ID "stops the service instead of reaching learners" (handoff 01; `content.py`). Because every test imports the app, CI also fails on bad content |
| Five result states: `passed`, `needs_work`, `unsupported`, `service_error`, `execution_error` | One true/false `passed` value | `build.md` section 11 asks for result states rather than one Boolean, because "valid work this checker cannot judge" is not a learner mistake |
| `/api/lessons` must return exactly the same JSON as before | Changing the response | The interface was not changing yet, so the old answer was frozen as a **fixture** and compared byte for byte |
| On a checker crash, show "Unable to assess this right now. Your code is unchanged…", award nothing, and let the learner retry | Showing the HTTP 500 error, as before | Handoff 01, "Behaviour before and after" |

### Bugs found and how they were fixed

- **Near-miss: learner code could have reached the server log.** The first version logged a checker crash with `logging.exception`, whose message and traceback can repeat text from the learner's code.
  - How it was found: a chat reviewer asked "is learner code logged?" (handoff 01, review follow-up).
  - Fix: log only the lesson ID, the error type and the server code location (commit `4a86973`).
  - Guard: a new test captured `RuntimeError: checker bug near learner-private-story-text`. It fails on the old code and passes on the fix.

### How it was tested

| Kind of test | What it proves | Result |
| --- | --- | --- |
| Backend tests | The content schema, every validation rule (one failing-content test per rule), and the result states | 42 → 71 passed |
| Equality test against a frozen fixture | `/api/lessons` is byte-for-byte the same as before | Passed |
| Browser tests | The lessons still work in a real browser, plus a new test of what a learner sees on `service_error` | 14 → 15 passed |
| Real-stack run | Real backend and frontend together, not mocked: every example ran in real Pyodide, and the real check returned `passed` | Passed |
| CI (GitHub Actions) | The same tests on a clean machine | Passed |

- **Mocks:** the browser tests faked account and check answers; Python ran for real.
- **Deliberate-break control:** changing one character in a lesson file made both equality tests fail; then it was reverted.

---

## Chapter 3. Changing the database safely (ENG-02)

**Sources:** handoff 02; PR #7; commit `71b4b30`.

**What was built:**
- **Migrations**, so the database can change safely.
- Two **ledgers**, `xp_awards` and `badge_awards`, so XP and badges can never be awarded twice.
- A **backfill** that gave existing learners their earned awards.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Use **Alembic** migrations instead of `create_all` | Keep creating tables with `create_all` | Database changes become "safe and repeatable" (handoff 02) |
| Adopt the live database as migration `0001` without touching data, only if its tables match exactly; otherwise refuse and change nothing | Migrate whatever is there | Production tables existed before migrations. Refusing leaves Render running the old version instead of damaging data (handoff 02) |
| Migrations only **add** tables or columns | Changing or dropping columns | During a **zero-downtime deploy** the old version keeps running for a moment, so it must keep working with the new schema (handoff 02; tested) |
| A database **unique constraint** plus `INSERT … ON CONFLICT DO NOTHING` for awards | Checking in code before inserting | Retries or two simultaneous requests cannot award twice; only the database can guarantee that (handoff 02) |
| The backfill uses the same rule as `/api/progress` and adds nothing when run again (**idempotent**) | Other options not recorded | It can be safely re-run, which chapter 4 needed |
| A **PostgreSQL advisory lock** around migrations | Other options not recorded | "One deploy at a time may migrate" (`migrate.py`) |
| New dependencies: `alembic`, `Mako`, `MarkupSafe`, pinned exactly | — | Needed for migrations (PR #7) |

### Bugs found and how they were fixed

- **PostgreSQL could not tell whether an award was inserted.** With `ON CONFLICT DO NOTHING`, the PostgreSQL driver reports an unknown row count.
  - How it was found: running the tests on PostgreSQL as well as SQLite.
  - Fix: use `RETURNING` to see whether a row came back (handoff 02).
- **Near-miss: the deploy-overlap gap.** A pass saved by the old version during the few seconds both versions run would get no award, because the backfill had already run.
  - How it was found: reasoning about the deploy (handoff 02, "Known limitations").
  - Fix: migration `0004` in chapter 4 re-runs the backfill before anything reads the ledgers.

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| **Migration tests**, each run on SQLite and PostgreSQL | A fresh database matches the models; `0001` matches the original tables; old data survives adoption unchanged; the backfill is right and idempotent; unexpected tables are refused; downgrade then upgrade keeps data; a duplicate award is ignored |
| **Production rehearsal** | The real old code created data, the new code migrated it, and the old code still worked on the migrated database: exactly what happens during a deploy |
| Real-stack run on PostgreSQL | The log showed `migration 0003`, and all five lessons passed in Chromium |
| CI with a throwaway PostgreSQL 16 service | The PostgreSQL variants also run on every PR |

Results: backend 71 → 87 passed (with PostgreSQL); browser tests unchanged at 15.

- **Mocks:** the browser tests faked API answers.
- **Not verified then:** the first deploy against Render's production database. The owner confirmed it live afterwards (handoff 03).
- **Deliberate-break controls:** none recorded.

---

## Chapter 4. The course catalog interface

**Sources:** handoff 03; PR #8; commits `9eb3b2d`, `5150a63`.

**What was built:**
- Migration `0004`.
- A public `GET /api/catalog` and a student-only `GET /api/awards`.
- Pages: `/courses`, `/courses/<id>`, and `/learn/<lesson>` with a unit sidebar.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Backend first: the backfill re-run and the read endpoints, as a separate first commit | Doing it all at once | Asked for by the maintainer; it closed the chapter 3 gap before anything read the ledgers |
| Progress comes from the XP ledger, not from attempts | Keep counting attempts | One source of truth. It also fixed the parent view counting legacy arithmetic attempts as completed (handoff 03) |
| Coming-soon courses show what they build on but have **no start button** | Hiding them, or allowing a start | Decision 8 |
| Keep the lesson's one-card flow and add a sidebar that collapses into a menu below 1100px wide | Other options not recorded | So moving through lessons does not change how a lesson teaches (handoff 03, human goal) |

### Bugs found and how they were fixed

- **An accessibility bug from before this stage:** the preview banner was a nested `<aside>` **landmark**. Found by an automated **axe-core** check; changed to a note (handoff 03).
- **The parent's "quests completed" count** included legacy arithmetic attempts. It became consistent once it read from the ledger (handoff 03).

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| Backend tests | The catalog matches a frozen fixture; awards are student-only and correct; progress comes from the ledger; `0004` awards a pass saved by old code |
| Browser tests (15 → 19) | Coming-soon courses cannot be started; statuses are right; the sidebar works from the keyboard; the mobile menu fits 375px; reduced motion is respected |
| axe-core accessibility scan, 10 pages × desktop and phone | 0 violations of WCAG 2.0/2.1/2.2 A and AA after the fix |
| Real-stack run with seeded accounts | No page errors and no horizontal scroll |

- **Mocks:** browser tests used frozen fixtures for API answers; screenshots and axe used locally signed test sessions, not Google.
- **Not verified:** Safari and Firefox, or a real screen reader.
- **Deliberate-break controls:** none recorded.

---

## Chapter 5. Goals and recommendations

**Sources:** handoff 04; PR #9; commits `d62b925`, `29db57c`.

**What was built:**
- A goal card shown after a student enrols.
- A **deterministic**, rule-based "recommended next" function.
- Migration `0005` (the `learner_goals` table).

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| The recommendation is a **pure function** of goal, catalog and progress: no database, clock, randomness or AI | An AI or adaptive recommender | Handoff 04: "Rule-based, deterministic, explained, no paid AI". It can be tested exactly and always gives a reason |
| The goal only changes suggestions and never locks or hides a course | Goal-gated courses | Plan section 2. The card tells learners every course stays open |
| Skipping the card stores the default goal, marked as not chosen | Asking again later | Plan section 2 |
| Students choose goals; parents can only see them | Parents choosing | Decision 2 |
| Placement and "Not now" dismissals are supported by the function but not yet supplied | Building them now | Their inputs (the skills check, a dismiss button) did not exist yet |

### Bugs found and how they were fixed

- **A course with no units yet counted as "completed",** which hid it from coming-soon notes. Found while building; fixed and covered by tests (handoff 04).
- The "path finished" wording read awkwardly, and two layout details were off; both were fixed before review (handoff 04).

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| Recommendation unit tests (14), on test catalogs with placeholder lessons | The plan's worked examples, prerequisite walk-back, dismissals, a finished path, and determinism. Placeholders were needed because only unit 1 existed |
| **Property-based test**, 400 random situations | The recommendation is always a released, unfinished, not-placed-out and not-dismissed lesson |
| API tests | Only students set goals; bad goals get 422; history records changes; parents see the goal |
| Browser tests (19 → 24) | Enrol and skip; choose with arrow keys; change or cancel; caught-up state; parent view; phone layout |
| axe-core and a keyboard walk-through on the real stack | 0 violations; the keyboard path works |

- **Mocks:** the browser tests' recommendation mock imitates the backend for unit 1 only; the backend tests check the real rules.
- **Deliberate-break controls:** none recorded.

---

## Chapter 6. One ordered backlog and a threat model

**Sources:** handoff 05; PR #10; commits `a8a0181`, `6aef0b2`.

**What was written:**
- `docs/plan/backlog.md`.
- Two feature plans: testers and feedback with an admin inbox, and end-of-unit skill checks.
- `docs/plan/feedback-security.md`, a **threat model** for feedback.

### Decisions and why

The owner's answers, 2026-10-25, from `course-catalog.md` section 9 (alternatives and consequences as recorded there):

| # | Decision | Options considered | Reason or recorded consequence |
| --- | --- | --- | --- |
| 11 | The feedback button is for testers only (the admin also sees it) | Every signed-in learner; everyone | Fewer, more focused reports |
| 12 | Feedback is stored anonymously; sign-in only stops bots | Store the sender; fully anonymous with no sign-in | No replies to testers and no status view for them (`feedback-security.md` section 9) |
| 13 | Passing the unit check is required to complete a unit; retakes allowed | Optional checks | Changes what "unit complete" means; retakes need different variants |
| 16 | The unit project keeps its 200 XP; the unit check earns a skill badge and no XP | The check replaces the project; split the XP | The check is the "later, different variation" that a skill badge needs |
| 18 | Feedback deleted after 50 days at the latest; at most 90 items; the oldest resolved items are dropped first, otherwise the new item is rejected | Keep forever; block when full | A flood of unresolved items blocks new feedback until the admin resolves some |
| 19 | Parents never see feedback | Parents see their learner's feedback | Follows from decision 23 (closed in stage 6) |
| 21 | Check variants by a self-chosen learner level, never derived from a birthdate | Derive the level from age | The enrolment age gate is unchanged; a level setting is needed (ASSESS-06) |
| 22 | Learners who already finished unit 1 keep it; the new unit 1 check is optional for them | Require everyone to pass it | No learner loses progress |
| 23 | Testers are students only; parents never see the feedback button | Parents or any account as testers | The tester flag is offered only on student accounts |
| — | SEC-03 (real logout) moves to "Next" and must come before the admin inbox | Leave it for later | An admin session must be revocable (`feedback-security.md` section 1) |

**ID conflicts.** `build.md` and the owner's backlog used some IDs differently. Each of 12 conflicts was resolved in favour of `build.md` and listed (handoff 05). The reason was recorded: `build.md` defines the IDs, and the backlog orders the work.

### Bugs found and how they were fixed

- **Near-miss (design): anonymous feedback was not going to be anonymous.** The app records every important action with the user's ID and exact time in the account history. Writing feedback there would identify the sender. The plan now forbids it, with a required test (handoff 05).
- **Near-miss (design): a link field open to `javascript:` attacks.** The admin's "GitHub issue" field could hold a `javascript:` link. The plan restricts it to this repository's issue and PR links.
- **Near-miss (honesty): overstating anonymity.** Render's own request logs hold addresses and times, so the form must say "sent without your name or email", not "untraceable".

### How it was tested

Documentation only. Every relative link resolved; each backlog ID was checked against `build.md`; statements about current code were checked against `main.py`. CI ran unchanged.

---

## Chapter 7. Rate limits and security headers (SEC-01, SEC-04)

**Sources:** handoff 06 (sections 1 to 13); PRs #11 and #12; commits `6c1f5d3`, `a8ec019`.

**What was built:**
- Limits on how often each write endpoint and sign-in can be used, answered with **HTTP 429** and **Retry-After**.
- Security headers: **HSTS**, `nosniff`, `Referrer-Policy`, framing blocked, and a **Content-Security-Policy (CSP)** in **Report-Only** mode.
- A fix after the first live check failed.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Counters live in the API's **memory** | Counters in the database | Recorded in a comparison table (handoff 06 section 3). Memory needs no migration and no extra write per request, and is more private: nothing is written to disk. The costs: counters reset on each deploy, and it breaks with more than one API instance. "Move the counters to the database first" if the API is ever scaled |
| Counters store only a keyed **hash** (**HMAC**) of the user or address, a window start and a count | Storing the raw address or ID | Never store message text or learner code; a plain hash of an IPv4 address is easy to reverse |
| Signed-out limits looser than signed-in ones | Equal limits | A school or a family can share one address; 30 learners on one address were tested |
| Also limit enrolment, which was not on the list | Leave it unlimited | It is a write endpoint where invitation codes are typed in (handoff 06) |
| CSP first in Report-Only mode | Enforce straight away | Report-Only shows what would break without breaking anything |
| `frame-ancestors 'none'` enforced as its own policy | Inside the Report-Only policy | Browsers ignore `frame-ancestors` in Report-Only policies |
| `'unsafe-inline'` scripts allowed in the page policy for now | Script hashes; **nonces** | Next.js inline scripts change per page and per build, so hashes cannot list them. Nonces needed more work, which became SEC-09 (chapter 9) |
| **After the live failure:** trust exactly one configured source for the visitor's address (`CLIENT_IP_HEADER=cf-connecting-ip`); by default all signed-out visitors share one counter | "Rightmost public address" in `X-Forwarded-For`; trusted proxy hops | Nothing a caller sends can change the default. **Cloudflare** refuses any request that tries to set `CF-Connecting-IP` (verified live: 403, `error code: 1000`) |

### Bugs found and how they were fixed

- **Live bug: a made-up `X-Forwarded-For` header bypassed the limit.**
  - How it was found: the owner's live check. 61 requests, each with a different made-up `X-Forwarded-For`, all returned 200.
  - Investigation, "do not guess": a temporary diagnostic, off by default, logged only counts, header names and a short keyed hash. Next.js's proxy was checked by running it: it passes `X-Forwarded-For` through unchanged and adds none.
  - Fix (PR #12): use only a configured trusted source. A test reproduces the bypass: it fails on the old code and passes on the fix.
  - Re-check: the same loop gave 59 × 200 and 2 × 429.
  - **Lesson:** a header the caller can send is not evidence of who the caller is.
- **Near-miss: documentation addresses.** Address ranges such as 198.51.100.0/24 are not "public", so the old "rightmost public" rule skipped them and could fall back to a caller-made value.
- **Findings while building** (handoff 06):
  - Next.js applies the last matching header rule, so the worker's rule had to be listed last.
  - Next.js does not add its own headers to proxied API responses, so the API sets HSTS itself.
- **(Implementer's session notes)** Fixed while writing tests:
  - a CSP probe used `127.0.0.1` against an origin of `localhost` and got 403
  - test addresses in documentation ranges are not "global", so the tests switched to other addresses
  - Chromium's Local Network Access blocked the framing test, so it moved to a same-origin page
  - `getByRole('alert')` also matched Next.js's route announcer, so the locator was made specific

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| Backend tests (23, then 31 for the fix) | Every limit trips at the right request; normal use and a classroom stay under; 429 has `Retry-After`; counters and logs hold no code, ID or address; memory stays bounded; every write route has a limit (a test fails if a new one does not) |
| Spoof tests | Made-up forwarding headers do not change the counter in any mode |
| Browser tests | Python still runs with the headers on; the app refuses to be framed; a 429 shows its message and keeps the learner's code; **any CSP report fails any test** |
| Enforce-mode rehearsal | The proposed enforced policy passed all 27 browser tests locally |
| Live checks | Spoof loops, `Retry-After`, separate counters for a phone and a Mac, headers (owner, 2026-10-25) |

- **Deliberate-break controls:**
  - A stricter `script-src 'self'` made the header test fail with `script-src-elem blocked inline`, proving the CSP listener works.
  - The new spoof test, run against the old `limits.py`, failed: it reproduces the production bypass.
- **Mocks:** browser tests mocked the API; the 429 test used a mocked 429; the real 429 was checked against the local API.

---

## Chapter 8. Logout that really logs out (SEC-03)

**Sources:** handoff 07; PR #13; commit `ffaffa4`.

**What was built:**
- **Server-side sessions**: the cookie holds only a random session ID, and the `sessions` table (migration `0006`) holds the session.
- Logout deletes the row.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Store a SHA-256 digest of the session ID, not the ID | Storing the ID | A copy of the table or a backup cannot be turned into a working cookie (tested) |
| Idle timeout 24 hours | Shorter, for example 2 hours | It matches the old cookie's behaviour, so learners are not signed out more often; a shared family computer's cookie dies by the next day |
| Absolute lifetime 7 days | No limit (the old behaviour) | Stops a copied cookie being kept alive forever; re-signing in with Google once a week is quick |
| Signing in deletes this browser's previous session and makes a new ID | Keeping the old ID | Prevents **session fixation** |
| Old cookies (holding a user ID) are refused and emptied, signing everyone out once | Accepting both kinds | Simpler and safer; a rollback cannot bring old cookies back |
| `last_seen` written at most every 5 minutes | Writing on every request | Most requests only read the database |
| Cleanup at each sign-in, no scheduled job | A scheduled cleanup job | Keeps the table small without new infrastructure |

### Bugs found and how they were fixed

- **Found while building: stolen cookies never expired.** Starlette re-signs the cookie on every response, so the old 24-hour limit restarted with each use. A copied cookie worked after logout, and for as long as it was used at least once a day (handoff 07 section 4).
- **Near-miss: old cookies kept alive by the new code.** The new code would have kept re-sending old cookies (with the user ID) for up to 7 days, and a rollback would have accepted them again. Fix: the new code drops that key (handoff 07 section 5; tested).

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| Session tests (43) | Logout ends the old cookie; other devices stay signed in; 7-day and 24-hour expiry (with a **fake clock**); 7 kinds of forged or tampered cookie are refused; a deleted user's sessions stop working |
| A route-list test | Every route must be listed as public or authenticated; authenticated ones must refuse requests without a live session, so a new route that skips the check fails |
| Migration test on SQLite and PostgreSQL | Deleting a user deletes their sessions (cascade) |
| Local server on PostgreSQL with `curl` | A copied cookie returned 200 before logout and 401 after; nothing logged |

- **Deliberate-break controls:**
  - A new route with no session check failed the route-list test, then the 401 test.
  - Logout that only empties the cookie failed both logout tests.
  - Removing expiry and the deleted-user check failed 14 tests.
- **Mocks:** Google's answer was replaced in tests; the callback route, the session and the cookie were real.

---

## Chapter 9. A Content-Security-Policy with nonces (SEC-09)

**Sources:** handoff 08; PR #14; commit `f3babeb`.

**What was built:**
- A Next.js **proxy** makes a new random nonce for every page request, so only scripts the server added can run.
- It ships in Report-Only mode, next to the previous policy.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Nonces | Keep `'unsafe-inline'`; hash-based Subresource Integrity (experimental) | Nonces are the approach Next.js documents. SRI is experimental and does not cover Next.js's changing inline data |
| No `'strict-dynamic'` | Adding it, as Next.js's guide does | It makes browsers ignore `'self'` and trust any script a trusted script inserts; same-origin files are already allowed by `'self'` |
| Every page renders per request (`connection()` in the layout) | Keep some pages static | A static page is written at build time, when there is no nonce. The control: leaving pages static failed 26 tests |
| Both policies in one Report-Only header | Sending them from `next.config.mjs` and the proxy | In Next.js, the proxy's header **replaces** a `next.config` header with the same name |
| One-line switch to enforce: `const ENFORCE = true` | Editing several lines | It makes the switch hard to get wrong |
| `next dev` always stays Report-Only | Adding `'unsafe-eval'` in development | The development server injects inline styles and uses `eval`. **(Implementer's session notes)** `'unsafe-eval'` was tried first and dropped, because inline styles would still break |

**Cost** (measured locally): about 0.5 ms more CPU per page and about 380 bytes more per page. **Cloudflare** was not caching pages anyway (`cf-cache-status: DYNAMIC`). No extra money on Render's flat-price plan; memory is the thing to watch.

### Bugs found and how they were fixed

- **Next.js's built-in 404 page breaks `style-src 'self'`.** It uses inline styles with no nonce, under both the old and new policy. Handoff 06 never visited a missing page. Found by counting style tags per page; fixed with a custom 404 page (handoff 08 section 4).
- **The Report-Only header replacement** described above was found by inspecting real response headers.

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| Browser tests (27 → 30) | Every request gets a new nonce and every script carries it; every page as visitor, student and parent has zero reports; an injected script with no nonce or a guessed nonce is reported, and blocked when enforced, while the real nonce runs |
| Enforce-mode rehearsal | All 30 tests pass with `ENFORCE = true`; with the real API (no mocks), Python ran, the check passed and the badge showed, with 0 violations |
| A simple load measurement | The per-page cost above |

- **Deliberate-break controls:** no nonce in the policy failed 29 tests; the same nonce on every request failed 2; pages left static failed 26.
- **Mocks:** browser tests mock the API; the injection test alters the page HTML to stand in for a real injection.

---

## Chapter 10. How we teach, and how feedback should work

**Sources:** handoff 09; PR #15; commit `a2b7d84`.

**What was written:**
- `teaching-design.md`, `lesson-feedback.md` and `ai-helper.md`.
- An investigation into why `print("hi")` then `print("woah")` passed the first unit 1 challenge.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Ground the teaching design in published research (worked examples, **PRIMM**, **Parsons problems**, spaced practice), and say where the evidence is **mixed** | A plain list of features | So reviewers can check the claims; rewritten error messages have mixed evidence, so they are measured rather than assumed |
| Do not try to detect "a location" or "a surprise" automatically | Keyword lists, word minimums | They would reject valid creative answers and accept nonsense. The meaning is the learner's call, so it becomes a self-check question |
| The AI helper is **deferred** and off by default; no grading; server-side key; caps and a hard spending limit | Build it now | Cost (the owner's free-first rule), the provider's age terms for 13 to 17 year olds, and consent must be decided first |
| A new "Working with AI" course, with a no-cost path | Paid tools required | The owner's free-first rule; many AI services set minimum ages above 13 |
| No stage row added to the backlog | Adding it | Avoids a merge conflict with an open PR |

### Bugs found and how they were fixed

- **The `hello` check claimed what it did not check.** It accepted any two non-empty lines, including the same line twice, numbers, and the worked example copied. Yet it told everyone "Your scene has a setting and a surprise". It was found by reading the checker and running it on real cases (read-only); it was fixed in chapter 11.
- **Hints gave away answers.** `hello` hint 3, and `input` hints 1 and 2 together, were complete passing answers.
- **An overclaim in this stage's own documents.** It said `variables` hints 1 and 3 were a passing answer; they only passed once the learner typed their own values. Found by the hint audit in chapter 11, and corrected there.

### How it was tested

- Documentation only: the full test suites ran unchanged, and every link resolved.
- The investigation called the real checker function directly, with no mocks.
- The quoted Python error messages were captured with local Python 3.12, not Pyodide (stated as a limitation).

---

## Chapter 11. Honest checks (ASSESS-07)

**Sources:** handoff 10; PR #16; commit `1b600bf`.

**What was built:**
- All five unit 1 success messages now say only what was checked, plus a question for the learner.
- A stricter `hello` check.
- Rewritten hints, and a hint audit test.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| `hello` requires two **different** lines with **letters**, not the worked example or a hint copied unchanged; **no word minimum** | A minimum word count; keyword detection | Each rule matches the card's wording; a word minimum would reject "Mars." / "Boom!" (decision 5 in `lesson-feedback.md`) |
| `print("hi")` then `print("woah")` still passes, on purpose | Rejecting it | Both are different text with letters. The check now says honestly what it verified |
| The old hint 3 is refused by name | Allow it now that it is no longer shown | Learners were given it as an answer |
| Hints use other variable names (`friend`, `pet`) | Partial hints with blanks only | They teach the pattern without writing the learner's line |
| Bump lessons, challenges and the validator to version 2; keep XP, badges and IDs | Changing XP or IDs | The content format requires a version bump for a check fix, and awards are keyed by task ID, so earlier completions stay valid |

### Bugs found and how they were fixed

- The two issues from chapter 10 were fixed.
- **Near-miss:** many existing tests used `hello`'s worked example as a "passing answer". Making the check honest broke them on purpose. Each was given its own trusted answer instead, which `build.md` section 4 asks for anyway.
- **(Implementer's session notes)** A new test first required the success message to end with "?". The agreed `hello` wording ends with "That part is your call.", so the test was loosened to require a question anywhere in the message.

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| Appendix A cases (7) | Each investigated case gets its exact result and message |
| Old passing answers that should now fail (10), and valid answers that must still pass (5) | The new rules are neither too loose nor too strict |
| **Hint audit** | Every program a learner could build from the starter and hints alone is run through the real checker, and none may pass |
| Version and award tests | A learner with a version 1 award keeps progress, XP and badge; passing again adds nothing |
| Real-API browser probe | In a real browser, `hi`/`woah` passes and the copied example is refused |

- **Deliberate-break control:** the hint audit, fed the **old** `input` hints, finds a passing program, so the audit can catch a giveaway.
- **Mocks:** none in the new tests.

---

## Chapter 12. Checking code in the browser (ENG-03)

**Sources:** handoff 11 (on PR #17's branch, `eng/browser-checks`, which was still open when this log was written); PR #17 description.

**What was built:**
- A contract for lessons in unit 2 and later:
  - content declares test cases
  - the Pyodide worker runs them
  - a page-side runner enforces a time limit
  - the API compares the reported output and never runs the code
- A test fixture lesson kept outside the course content.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| A hidden case's **expected output never leaves the server**; its **inputs do reach the browser** | Keeping inputs secret too (only possible with a hosted runner) | The code runs in the learner's browser, which cannot run a case without its inputs. Knowing an input does not give away the answer (handoff 11 section 4) |
| The API decides the result, not the worker | The worker returning result states, as first asked | The worker cannot judge hidden cases without their answers; one judge also keeps preview and saved attempts identical |
| Required and forbidden constructs are per challenge and checked by **parsing** | Per test case; checked by running | They describe the program, not one run; parsing never executes code |
| The time limit is enforced by the page **terminating the worker** | The worker timing itself | A loop that never ends blocks the worker, so it cannot stop itself |
| No network for learner code: network APIs removed after Pyodide loads, on top of the worker's existing CSP | CSP only | Defence in depth |
| Practice-level evidence, not tamper-proof | A hosted runner | Cost and isolation; the same trust level as unit 1 |

### Bugs found and how they were fixed

**(Implementer's session notes:** both were found by the new Playwright tests, but handoff 11 did not record them.)

- **The wrong line for missing replies.** An `EOFError` reported line 9 instead of line 3, because the helper code that feeds replies to `input()` also ran under the name `<exec>`. Fix: run the helper under its own file name, `<academy>`.
- **A last line with no newline was lost.** Pyodide's "batched" output only delivers complete lines, so output from `print(…, end="")` disappeared, even after a flush. Fix: use Pyodide's raw `write` output handler.

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| Schema tests (14 invalid kinds) | Bad checks stop content loading, including a hidden description that shows its inputs or answer |
| Judge tests | Pass, wrong output (with the first different line), timeout, output cap, errors with type and line, constructs, `service_error` |
| Leak test | Across more than 30 responses, the hidden expected output never appears, and hidden inputs appear only in the check plan |
| "Never runs code" test | Code that would write a file is judged, and no file appears |
| Browser tests with real Pyodide (9) | A correct solution passes; a loop is stopped; output is capped; no network; error type and line; fresh variables per case |
| Full chain with no mocks | A solution that hard-codes the visible answers is caught only by the hidden case |
| Merge rehearsal with the other open PR | The two merge cleanly, and 255 backend tests pass on the result |

- **Deliberate-break controls:** a plan with hidden expected output, a message that reveals it, no hidden-description check, and a judge that ignores timeouts. Each failed the right tests.
- **Mocks:** backend judge tests post hand-written browser reports; browser tests build the plan from the fixture rather than calling the API.

---

## Chapter 13. Patterns that kept coming back

These ideas appear in several chapters. They are good candidates for chapters of their own in the book.

| Pattern | Where | In one sentence |
| --- | --- | --- |
| Never run learner code on the server | 0, 2, 12 | Parse it or run it in the learner's own browser; the server only compares results |
| Freeze what must not change | 2, 4, 11 | Save today's exact output as a fixture, and fail the test if it changes by accident |
| Additive changes during deploys | 3, 8 | Old and new versions overlap for a moment, so both must work with the new database |
| Make retries harmless | 3, 4 | Unique keys and idempotent backfills mean running something twice changes nothing |
| Report first, enforce later | 7, 9 | Turn on a security policy in Report-Only mode, watch, then enforce with a one-line switch |
| Do not trust what the caller sends | 7, 8, 12 | Headers, cookies and browser reports can be made up; trust only what the server or edge controls |
| Prove the tests can fail | 2, 7, 8, 9, 11, 12 | Break the code on purpose and watch the tests catch it |
| Say only what was checked | 10, 11 | Feedback and handoffs claim only what the evidence supports, and say what was not verified |
| Do not guess; measure | 7, 9 | When the live check failed, a diagnostic and a real run found the cause; costs were measured |
| Privacy by default | 2, 6, 7, 8 | Logs and counters never hold learner code, message text, emails or user IDs |

---

## Chapter 14. Feedback a beginner can act on (ENG-04, part 1)

**Sources:** handoff 15 (branch `feat/lesson-feedback`, still open when this chapter was written); `docs/plan/lesson-feedback.md`.

**What was built:**
- Friendly explanations for the 19 Python errors in the specification, with Python's own message one click away.
- The failing line highlighted in the editor, with a marker, the words "Line N" and a "Go to line" button.
- Results labelled by their state in words, and hints as a three-step ladder beside the code.

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| `print("hi")` then `print("woah")` **still passes**; the test checks the pass is honest | Adding a word minimum so it fails, as the task first asked | The owner chose to keep decision 5 (no word minimum) when asked on 2026-10-27. A word minimum would also reject valid short stories |
| Build sections 4, 5 and 7 now; check rules, tagged hints and predict-first later | One large pull request with all five parts | The other parts need content changes (rule and hint IDs) that should be reviewed on their own |
| A gutter and highlight layer behind the plain textarea | An editor library such as CodeMirror | No new dependency, as the specification proposes (section 11, decision 1) |
| Lines in the editor do not wrap | Wrapping, as before | With wrapping, line N of the code is not row N of the gutter, so the highlight would land on the wrong row |
| The page treats only `result: "passed"` as a pass | Trusting `passed: true` | One source of truth; an unknown state is shown as "Check unavailable" |
| Number errors (unit 2) get the general message in unit 1 | Always using every translation | The specification says not to teach ahead of the unit |
| Python's own suggestion is used only for built-ins learners have met | Always repeating Python's suggestion | Python suggests `help` for `hello`, which no learner has met |

### Bugs found and how they were fixed

- **The output limit looked like a disk error.** In unit 1 mode, a program that printed too much stopped with `OSError: [Errno 29] I/O error`, so no message could recognise it. Found while capturing real Pyodide errors for the tests. Fix: the worker now says why it stopped (`outputLimit`); a test guards it.
- **The wrong line for missing replies, in unit 1 mode.** ENG-03 had fixed this for check cases only: the reply helper also ran as `<exec>`, so a missing reply pointed inside our own helper. Found while reading the worker. Fix: the helper runs as `<academy>` in both modes; the `replies` translation test guards it.
- **Output before an error was hidden.** The output panel showed Python's message instead of what had already printed. Found while building. Fix: the output stays, and the explanation appears below it.
- **Keyboard focus was lost after the last hint.** The hint button disappeared, or was disabled, while it had focus. Found in review of the change. Fix: the button stays, marked `aria-disabled`; a browser test checks focus stays on it.
- **Near-miss while testing:** a local server left running from the screenshots made the test runner stop before running any test. The filtered output showed no results at all, which was checked rather than read as a pass.

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| Unit tests on 22 real Pyodide error samples | Each of the 19 translations, the line (inside a function, syntax errors, missing replies) and Python's cleaned message |
| Fixture check against the live worker | The saved error text still matches what the worker reports, so the unit tests use real text |
| Snapshot of every message template | Any change to a message is visible in review; code in a message is one line at most |
| Browser tests with real Pyodide | The highlight is on the right line, "Go to line" moves the cursor, the hint ladder goes in order, nothing looks like a pass unless the check said so, and it fits a phone |
| API test | The `hi`/`woah` answer used by the browser test is the real API answer |
| axe-core scan, 6 states × desktop and phone | 0 accessibility violations |

- **Deliberate-break controls:** reading the first traceback frame instead of the last (2 tests failed), ignoring the unit of a translation (1), trusting `passed: true` over the state (1), and moving the highlight one line down (6). Each was undone.
- **Mocks:** the browser tests mock the API answers; the worker and Python are real.

---

## Chapter 15. Feedback nobody can trace (FB-02)

**Sources:** handoff 17 (branch `feat/feedback-storage`, still open when this chapter was written); `docs/plan/feedback-security.md`.

**What was built:** the server side of tester feedback:
- a table with nothing that identifies the sender
- one route that only testers and the admin can use
- rate limits, length limits and fixed categories
- deletion after 50 days, and a 90-item cap that never silently drops unresolved items

### Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Rate limits use the existing in-memory counters | A database counter table (`feedback-security.md` section 7) | The owner asked for the existing `limits.py` approach. The counters hold only keyed hashes, and nothing is stored next to the message. They reset on redeploy; the 90-item cap still bounds the damage |
| Store the **date** an item was sent, not the time | A timestamp | A time could be matched to a sign-in or a request log, which would undo the anonymity |
| A full inbox with nothing resolved answers **409** and keeps everything | Deleting the oldest item anyway | Decision 18: unresolved feedback is never dropped silently |
| Retention runs when feedback is sent and at most once an hour on any request | A scheduled job | Render has no free scheduler for this; the hourly check needs no new service |
| Sending feedback writes **no** account-history event | An event, like other actions | An event holds the user ID and an exact time |

### Bugs found and how they were fixed

- **A helper was collected as a test.** pytest runs any function whose name starts with "test", and a helper called `tester()` returned a value, which pytest warned about. Found from the warning; renamed.
- **Near-miss in the tests:** a refused request still counts towards the daily limit, as with every limit in `limits.py`. The first daily-limit test assumed it did not. The test now states the rule.

### How it was tested

| Kind of test | What it proves |
| --- | --- |
| API tests for each role | Signed out 401; pending, parent, non-tester student and a parent with the tester flag 403; tester and admin 200 |
| Anonymity test | The stored row and the responses hold no user ID, email, IP address or session ID; no event is added |
| Retention with a fake clock | An item is kept on day 49 and gone on day 50 |
| Cap tests | The oldest resolved item goes first; an inbox full of unresolved items refuses the new one |
| Log test | No message, code, email or user ID in any log line |
| Migration test, SQLite and PostgreSQL | 0008 adds the table and removes it on downgrade, leaving accounts untouched |
| Local run with the real API | Migration 0008 in the log; 401, 403, 200 and 429 from the real routes |

- **Deliberate-break controls:** recording the sender in the account history, writing the sender's email into the row, removing the tester check, deleting unresolved items to make room, deleting one day late, storing code without opting in, and logging the message. Every one failed at least one test.

---

## Glossary

Plain-language meanings, in alphabetical order, with the chapter where each first matters.

| Term | Meaning | Chapter |
| --- | --- | --- |
| Abstract syntax tree (AST) | The structure Python builds when it reads code: statements, expressions, names. Reading it tells you what code *says* without running it | 0 |
| Accessibility (axe-core, WCAG) | Making the app usable for everyone, including with a keyboard or screen reader. WCAG is the standard; axe-core is a tool that checks pages against it automatically | 4 |
| Advisory lock | A lock in PostgreSQL that programs agree to respect, so only one deploy migrates at a time | 3 |
| Alembic | A Python tool for writing and running database migrations | 3 |
| API, endpoint | The backend's interface. Each endpoint is one URL and method, such as `GET /api/catalog` | 0 |
| Backfill | Filling a new table from data that already exists, such as awards from earlier passes | 3 |
| Branch, commit, pull request (PR), merge | Git basics: a commit saves a change; a branch is a line of work; a PR asks for review; merging adds it to `main` (which deploys here) | 1 |
| Cascade delete | When a row is deleted, the database also deletes the rows that point to it | 8 |
| CDN | A content delivery network: servers around the world that serve files quickly. Pyodide loads from one | 0 |
| CI (GitHub Actions) | Continuous integration: every PR runs all the tests on a clean machine | 2 |
| Cloudflare | The network service in front of Render that receives every request first | 7 |
| Content-Security-Policy (CSP) | A response header telling the browser which scripts, styles and connections a page may use; it limits damage from injected code | 7 |
| Cookie (signed, HttpOnly, Secure, SameSite) | A small value the browser sends back on each request. Signed: tampering is detectable. HttpOnly: page scripts cannot read it. Secure: sent only over HTTPS. SameSite: not sent on most cross-site requests | 8 |
| CSRF | Cross-site request forgery: another website making your browser send a request. Blocked here by checking the `Origin` header | 6 |
| Deterministic | The same inputs always give the same output | 5 |
| Deliberate-break control | Breaking the code on purpose to prove a test can catch that mistake, then putting it back | 2 |
| Fixture | Saved test data, for example the exact JSON an endpoint must keep returning | 2 |
| frame-ancestors, clickjacking | A CSP rule saying who may show the page inside a frame. Blocking framing stops clickjacking, where a page is hidden under another to trick clicks | 7 |
| Hash, HMAC | A hash turns data into a fixed-length fingerprint that cannot easily be reversed; an HMAC is a hash mixed with a secret key, so others cannot recompute it | 7 |
| Hidden test case | A test whose expected output the learner never sees, so hard-coding the visible answers fails | 12 |
| HSTS | A header telling browsers to use HTTPS only for this site | 7 |
| HTTP 429, Retry-After | "Too many requests", and how many seconds to wait | 7 |
| Idempotent | Doing it twice has the same effect as once | 3 |
| Idle timeout, absolute lifetime | A session ends after a period without use, or after a fixed time however much it is used | 8 |
| JSON | A text format for structured data, used for the content files and API answers | 2 |
| Landmark (ARIA) | Page regions (header, main, navigation) that screen readers can jump between | 4 |
| Ledger | An append-only list of records, such as XP awards; totals are the sum of rows | 3 |
| Live check | A person checking the deployed site after a merge | 0 |
| Migration | A numbered script that changes the database's structure, run in order | 3 |
| Mock | A stand-in for something real, such as a fake API answer in a browser test; fast and repeatable, but it proves nothing about the real thing | 0 |
| Next.js, React, TypeScript | The frontend: React builds the interface from components; Next.js serves the pages; TypeScript is JavaScript with types | 0 |
| FastAPI, Pydantic | The backend framework (Python), and the library that checks data against a schema | 0 |
| Nonce | A random value made fresh for each page; only scripts carrying it may run | 9 |
| ON CONFLICT DO NOTHING, RETURNING | SQL that skips an insert that would break a unique key, and returns the inserted row so the code knows whether it happened | 3 |
| Parsing | Reading code into an AST without running it | 12 |
| Parsons problem | Putting given lines of code in the right order | 10 |
| PostgreSQL, SQLite | Two databases: PostgreSQL in production and CI, SQLite for quick local tests | 0 |
| PRIMM | Predict, Run, Investigate, Modify, Make: a way to structure programming lessons | 10 |
| Property-based test | A test that checks a rule over many random inputs instead of a few chosen ones | 5 |
| Proxy (Next.js) | Code that runs before each page request; here it creates the nonce | 9 |
| Pure function | A function whose result depends only on its inputs, with no side effects | 5 |
| Pyodide, web worker | Python compiled to run in the browser; a worker runs it in the background so the page stays responsive | 0 |
| Rate limit, fixed window | A cap on requests per time window, such as 20 checks a minute; the counter resets when the window ends | 7 |
| Render | The hosting service that runs the app | 0 |
| Report-Only | A CSP mode where the browser reports what it *would* block but blocks nothing | 7 |
| Result states | `passed`, `needs_work`, `execution_error`, `unsupported`, `service_error`: telling a learner mistake from a checker limit or a broken service | 2 |
| Schema | The agreed shape of data, checked automatically | 2 |
| Server-side session | The server keeps the session record, so it can end it; the cookie holds only an ID | 8 |
| Session fixation | An attack where someone plants a session ID before you sign in and then uses it after | 8 |
| Spoofing | Sending made-up values, such as a fake `X-Forwarded-For` header | 7 |
| Static and dynamic rendering | Static pages are built once and reused; dynamic pages are built for each request | 9 |
| Threat model | A list of what could go wrong, who might cause it, and the controls against each | 6 |
| Transaction | A group of database changes that all happen or none do | 3 |
| Unique constraint | A database rule that no two rows may have the same value in some columns | 3 |
| Unit test, API test, browser test (Playwright) | Testing one function; sending real requests to the backend; driving a real browser | 0 |
| X-Forwarded-For, CF-Connecting-IP | Headers that say which address a request came from. The first can be set by anyone; the second is set by Cloudflare and cannot be sent by a caller | 7 |
| Zero-downtime deploy | The new version starts before the old one stops, so for a moment both run | 3 |

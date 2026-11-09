# Engineering book and course outline (proposed)

Last updated: 2026-11-09 (America/Toronto)  
Status: **proposed** (backlog DOC-02, handoff 14; expanded for DOC-03, handoff 50). An outline only; nothing is written beyond [`decision-log.md`](decision-log.md), which is the raw material.  
Related: [`decision-log.md`](decision-log.md); [`teaching-design.md`](teaching-design.md), whose methods (worked examples, predict-then-run, fix-the-bug, gradually removing support) the course below uses; [`build.md`](../../build.md) section 15 ("Learn while building the platform").

Two products from one source:

1. **The book:** a long PDF, *How Python Academy Was Built*. It tells the real story of building a learning platform in small, reviewed steps with AI assistants: every decision, bug and test, for a first-year computer engineering student.
2. **The course:** *How This App Was Built*, a lecture-and-problem-set course in the style of Harvard's CS50 (lectures, sections, weekly problem sets, a final project). It uses this app as the case study throughout. "CS50-style" describes the format only; the course is not affiliated with Harvard or CS50.

## 1. Principles for both

- **True to the record.** Every claim traces to `decision-log.md`, a handoff, a pull request or a commit. Where the log says "reasoning not recorded", the book says so too. It may then discuss what the reasons *could* have been, clearly labelled as discussion.
- **Real code at real commits.** Examples quote the repository at a named commit, so readers can check out that exact version and run it.
- **Mistakes are the best material.** Each bug and near-miss becomes a worked example: what happened, how it was found, the fix, and the test that now guards it.
- **Plain language first, precise terms second.** Each new term is explained when it first appears and collected in the glossary (from `decision-log.md`).
- **No secrets, no personal data.** Screenshots use test accounts; no real emails, keys or learner work.
- **Free tools only.** Every exercise runs locally with free tools, as the project itself does.

## 2. Book outline

Each chapter has the same parts:
- **The problem:** what a user or the owner needed.
- **Choices:** the options and the decision.
- **Build:** the key code, explained.
- **What broke:** bugs and near-misses.
- **Evidence:** how it was tested, including mocks and controls.
- **Questions to think about**, ending with "what would you do differently?"

| Part | Chapter | Built from (decision-log chapters) | Main ideas |
| --- | --- | --- | --- |
| **I. Starting out** | 1. A learning app in one weekend | 0 | Frontend, backend, database, hosting; sign-in with Google; running Python in the browser |
| | 2. Plans, roadmaps and working with AI assistants | 1 | One branch per step, handoffs, reviews, "never merge without the owner"; the maintainer's decisions |
| **II. Data you can trust** | 3. Content as data | 2 | Schemas, validation at start-up, frozen fixtures, result states; the logging near-miss |
| | 4. Changing a live database without losing anyone | 3 | Migrations, adopting a legacy database, transactions, additive changes, the deploy-overlap gap |
| | 5. Never award twice | 3, 4 | Unique keys, `ON CONFLICT`, idempotent backfills, a PostgreSQL-only bug |
| **III. Interfaces people can use** | 6. A catalog that does not mislead | 4 | Coming-soon rules, progress from one source of truth, accessibility checks, keyboard and mobile |
| | 7. Recommending without AI | 5 | Pure functions, deterministic rules, explanations, property-based tests |
| **IV. Planning for people you cannot see** | 8. Backlogs, decisions and threat models | 6 | Ordering work, resolving ID conflicts, designing anonymity honestly |
| **V. Security in practice** | 9. Rate limits, and the header that lied | 7 | Fixed windows, hashing for privacy, memory or database; the live spoofing failure and "do not guess" |
| | 10. Logout that really logs out | 8 | Cookies, server-side sessions, session fixation, timeouts, route-list tests |
| | 11. Content-Security-Policy, from report to enforce | 7, 9 | Report-Only, nonces, static or dynamic rendering, measuring cost |
| **VI. Teaching honestly** | 12. How people learn to program | 10 | Worked examples, PRIMM, Parsons problems, spaced practice; mixed evidence |
| | 13. Checks that say only what they checked | 10, 11 | The `print("hi")` investigation, giveaway hints, hint audits, versioning content |
| | 14. Running untrusted code safely in a browser | 12 | Workers, time limits by termination, output caps, no network, hidden cases and their limits |
| | 15. Feedback a beginner can act on | 14, 16 | Real error messages turned into plain words, the right line, tagged hints, similar examples that must not pass |
| | 16. Writing lessons that check honestly | 19, 21, 22 | Hidden cases, hint audits that run code, "unit complete" only when it is, loops that always finish |
| **VII. Privacy and trust** | 17. Feedback nobody can trace | 15 | Anonymity by design, not by promise: what is not stored, limits that don't identify, retention |
| | 18. A page that trusts the server | 17 | Showing nothing to a refused visitor, the server as the only judge, a switch that waits for the answer |
| | 19. Who may sign up | 20 | Planning accounts for people you can't see: age, parents, independent learners, a switch and a cap |
| **VIII. Growing the checker** | 20. One unit at a time | 18 | Changing an API without breaking the old page, fallbacks, recordings that must match exactly |
| | 21. Imports, files and the learner's own modules | Master run (handoffs 34, 35, 43) | A guide is not a sandbox; state that leaks between cases; a file named `datetime.py` that got past the guard |
| | 22. Tests that call functions, and tests the learner writes | Master run (handoffs 29, 40, 41) | Calling a learner's function safely; hidden arguments; correct and broken reference programs |
| **IX. Supply chain and operations** | 23. Trusting what you download | Master run (handoffs 37, 39, 44) | Pinning CI actions to commits, Dependabot, checking a CDN's files against hashes from a second source |
| | 24. Secrets in addresses, counters in databases | Master run (handoffs 45, 46) | Why `#` keeps a token out of logs; atomic counters shared between instances; keeping feedback anonymous anyway |
| | 25. Accessibility you can test, and what you can't | Master run (handoffs 42, 47) | Keyboard-only tests that found a real trap, axe and its limits, other browsers, the screen reader sheet |
| **X. Evidence** | 26. How we knew it worked | All | Unit, API, browser and live tests; mocks and their limits; deliberate-break controls; CI; trial merges |
| | 27. Patterns, and what we would do differently | 13, and the master run | The recurring patterns as reusable rules; open questions and future work |
| **Appendices** | A. Glossary · B. Timeline of commits and PRs · C. How to run the project at any commit · D. The handoff template and why each section exists | — | — |

### 2.1 The new chapters in more detail (DOC-03)

Each is built from the decision log and handoffs named, and each "what broke" is a real bug from them. Section and exercise ideas only; nothing is written. **Handoffs 44 to 49 are on pull requests still open on 2026-11-09** (#52 to #57); a chapter built on them waits until they are merged and the decision log has them.

| Chapter | What the reader builds or reads | What broke (the worked example) | Exercise |
| --- | --- | --- | --- |
| 15. Feedback a beginner can act on | Turning a Python error into plain words and a line number | The output limit showed as `OSError: [Errno 29] I/O error`; a missing reply pointed inside the academy's own helper; a similar example that filled the starter into a passing program | Write the explanation for one error type, with a test that reads the last traceback frame, not the first |
| 16. Writing lessons that check honestly | A lesson with visible and hidden cases, and a hint audit | "Unit complete" after three of six lessons; advice that suggested `str(...)` and made `10 + 3` print `103`; a sample meant to loop for ever that passed | Find a hint that, combined with the starter, passes the check |
| 17. Feedback nobody can trace | A table that can't identify its sender | A first test assumed refused requests don't count toward a limit | List every place a sender could be linked to a message, and close each |
| 18. A page that trusts the server | An admin page that shows nothing to a refused visitor | "Off" broke into "Of" and "f" on a phone; a test matched Next.js's own hidden alert | Make a switch wait for the server's answer, with a test that the server can refuse |
| 19. Who may sign up | A plan, not code | None: a planning chapter | Write the questions you'd need answered before letting adults sign up |
| 20. One unit at a time | A new route beside an old one that must not change | An empty answer made the page fail instead of falling back; a mock chose answers by code alone, so "Python could not start" returned "passed" | Add a field to an API response and prove an old page still works |
| 21. Imports, files and the learner's own modules | An import guard, file fixtures, learner modules | The plan's "any import is unsupported" was wrong; files carried over between cases; a program could write `datetime.py` and import `os` from it | Find a way round a guard, then write the test, then close it, and say what is still open |
| 22. Tests that call functions, and tests the learner writes | Function-call checks and reference programs | A hidden call's arguments had to reach the browser, so decision 28 said what "hidden" means | Decide what must stay on the server and what may not, for a new kind of check |
| 23. Trusting what you download | Hashes for five Pyodide files, checked twice | A changed `.wasm` left Pyodide waiting for ever instead of failing; a copy of `fetch` kept for checking would have reopened the network | Pin one file of a dependency by hash, and change one byte to watch it refused |
| 24. Secrets in addresses, counters in databases | `#invite=` and a shared rate-limit table | A hash key read before its secret was set; counters in a database could show who sent feedback | Move a counter to a database with one atomic statement, on two databases |
| 25. Accessibility you can test, and what you can't | Keyboard-only tests, axe, Firefox and WebKit | Tab in the editor typed spaces for ever, so Run couldn't be reached; tests that called `focus()` had hidden it | Walk your own page with only the keyboard, and write down every stop |

**Building the PDF:**
- Write each chapter as Markdown in a future `docs/book/` folder.
- Reuse `docs/handoffs/make_pdf.py`, or a similar free local script, to join and render them, with a table of contents and the glossary.
- Images come from `docs/handoffs/images/` and new screenshots of test accounts.
- Nothing is published until the owner decides (section 5).

## 3. Course outline: *How This App Was Built*

**Audience:** first-year computer engineering students, and motivated high-school students who have finished Python Foundations units 1 to 5.

**Format, per week:**
- a 60 to 90 minute **lecture** built on one book chapter, with live demos at real commits
- a **section** (a small-group walkthrough)
- a **problem set**, done in a disposable copy of the repository

**Assessment:**
- Problem sets are checked by tests plus a short written explanation, called "explain your change".
- The final project is reviewed against a rubric.
- Following `teaching-design.md`, written explanations are self-checked or reviewed, never auto-graded.

**Tools:** Git, Python, Node, a browser and a code editor. All free; no paid services or accounts beyond GitHub.

| Week | Lecture | Case study (decision-log chapter) | Problem set (in a practice copy of the repository) |
| --- | --- | --- | --- |
| 0 | What it takes to ship a web app | 0, 1 | Run the app locally at the first commit; trace one request from browser to database and write it up |
| 1 | Data, schemas and validation | 2 | Add a validation rule to the content loader with a failing-content test; a deliberate-break control |
| 2 | Databases and migrations | 3 | Write an additive migration with an upgrade test on SQLite; explain what happens during a deploy overlap |
| 3 | Correctness under retries | 3, 4 | Make a "do it once" action idempotent with a unique key; prove a retry adds nothing |
| 4 | Interfaces and accessibility | 4 | Build a small page with a keyboard-accessible list; run an automated accessibility check and fix what it finds |
| 5 | Algorithms you can explain | 5 | Write a pure recommendation-style function with worked-example tests and one property-based test |
| 6 | Security I: who is calling? | 7 | Implement a fixed-window rate limiter; write the spoofing test before the fix, watch it fail, then make it pass |
| 7 | Security II: sessions and browser policies | 8, 9 | Add server-side session revocation to a toy app; turn on a Report-Only CSP, read the reports, then enforce it |
| 8 | Teaching and honest feedback | 10, 11 | Audit a set of hints with code: can any combination pass the check? Rewrite a success message so it claims only what is checked |
| 9 | Running untrusted code | 12 | Add a time limit by worker termination and an output cap to a toy runner; test an endless loop and a flood |
| 10 | Evidence, review and working with AI | 13; all handoffs | Use an AI assistant on a small change, then write a handoff with the three new sections: decisions, bugs and how it was tested. A classmate reviews it |
| 11 | Feedback and lessons that tell the truth | 14, 16, 19, 21, 22 | Write a check with a hidden case and a hint ladder; run a hint audit that tries every hint with the starter |
| 12 | Privacy by design | 15, 17, 20; handoffs 45, 46 | Design a feature that stores nothing that identifies its user, and list what a log or a counter could still reveal |
| 13 | Supply chain and accessibility | Handoffs 37, 42, 44, 47 | Pin a dependency by hash and an action by commit; walk a page with the keyboard only and fix the first trap |
| Final project | Build and ship a small feature end to end | — | Proposal, branch, tests (including one deliberate-break control), pull request, handoff and a five-minute demo |

**Each lecture follows `teaching-design.md`:**
- a worked example from the real repository
- a "predict what happens" moment before running anything
- a "fix the bug" exercise taken from the log's real bugs
- support removed across the weeks: early problem sets give starter code and named steps; later ones give only a brief and tests

**Safety and fairness rules for the course:**
- Problem sets never touch the live app, real accounts or secrets. They use a disposable copy with test data.
- AI assistants are allowed, as in the real project, but every submission includes "explain your change" and the evidence. Grading never relies on detecting AI use.
- No timed beginner tasks and no public rankings, as in `build.md` section 4.

## 4. How the log feeds these

- From handoff 14 on, every handoff has "Decisions and why", "Bugs found and how they were fixed" and "How it was tested" (`build.md` section 14). Each stage then adds a chapter to `decision-log.md` with the same sections, so the book's raw material grows with the project.
- When a stage closes, add any new terms to the log's glossary and any new recurring idea to its "Patterns" chapter.
- Before writing a book chapter, re-read the PR diff at the named commits. The log is a summary, and the diff is the source of truth (`build.md` section 14).

## 5. Open decisions for the owner

The repository was made public on 2026-11-08, which bears on question 2 but does not decide questions 1 or 3.


1. **Audience and publication:** private (maintainer and family), shared with testers, or public? This decides how screenshots, names and the repository are handled.
2. **Repository access for students:** a public teaching copy of the repository, or exercises in separate small repositories?
3. **Format:** PDF only, or also lessons inside Python Academy itself (as a later course, linked to the `ai` course and `git`)?
4. **Order:** write the book first and build the course from it (proposed), or both together?

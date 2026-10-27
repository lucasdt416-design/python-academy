# Build plan: from Python Academy to a practical computing academy

Last updated: 2026-10-24 (America/Toronto)  
Status: proposed product and engineering roadmap; only the baseline below is implemented.  
Working name: Python Academy. A broader brand is an open decision, not a prerequisite for building.

## 1. Start here

We are building a learning platform that helps someone go from their first program to independently designing, testing, explaining, and shipping useful software. Python is the entry point. Practical development skills, computer science, databases, web development, and an optional computer engineering path follow.

The project is now being continued by the original owner's son, a first-year computer engineering student. He should be able to learn through the platform and through contributing to its development. The beginner experience must still work for someone with no programming experience.

This file is the shared plan for the human maintainer, ChatGPT, and Claude. Repository files, issues, commits, and test evidence carry state between assistants. A conversation summary is background; current source and verified deployment state determine what actually exists.

Immediate priorities:

1. Agree on this roadmap and select one small milestone.
2. Design the optional onboarding skills check already tracked in [Issue #4](https://github.com/torontojohn/python-academy/issues/4).
3. Establish versioned content, progress, and validation contracts before adding substantial curriculum.
4. Deliver one complete new learning slice, likely loops, including trustworthy checks and a project extension.
5. Teach basic Git/GitHub alongside that work, then expand in measured stages.

Do not treat this entire roadmap as the next implementation request. No new languages, account changes, infrastructure, or paid AI integrations are being implemented by writing this plan.

## 2. Verified baseline and limits

Baseline inspected at application commit `0b191818753ab4c36bb40ff5fd7aa46d0a0ae753`.

| Area | Implemented | Limits / next work |
| --- | --- | --- |
| Hosting | Frontend and API on Render; PostgreSQL | Staging and release controls need a deliberate setup |
| Identity | Google sign-in, signed sessions, parent/student onboarding | Current model has no independent adult learner role |
| Family flow | Email-bound, single-use, expiring invitation links; parent shares manually | No invitation email delivery service |
| Age rules | Invited learners at least 13; parents strictly over 25 | Self-declared age; these existing rules remain until deliberately changed |
| Curriculum | Five adventure quests: output, variables, input, if/else, combined story | One introductory chapter, not a complete Python course |
| Teaching UI | One active card: discover, example, predict, guided practice, challenge | Preserve this interaction pattern as content grows |
| Practice | Real browser Python in a worker, ordered input replies, stop/timeout | Not a general hosted terminal or a multi-language runtime |
| Checking | Bounded interpretation of an explicitly supported Python subset | Does not support general loops, functions, imports, or full Python semantics |
| Progress | Saved student attempts/completions; family view | Versioned skill evidence, placement, resumes, and badge records are future work |
| Rewards | Five quest badges and 100 XP per completed quest | Practice completion, not an independent certification of mastery |
| Preview | Public lesson/card links; no private family/progress reads | Preview progress is session-only |
| Quality | Last completed release reported 42 backend and 14 browser checks passing | Historical evidence, not a claim that a later working tree has been tested |
| Accessibility | Keyboard access, responsive layout, reduced motion, semantic controls | Full WCAG 2.2 AA audit remains outstanding |

Repository: https://github.com/torontojohn/python-academy  
Live preview: https://python-academy-dji8.onrender.com/preview?lesson=hello&card=1

Important source locations:

| Path | Purpose |
| --- | --- |
| `backend/content/` | Versioned course catalog and lesson content (format: `backend/content/README.md`) |
| `backend/app/content.py` | Content schema, load-time validation, and the original `/api/lessons` shape |
| `backend/app/lesson_checks.py` | Current bounded chapter checker |
| `backend/app/main.py` | API, identity, family records, attempts, progress |
| `backend/app/db.py`, `backend/migrations/` | Tables and Alembic migrations, applied automatically at startup (`backend/app/migrate.py`) |
| `backend/app/awards.py` | Idempotent XP and badge awards |
| `backend/app/recommend.py` | Learner goals and the rule-based "recommended next" function |
| `frontend/app/adventure.tsx` | Lesson page: card flow, unit sidebar, editor, current rewards |
| `frontend/app/catalog.tsx`, `frontend/app/course.tsx`, `frontend/app/catalog-data.ts` | Course catalog, course pages, and shared catalog/progress helpers |
| `frontend/app/academy.tsx`, `frontend/app/goal-card.tsx` | Account and family experience, and the learner goal card |
| `frontend/public/python-worker.js` | Browser Python execution and input adaptation |
| `frontend/public/check-runner.js`, `backend/app/browser_checks.py`, `docs/plan/browser-checks.md` | Browser behaviour checks for unit 2 onwards: run test cases in the browser, judge the reports on the server (ENG-03) |
| `frontend/app/style.css` | Visual design, responsive rules, reduced motion |
| `backend/tests/test_academy.py` | Backend and authored-reference checks |
| `frontend/tests/academy.spec.ts` | Browser flows and real Python execution |
| `.github/workflows/ci.yml` | Automated build and test workflow |
| `render.yaml`, `DEPLOYMENT.md`, `README.md` | Service definition, deployment notes, setup |
| `docs/plan/backlog.md` | Ordered backlog: source of truth for the order of work |
| `docs/plan/course-catalog.md`, `docs/plan/feedback-security.md` | Catalog, goals, recommendations and feature plans; feedback threat model |
| `docs/plan/teaching-design.md`, `docs/plan/lesson-feedback.md`, `docs/plan/ai-helper.md` | How we teach and per-course methods; the lesson feedback engine specification; the deferred AI helper design note (all proposed) |
| `docs/plan/decision-log.md`, `docs/plan/engineering-book-outline.md` | How the platform was built, stage by stage (decisions, bugs, testing), and the proposed book and course built from it |
| `docs/handoffs/` | One handoff per completed step, for reviewers without repository access |

## 3. What success means

A successful learner can explain what a program does, change it intentionally, debug a failure, test more than the happy path, and complete an unfamiliar project with progressively less guidance.

A successful platform does not confuse clicking through cards with understanding. It shows what evidence supports progress, accepts multiple correct solutions, and says when a check cannot judge a solution.

A successful student contributor can explain their own change, identify relevant files, use a branch and pull request, interpret test failures, and inspect a release. Using AI should strengthen those skills rather than remove the need to learn them.

### Learner modes

| Mode | Needs | Proposed experience |
| --- | --- | --- |
| Complete beginner | Small vocabulary, low setup burden, reassurance | Browser-first Python, visual examples, short cards, scaffolded projects |
| Returning beginner | Skip material already understood | Optional evidence-based placement, recaps, easy revisiting |
| First-year CS/engineering learner | Depth and transfer beyond syntax | Algorithms, C and memory, testing, discrete foundations, engineering projects |
| Practical builder | Build something useful and share it | Websites, APIs, SQL, Git, deployment, project rubrics |
| Parent | Know whether the learner is progressing | Private, understandable progress; no public ranking |
| Contributor | Work safely and learn the codebase | Guided issues, reproducible setup, review, tests, handoffs |

Account-model decision: a first-year student should eventually be able to learn without misrepresenting their age or becoming a parent account. Design an independent adult learner role, including how an existing invited adult learner gains control of their account and family visibility. This requires an explicit product decision and migration; do not silently relax the current gates. Continue excluding under-13 registration unless a separately scoped decision changes that.

## 4. Teaching contract for every learning unit

Keep one primary teaching card visible at a time. Instructions and an editor may sit beside each other on a coding card. On mobile they stack in a clear reading order.

The standard sequence is:

1. Discover: one learning objective and a short explanation before new syntax is used.
2. Worked example: annotated code and expected behavior, with vocabulary explained.
3. Predict: a question that reveals a misconception, followed by a reasoned explanation.
4. Guided practice: change one aspect of a working program and observe the effect.
5. Independent challenge: a new but related problem, with progressive hints and behavioral checks.
6. At chapter boundaries: a project milestone, reflection, and later retrieval practice.

Five cards are the current implementation, not a rule that every future concept must fit an identical amount of content. Split a difficult concept into multiple units rather than packing a long lesson inside one card. Introduce one small idea at a time.

Each unit must define prerequisites, learning objectives, vocabulary, starter code, trusted reference solutions, misconception examples, valid alternative solutions, checks, hint levels, and completion evidence. Runtime limitations must be explained before they affect a task.

Feedback should explain cause and a useful next action. Avoid saying an approach is wrong merely because it differs from the reference answer. For freeform work, distinguish an automated observation from a human judgment about creativity or design.

Learning support should include optional deeper explanations, accessible illustrations, replayable examples, drafts, clear reset controls, and a way to say a lesson was confusing. Avoid punitive streaks, timed beginner assessments, or making a learner repeat a whole chapter after one mistake.

## 5. Curriculum map and prerequisites

This is a proposed sequence, not a promise that each stage is complete or equivalent to a university course. A learner may branch after the common foundation. Developer-tool tutorials accompany real projects instead of delaying the first coding experience.

| Stage | Core topics | Project evidence | Prerequisite |
| --- | --- | --- | --- |
| 0. Find your starting point | Goals, prior experience, optional placement, basic computer vocabulary | A recommended path the learner can change | None |
| 1. First programs | Output, variables, strings, input, conditions | Interactive adventure | None; current chapter exists |
| 2. Python foundations | Numbers, conversions, Boolean logic, loops, collections, functions, scope | Adventure with inventory and replay; quiz or budget tool | Stage 1 skills |
| 3. Reliable Python | Debugging, exceptions, tests, files, JSON/CSV, modules, environments, basic OOP | Tested study planner or data tool | Stage 2 |
| 4. Computer science foundations | Representation, pseudocode, searching, sorting, complexity, recursion, data structures | Explain and compare algorithms on real inputs | Loops, functions, collections |
| 5. Web foundations | HTML, semantic structure, CSS, accessibility, JavaScript, DOM, events, HTTP | Accessible personal site and interactive app | Basic programming; HTML may start earlier |
| 6. Data and SQL | Tables, queries, joins, modeling, constraints, transactions, indexes, parameterized queries | Course planner or personal library database | Basic programming; SQL can run alongside web |
| 7. Backend and full stack | Node.js, npm, async JS, routes, API contracts, validation, auth concepts, database access | Deployed application with client, API, and database | JavaScript, HTTP, SQL |
| 8. Engineering practice | Git collaboration, CI, integration tests, logs, deployment, security, performance, documentation | Maintained capstone and reviewed contributions | Applied throughout; advanced parts need Stage 7 |
| 9. Engineering depth electives | C, memory, bitwise logic, discrete math, numerical methods, embedded systems | Simulation, C data structure, virtual sensor dashboard | Relevant math/programming prerequisites |

Node.js is a JavaScript runtime, not a separate programming language. Teach JavaScript first. SQL teaches a different way to express data operations; introduce it through useful questions about a small dataset. HTML and CSS serve structure and presentation rather than general-purpose program control.

The existing application remains Next.js/React/TypeScript plus FastAPI/PostgreSQL unless a separately justified architecture decision changes it. Teaching Node.js does not require rewriting the platform backend.

### Python progression in more detail

| Chapter | Topics | Project extension | Evidence required |
| --- | --- | --- | --- |
| Adventure opening | Current five quests | Setting, hero, player, choice | Current checks plus reviewed teaching content |
| Repeat and explore | Arithmetic, conversion, comparison, `while`, `for`, `range`, loop termination | Replay a scene or repeat a quiz | Correct counts, boundaries, termination, changed inputs |
| Keep track of a world | Lists, indexing, iteration, dictionaries, sets where useful | Inventory, scores, rooms | Empty/single/multiple-item cases and explanations |
| Organize your code | Functions, parameters, return values, local scope | Reusable scene and scoring functions | More than one input, useful return values, limited unintended side effects |
| Recover and investigate | Tracebacks, debugging strategy, exceptions | Validate player input and explain a failure | Identify root cause and repair a broken example |
| Save and load | Text files, JSON/CSV, modules, environment concepts | Save game or study tracker | Round trip, invalid/missing data, clear runtime file limits |
| Trust your changes | Unit tests, boundaries, simple type hints, refactoring | Tested reusable project | Tests distinguish correct and intentionally broken versions |
| Model a larger program | Classes, composition, separation of responsibilities | Inventory or simulation model | Explain why the abstraction helps; avoid unnecessary OOP |

Library/network exercises come after fundamentals. Their tasks need deterministic fixtures and offline failure handling; avoid grading against an unpredictable public API.

## 6. University reference path and engineering depth

Use public course outlines as reference maps. Author original explanations, datasets, project briefs, tests, and feedback. Link to external lectures for optional depth. Do not imply Harvard affiliation, equivalent credit, or a Harvard certificate. Check licensing and attribution before reusing any material; keep current course assignment solutions separate from our original practice.

| Reference | How it informs our proposed path | Important distinction |
| --- | --- | --- |
| Harvard CS50P | Broader Python coverage including tests, exceptions, files, and classes | We start with a gentler project-based introduction |
| Harvard CS50x | A foundation spanning representation, C, algorithms, memory, data structures, Python, databases, and the web | Use an optional depth path; our default order need not copy its order |
| Harvard CS50 SQL | A structured progression through querying, relationships, design, writes, views, optimization, and scaling | Practice against isolated learning datasets |
| Harvard CS50 Web | A later reference for project-based web work, data models, interfaces, testing, and deployment | Our Node.js track is our own choice, not a claim about its backend curriculum |

A first-year computer engineering path should extend beyond a web-development checklist:

- Representation: binary/hexadecimal, signed values, overflow, floating-point limits, text encoding.
- C and systems: compilation, arrays, pointers, allocation, stack/heap, file I/O, debugging memory errors.
- Discrete foundations: logic, sets, functions, proof intuition, induction, counting, graphs.
- Algorithms: reasoning about time/space, tracing search and sort, recursion, appropriate data structures.
- Engineering mathematics in code: unit conversions, numerical error, vectors, plotting, simple simulations and Monte Carlo reasoning.
- Digital/embedded introduction: Boolean logic, truth tables, state machines, simulated sensors, sampling, serial communication concepts, then optional hardware projects.

Do not describe that list as the complete first-year Harvard or computer engineering curriculum. Exact alignment needs a separate mapping to the student's actual course outlines. Hardware purchases and physical experiments remain optional; simulations should be usable without equipment.

## 7. Projects as the spine of the experience

Offer three versions of each project: guided build, independent brief, and stretch extensions. A project should produce a useful artifact, not just a number of lessons completed. No public posting or paid hosting should be required to earn a learning badge.

| Project | Skills introduced | Minimum deliverable | Stretch work |
| --- | --- | --- | --- |
| Adventure game | Python control flow, collections, functions | Replayable game with meaningful choices and tests | Save/load, data-driven scenes |
| Quiz and spaced-practice tool | Functions, data modeling, files | Load questions, record answers, summarize learning | Scheduling and weak-area review |
| Engineering calculator | Units, validation, functions, numeric limits | Explainable calculations with boundary tests | Graphing and numerical comparisons |
| Data investigation | CSV, aggregation, visualization | Answer an original question with documented data | Compare methods or uncertainty |
| Personal website | HTML, CSS, accessibility, Git | Responsive site with semantic navigation | Custom design and deployment |
| Interactive study dashboard | JavaScript, DOM, state, storage | Add/edit/filter tasks with useful errors | Accessibility audit and offline behavior |
| Course or book database | SQL queries, joins, constraints | Schema, seed data, query answers, design notes | Transactions, indexes, query plans |
| Full-stack planner | Node.js, API, SQL, validation | Client/API/database with automated checks | Authentication and private accounts |
| Engineering simulation | Algorithms, data, mathematical reasoning | Reproducible simulation with assumptions and results | Sensitivity analysis and visualization |
| Capstone | Independent design and engineering | Working project, README, tests, demo, tradeoff explanation | Real user feedback and measured improvement |

Project brief template:

- Problem and intended user.
- Skills/prerequisites and a small example of expected behavior.
- Required behavior, edge cases, and explicitly optional extensions.
- Deliverables: source, README, tests, screenshots/demo where appropriate.
- Suggested milestones that can be completed in separate sessions.
- Evaluation rubric and examples of acceptable variation.
- Reflection: explain a design decision, a bug, and a test that mattered.

Proposed project rubric: behavior 40%, testing/debugging 20%, explanation/design 15%, usability/accessibility 15%, reproducibility/documentation 10%. Adjust weights for non-UI projects; never penalize a console project for not having a website. Publish the rubric before work starts. Treat these weights as a starting proposal to pilot, not measured educational thresholds.

## 8. Developer-tool tutorials

Use small, safe practice repositories and files. Explain the meaning of each command before asking someone to run it.

| Tutorial | What the learner should do independently |
| --- | --- |
| Files and folders | Find a project, understand paths/extensions, distinguish source from generated output |
| Terminal basics | Navigate, run a program, interpret an error, understand the working directory |
| Git versus GitHub | Explain local version history versus a service hosting repositories |
| First repository | Create or clone a practice repo and read its README |
| First commit | Inspect a diff, stage selected changes, write a useful commit message |
| Pull and push | Explain downloading remote changes versus uploading local commits |
| Branches and pull requests | Work on a feature branch, ask for review, interpret checks |
| Conflicts and recovery | Resolve a small exercise conflict; understand revert before destructive history edits |
| Credentials and configuration | Keep secrets out of source, use example configuration, distinguish public and private repos |
| Local dependencies | Python environments and packages; later npm, package manifests, lockfiles |
| Testing and CI | Run checks locally, inspect a CI failure, repair the underlying problem |
| Deploy a small app | Distinguish local/staging/production, read logs, verify a release and understand rollback |
| Working with AI | Ask for explanations, inspect diffs, verify generated claims, write a handoff |

First Git project: change a README in a disposable repository, commit, push, open a PR, and review the diff. A platform lesson can simulate the workflow first, but simulation alone should not earn the same evidence label as an actual repository contribution.

## 9. Onboarding and placement

Existing backlog: [Issue #4](https://github.com/torontojohn/python-academy/issues/4). This is not implemented.

Proposed first experience:

1. Choose a goal: learn from scratch, build projects, strengthen university fundamentals, or explore.
2. Offer Start from the beginning and Find my starting point.
3. Collect optional prior experience, then assess a few concepts with prediction/debugging questions and a short coding task.
4. Show the evidence and recommended starting point. Let the learner accept, start earlier, or revisit anything.
5. Supply a short recap/starter project so skipping a concept does not break the connected adventure.

Keep the assessment untimed, one card at a time, and optional. Aim initially for roughly five to eight minutes; validate that expectation with learners. Fatigue, skipping a question, a network error, or a checker limitation should not be treated as evidence of inability.

Proposed skill states: unknown, introduced, practiced, independently demonstrated, and due for review. These are not yet database fields. Confidence should come from diverse evidence; one correct multiple-choice guess is not enough to skip a core coding skill.

Initial placement rule to pilot: recommend skipping a skill only when a concept question and a different applied task both show it. If evidence conflicts, recommend a short refresher. Do not invent precise confidence percentages before calibrating the assessment.

Store the recommendation separately from completed lessons, with assessment/content versions and the learner's chosen starting point. A placement skip does not automatically grant XP, badges, or completed-project status. Define retake behavior and adult account privacy before implementing parent views of placement.

## 10. Badges, progress, and motivation

Keep existing practice rewards honest. Introduce stronger evidence categories over time:

| Badge category | Example | Required evidence |
| --- | --- | --- |
| Practice | Story spark | Existing quest challenge completion, labeled as practice |
| Skill | Loop navigator | Independent loop problem plus a later variation |
| Project | Website builder | Published rubric met; private demo/local delivery is acceptable |
| Engineering habit | Bug detective / test writer | Explain a real failure and add a meaningful regression check |
| Collaboration | First reviewed contribution | A reviewed practice or project PR, not just account linking |
| Capstone | Independent builder | Working project, tests, documentation, and explanation |

No badges merely for clicking, linking an account, or accepting placement. Award each badge/version once. Keep rewards idempotent so retries cannot inflate XP. Provide an accessible text equivalent to every visual badge, clear earning criteria, and progress toward the next useful milestone.

Avoid public leaderboards and making streak preservation a condition of progress. Keep profiles private by default. Share project evidence only through a deliberate learner action under the account model's permissions.

For version changes, define whether existing evidence stays valid, needs a refresher, or maps to a successor skill. Do not erase history or silently award a different badge when reusing an old lesson ID.

## 11. Product and technical foundation

### Content model

Move from one hard-coded chapter toward typed, versioned track/chapter/lesson/card content. Preserve stable IDs. Proposed fields include objective, prerequisite skill IDs, vocabulary, card type, runtime, starter files, input fixtures, validator ID/version, hints, references, badge rules, and accessibility descriptions.

Validate content at build/test time: every prerequisite exists, dependencies have no cycles, references resolve, examples match checks, hints progress sensibly, and a runtime supports the lesson's syntax. Keep learner text separate from execution and checking code.

Start with version-controlled content. A full visual authoring CMS is later work, not a prerequisite for adding the next chapter. Preview should eventually support any unpublished content version while never exposing family records or confidential grading material.

### Proposed data changes

| Record | Key information | Required behavior |
| --- | --- | --- |
| Skill evidence | Learner, skill, task/version, result, hint usage, source, timestamp | Distinguish placement, practice, and independent evidence |
| Assessment session | Version, responses, interruptions, recommendation, learner choice | Resume safely; no duplicate completion on retries |
| Learning progress | Stable IDs, content version, card/checkpoint, completion state | Resume across devices; preserve historical meaning |
| Draft/project | Owner, files, project/version, save state | Explicit reset, reliable save, private by default |
| Badge award | Badge/version, learner, qualifying evidence | Unique award; consistent revocation/correction rules |
| Learning event | Minimal event type, content version, useful context | Privacy-aware measurement with defined retention |

Use schema migrations before introducing these records. Test migration from existing accounts and attempts, including the old arithmetic exercise that previously used the variables ID. Define transaction boundaries and unique constraints for awards and assessment completion.

Keep technical execution failures separate from learning failures. A service timeout or unsupported checker should say Unable to assess, retain the draft, and allow a retry.

### Runtimes and assessment

| Learning activity | Proposed execution approach | Release dependency |
| --- | --- | --- |
| Introductory Python | Existing browser worker | Keep current chapter regression checks |
| Broader Python | Extend browser execution and design a suitable behavior-check contract | Correct loops/functions/collections, bounds, meaningful error categories |
| HTML/CSS/JavaScript | Isolated preview with restricted capabilities | Prevent access to account/session data; test accessibility and rendering |
| SQL | Per-learner browser or isolated ephemeral dataset | Reset fixtures, bound queries, prevent production DB access |
| Node.js and C | Local setup tutorials first; hosted execution is a later decision | Never run arbitrary learner code inside the main API service |
| Hardware | Simulation first, optional local device tools | No mandatory purchase; clear separation from deployed app privileges |

Do not turn the current bounded interpreter into a pretend full Python implementation. Decide between limited structural checks plus real browser behavioral checks, or a separately isolated evaluation service when the use case justifies it. Browser-reported practice cannot be treated as tamper-resistant certification. Any hosted arbitrary-code execution needs its own resource isolation, network restrictions, lifecycle controls, quotas, tests, and cost review.

Use result states such as passed, needs_work, execution_error, unsupported, and service_error rather than one Boolean for every future situation. Support multiple valid solutions. Exact formatting checks are appropriate only when formatting is the stated objective.

## 12. Quality measures and release gates

These are proposed gates, not claims about current measured performance.

### Per-lesson accuracy gate

- State a measurable learning objective and identify every new concept.
- Execute all trusted reference solutions in the intended runtime.
- Include at least two meaningfully different correct solutions where the problem permits them.
- Include representative wrong solutions: hard-coded answers, wrong boundaries, missing branches, invalid/empty input, and the intended misconception.
- Verify that feedback describes the failure accurately and does not claim to judge untested qualities.
- Test runtime limits and unsupported syntax separately from incorrect reasoning.
- Have a human or a second review pass check both the teaching and the grading contract.

### Per-feature gate

- Defined scope, issue, owner, prerequisites, and acceptance criteria.
- Relevant unit/API/browser checks pass on the reviewed commit.
- Actual learner-code execution is tested where execution behavior changes.
- Real account boundaries are covered in backend checks; mocks alone do not establish authorization.
- Keyboard, focus, screen-reader labels, mobile overflow, contrast, reduced motion, and meaningful error messages checked as relevant.
- Saved data and retries behave correctly; existing users survive the migration.
- No secrets in source, output, screenshots, or handoffs.
- Review lists material limitations and remaining work.
- Release verification checks the intended commit and actual user behavior, not merely a successful build trigger.

### Broader-release gate

Before expanding beyond controlled use, address schema migration strategy, backup/restore verification, account/data deletion, invitation abuse controls, rate limits, privacy/retention policy, runtime review, dependency maintenance, operational alerts, and a documented accessibility audit. Prioritize concrete gaps relevant to the release; do not add unrelated infrastructure merely to satisfy a checklist.

### Product measures

| Measure | What it tells us | Initial treatment |
| --- | --- | --- |
| First useful program | Whether a beginner reaches a working creation | Establish a baseline; separate setup time from learning time |
| Delayed transfer task | Whether learning carries to a new problem | Pilot a short later variation; not just repeat the same answer |
| Placement override/refresher use | Whether skip recommendations help | Investigate wrong skips and confusing recommendations |
| Incorrect rejection rate | Whether valid work is unfairly blocked | Track reproducible reports; block a lesson release for known grading errors |
| Completion with hint levels | Whether scaffolding is effective | Interpret as support needs, not a leaderboard |
| Draft loss / duplicate rewards | Whether progress is reliable | Zero known reproducible cases at release |
| Runtime/service failures | Whether platform problems interrupt learning | Separate from student mistakes; record device/runtime context without code by default |
| Accessibility defects | Whether learners are excluded | Block critical barriers in the core learning flow |
| Project independence | Whether learners can build and explain | Assess against a published rubric, with permitted support recorded |

Do not claim mastery, employment readiness, or university equivalence from a completion percentage. Set numeric engagement/performance targets after collecting a small, consented baseline. Analytics should use minimal necessary data, avoid logging raw student code by default, and support an appropriate retention/deletion policy.

## 13. Phased delivery and explicit priorities

Use milestone exit criteria rather than ambitious calendar promises. The first-year maintainer can work in small sessions around coursework. Estimate an issue after inspecting its dependencies, not the whole platform at once.

| Milestone | Deliverable | Exit criteria |
| --- | --- | --- |
| M0: shared plan | This roadmap, contribution workflow, next issue selected | Both assistants and maintainer reference the same revision and scope |
| M1: trustworthy foundation | Content schema, validator contract, migration plan, independent learner decision | Existing chapter still works; unsupported/checker errors are distinct; data model reviewed |
| M2: placement vertical slice | Versioned short assessment and optional recommendations for current basics | Valid/invalid/uncertain answers tested; skip reversible; no false reward; adult/family privacy resolved |
| M3: Python depth pilot | One complete loops unit plus adventure extension, then collections/functions | Real-runtime and alternative-solution tests pass; learner can transfer the idea |
| M4: reliable project workflow | Testing/files chapters, saved projects, Git/GitHub starter tutorials | Learner builds, tests, documents, and versions a small Python project |
| M5: websites and data | HTML/CSS/JS project track and a SQL project track | Isolated runtimes/fixtures; accessible project briefs and checks |
| M6: full-stack builder | Node.js/API/database project and deployment tutorials | Prerequisites met; integration checks, private data boundaries, operational docs |
| M7: university and engineering depth | Algorithms/C/memory and selected math/engineering projects | Objective mapping, realistic projects, trustworthy assessment, reviewed depth |
| M8: capstone and growth | Portfolio-quality capstone, maintainable authoring and progress | Independent demonstration, supportability, evidence-based iteration |

M1 and placement design can overlap conceptually, but implementation should stay in small separate PRs. Do not block a carefully scoped placement pilot on a complete platform rewrite. Finish one useful vertical slice before expanding multiple tracks.

### Next-session backlog

**The ordered, current backlog is [`docs/plan/backlog.md`](docs/plan/backlog.md). It is the source of truth for the order of work and each item's status.** The IDs below, and what they mean, stay defined here: where the backlog disagrees on an ID, its meaning, or its priority, this table wins until one of them is deliberately updated.

| ID | Priority | Task | Dependencies / definition of done |
| --- | --- | --- | --- |
| PLAN-01 | Now | Review this plan and select a milestone owner | Human confirms scope; unresolved choices recorded |
| PLAN-02 | Now | Give the continuing maintainer appropriate repo access | Owner-managed permission change; each person uses their own account |
| EDU-01 | Next | Write placement question/task examples for current four skills | Concepts explained, answer rationale, valid alternatives, misconception cases; relates to Issue #4 |
| ENG-01 | Next | Specify typed content and result-state contracts | Inventory current format; migration path; one existing lesson represented correctly |
| ID-01 | Next | Decide independent adult learner onboarding and visibility | Define account lifecycle, adult control, parent boundaries, and migration before implementation |
| ENG-02 | Next | Design versioned evidence/progress and schema migrations | Stable IDs, legacy mapping, retries, retention, migration tests |
| EDU-02 | After design | Pilot placement on one skill before all four | End-to-end recommendation with unknown/error/override cases |
| EDU-03 | After checker design | Author one loops unit and project extension | Trusted examples, alternative solutions, termination/boundary checks |
| TOOL-01 | Alongside projects | Draft Git versus GitHub and first commit lessons | Safe practice repo, screenshots/steps, clear diff/commit/push concepts |
| QA-01 | Before broader use | Audit core lesson accessibility and grading reports | Reproducible defects, priority, fixes, retest evidence |
| OPS-01 | Before broad rollout | Confirm staging, recovery, privacy, quotas and alerts | Evidence appropriate to intended release scope |
| DATA-01 | Later | Design SQL runtime and first investigation project | Isolated data; no route to application database |
| WEB-01 | Later | Design website project track and isolated previews | HTML/CSS before advanced JS/frameworks |
| NODE-01 | Later | Plan Node.js/SQL capstone | JavaScript/HTTP/SQL prerequisites and local setup first |
| CE-01 | Later | Map university courses to optional deep-dive units | Obtain actual course outlines; distinguish reference from equivalence |

These IDs are roadmap references, not claims that corresponding GitHub issues have already been created. Keep Issue #4 as the existing placement discussion; split approved implementation slices into linked issues when work starts.

## 14. Working with ChatGPT and Claude efficiently

Start with shared GitHub state. This plan does not connect accounts, synchronize chat histories, configure an AI-to-AI bridge, or authorize new paid API usage.

If using Claude Code, it can work directly with a checked-out codebase and development commands. If using ordinary Claude chat without repository access, provide `build.md`, the relevant source files, the issue, and an exact diff/commit context. Never assume a pasted repo URL gives an assistant access to private source.

### Roles per task

| Role | Responsibility | Can be performed by |
| --- | --- | --- |
| Human maintainer | Choose goals, understand tradeoffs, review actual behavior, approve consequential releases | Continuing project owner |
| Implementer | Own one issue, inspect current source, write scoped changes, run relevant checks | ChatGPT or Claude |
| Reviewer | Compare diff against acceptance criteria, probe edge cases, identify missing evidence | The other assistant plus human judgment |
| Test system | Execute reproducible checks and report results | Local tools and GitHub Actions |

Choose the implementer for each task rather than assigning permanent intelligence-based roles. Alternate when useful. A second assistant adds value by reviewing assumptions, teaching accuracy, or failure cases; asking both to independently build the same feature is usually duplicate work.

### Task workflow

1. Read current `build.md`, `README.md`, the issue, relevant source, and any repository instructions. Record the base commit.
2. Agree on one small outcome, acceptance criteria, non-goals, file ownership, and relevant checks.
3. Create a feature branch or isolated checkout. One implementer owns the change. If doing genuinely independent work concurrently, use separate branches/files and an explicit integration plan.
4. Implement and explain the change. Keep curriculum, assessment, and account logic consistent.
5. Run relevant tests. Record exact commands, commit, results, and what was mocked or not verified.
6. Open a PR with problem, resulting behavior, evidence, and limitations. Ask the reviewer to inspect the actual diff at a specific SHA.
7. Address material review findings; rerun affected checks. Do not merge stale review evidence after source changes.
8. Human reviews the visible experience. Follow the session's authorization and repository release rules; merging `main` can trigger production deployment.
9. Verify the specific release and user behavior. Update issue status and the plan only when evidence supports the status.

Use short handoffs rather than repeatedly pasting the entire conversation. Keep long-lived decisions in this file or a linked issue/decision record. When the other assistant finishes, import the resulting diff/commit and evidence; do not treat its narrative summary as proof of tests or deployment.

### Handoff template

```text
Task / issue:
Human goal:
Relevant build.md section:
Repository and branch:
Base commit / reviewed head commit:
Implementer / reviewer:
Files changed and why:
Acceptance criteria:
Non-goals:
Behavior before / after:
Tests run, exact commands, result, and commit:
Mocks / unverified behavior:
Screenshots or demo evidence:
Data migration / compatibility implications:
Decisions and why:
  - Decision: what was chosen
    Options considered: the alternatives, including "do nothing"
    Reason: why this one; "reasoning not recorded" if nobody wrote it down
    Who decided: owner / implementer / reviewer, and when
Bugs found and how they were fixed:
  - What went wrong, or nearly went wrong
    How it was found: unit test / browser test / live check / review / while building
    Fix and commit, and the test that now guards it
How it was tested:
  - Each kind of test used, and what it proves (and does not prove)
  - What was mocked, and why
  - Deliberate-break controls: what was broken on purpose, and which tests failed
Known limitations or open decisions:
Next concrete action:
Deployment status: not requested / pending / verified at commit ...
```

Every handoff includes the three middle sections, even when one is short ("No bugs found."). They feed the decision log (`docs/plan/decision-log.md`), which records how the platform was built, for a later book and course (`docs/plan/engineering-book-outline.md`). Write them for a first-year student:

- **Decisions and why.** A decision is any choice where a reasonable person could have done something else, such as where to store data, what a limit should be, or which page to build first. List the options that were really considered, not ones invented afterwards. If the reason was never written down, say "reasoning not recorded" rather than guessing.
- **Bugs found and how they were fixed.** A bug is the program doing something other than what was intended. Include **near-misses**: problems caught before they reached anyone, for example by a test, a review or a live check. These are often the most useful lessons. Say how each was found, because "a test caught it" and "a user hit it" teach different things.
- **How it was tested.** Name each kind of test and what it proves:
  - A **unit test** checks one function on its own.
  - An **API test** sends real requests to the backend.
  - A **browser test** (Playwright) drives a real browser.
  - A **live check** is done by a person on the deployed site.
  - A **mock** is a stand-in for something real, such as a fake server answer. It makes tests fast and repeatable, but it proves nothing about the real thing, so list every mock.
  - A **deliberate-break control** means breaking the code on purpose and confirming the tests fail. It shows that the tests can actually catch that mistake. Then the code is put back.

### Starter prompt for either assistant

```text
You are helping me continue Python Academy, which is expanding into a broader
computing learning platform. Read build.md and README.md from the current
repository revision, then inspect the issue and relevant source. Treat roadmap
items as proposals unless their status and code show they are implemented.

For this session, work on: [one issue or narrowly defined outcome].
Your role is: [implementer or reviewer].
Base commit and branch: [fill these in].

Explain unfamiliar concepts at a first-year computer engineering level.
Preserve the one-card-at-a-time lesson experience. Verify educational feedback
and accept legitimate alternative solutions. Keep changes scoped. Record test
commands, actual results, mocks, limitations, and the next action using the
handoff template. Do not claim that a feature is live without verifying it.
Do not change paid services, credentials, account policy, or production merely
because they appear as future items in build.md.
```

### Efficiency and spending

- Use one assistant for routine edits; use the second for meaningful review or a separate bounded task.
- Let deterministic tests judge deterministic behavior; reserve AI review for reasoning and ambiguous design questions.
- Send the relevant files and diff, not an entire repo snapshot on every message.
- Timebox exploratory work and stop when acceptance criteria are met.
- Track task scope and rework before assuming two assistants are faster or cheaper.
- No custom multi-model API orchestration in the initial plan. Revisit only if a concrete bottleneck justifies engineering, credentials, recurring cost, retry controls, and privacy review.

## 15. Learn while building the platform

For the first-year maintainer, each contribution can be a small lesson:

1. State the behavior you want in plain English.
2. Ask the implementer to identify relevant files and explain the smallest change.
3. Predict what the code or test will do before running it.
4. Inspect the diff and explain at least one design choice in your own words.
5. Make a small modification yourself and see whether the tests catch a mistake.
6. Write the PR summary and one thing you learned.

Suggested first contribution: improve one confusing explanation or add a regression test for a known learner mistake. Then implement one bounded placement question, followed by a result/recommendation display. Avoid starting with a full authentication rewrite or arbitrary-code execution service.

For every AI-assisted feature, be able to answer: What changed? Why does it work? What could fail? Which test would notice? Where is the evidence? What did I still not verify?

## 16. Decisions to make, without blocking this plan

| Decision | Initial recommendation | When needed |
| --- | --- | --- |
| Brand | Keep Python Academy while testing the broader vision | Before a public multi-track launch |
| First expansion | Placement design and one deeper Python slice | Next planning session |
| Audience/account model | Support beginners and independent adult learners with distinct permissions | Before self-service adult onboarding |
| University alignment | Start with a CS50-informed optional depth map; request actual course outlines | Before claiming course-specific coverage |
| Badge strength | Keep practice rewards separate from demonstrated skill/project evidence | Before new badge types launch |
| Execution strategy | Browser-first where suitable, local tutorials for Node/C initially | Before selecting new hosted runtimes |
| AI collaboration | GitHub issues, PRs, this plan, and short handoffs | Immediately |
| Business model | Keep learning/engineering evidence ahead of monetization decisions | After an initial learning pilot |

## 17. Reference sources

Checked while preparing this plan on 2026-10-24. These inform topic coverage and workflow; the roadmap and original project briefs are our proposed design. Recheck current documentation before teaching changing setup commands or service-specific behavior.

- Harvard CS50P syllabus: https://cs50.harvard.edu/python/syllabus/
- Harvard CS50x syllabus: https://cs50.harvard.edu/x/syllabus/
- Harvard CS50 SQL: https://cs50.harvard.edu/sql/
- Harvard CS50 Web: https://cs50.harvard.edu/web/
- Node.js introduction: https://nodejs.org/en/learn/getting-started/introduction-to-nodejs
- GitHub Hello World workflow: https://docs.github.com/en/get-started/using-github/hello-world
- Claude Code overview: https://code.claude.com/docs/en/overview
- Python language tutorial, existing project reference: https://docs.python.org/3/tutorial/

## 18. Plan maintenance and completion record

Use these status words consistently: proposed, ready, in_progress, in_review, verified, blocked, deferred. A roadmap entry becomes verified only with linked evidence. Do not mark a whole milestone complete because one part shipped.

For an approved decision, record date, decision, reason, alternatives considered, and consequences. For completed work, record issue/PR, commit, checks, release verification where applicable, and follow-up work.

Current session record:

- Created the comprehensive roadmap and shared-assistant workflow.
- Preserved the existing application baseline and the pending placement idea.
- Proposed curriculum, projects, assessment, badges, technical foundations, quality measures, and phased delivery.
- No new learning tracks, placement flow, independent adult onboarding, or AI integrations implemented in this documentation change.

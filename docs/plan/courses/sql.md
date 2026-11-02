# Data and SQL (`sql`): course design

Status: **proposed**, written 2026-11-02. No code and no catalog change. **Box B-D1 is empty, so this stays a design document.** Sources: `course-catalog.md` section 3.4, `teaching-design.md` section 6.5, `build.md` sections 5 and 7, backlog DATA-01.

## Audience and prerequisites

Learners who want to answer questions with data; needed for back-end work.

- **Required:** `py.u01` to `py.u04`.
- **Suggested:** `web`, which can run alongside.

## Outline

| Unit | Title | Lessons (proposed IDs) |
| --- | --- | --- |
| `sql.u01` | Asking questions | `sql.select`, `sql.where`, `sql.order-and-limit`, `sql.null` |
| `sql.u02` | Summing up | `sql.count-and-sum`, `sql.group-by`, `sql.having` |
| `sql.u03` | More than one table | `sql.why-two-tables`, `sql.join`, `sql.left-join`, `sql.join-traps` |
| `sql.u04` | Designing tables | `sql.create-table`, `sql.keys`, `sql.constraints`, `sql.design-a-schema` |
| `sql.u05` | Changing data | `sql.insert-update-delete`, `sql.transactions`, `sql.parameterized-queries` |
| `sql.u06` | Going faster, and your project | `sql.indexes`, `sql.query-plans`, `sql.project` |

Each lesson starts with a question about a small, friendly, original dataset, such as a library or a course planner.

## Projects and evidence

**Course or book database** (`build.md` section 7): schema, seed data, query answers and design notes. Query tasks are automated practice evidence, and design notes follow a rubric.

## Runtime and safety

**A SQL engine in the learner's browser**, in a worker. Each run opens a new in-memory database, loads the lesson's dataset, runs the learner's SQL, reports the result rows and closes it.

| Threat | Control |
| --- | --- |
| Reaching the application's database | Impossible by design: the engine is in the browser and has no connection to the server. **Learner SQL never runs on the server** (`build.md` section 13, DATA-01: "no route to application database") |
| Network from the engine | Same worker rules as Python: network APIs removed, and a strict worker policy |
| `ATTACH` or file access | In-memory only. There is no real filesystem in the worker |
| A query that never ends, such as a huge cross join | Time limit by terminating the worker, as for Python |
| Huge output | A row and character cap, reported as a result state |
| `load_extension` | Not available in the proposed build. Test it and deny it |

**A hidden dataset needs an owner decision.** `teaching-design.md` section 6.5 asks for a second hidden dataset, so queries that only fit the visible rows fail. Running in the browser means its rows have to reach the browser, while the expected results can stay on the server. This is the same issue as hidden function arguments. See question 2.

## Dependencies

This needs a new dependency, hence box B-D1. Measured on 2026-11-02 from the npm packages:

| | `sql.js` 1.15.2 (recommended) | `@sqlite.org/sqlite-wasm` 3.54.1-build1 |
| --- | --- | --- |
| Licence | MIT | Apache-2.0 |
| Size | `sql-wasm.wasm` 685,235 bytes (335,732 gzipped), `sql-wasm.js` 47,441 bytes (17,273 gzipped) | 3.0 MB unpacked; files to ship not measured |
| npm integrity | `sha512-ZmMYFsZPZWDKIJUh3A5rdnpRV3hB/r7AijwAzSzLnfv/9CSx4obUmDtA8brAjWJWjGtUVh43nIEJ+6nl6HuOUg==` | `sha512-foW427VBLJ3G87bsnvQTZCc9zYe0Fq1wH0pz1I6BlKLKXcArIAyTkHtq0iT2llmhcMQt9T/p6l5PpQQh+6O8uQ==` |
| Why | Small, simple in-memory use | The official build, with storage features this course does not need |

**Integrity:** self-host a pinned copy in the frontend, so no outside CDN is involved. A test compares the file's hash with a recorded value, and the worker's policy only allows its own origin. A design PR repeats these checks before anything is added, as B-D1 asks.

**Cost:** free; a little more to download for learners on this course only.

## Checker features required

- A SQL runner following the ENG-03 contract: plan, reports, judge.
- **Result-set comparison on the server.** Column count, rows compared as sets unless the question asks for an order, with a documented rule for numbers and `NULL`.
- Friendly translations of SQLite's error messages.
- Schema tasks: the worker reports the resulting table structure and which test inserts were refused.
- Parsing SQL on the server is **not** needed: results decide, so correct queries written differently pass.

## Risks

- **SQLite is not PostgreSQL.** Types and some functions differ, and lessons must say so, because `node` later uses a different engine.
- **`sql.parameterized-queries`** needs a host language. Teach the idea with the engine's own bound values, then again in `node`.
- **`sql.query-plans`** output is specific to SQLite, so teach reading it, not exact plans.
- **Faked reports,** as in every browser check. Practice evidence only.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. Tick B-D1, to allow a design PR for `sql.js`? *Recommended: yes, when this course is next in line, not before.*
2. May hidden dataset rows reach the browser, with expected results kept on the server? *Recommended: yes. Without it, only visible rows can be checked, and hard-coded answers would pass.*
3. SQLite for teaching, though production is PostgreSQL? *Recommended: yes. No browser-ready PostgreSQL is proposed here.*

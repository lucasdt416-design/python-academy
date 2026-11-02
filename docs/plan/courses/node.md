# Node.js and APIs (`node`): course design

Status: **proposed**, written 2026-11-02. No code and no catalog change. Sources: `course-catalog.md` section 3.4, `build.md` sections 5, 13 and 16, backlog NODE-01.

## Audience and prerequisites

Learners who know JavaScript and SQL and want to build a server. Node.js is a JavaScript runtime, not a new language (`build.md` section 5). Teaching it does not change the platform's own backend.

- **Required:** `js` and `sql`.
- **Suggested:** `git`.

## Outline

| Unit | Title | Lessons (proposed IDs) |
| --- | --- | --- |
| `node.u01` | Your machine | `node.install`, `node.run-a-script`, `node.npm-and-lockfiles`, `node.safe-packages` |
| `node.u02` | Async JavaScript | `node.callbacks-to-promises`, `node.async-await`, `node.errors-in-async` |
| `node.u03` | A first API | `node.http-server`, `node.routes`, `node.json-responses`, `node.status-codes` |
| `node.u04` | Trust nothing | `node.validate-input`, `node.api-contracts`, `node.secrets-and-env` |
| `node.u05` | A database | `node.connect-sqlite`, `node.parameterized-queries`, `node.migrations` |
| `node.u06` | Auth concepts and tests | `node.sessions-concepts`, `node.test-an-api`, `node.read-logs` |

## Projects and evidence

A small API with routes, validation and a database, on the learner's machine. Evidence is **self-reported** against a published rubric, optionally with a link to their practice repository. Earlier evidence labels stay stricter than this one.

## Runtime and safety

**The server never runs a learner's Node code.** That is the one decision this course cannot bend on. `build.md` section 16 proposes "local tutorials for Node/C initially".

| Part | Where | Checked how |
| --- | --- | --- |
| Async and logic | The `js` worker, in the browser | ENG-03 and ENG-06 |
| Reading a server's behaviour | **A simulated request and response in the page:** the learner's handler function runs in the `js` worker, with a fake request object | Function-call cases |
| A real server | The learner's own machine | ENG-09 "read and confirm", and a rubric |

| Threat | Control |
| --- | --- |
| Installing a harmful package | `node.safe-packages` comes early. Lessons name exact packages and versions, which are reviewed each term |
| A secret committed | `node.secrets-and-env`, and `git.committed-a-secret` before it |
| Setup commands damaging a machine | Explain each one first. A disposable folder only, with no `sudo` |
| A learner exposes a server to the internet | Bind to `localhost` in every example, and say why |

**Not proposed:** an in-browser Node system (such as a commercial browser-based runtime), because licensing and cost were not checked and it would be a large dependency. A hosted runner is also out: isolation and quotas cost money, and it would mean running learner code on a server.

## Dependencies

None in the product. Learners install Node.js and a small number of named packages on their own machines, at no cost.

## Checker features required

- The `js` runtime, with a fake request and response harness.
- ENG-09's local-tutorial type.
- Optional: a learner runs a provided test script locally and reports the result, labelled self-reported.

## Risks

- **It cannot be auto-checked for real.** Evidence is weaker here, and labels must say so.
- **Setup differs by system.** Windows, macOS and Linux all need steps, and only macOS is available to test now.
- **Package advice ages quickly,** so keep it in short, dated lessons.
- **Younger learners installing software.** Note that this may need a parent's help.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. Is self-reported evidence acceptable for the real-server parts? *Recommended: yes, with a clear label and no skill badge from it alone, as ENG-09 says.*
2. SQLite or PostgreSQL in projects? *Recommended: SQLite, because it costs nothing and needs no service.*
3. Which web framework, if any? *Recommended: Node's built-in `http` first, then decide. Naming one here is premature.*

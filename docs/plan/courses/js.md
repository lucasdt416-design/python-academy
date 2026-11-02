# JavaScript and the DOM (`js`): course design

Status: **proposed**, written 2026-11-02. No code and no catalog change. Sources: `course-catalog.md` section 3.4, `teaching-design.md` section 6.4, `build.md` sections 5 and 7.

## Audience and prerequisites

Learners who finished `web` and want interactive pages.

- **Required:** `web`, plus `py.u01` to `py.u05`.
- **Suggested:** `git`.

## Outline

| Unit | Title | Lessons (proposed IDs) |
| --- | --- | --- |
| `js.u01` | Python to JavaScript | `js.values-and-let`, `js.conditions`, `js.loops`, `js.functions` |
| `js.u02` | Collections | `js.arrays`, `js.objects`, `js.map-and-filter`, `js.equality-traps` |
| `js.u03` | The page | `js.find-elements`, `js.change-the-page`, `js.events`, `js.event-order` |
| `js.u04` | State and forms | `js.state`, `js.form-input`, `js.useful-errors`, `js.local-storage` |
| `js.u05` | Talking to servers | `js.http-basics`, `js.promises`, `js.fetch-from-a-fixture`, `js.when-it-fails` |
| `js.u06` | Your dashboard | `js.plan-the-app`, `js.keyboard-and-focus`, `js.check-your-app` |

## Projects and evidence

**Interactive study dashboard** (`build.md` section 7): add, edit and filter tasks with useful errors. Function behaviour is automated as practice evidence; the finished project follows a published rubric, and is self-assessed or reviewed.

## Runtime and safety

This is the riskiest runtime in the plan, because JavaScript is the language the host page runs. Two parts are needed.

**Part 1: a JavaScript worker, for language lessons.** The same limits as the Python worker: fresh worker per run, time limit by terminating it, output cap, no network.

| Threat | Control |
| --- | --- |
| Code calls the app's API with the learner's cookies | The worker has the app's origin. Remove `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `importScripts`, `caches` and `indexedDB`, as `python-worker.js` does for most of these, with a `connect-src 'none'` policy on the worker file as the real barrier |
| An endless loop | Terminating a worker always works |
| Code needs `eval` to run | Needs `'unsafe-eval'` in **this worker's** policy only, never the page's. This is a new setting to review |

**Part 2: a scripted preview, for DOM lessons.** A sandboxed `iframe` with `allow-scripts` and **without** `allow-same-origin`, and a policy of `default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'`.

| Threat | Control |
| --- | --- |
| Scripts reach the app | The opaque origin blocks cookies, storage and the parent's page |
| Data is sent out | `default-src 'none'` blocks connections. Navigation can still carry data out: no `allow-top-navigation`, and `navigate-to` is not available in browsers, so this needs testing |
| **An endless loop freezes the whole page** | **Unsolved.** A sandboxed frame may share the page's thread, so nothing can stop it. Options: serve the preview from a separate origin so browsers may isolate it (not guaranteed); rewrite loops to count, which needs a JavaScript parser, a new dependency; or keep DOM tasks short and warn. This needs a decision before building |
| `postMessage` from the frame is forged | The page treats it as untrusted: checks the source frame and accepts only a fixed shape |

`js.local-storage` needs its own answer, because an opaque origin has no storage: a small stand-in, explained honestly to learners.

## Dependencies

None for the plain design. A loop-rewriting parser, if chosen, would be a new dependency and stops this stage to ask.

## Checker features required

- The ENG-03 contract, for a second language: the plan, the reports and the judge need no change, and the runner would choose the worker.
- ENG-06's function-call cases, for JavaScript values. `undefined`, `NaN` and `==` need their own equality rules.
- Event-driven cases: "after clicking this, the list holds 3 items", reported from inside the preview.
- Friendly explanations of JavaScript's errors, the ENG-04 work again for a new language.

## Risks

- **A new attack surface.** The code runs under the app's origin in Part 1, and a mistake there touches accounts. This stage needs its own security review.
- **Copy-pasted code.** A learner may run something from elsewhere, so controls must hold against hostile code, not only mistakes.
- **Two languages at once.** `=` and `==`, truthiness and `let` conflict with Python habits.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. How should an endless loop in a DOM task be handled? *Recommended: decide after a test on real browsers of a separate-origin preview. A separate origin may be a new Render service or setting, which would be yours to make.*
2. Is `'unsafe-eval'` acceptable in the worker's policy only? *Recommended: yes, if tests prove the page's policy is unchanged. Pyodide's worker policy is the model to compare with.*
3. Should a framework be taught? *Recommended: no. `build.md` puts HTML and CSS before advanced JavaScript and frameworks.*

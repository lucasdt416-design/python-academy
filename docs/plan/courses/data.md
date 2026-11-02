# Data Investigation with Python (`data`): course design

Status: **proposed**, written 2026-11-02. No code and no catalog change. Sources: `course-catalog.md` section 3.4, `build.md` sections 5 and 7.

## Audience and prerequisites

Learners who want to answer an original question with data.

- **Required:** `py` through `py.u09` (files, CSV and JSON), plus `sql`.
- **Suggested:** `cs`.

## Outline

| Unit | Title | Lessons (proposed IDs) |
| --- | --- | --- |
| `data.u01` | Asking a good question | `data.questions`, `data.where-data-comes-from`, `data.read-a-dataset` |
| `data.u02` | Cleaning | `data.missing-values`, `data.bad-rows`, `data.types-and-units` |
| `data.u03` | Summarising | `data.counts-and-groups`, `data.mean-and-median`, `data.spread` |
| `data.u04` | Showing it | `data.text-charts`, `data.choosing-a-chart`, `data.charts-that-mislead` |
| `data.u05` | Claims and limits | `data.correlation`, `data.sample-size`, `data.say-what-you-did-not-check` |
| `data.u06` | Your investigation | `data.plan`, `data.document-the-data`, `data.write-it-up` |

## Projects and evidence

**Data investigation** (`build.md` section 7): answer an original question with documented data. Computation steps can be automated on fixtures as practice evidence. The write-up follows a published rubric: never an automated pass on its own.

## Runtime and safety

**The existing Python worker with ENG-08's in-memory file fixtures.** The harness loads a CSV for each case, and it is gone afterwards. **No network**, so no downloads and no live APIs.

| Threat | Control |
| --- | --- |
| Personal data in a dataset | Original or clearly licensed datasets only, checked for people's details. Licence recorded beside each file |
| A learner's own dataset | Stays in the browser, and is never uploaded. Say so plainly. If it might hold personal details, say not to use it |
| Large files freezing the page | A size cap on fixtures. The worker's time and output limits are unchanged |
| Hidden data | A hidden fixture's rows reach the browser, as in `sql.md`. Expected results stay on the server |

## Dependencies

**None for the core.** The `csv` and `statistics` modules are in Python's standard library, and need ENG-07's allowlist. Text charts need nothing.

Real charts would need `matplotlib`, and table work would need `pandas`, both Pyodide packages. They add a large download and the network access to fetch it, so they are not part of this design. If wanted, that is a new dependency and stops to ask.

## Checker features required

- **ENG-08** virtual files. **ENG-07** for `csv`, `json` and `statistics`.
- **ENG-06** function-call cases, with `tolerance` for averages.
- **ENG-09** rubric and self-review for write-ups.
- A fixed seed for anything random, as ENG-07 says.

## Risks

- **Teaching false confidence.** A small dataset can suggest a false pattern, so `data.u05` is core, not extra.
- **Dataset licences.** Every file needs a recorded source and licence, which takes time.
- **Depends on a lot.** `py.u09` and `sql` must exist first, so this course is far off.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. Are text charts enough at first, with no `matplotlib`? *Recommended: yes. Add real charts only after measuring the download on a phone.*
2. May learners load their own file in the browser? *Recommended: not in the first version, because that keeps the data question simple.*
3. Should datasets be original or real? *Recommended: original for lessons, and one clearly licensed real dataset for the project.*

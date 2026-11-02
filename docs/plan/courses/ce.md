# Engineering Depth (`ce`): course design

Status: **proposed, later**, written 2026-11-02. No code and no catalog change. Sources: `course-catalog.md` section 3.4, `build.md` sections 5 and 6, backlog CE-01.

## Audience and prerequisites

Learners heading into computer engineering. Exact alignment needs a mapping to a student's real course outlines (CE-01). This is not a complete first-year curriculum, and must not be described as one (`build.md` section 6).

- **Required:** `cs`, plus `py` complete.
- **Suggested:** the relevant math for each elective.

## Outline: four separate electives

| Unit | Title | Lessons (proposed IDs) | Runtime |
| --- | --- | --- | --- |
| `ce.u01` | C and memory | `ce.compile-and-run`, `ce.types-and-overflow`, `ce.arrays-and-strings`, `ce.pointers`, `ce.malloc-and-free`, `ce.debug-memory-errors` | Learner's machine |
| `ce.u02` | Discrete foundations | `ce.logic`, `ce.sets-and-functions`, `ce.proof-intuition`, `ce.induction`, `ce.counting`, `ce.graphs` | Reasoning; Python worker |
| `ce.u03` | Numerical methods | `ce.units-and-conversion`, `ce.float-error`, `ce.vectors`, `ce.simple-simulation`, `ce.monte-carlo` | Python worker |
| `ce.u04` | Embedded simulation | `ce.truth-tables`, `ce.state-machines`, `ce.simulated-sensors`, `ce.sampling`, `ce.serial-concepts` | Python worker |

## Projects and evidence

| Project | Evidence |
| --- | --- |
| A C data structure | Self-reported against a rubric, with local tests the learner runs |
| An engineering simulation | Reproducible results with stated assumptions; automated for fixed seeds, rubric for the write-up |
| A virtual sensor dashboard | Automated for state machine behaviour on fixtures; rubric otherwise |

Hardware is always optional: "simulations should be usable without equipment" (`build.md` section 6).

## Runtime and safety

Each elective needs its own analysis, because they differ.

**C and memory.** C compiled for a learner's machine can crash programs and corrupt memory on purpose: that is the lesson.

| Option | Assessment |
| --- | --- |
| Run C on the server | **Rejected.** It is learner code on the server |
| A C compiler in the browser, as WebAssembly | Possible and safe in a worker, but it is a large new dependency, and memory errors do not behave the same way there. That would teach the wrong thing about the very topic. Not proposed at first |
| The learner's own machine, with a free compiler | **Proposed,** as `build.md` section 16 suggests. Reasoning tasks in the browser: trace a pointer, draw memory |

Controls: a disposable folder, no `sudo`, and each command explained. Memory bugs in a learner's own small program affect only that program, because modern systems isolate processes.

**Discrete, numerical and embedded.** The existing Python worker with its limits. `math` and `random` need ENG-07, with seeds fixed by the harness. Answers use `tolerance` (ENG-06). Plotting is left out for now, as in `data.md`.

**Optional hardware.** No purchase is ever required. Lessons involving mains power are not proposed. Anything physical gets a safety review on its own.

## Dependencies

None at first. A browser C compiler or a plotting library would each be a new dependency, and would stop to ask, with name, size, licence and integrity.

## Checker features required

- **ENG-06** with `tolerance`; **ENG-07** for `math` and `random`.
- **ENG-09** local tutorial and rubric types.
- A **memory diagram** task type, for pointers: new, needs no runtime.

## Risks

- **Math level** is well above grade 9. Prerequisites must be honest.
- **Accuracy needs real expertise.** These lessons need a reviewer with subject knowledge, who does not exist yet (`build.md` section 12's accuracy gate).
- **False equivalence with university courses.**
- **Effort.** Four electives is a lot for a small project, so build one, then decide.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. Which elective first? *Recommended: numerical methods. It needs no new runtime, and is useful right away.*
2. Can you share real course outlines for CE-01? *Recommended: yes, when you have them. Without them, this outline is a guess at what helps.*
3. Who reviews accuracy? *Recommended: decide before building. A professor or senior student would be ideal.*

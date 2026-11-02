# Computer Science Foundations (`cs`): course design

Status: **proposed**, written 2026-11-02. No code and no catalog change. Sources: `course-catalog.md` section 3.4, `build.md` sections 5 and 6.

## Audience and prerequisites

Learners heading to university or wanting depth. Not presented as equal to any university course, and no outside affiliation is implied (`build.md` section 6).

- **Required:** `py.u01` to `py.u05`.
- **Suggested:** `py.u06` to `py.u08`.

## Outline

| Unit | Title | Lessons (proposed IDs) |
| --- | --- | --- |
| `cs.u01` | How data is stored | `cs.binary`, `cs.hexadecimal`, `cs.text-encoding`, `cs.float-limits` |
| `cs.u02` | Thinking in steps | `cs.pseudocode`, `cs.tracing`, `cs.invariants` |
| `cs.u03` | Searching | `cs.linear-search`, `cs.binary-search`, `cs.counting-steps` |
| `cs.u04` | Sorting | `cs.selection-sort`, `cs.merge-sort`, `cs.compare-on-real-inputs` |
| `cs.u05` | Recursion | `cs.recursion`, `cs.base-cases`, `cs.recursion-or-loop` |
| `cs.u06` | Data structures | `cs.stacks-and-queues`, `cs.hash-tables`, `cs.trees`, `cs.graphs` |
| `cs.u07` | Your comparison | `cs.design-an-experiment`, `cs.write-it-up` |

## Projects and evidence

**Explain and compare algorithms on real inputs** (`build.md` section 5). Implementations are automated practice evidence. The explanation follows a rubric.

## Runtime and safety

**The existing Python worker,** with nothing new to secure. Mostly reasoning tasks: trace this, predict the step count.

| Concern | Control |
| --- | --- |
| Timing inside the worker is unreliable | Count steps instead of measuring time. Count comparisons through a provided helper, or the learner's own counter |
| Deep recursion | Python's own `RecursionError`, explained by ENG-04. The worker's limits are unchanged |
| Exhaustive tasks | Inputs small enough to finish well within 3 seconds |

## Dependencies

None.

## Checker features required

- **ENG-06** function-call cases.
- **A trace task type:** "what is `low` after step 2?", with an ordered list of answers. New, but needs no runtime.
- **Step-count checks,** to tell binary from linear search by behaviour. No construct rule is needed if the harness counts comparisons by giving a list-like object, which needs ENG-06 to pass non-JSON test objects. **This is a real gap:** ENG-06 only passes plain JSON values, so a design is needed.
- **ENG-09** for write-ups.

## Risks

- **Math reading level.** Grade 9 readers may meet this. Big-O is taught as counting, with no formal definitions.
- **A check that demands one algorithm** could reject a correct different one. State what is being measured, as step count, not the construct.
- **False equivalence.** Say plainly that this is an introduction.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. Should `cs` come before `web` for university-bound learners? *Recommended: leave the order to the goal-based recommendations already planned.*
2. Should outside courses be linked? *Recommended: optional links only, after checking terms, with no claim of equivalence.*
3. Is the amount of proof right? *Recommended: intuition only here. Formal work goes in `ce`.*

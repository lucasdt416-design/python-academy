# Construct rule naming: a proposal

Written 2026-11-02 (America/Toronto), checked against the code on `main` at `59f8d0b`, for master run stage S26.  
Status: **proposed**. Nothing here is decided or built. No code changes until Lucas decides.  
Related: [`browser-checks.md`](browser-checks.md) sections 2 and 4, [`lesson-feedback.md`](lesson-feedback.md) section 6, handoff 22 section 7, handoff 24 section 9, handoff 27 question 2.

## 1. The short version

A browser check can already require or forbid a construct, such as `while` or `eval()`, but **no lesson uses this**, and a learner who fails such a rule gets no tagged hint. This document proposes the names and the judge change that would fix that.

**The main recommendation is to keep not using construct rules unless a lesson truly needs one.** All 9 lessons with browser checks on `main` (unit 2, and part 1 of unit 3) were checked fairly by behaviour alone, and so are the 2 in unit 3 part 2 (PR for S02). A construct rule can reject a correct program, so it should be rare.

## 2. What exists today

| Part | Today | Where |
| --- | --- | --- |
| Declaring a rule | `check.require` and `check.forbid`, lists of construct names, for the whole challenge | `backend/app/content.py`, `BrowserCheck` |
| Finding a construct | Parsing with `ast`. The server never runs the code | `backend/app/browser_checks.py`, `constructs()` |
| Names | `for`, `while`, `if`, `elif`, `def`, `return`, `import`, `f-string`, `list`, `dict`, `comparison`, `input()`, `print()`, `int()`, `float()`, `str()`, `range()`, `len()`, `eval()`, `exec()`, `open()` | `content.py`, `CONSTRUCTS` |
| Failing a rule | `needs_work`, with `failed: {id: null, reason: "construct", construct: <name>}` and `rule: null` | `browser_checks.judge` |
| Use in real lessons | **None.** A script over every file in `backend/content/py/` found no non-empty `require` or `forbid` | Handoff 33 |

## 3. Problems this must solve

| # | Problem | Why it matters |
| --- | --- | --- |
| 1 | **Names do not fit an ID.** `input()` has brackets, and the ID pattern is `^[a-z0-9]+([.-][a-z0-9]+)*$` | A rule ID must fit that pattern |
| 2 | **No rule ID, so no tagged hint.** `rule` is null for a construct failure, and `content.feedback_errors` accepts only error names and rule IDs | The learner gets one generic sentence: "This task asks you to use a while loop." |
| 3 | **The construct is checked before the cases.** A program that prints the wrong thing and lacks the construct hears only about the construct | The learner cannot tell whether the program works |
| 4 | **`elif` is not detected reliably.** `else:` with an `if` inside it gives the same parse tree as `elif`, apart from column numbers (checked in Python 3.12), so `constructs()` counts both as `elif` | Requiring `elif` would pass a program that does not use it. The message would be untrue |
| 5 | **No name for "any loop", "a loop inside a loop" or "a function that is called".** `def` only means a definition exists | These are what lessons would most want to ask for |
| 6 | **Parsing sees code that never runs.** `if False:` with a `while` inside it satisfies `require: ["while"]` | Wording may only claim what was checked: "your code contains", never "your code uses" |

## 4. The proposal

### 4.1 Rule IDs

| Rule | Proposed ID | Example |
| --- | --- | --- |
| A required construct is missing | `<lesson>.require.<name>` | `py.decompose.require.called-function` |
| A forbidden construct is present | `<lesson>.forbid.<name>` | `py.sets.forbid.list` |

These follow handoffs 22 and 24. They mirror the content fields, sit apart from `<lesson>.case.<case id>`, and start with the lesson ID as `feedback_errors` requires.

### 4.2 ID-safe names

Names that already fit stay the same, so nothing in the content format has to be renamed: `for`, `while`, `if`, `elif`, `def`, `return`, `import`, `f-string`, `list`, `dict`, `comparison`.

Calls lose their brackets only inside the rule ID, through a fixed table:

| Construct | Name in a rule ID |
| --- | --- |
| `input()` | `call-input` |
| `print()` | `call-print` |
| `int()` | `call-int` |
| `float()` | `call-float` |
| `str()` | `call-str` |
| `range()` | `call-range` |
| `len()` | `call-len` |
| `eval()` | `call-eval` |
| `exec()` | `call-exec` |
| `open()` | `call-open` |

Three new names (problem 5), all found by parsing:

| Name | Meaning | Honest limit |
| --- | --- | --- |
| `loop` | Contains a `for` or a `while` | A comprehension counts, as it does for `for` today |
| `nested-loop` | A `for` or `while` inside the block of another | A loop inside a function called from a loop does not count, so such a program would fail. See section 5 |
| `called-function` | A `def` whose name is also called somewhere in the file | A call on a branch that never runs still counts |

### 4.3 The judge

1. **Return a rule ID:** `rule: <lesson>.require.<name>` or `<lesson>.forbid.<name>`. The `failed` object stays exactly as it is, so this is additive.
2. **Accept the tags:** `feedback_errors` adds those IDs, for the names the challenge really lists, to the rules a hint may be tagged with.
3. **Check `require` after the cases, and only if they all passed.** The learner then hears "Your program prints the right thing. This lesson is practising a while loop, so try writing it with one." `forbid` stays first.
4. **Tell `elif` from `else: if`,** by comparing the inner `if`'s column with the outer one's.
5. **Allow a message per rule,** so the wording can name the idea and say why it is asked for. Unit 1's named rules have messages (`lesson-feedback.md` section 6), but today `messages` are for bounded-story checks only, so browser checks would need this added.

Changing the order in item 3 alters what a failing program is told, for checks that use `require`. No real lesson does, so no learner sees a change today. Existing tests of the order use a test fixture and would need updating.

### 4.4 When a lesson may use a rule

Proposed test: **all three must be true.**

1. The construct is the skill being taught, and the lesson would be pointless without it.
2. Behaviour cannot show it: the cases have been tried and cannot tell the programs apart.
3. A fair alternative was considered. If another program is just as good, it passes, and "Other ways" shows it.

`forbid` needs a further reason, such as a lesson on writing something yourself, and is never used to make a task harder for its own sake.

**Practice badges and XP depend on behaviour first.** A rule failure is `needs_work`, never an error, and the learner keeps their code.

## 5. Where this would and would not be used

An implementer's reading of Part 8 of the master run. Each row is **proposed**.

| Lesson | Is a rule needed? | Why |
| --- | --- | --- |
| `py.elif` | No | Built without one. The cases force a single answer, and separate `if`s with one print are correct |
| `py.for-range` | No | A `while` version prints the same and is correct; "Other ways" shows it |
| `py.nested-loops` | No | One loop that works out the row and column is correct, and is shown under "Other ways" |
| `py.functions`, `py.parameters`, `py.return-values` | No | ENG-06 (#34) calls the function by name, which forces a real function by behaviour |
| `py.scope` | Probably not | A function-call check can see whether the score changed |
| `py.decompose` | **Maybe the first real use** | Splitting a program up cannot be seen from what it prints. `called-function` is too weak to prove good design, so a rubric (ENG-09) may fit better |
| `py.classes`, `py.composition` | Probably not | ENG-06 can call the constructor. `class` is not on the construct list, and would be added only if needed |
| Unit checks (ASSESS-02 onward) | Decide with B-A1 | Handoff 27 question 2 suggests revisiting here. A "write it with a loop" task might use `loop` |

So there may be **no lesson that needs this before unit 5,** and possibly none at all.

## 6. If it is built: what the tests need

- Each name found and not found, by parsing, including `elif` against `else: if`, a nested loop, and a function defined but not called.
- Every rule ID fits the ID pattern, and each is accepted as a hint tag only when the challenge lists that name.
- `require` is checked only after every case passes. `forbid` is checked first.
- Wrong output plus a missing construct reports the wrong output.
- Older answers are unchanged: `failed` has the same shape, and units 1 to 3 snapshots still pass.
- Hidden expected output is still never sent.
- At least three deliberate breaks.

No migration and no new dependency are needed.

## 7. Questions for the owner

Each recommendation is **recommended, not yet confirmed**.

1. **Naming.** Use `<lesson>.require.<name>` and `<lesson>.forbid.<name>`, with `call-input` for calls? *Recommended: yes. Handoffs 22 and 24 suggested `uses-input` and `no-import` as names, but a name with "uses" inside `.require.` says it twice, and the same name now works for both lists.*
2. **Build it now, or wait?** *Recommended: wait until a lesson needs it, and make the first such lesson's PR carry the change. The `elif` fix is the exception: a small separate fix would keep the judge truthful, but nothing depends on it yet.*
3. **The test in section 4.4.** Adopt it as the rule for lessons? *Recommended: yes.*
4. **The order in section 4.3, item 3.** Check `require` only after every case passes? *Recommended: yes, so a learner always hears first whether the program works.*
5. **`py.decompose`.** A construct rule, or a rubric? *Recommended: a rubric, with ENG-09, because no parser can tell whether a program is well split up.*

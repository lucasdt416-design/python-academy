# Placement: questions and tasks for unit 1 (EDU-01)

Written 2026-11-09 (America/Toronto) for master run stage WE8. Status: **proposed.** Nothing here is built or decided.  
Related: [Issue #4](https://github.com/lucasdt416-design/python-academy/issues/4), [`course-catalog.md`](course-catalog.md) sections on placement and prerequisites, [`retention.md`](retention.md) (placement answers), [`teaching-design.md`](teaching-design.md), [`browser-checks.md`](browser-checks.md).

## 1. The short version

An optional skills check, after registration, for a learner who may already know some Python. It covers the four skills of unit 1: `print()`, variables, `input()` and `if`/`else`. Each skill gets **one question and one small task, in different contexts**. A skill counts as shown only when both are right. A learner who shows all four could start at unit 2, with a recap card. **Placement never gives XP, badges or completion,** and every lesson it skips stays open.

Every expected answer below was run in Python 3.12 (section 7).

## 2. What it is for, and what it is not

| It is | It is not |
| --- | --- |
| A suggestion of where to start | A test, a grade or a gate |
| Optional, with "Start from the beginning" first | Something a beginner has to sit through |
| Based on what the learner does, with their own say as a first step | Based on a self-rating alone |
| Separate from earned progress | A way to earn badges or XP |

## 3. The check, step by step (proposed)

1. **"Have you written Python before?"** *Not yet* goes straight to unit 1, lesson 1, with no questions. *A little* and *Yes* go on.
2. **Four short parts, one per skill, in unit order.** Each part is a predict question, then a task.
3. **Stop early, kindly.** After a skill isn't shown, the check stops and suggests starting at that skill's lesson: there is no point asking about `if`/`else` when `print()` is new.
4. **The suggestion,** with its reason in one sentence, and three buttons: accept, start earlier, or choose any lesson.

**Length:** at most 4 questions and 4 tasks, about 10 minutes. **One card at a time,** like the lessons.

## 4. Questions and tasks

Each question has one right answer and distractors that match a real misconception, so a wrong choice says what to practise. The tasks use the same browser checks as challenges, with hidden cases.

### 4.1 `print()` (lesson `hello`)

**Question.** What does this print?

```python
print("Hi")
print("there")
```

| Option | Misconception it catches |
| --- | --- |
| **`Hi` and `there`, on two lines** (right) | |
| `Hi there`, on one line | Each `print()` starts a new line |
| `"Hi"` and `"there"`, with the quotes | Quotes mark text; they aren't printed |

**Task: fix it.** The starter has a bug: `print(Your quest begins)` has no quotes. The learner fixes it so the program prints two lines.

```python
print("Welcome, traveller")
print(Your quest begins)
```

- **Check:** one visible case, expected `Welcome, traveller` then `Your quest begins`.
- **Not shown by:** leaving the bug (a `SyntaxError`), or printing anything else.

### 4.2 Variables (lesson `variables`)

**Question.** What does this print?

```python
place = "cave"
place = "castle"
print("You enter the " + place)
```

| Option | Misconception it catches |
| --- | --- |
| **`You enter the castle`** (right) | |
| `You enter the cave` | A variable keeps its first value |
| `You enter the place` | The name, not the value, is printed |

**Task: write it.** "Make two variables, `hero` and `tool`, and print one sentence using both, such as `Ana packs a map`."

- **Check:** the program must print a line containing both values. A hard-coded sentence also passes behaviour alone, so this task needs a **construct rule** (two assignments), which no lesson has yet ([`construct-rules.md`](construct-rules.md)). **Alternative without one:** give `hero` and `tool` as replies and check the sentence changes with them, which tests `input()` too early. **Question 2 for the owner.**

### 4.3 `input()` (lesson `input`)

**Question.** The player types `Mira`. What appears in Output?

```python
name = input("Name? ")
print("Hello, " + name)
```

| Option | Misconception it catches |
| --- | --- |
| **`Hello, Mira`** (right) | |
| `Hello, name` | The variable's name is printed |
| `Name? Hello, Mira` | The prompt is part of what `print()` shows. In this app, prompts don't appear in Output, as each lesson says (in a terminal they do), so the question asks what appears in Output |

**Task: write it.** "Ask for a name, then a pet, and print `<name> walks with <pet>`."

- **Check:** visible case `Leo` and `a fox` gives `Leo walks with a fox`; hidden case `Sam` and `an owl` gives `Sam walks with an owl`. A hard-coded line fails the hidden case.

### 4.4 `if`/`else` (lesson `choices`)

**Question.** What does this print?

```python
path = "left"
if path == "right":
    print("A river")
else:
    print("A forest")
```

| Option | Misconception it catches |
| --- | --- |
| **`A forest`** (right) | |
| `A river` | The first block always runs |
| `A river` and `A forest` | Both blocks run |

**Task: write it.** "Ask which door the player opens. If it is `gold`, print `Treasure!`; otherwise print `Just dust.`"

- **Check:** visible case `gold` gives `Treasure!`; hidden cases `wood` and `Gold` give `Just dust.` (comparison is exact, as lesson `choices` teaches). Printing `Treasure!` always fails the hidden case.

## 5. From answers to a suggestion

| Shown for a skill | State (`course-catalog.md`) | Effect |
| --- | --- | --- |
| Question **and** task right | independently demonstrated | Its lesson can be skipped |
| Only one right | introduced | Start at that lesson |
| Neither, or not asked | unknown | Start at that lesson, or earlier |

- **Start at the first skill not shown.** All four shown: unit 2, with a recap card of the four skills and the adventure so far.
- **The page never says "failed".** It says, for example: "Let's start with variables. You already know `print()`, so the first lesson is there if you want a reminder."
- **Skipped lessons stay open,** marked "skipped by your skills check", which is different from "done".

## 6. What gets stored

Proposed, for the owner to decide with EDU-02 (`retention.md` lists it as open):

- **The latest result only:** each skill's state and the date. Not the answers or the code.
- Deleted with the account. The learner can retake the check, which replaces it.
- **A parent sees the suggestion and what was skipped, not the answers** (decision 2).
- Recorded as a learner choice when they accept or override it, so "placement override" can be measured (`build.md` section 12).

## 7. How the answers were checked

Each code sample and task above was run in Python 3.12.14, with `input()` replaced by the replies given, the same way the checks run. Outputs, exactly:

| Sample | Output |
| --- | --- |
| 4.1 question | `Hi`, `there` |
| 4.1 task, as given | `SyntaxError` |
| 4.1 task, fixed | `Welcome, traveller`, `Your quest begins` |
| 4.2 question | `You enter the castle` |
| 4.2 task, one answer | `Ana packs a map` |
| 4.3 question, `Mira` | `Hello, Mira` |
| 4.3 task, `Leo`/`a fox` and `Sam`/`an owl` | `Leo walks with a fox`, `Sam walks with an owl` |
| 4.4 question | `A forest` |
| 4.4 task, `gold`, `wood` | `Treasure!`, `Just dust.` |
| 4.4 task, a hard-coded `print("Treasure!")` with `wood` | `Treasure!`, so the hidden case fails it |
| A distractor check: `"Left"` against `"left"` | Not equal, so `else` runs |

## 8. Questions for the owner

Each recommendation is **recommended, not yet confirmed**.

1. **Granularity:** whole lessons or single cards? *Recommended: whole lessons, as above.*
2. **The variables task:** a construct rule, or replies? *Recommended: a construct rule, built with the first lesson that needs one, or leave this task out of the pilot.*
3. **The threshold:** question and task both right? *Recommended: yes. One right is "introduced".*
4. **Retakes:** any time, or once a week? *Recommended: any time, as the result is only a suggestion.*
5. **The pilot (EDU-02):** which skill first? *Recommended: `print()`, the simplest, to test the flow before the content.*
6. **Storage:** latest result only, deleted with the account? *Recommended: yes (section 6).*

# Handoff 48: Placement questions and tasks for unit 1 (master run WE8, EDU-01)

Date: 2026-11-09 (America/Toronto)  
Written by: Claude Code (implementer), in a separate git worktree  
For: the human maintainer, and ChatGPT or Claude chat (reviewer) without repository access  
Status: **in_review**: one pull request (#56), documentation only, not merged. Nothing decided.

> **How to use this file:** upload it with `docs/plan/placement.md`, `docs/plan/course-catalog.md` and Issue #4's text. The pull request diff is the source of truth (`build.md` section 14).

## Starter prompt for the chat assistant

```text
You are reviewing a proposal for Python Academy's optional skills check (placement), for the four
unit 1 skills: print(), variables, input() and if/else. Check that each question has exactly one
right answer, that each distractor matches a real beginner misconception, that each task can't be
passed by hard-coding, and that nothing gives XP, badges or completion. Say whether "question and
task both right" is the right threshold.
```

## Run plan details

| Field | Value |
| --- | --- |
| Stage | WE8, first part: EDU-01 |
| Base | `main`, at `1dc4b59` |
| Part 2 boxes relied on | **None** |
| Skipped | **EDU-02, the pilot:** it needs this design reviewed, and the placement storage decision `retention.md` leaves open |

## 1. Handoff record

| Field | Value |
| --- | --- |
| Task | Write placement question and task examples for the current four skills (Issue #4) |
| Human goal | A learner who knows the basics can start later, without losing anything |
| Non-goals | Building the check; storing anything; deciding |
| Deployment status | None: documents only. Commits carry `[skip render]` |

**Files changed:** `docs/plan/placement.md` (new), `docs/run-log.md`, this handoff and its PDF.

## 2. What it proposes

One predict question and one task per skill, in different contexts. A skill is shown only when both are right. Stop at the first skill not shown and suggest its lesson. All four shown: unit 2 with a recap card. Never XP, badges or completion; skipped lessons stay open and are marked differently from done.

## 3. What was found

| Finding | Effect |
| --- | --- |
| **A variables task can be passed by hard-coding the sentence,** because behaviour alone can't tell `print("Ana packs a map")` from two variables | The task needs a construct rule, which isn't built, or a different design. **Question 2** |
| **The app doesn't show `input()` prompts in Output** (each lesson says so), so "what does this print?" would be unfair for an `input()` question | The question asks "what appears in Output" |

## 4. How it was checked

Every code sample and task was run in Python 3.12.14, with `input()` given the replies in the document. The outputs are in `placement.md` section 7, including that a hard-coded `print("Treasure!")` fails the `if`/`else` task's hidden case. Links to other plan documents were checked to exist.

**Not checked:** no learner has seen these. The misconceptions come from the lessons' own hints and "Let's look again" answers, not from data.

## 5. Questions for you

`placement.md` section 8 has six, each **recommended, not yet confirmed**. The two to answer first:

1. **The threshold:** a skill counts only when both its question and task are right? *Recommended: yes.*
2. **The variables task:** a construct rule, or leave it out of the pilot? *Recommended: leave it out of the pilot.*

## 6. For the docs sync

| Where | What |
| --- | --- |
| Backlog | EDU-01 `in_review` (#56, handoff 48). EDU-02 stays `proposed`, waiting for this and the storage decision |
| Decision log | Under "Open, awaiting the owner": a link to `placement.md` section 8 |

## 7. Next concrete action

Answer the questions, and merge this if you accept it as the proposal.

## 8. Removing the worktree safely

```sh
cd /Users/DEV/Projects/python-academy
git -C ../python-academy-place status --short   # expect nothing
git worktree remove ../python-academy-place
git worktree prune
git branch -d docs/placement-examples
```

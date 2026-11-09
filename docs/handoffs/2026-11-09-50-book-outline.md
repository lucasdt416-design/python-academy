# Handoff 50: The book and course outline, expanded (master run WE11, DOC-03)

Date: 2026-11-09 (America/Toronto)  
Written by: Claude Code (implementer), in a separate git worktree  
For: the human maintainer, and ChatGPT or Claude chat (reviewer) without repository access  
Status: **in_review**: one pull request (#58), documentation only, not merged. Nothing decided.

> **How to use this file:** upload it with `docs/plan/engineering-book-outline.md` and `docs/plan/decision-log.md`. The pull request diff is the source of truth (`build.md` section 14).

## Starter prompt for the chat assistant

```text
You are reviewing an expanded outline for a book and a CS50-style course built from Python
Academy's decision log. Check that every "what broke" in section 2.1 is a real bug from the log or
the handoffs it names, that each exercise can be done safely in a practice copy with free tools,
and that the chapter order would make sense to a first-year student.
```

## Run plan details

| Field | Value |
| --- | --- |
| Stage | WE11: DOC-03 |
| Base | `main`, at `1dc4b59` |
| Part 2 boxes relied on | **None** |

## 1. Handoff record

| Field | Value |
| --- | --- |
| Task | Expand the book and course outline from the decision log |
| Human goal | When the book is written, every chapter already knows its sources and its worked example |
| Non-goals | Writing any chapter; deciding publication |
| Deployment status | None: documents only. Commits carry `[skip render]` |

**Files changed:** `docs/plan/engineering-book-outline.md`, `docs/run-log.md`, this handoff and its PDF.

## 2. What changed

| Where | Change |
| --- | --- |
| Section 2, the parts | From 16 chapters in 7 parts to 27 in 10. New: feedback, honest lessons, privacy and trust, growing the checker, supply chain and operations, accessibility |
| Section 2.1 (new) | For each new chapter: what the reader builds, the real bug used as the worked example, and an exercise |
| Section 3, the course | Weeks 11 to 13: feedback and honest lessons, privacy by design, supply chain and accessibility |
| Section 5 | Notes that the repository is now public, which bears on question 2 |

## 3. How it was checked

Each "what broke" in section 2.1 was taken from decision-log chapters 14 to 22 or the handoffs named, and the handoff numbers were checked against `docs/handoffs/`. **Handoffs 44 to 49 are on open pull requests** (#52 to #57); the outline says chapters built on them wait until they are merged.

**A slip in my first draft:** one row cited "handoffs 29, 41, 45 to 46 of the first batch", which doesn't exist. Corrected to 29, 40 and 41.

## 4. Questions for you

Section 5 of the outline has the four open decisions (audience, repository access, format, order). None is answered here.

## 5. For the docs sync

| Where | What |
| --- | --- |
| Backlog | DOC-03 `in_review` (#58, handoff 50) |

## 6. Next concrete action

Review, and merge if you accept the outline.

## 7. Removing the worktree safely

```sh
cd /Users/DEV/Projects/python-academy
git -C ../python-academy-book status --short   # expect nothing
git worktree remove ../python-academy-book
git worktree prune
git branch -d docs/book-outline
```

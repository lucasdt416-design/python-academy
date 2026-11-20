# Handoff 59: Python Foundations final projects, designed and built first

Date: 2026-11-20 (America/Toronto)  
Written by: Claude Code (implementer), in a separate git worktree  
Status: **in_review**: one pull request ({{PR}}), **based on #66**. A plan, three reference projects and their tests. No app code, migration or dependency changes.

## Starter prompt for the chat assistant

```text
Review docs/plan/courses/py-final-project.md and docs/plan/final-projects/. Three final projects for
Python Foundations (Lockpick, a hangman-style game; Site Builder, a website made by Python; Planner, a
multi-file app with saved data), ranked by difficulty, each built first as a reference version. Check
that the ranking is right, that each reference uses only what the course teaches or the plan's new
lessons add, that the gap list is complete, and that the engineering items (ENG-09, a project
workspace, live play, a sandboxed page preview) are the least needed.
```

| Field | Value |
| --- | --- |
| Request | The owner's message of 2026-11-20: make the final projects before more lessons; three options for different ages and skills, the easiest a hangman game, then a website, then a full app; rank them and recommend what Python Foundations must add. Also: decide the release order and whether the creatures suit 13+ |
| Base | `content/cs-foundations` (#66) |
| Branch and worktree | `plan/py-final-project`, `../python-academy-final` |
| Stage IDs | `py.u12` (EDU-08, WD11). Suggested new: `ENG-12` project workspace, `ENG-13` live play, `ENG-14` sandboxed page preview |

## 1. The three projects

| | Lockpick | Site Builder | Planner |
| --- | --- | --- | --- |
| Level | first-timers, about 13+ | about 14 to 16 | about 16+ |
| Time | 6 to 8 h | 10 to 15 h | 20 to 30 h |
| Reference | `lockpick/` | `site-builder/` | `planner/` (4 modules) |

Ages guide the recommendation only; anyone may choose any project. The plan says plainly that a "full app" in Python Foundations is a command app with saved data and tests, not a graphical one, and how the web, JavaScript and full-stack courses lead on from it.

## 2. What it found

Nothing in the 52 lessons teaches triple-quoted strings, `format()`, HTML, escaping, a command loop or keeping data between runs, and no lesson uses ENG-10. The browser keeps no file between runs, and replies to `input()` are typed before the run, so a game cannot yet be played live. The plan lists **8 new lessons** (plus the 4 already planned that need ENG-09) and **4 engineering items**, in build order. **Lockpick needs only two new lessons**, so it can open first.

## 3. Decisions taken on the owner's behalf

Release #63 to #66 in order; CS keeps units 1 and 3 open, unit 2 waits for ENG-09. All thirteen creatures stay, judged fine for 13+. The home page names CS when its unit 2 opens. (Plan section 5.)

## 4. How it was tested

| Command | Result |
| --- | --- |
| `tests/test_final_project_references.py` (new) | **9 passed**: allowed imports and no file shadowing a Python module (3); each project's own tests pass under the browser's rules (3); Lockpick won and lost rounds with bad guesses explained; Site Builder writes 4 pages with no broken links and no data text turned into tags; Planner saves, reloads in a second run, and survives a damaged file |

Deliberate breaks, each undone: escaping `<` removed (**1 failed**); a damaged save file left to crash (**2 failed**); `import os` added (**1 failed**: the browser refuses it).

## 5. Questions (each recommended, not yet confirmed)

1. **These three projects, in this order?** *Recommended: yes.*
2. **Live play by re-running with all replies so far** (no new headers), rather than cross-origin isolation? *Recommended: yes.*
3. **A sandboxed preview for Site Builder** is a CSP change, shared with the web course. *Recommended: approve when step 4 of the plan is reached.*

## 6. Removing the worktree safely

```sh
cd /Users/DEV/Projects/python-academy
git -C ../python-academy-final status --short   # expect nothing
git worktree remove ../python-academy-final
git branch -d plan/py-final-project
```

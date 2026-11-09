# Handoff 49: Video scripts for unit 1 (master run WE10, EDU-10)

Date: 2026-11-09 (America/Toronto)  
Written by: Claude Code (implementer), in a separate git worktree  
For: the human maintainer, and ChatGPT or Claude chat (reviewer) without repository access  
Status: **in_review**: one pull request, documentation only, not merged. Nothing recorded or decided.

> **How to use this file:** upload it with `docs/plan/video-scripts/unit-1.md` and `docs/plan/teaching-design.md` section 7. The pull request diff is the source of truth (`build.md` section 14).

## Starter prompt for the chat assistant

```text
You are reviewing five short video scripts for Python Academy's unit 1 (print, variables, input,
if/else, and a combined adventure), written to the rules in teaching-design.md section 7. Check
each is one idea, under 6 minutes, has a fair pause-and-predict moment, matches its lesson's own
example and words, never shows the challenge's answer, and that the narration works as captions.
```

## Run plan details

| Field | Value |
| --- | --- |
| Stage | WE10: EDU-10 |
| Base | `main`, at `1dc4b59` |
| Part 2 boxes relied on | **None** |
| Dependency | The backlog lists **PLAN-03** (the teaching design review), which isn't done. The master run gives WE10 no gate. The scripts are text only, so they can be reviewed with it, and changed if it changes |

## 1. Handoff record

| Field | Value |
| --- | --- |
| Task | Video scripts: short, one idea, pause-and-predict, captions and transcripts, lessons work without them |
| Human goal | Optional videos for learners who learn better watching, ready to record if Lucas chooses to |
| Non-goals | Recording, hosting, cost, linking from lessons; units 2 and 3 |
| Deployment status | None: documents only. Commits carry `[skip render]` |

**Files changed:** `docs/plan/video-scripts/unit-1.md` (new), `docs/run-log.md`, this handoff and its PDF.

## 2. Decisions and why

| Decision | Options considered | Reason | Who decided |
| --- | --- | --- | --- |
| Unit 1 only, one video per lesson | Every unit | A sample to review before writing more | Implementer |
| Each video stops at the "Try it" card | Show the challenge | A video must not give the answer | Implementer |
| The narration column is the transcript | A separate transcript | One text to review and keep in step | Implementer |
| Code read aloud once, then described | Read every symbol every time | Easier to follow; captions stay short | Implementer |

## 3. How it was checked

| Check | Result |
| --- | --- |
| Every code sample, with the replies shown, in Python 3.12.14 | **13 of 13 printed exactly the Output in the script**, including the `NameError` and the capital-L `Left` |
| Narration words per script | 133 to 172, so about one minute of speech; with typing, runs and pauses, about 2 minutes each |
| Against each lesson's own example, words and predict question | Read side by side with `backend/tests/fixtures/legacy_lessons_v1.json` |

**A slip in my first draft,** found by counting: it said each video was 2 to 3 minutes of narration. Narration is about one minute; the rest is typing, running and pausing. Corrected.

## 4. Known limitations

- **Not timed with a real recording.** The Time column is an estimate.
- **No learner has seen them.**
- Units 2 and 3 have no scripts yet.

## 5. Questions for you

1. **Record these at all, and when?** *Recommended: after PLAN-03, and after unit 1 has had testers, so the videos answer their real questions.*
2. **Hosting:** something with no trackers and no autoplay, decided separately. *Recommended: decide only if you choose to record.*

## 6. For the docs sync

| Where | What |
| --- | --- |
| Backlog | EDU-10 `in_review`: unit 1 scripts (#PR, handoff 49) |

## 7. Next concrete action

Review, and merge if you accept them as drafts.

## 8. Removing the worktree safely

```sh
cd /Users/DEV/Projects/python-academy
git -C ../python-academy-video status --short   # expect nothing
git worktree remove ../python-academy-video
git worktree prune
git branch -d docs/video-scripts
```

# Handoff 47: Tests that failed only in Firefox or WebKit (QA-03 follow-up)

Date: 2026-11-09 (America/Toronto)  
Written by: Claude Code (implementer), in a separate git worktree  
For: the human maintainer, and ChatGPT or Claude chat (reviewer) without repository access  
Status: **in_review**: one pull request (#55), not merged. **Test changes only:** nothing a learner sees changes.

> **How to use this file:** upload it with handoff 42. The pull request diff is the source of truth (`build.md` section 14).

## Starter prompt for the chat assistant

```text
You are reviewing two test fixes for Python Academy, after the first Firefox and WebKit report.
Check that each still fails when the thing it protects is broken, in every browser, and that
neither was loosened more than the browser difference needs.
```

## Run plan details

| Field | Value |
| --- | --- |
| Stage | QA-03 follow-up (handoff 42 section 7) |
| Base | `main`, at `1dc4b59` |
| Part 2 boxes relied on | **None** |
| Merge order | Any. Conflicts only in `docs/run-log.md`, with other PRs from tonight |

## 1. What failed, and why

The last report on #50 (commit `843ea72`): Firefox 1 failed of 324, WebKit 3 failed of 324.

| Test | Browsers | Cause | Change |
| --- | --- | --- | --- |
| "the app refuses to be shown inside a frame" | Firefox, WebKit | **The test,** not the app: it waited for Chromium's own console message and its `chrome-error:` page. Other browsers refuse the frame in their own way | Now checks what the frame holds, beside a control frame that proves the test can see inside one, and the header itself |
| "every unit 1 card, hint and result reads exactly as before UI-05" | WebKit | **The test:** WebKit's `innerText` reports the lesson `<progress>` bar as two extra blank lines | Runs of blank lines count as one, on both sides. Every line of text must still match |
| "after the fifth lesson the unit is complete" | WebKit | **Not established.** It waited 5 seconds for "badge earned!" once in CI. It passed 3 runs of 3 in WebKit here, and the same file has failed once before in Chromium under load (handoff 41) | **No change.** The weekly report will show if it recurs |

## 2. Files changed

`frontend/tests/academy.spec.ts`, `frontend/tests/unit1-unchanged.spec.ts`, `docs/run-log.md`, this handoff and its PDF.

## 3. How it was tested

| Command | Result |
| --- | --- |
| The frame test in Chromium and Firefox | **Passed in both** |
| The unit 1 snapshot test in Chromium, Firefox and WebKit | **Passed in all three** |
| `unit3-part2.spec.ts` in WebKit, 3 times | **24 passed, each time** |
| The full suites, and Firefox and WebKit on this branch | In CI. I started the cross-browser report on this branch by hand |

### Deliberate-break controls (each undone; files matched saved copies byte for byte afterwards)

| What I broke | Tests that failed |
| --- | --- |
| B1. The frame headers removed (`frame-ancestors` in `proxy.ts` and `next.config.mjs`) | **1** |
| B2. One word of unit 1 changed ("could" to "can") | **1** |

## 4. Known limitations

- **The frame test waits 1.5 seconds** before looking inside the refused frame, because no browser announces a refusal in a way every browser shares.
- **The unit 3 failure in WebKit is unexplained.**

## 5. Questions for you

None.

## 6. For the docs sync

| Where | What |
| --- | --- |
| Backlog | QA-03: the first report's test-only failures fixed (#55, handoff 47) |

## 7. Next concrete action

Review and merge.

## 8. Removing the worktree safely

```sh
cd /Users/DEV/Projects/python-academy
git -C ../python-academy-xb status --short   # expect nothing
git worktree remove ../python-academy-xb
git worktree prune
git branch -d qa/cross-browser-fixes
```

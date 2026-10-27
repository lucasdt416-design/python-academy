# Handoff 14: Decision log, handoff template and book outline (DOC-01, DOC-02)

Date: 2026-10-26 (America/Toronto)  
Written by: Claude Code (implementer), overnight session  
For: the human maintainer, and ChatGPT or Claude chat (reviewer) without repository access  
Status: **in_review**: one pull request, not merged, not deployed. **Documentation only**: no application code, content, tests, settings or deployment changed.

> **How to use this file:** upload it with `build.md` (section 14, the updated handoff template), `docs/plan/decision-log.md` and `docs/plan/engineering-book-outline.md`. The pull request diff is the source of truth (`build.md` section 14). This is the first handoff written with the new template.

## Starter prompt for the chat assistant

```text
You are reviewing Python Academy DOC-01 and DOC-02, which are
documentation only: an updated handoff template with three new sections
(decisions and why, bugs found and fixed, how it was tested), a decision
log backfilled from handoffs 01 to 11, PRs and commits, and an outline
for a book and a CS50-style course built from it. I'm attaching build.md,
the decision log, the outline and this handoff. Check that every claim in
the log traces to a named source, that nothing missing was invented
(look for "reasoning not recorded"), that the plain-language explanations
are right for a first-year student, and that the glossary is accurate.
```

## 1. Where we are

| Stage | What | Status |
| --- | --- | --- |
| 10 | ASSESS-07 honest unit 1 checks | Merged (PR #16); your live check not yet recorded |
| 11 | ENG-03 browser behaviour checks | PR #17, open. This PR does not depend on it; the log describes it as in review |
| 14 | DOC-01, DOC-02 decision log | **in_review**: this PR |

## 2. Handoff record (build.md template)

| Field | Value |
| --- | --- |
| Task | DOC-01: every future handoff records decisions, bugs and testing. DOC-02: a decision log backfilled from the start, and an outline for a book and a course |
| Human goal | Keep the reasoning, mistakes and evidence behind the platform, so a first-year student can learn from how it was really built |
| Relevant build.md sections | 14 (handoff template), 15 (learn while building), 18 (decision records) |
| Repository and branch | `torontojohn/python-academy`, branch `docs/decision-log` |
| Base commit | `27ab31b` (`main` after PR #16) |
| Implementer / reviewer | Claude Code / owner, plus ChatGPT or Claude chat |
| Deployment status | Not applicable (documentation only); not merged |
| New dependencies | None |

### Files changed

| File | Change |
| --- | --- |
| `build.md` | Section 14's handoff template gains "Decisions and why", "Bugs found and how they were fixed" and "How it was tested", with a plain-language explanation of each and of unit, API, browser and live tests, mocks and deliberate-break controls. Section 2 lists the two new documents |
| `docs/handoffs/README.md` | Says that from handoff 14 on every handoff has the three sections, which also feed the decision log |
| `docs/plan/decision-log.md` | New. 14 chapters: the first version, the plan, stages 1 to 11 (ENG-01 to ENG-03), and recurring patterns. Each has the three sections, sources and a running glossary of 55 entries |
| `docs/plan/engineering-book-outline.md` | New. A 16-chapter book outline in 7 parts with appendices, and an 11-week CS50-style course with a final project |

### Acceptance criteria

- The handoff template includes the three sections, with terms explained for a first-year student. **Met** (`build.md` section 14).
- `decision-log.md` is backfilled from handoffs 01 to 11, the merged PR descriptions and the commits: one chapter per stage with the three sections, "reasoning not recorded" where it was not recorded, and a running glossary. **Met.**
- `engineering-book-outline.md` has a chapter outline for a long PDF and a CS50-style course outline using this app. **Met.**
- Handoff 14 in md and pdf; backlog not edited; nothing merged. **Met.**

## 3. Decisions and why

| Decision | Options considered | Reason |
| --- | --- | --- |
| Put the three sections inside the existing template in `build.md` section 14, with the explanations right under it | A separate template file | The template already lives there, and every handoff points to `build.md` section 14 |
| One log chapter per **stage**, plus a chapter 0 for the work before stage 1 and a final "patterns" chapter | One chapter per handoff; one per PR | Stages match how the work was planned and reviewed. Stage 6 had two PRs (the bypass fix) that belong to one story |
| Add a chapter for the first version (PRs #1 to #3), although no handoff exists for it | Start at handoff 01 | The task included "the commit history", and those PRs made the decisions everything else rests on (for example, never running learner code on the server) |
| Use the plan's recorded alternatives and consequences for decisions 1 to 23 | Writing "reasoning not recorded" for all of them | `course-catalog.md` section 9 records alternatives and consequences. Where it gives a consequence but no reason, the log says so |
| Include small bugs that appear only in the implementer's session notes, labelled **(implementer's session notes)** | Leave them out | They are real and useful for teaching, and handoffs had no section for them before. The label makes clear they cannot be checked against a handoff |
| Describe stage 11 (PR #17) from its handoff on the open branch, marked "in review" | Leave it out until merged | The task asked for handoffs 01 to 11. The log changes nothing in that PR |
| Number this handoff 14 | Number it 12 | As the task asked. Numbers 12 and 13 are left unused, as assumed in section 7 |

## 4. Bugs found and how they were fixed

No bugs in code, which did not change. Found while writing the log:

- **Handoff 11 omitted two bugs** that the new Playwright tests had caught and that were fixed before the PR:
  - the wrong line number for `EOFError`
  - a last line of output lost without a newline

  They are now in the decision log, chapter 12, labelled as session notes. This is exactly the gap the new template closes.
- **Handoff 06's small test-writing fixes** (the `localhost` origin, test addresses, Chromium Local Network Access, an ambiguous locator) were also never recorded in a handoff. They are now in chapter 7, labelled the same way.
- **First draft of the log:** it said "reasoning not recorded" for the owner's decisions 1 to 23, although `course-catalog.md` section 9 records alternatives and consequences. It was corrected before the PR, after re-reading that section.

## 5. How it was tested

- **Source checks:**
  - Every chapter names its sources (handoffs, PRs, commits).
  - Every table row was written from those sources, which were re-read in this session: handoffs 01 to 04 in full, PRs #1, #2, #3 and #6, the commit messages, and `course-catalog.md` section 9. Handoffs 05 to 11 were written in this working session and re-checked against their text.
- **Link check:** every relative link and every in-page anchor in the two new documents resolves (scripted check).
- **Full test suites,** run although nothing executable changed, to show `main` plus this PR is still green:

  | Command | Result |
  | --- | --- |
  | `cd backend && .venv/bin/python -m pytest -q` | `213 passed, 9 skipped` |
  | `cd frontend && npm run build` | Compiled successfully |
  | `cd frontend && CI=1 npm run test:e2e` | `30 passed` |

- **Mocks:** none; documentation only.
- **Deliberate-break controls:** not applicable; there was no code to break.
- **What a review should check:** this log is a summary written by the implementer, so a second reader should spot-check a few rows against their named sources. The starter prompt asks for that.

## 6. Backlog changes (not edited, as instructed)

Please add when convenient:

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| DOC-01 | Next | Every handoff includes "Decisions and why", "Bugs found and how they were fixed" and "How it was tested" (`build.md` section 14) | None | in_review (handoff 14) |
| DOC-02 | Later | Decision log (`docs/plan/decision-log.md`), kept up to date each stage, and a book and course built from it (`docs/plan/engineering-book-outline.md`) | DOC-01 | in_review (handoff 14): log backfilled and outline proposed; book and course not written |

Also add a stage row: "14. DOC-01 and DOC-02 | Decision log and handoff template | in_review (handoff 14)". The rows for stage 11 (ENG-03) are listed in handoff 11 section 6.

## 7. Assumptions

1. **Handoff number 14**, as asked. If 12 and 13 are meant for other work, those numbers are free; nothing here refers to them.
2. **"Stage" chapters:** the log groups PR #11 and its fix PR #12 into one chapter, and adds chapters 0 (first version) and 1 (plan), which had no handoffs.
3. **The CS50-style course** borrows only the format (lectures, sections, problem sets, final project). It is not affiliated with Harvard or CS50, and the outline says so.
4. **The book and course are not written yet,** only outlined. Publication and audience are open decisions (outline section 5).

## 8. Live checks for you

Nothing is deployed by this PR. Instead:

- [ ] **Template:** open `build.md` section 14, "Handoff template". The three new sections appear between "Data migration / compatibility implications" and "Known limitations", with the explanations below the template.
- [ ] **Spot-check the log:** pick any two rows in `docs/plan/decision-log.md` and open the named source (for example handoff 07 for chapter 8). The row should say what the source says. Note any row that doesn't.
- [ ] **"Reasoning not recorded":** search the log for it. There should be a handful, mainly in chapter 0 (the stack choice and the age rules) and in decisions where only a consequence was recorded. If you remember a reason, tell me and I will add it with "(owner, recalled on <date>)".
- [ ] **Outline:** read `docs/plan/engineering-book-outline.md` section 5 and answer the four open decisions when ready.
- [ ] **PDF:** open `docs/handoffs/2026-10-26-14-decision-log.pdf` and check it renders.

## 9. Questions for the owner

1. Can you supply the missing reasons for the first version (chapter 0): why this stack, and why the age rules of 13 and over 25? I will record them as recalled, with the date.
2. The four open decisions in the outline, section 5: audience and publication, repository access for students, format, and order.

## 10. Next concrete action

The owner reviews and merges this PR and adds DOC-01 and DOC-02 to the backlog. From the next stage on, each handoff uses the three new sections, and its content is added as a new chapter of `decision-log.md`.

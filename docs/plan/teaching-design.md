# Teaching design: how Python Academy teaches

Last updated: 2026-10-26 (America/Toronto)  
Status: **proposed** (backlog PLAN-03 asks for its review). Documentation only: no content, checker, XP or application change. Nothing here is implemented unless it is labelled as existing.  
Related: [`build.md`](../../build.md) sections 3, 4, 5, 7, 8 and 12; [`course-catalog.md`](course-catalog.md) sections 3, 5 and 12; [`lesson-feedback.md`](lesson-feedback.md) (the feedback engine); [`ai-helper.md`](ai-helper.md) (deferred AI helper); [`backlog.md`](backlog.md).

`build.md` section 4 is the teaching contract every unit already follows: discover, worked example, predict, guided practice, independent challenge, then a project milestone and later retrieval practice. This document explains **why** that contract works, adds the task types it does not yet have, and says how each course applies it. Where this document and `build.md` disagree, `build.md` wins until one is deliberately updated.

## 1. What we are aiming for

From `build.md` section 3: a learner can explain what a program does, change it on purpose, debug a failure, test more than the happy path, and finish an unfamiliar project with less and less help. Each practice below serves one of those five abilities:

| Ability | Main practices |
| --- | --- |
| Explain what a program does | Worked examples, predict-then-run, tracing, explain-in-words |
| Change it on purpose | Guided modification (use-modify-create), fill-in-the-gap |
| Debug a failure | Fix-the-bug tasks, friendly error feedback, reading Python's own message |
| Test more than the happy path | Behaviour checks with several inputs, "try to break it" tasks, later unit tests |
| Finish unfamiliar projects | Small projects, support removed gradually, spaced review, unit checks |

## 2. Principles, the evidence behind them, and how we apply them

The research is summarized in plain terms; full references are in section 10. Findings in education research depend on context, so each principle names what we would measure to see whether it works here (section 9).

### 2.1 Worked examples first, then remove support gradually

- **Evidence.** Beginners learn more from studying worked examples than from solving the same problems unaided, because unaided problem solving uses up working memory on search instead of learning (the "worked-example effect", Sweller and Cooper 1985). The benefit fades and can reverse as learners gain expertise (the "expertise reversal effect", Kalyuga and colleagues 2003). Gradually removing steps from examples ("fading") bridges the two (Renkl and Atkinson 2003).
- **How we apply it.** Every lesson starts with a complete, annotated example. Later tasks in the same lesson hide more of it: change one thing, then fill in a missing part, then write a new program. Across a course, the examples get shorter and the challenges more open (section 4). Learners who already know the material can skip ahead (placement, `build.md` section 9) instead of studying examples they do not need.
- **Existing:** cards 1–2 (discover, example). **Proposed:** fill-in-the-gap and faded examples as new task types.

### 2.2 Predict, then run

- **Evidence.** Reading and tracing code is a separate skill from writing it, and learners who cannot trace code reliably struggle to write it (Lister and colleagues 2004; Lopez and colleagues 2008). PRIMM (Predict, Run, Investigate, Modify, Make; Sentance, Waite and Kallia 2019) builds lessons around predicting first. Committing to a prediction makes a wrong mental model visible, to the learner and to us. Du Boulay (1986) called this mental model the "notional machine": what the learner believes the computer does.
- **How we apply it.** Card 3 already asks a prediction question with an explanation. Proposed: code cards get an optional "predict the output, then run" step (specified in [`lesson-feedback.md`](lesson-feedback.md) section 7). Wrong predictions are the most useful data we collect about misconceptions; they never cost XP or block progress.

### 2.3 Use, modify, create

- **Evidence.** Use-Modify-Create (Lee and colleagues 2011) moves learners from running a working program, to changing it, to making their own. It lowers the starting barrier and keeps a working program in hand at every step.
- **How we apply it.** Card 4 (guided) changes one aspect of the example; card 5 (challenge) creates something new but related. Project milestones extend the learner's own earlier program rather than starting from nothing (`build.md` section 7).

### 2.4 Fill-in-the-gap and Parsons problems

- **Evidence.** Parsons problems give the lines of a correct program in jumbled order, sometimes with a few wrong "distractor" lines, and the learner puts them in order. They take less time than writing the same code, with similar learning gains (Parsons and Haden 2006; Ericson, Margulieux and Rick 2017). Completion problems, which fill a gap in otherwise complete code, are a standard step in fading (2.1).
- **How we apply it.** Two proposed task types: **fill-in-the-gap** (one blank in working code, checked by behaviour) and **arrange-the-lines** (a Parsons problem, checked by running the arranged program). Both work well on phones, where typing code is slow.

### 2.5 Fix-the-bug

- **Evidence.** Debugging is a skill to teach directly, not something learners pick up on the side. Novices tend to make random changes instead of forming a hypothesis. Fixing someone else's small, deliberately broken program in a safe setting teaches reading error messages, locating the fault, and testing the fix.
- **How we apply it.** Proposed task type **fix-the-bug**: a short program with one realistic bug from that unit's misconception list (`build.md` section 4 requires one per unit). The learner first says what they think is wrong (a multiple-choice or one-line answer), then fixes it, and a behaviour check confirms the fix. The friendly error feedback ([`lesson-feedback.md`](lesson-feedback.md)) is the same feedback they get on their own code, so practising on planted bugs transfers.

### 2.6 Subgoals and naming the steps

- **Evidence.** Labelling the steps of a worked example with short subgoal names ("get the input", "decide", "show the result") improved performance and transfer to new problems (Margulieux, Guzdial and Catrambone 2012).
- **How we apply it.** Worked examples carry short comments naming each step, and the same names appear in hints. Content authors list the subgoals for each lesson alongside its learning objective.

### 2.7 Retrieval practice and spaced review

- **Evidence.** Recalling something from memory strengthens it more than re-reading it (the "testing effect", Roediger and Karpicke 2006). Spreading practice over days beats the same amount of practice in one session (Cepeda and colleagues 2006). Both are rated among the most useful study techniques in a large review (Dunlosky and colleagues 2013). Mixing earlier topics into later practice ("interleaving") helps learners choose the right tool, not just use the tool the lesson is about.
- **How we apply it.** Proposed **review cards**: one or two quick questions on earlier material at the start of a lesson, chosen from skills last practised about 1, 3 and 7 days earlier. They are low stakes: no XP lost, no streaks (`build.md` section 4 rules out punitive streaks), skippable, and recorded only as practice evidence. Unit checks (`course-catalog.md` section 12) mix all of the unit's skills.

### 2.8 Small projects as the spine

- **Evidence and rationale.** Projects give a reason to learn the next concept and practise combining skills, which isolated exercises do not. Large unguided projects overwhelm beginners (2.1), so projects are small, staged and scaffolded, with explicit milestones.
- **How we apply it.** Each unit's project (the unit 1 adventure; `course-catalog.md` section 5.3 for later units) grows across lessons. Each milestone is something the learner can run and show. The final project in a course has the least scaffolding.

### 2.9 Feedback that explains the cause and the next step

- **Evidence.** Feedback helps most when it tells the learner where they are, where they are going and what to do next, and when it is about the task rather than the person (Hattie and Timperley 2007; Shute 2008). Research on rewording compiler and interpreter errors for novices is **mixed**: some studies found fewer repeated errors (Becker and colleagues 2016), others no effect (Denny, Luxton-Reilly and Carpenter 2014). The details matter: the location, a concrete next step, and not hiding the original message (Becker and colleagues 2019).
- **How we apply it.** [`lesson-feedback.md`](lesson-feedback.md) specifies the feedback engine. Feedback states only what the check actually observed (section 2.10), and never hands over a full solution.

### 2.10 Honest checks

- **Rule from `build.md` sections 3 and 12.** A check must not claim to judge what it did not test. Creativity, design and meaning are human judgments. An automated message says what it observed ("Python printed two different lines") and, where judgment matters, invites a self-check ("Which line sets the scene, and which is the surprise?").
- **Known gap:** the unit 1 "Open the story" check tells every passing learner "Your scene has a setting and a surprise" without checking either. See [`lesson-feedback.md`](lesson-feedback.md) appendix A and backlog ASSESS-07.

### 2.11 One idea at a time, calm pacing, learner choice

- Cognitive load: keep one teaching card visible at a time, introduce one new idea per card, and split hard concepts across lessons instead of overloading one (`build.md` section 4).
- Motivation: learners choose their goal (`course-catalog.md` section 2) and their story words; progress is private; no timed beginner tasks, no leaderboards, no punitive streaks.

## 3. Task types

| Task type | Existing? | What the learner does | How it is checked | Notes |
| --- | --- | --- | --- | --- |
| Discover | Existing (card 1) | Reads one objective and a short explanation | Not checked | One new idea only |
| Worked example | Existing (card 2) | Studies and runs annotated code | Not checked | Subgoal labels (2.6); different context from the challenge |
| Predict | Existing (card 3, multiple choice) | Commits to what the code will do | Compared with the answer; explanation either way | Proposed: also on code cards (2.2) |
| Guided modify | Existing (card 4) | Changes one aspect of working code | Runs; no pass/fail today | Proposed: a light behaviour check |
| Independent challenge | Existing (card 5) | Writes a new, related program | Server checker today; browser behaviour checks later (ENG-03) | Hints never add up to a full solution ([`lesson-feedback.md`](lesson-feedback.md) section 8) |
| Fill-in-the-gap | Proposed | Completes one blank in working code | Behaviour check | A step between modifying and writing |
| Arrange the lines (Parsons) | Proposed | Orders given lines, may exclude distractors | The arranged program is run and checked | Good on phones |
| Fix-the-bug | Proposed | Names the likely cause, then fixes a planted bug | Behaviour check plus the cause answer | Bugs come from the unit's misconception list |
| Trace | Proposed | Steps through code and records variable values | Compared with the real values from running it | For loops and functions (units 3–5) |
| Explain in words | Proposed | Writes one or two sentences on what code does or why a fix works | Self-check against a model explanation; never auto-graded | Human-judgment evidence, labelled as such |
| Review card | Proposed | Answers a quick question on earlier material | Like a predict or fill-in-the-gap task | Spaced (2.7); no penalty |
| Project milestone | Partly existing (unit 1 adventure) | Extends their own project | Behaviour checks and a short checklist | `build.md` section 7 |
| Unit check | Proposed (ASSESS-02 to ASSESS-05) | Four to six mixed tasks | As above | `course-catalog.md` section 12 |

**Content-format impact.** The content README fixes every lesson at exactly five tasks in a set order. New task types need a deliberate schema change (ENG-01 follow-up, under ASSESS-02 and ENG-03). The existing five-card lessons stay valid.

## 4. Removing support gradually

Support goes down within a lesson, across a unit and across a course:

| Where | High support | Medium | Low |
| --- | --- | --- | --- |
| Within a lesson | Worked example, predict | Guided modify, fill-in-the-gap | Challenge |
| Across a unit | First lesson: starter code with comments | Middle lessons: comment outline only | Project milestone: empty editor and a short brief |
| Across a course | Unit 1: every step named | Units 2–5: steps named in hints only | Final project: brief, rubric and tests only |
| Hints | Hint 1 names the concept | Hint 2 points to the part of the program | Hint 3 shows a partial pattern from a different context; **never a full solution** |

Learners can always go back to earlier examples. Support is never taken away as a penalty.

## 5. Spaced review: proposed rules

- Each skill tag (for example `py.output`, `py.variables`) records when it was last practised.
- At the start of a lesson, offer up to two review cards for skills last practised about 1, 3 or 7 days earlier, and later 30 days.
- A wrong answer shows the explanation and schedules that skill again sooner; it never removes XP or a badge.
- Review data is practice evidence only (`course-catalog.md` section 6.2), with retention decided under OPS-04.
- Needs: the versioned skill evidence in ENG-02 (still open). Until then, review cards can be fixed per lesson (for example, lesson 3 always reviews lesson 1).

## 6. Per-course design

The course IDs follow `course-catalog.md` section 3.3; `ai` is new and proposed here.

### 6.1 Python Foundations (`py`)

- **Who and why.** Complete beginners to first-year engineering students; the entry point for every path.
- **Method.** The full sequence of section 2: worked example, predict, modify, fill-in-the-gap or arrange-the-lines, challenge, project milestone, unit check, review cards. A story project in unit 1 (existing), then the project spine in `course-catalog.md` section 5.3.
- **Task kinds.** All of section 3. Fix-the-bug from unit 1 onwards (missing quotes, `Print` instead of `print`, `=` instead of `==`). Tracing from unit 3 (loops). "Try to break it" tasks and simple tests from unit 8.
- **Checks.** The bounded checker for unit 1; browser behaviour checks (ENG-03) from unit 2 on, with several inputs so hard-coded answers fail.
- **Cautions.** Explain runtime limits before a task hits them (`build.md` section 4). Accept different correct solutions.

### 6.2 Hackathon Ready (`hack`)

- **Who and why.** Learners who know Python units 1–7 and want to build something quickly with others (`course-catalog.md` section 5.5).
- **Method.** Project-based from the start, with **worked examples of decisions** rather than of syntax: a sample idea cut down to a minimum viable product (MVP), a sample time-boxed plan, a sample demo script. Each unit studies one example, critiques a flawed one, then applies it to the learner's own project.
- **Task kinds.** Critique-the-plan (spot the scope creep), cut-list exercises, a fix-the-bug on API error handling with a saved response file, a branch-and-pull-request practice in a safe repository, a two-minute demo script, and a self-assessment against a rubric.
- **Checks.** Mostly rubric and checklist evidence, labelled as self-assessed or reviewed, not automated pass/fail. Automated checks only where behaviour is deterministic (for example, the program works against a saved API response).
- **Cautions.** Never require a real hackathon, public posting, paid hosting, or a live public API for grading.

### 6.3 Git and GitHub Essentials (`git`)

- **Who and why.** Everyone who builds projects; required for contributing to this platform (`build.md` section 15).
- **Method.** Explain the meaning of each command before it is run (`build.md` section 8). A **simulated** repository in the browser comes first, to predict what `status`, `diff` and `log` will show. Then the same steps in a **real, disposable practice repository**. Simulation and real work earn different evidence labels (`build.md` section 8).
- **Task kinds.** Predict the output of `git status` after a change; read a diff and say what changed; put the commit-and-push steps in order (arrange the lines); fix-the-bug on a broken workflow (forgot to stage, committed to the wrong branch); resolve a small planted conflict; write a useful commit message and a pull request description; review a teammate's small pull request.
- **Checks.** In the simulation, the resulting repository state. For real work, the learner pastes a link to their own practice pull request and ticks a checklist. Nothing is auto-verified from their GitHub account without a separate decision.
- **Cautions.** Never ask for tokens or passwords in the app. Teach recovery (`revert`) before any history-rewriting command.

### 6.4 Web Foundations (`web`, then `js`)

- **Who and why.** Practical builders; leads to full-stack work (`build.md` section 5, stage 5).
- **Method.** Structure before style, style before scripting. Each lesson pairs a worked example with a **live preview**. Predict-then-run becomes predict-then-render: "what will this page look like?" Use-modify-create on a personal page that grows through the course. Accessibility is part of every lesson, not a separate unit.
- **Task kinds.** Predict the render; fix-the-bug (an unclosed tag, a selector that matches nothing, a missing `alt` text); fill-in-the-gap in CSS; arrange the HTML structure; keyboard-only and screen-reader checks of their own page; in `js`, trace event order and fix event-listener bugs.
- **Checks.** Structural checks on the HTML (headings in order, labels on inputs, `alt` text) and automated accessibility rules in an isolated preview; visual design is self-assessed or reviewed.
- **Cautions.** Previews must be isolated from the app's own pages and session (`build.md` section 11; WEB-01 designs this). No third-party scripts in previews.

### 6.5 Data and SQL (`sql`)

- **Who and why.** Learners who want to answer questions with data; needed for back-end work (`build.md` section 5, stage 6).
- **Method.** **Question first**: each lesson starts with a question about a small, friendly dataset (for example a course planner or a library) and a worked query that answers it. Predict the result table before running. Build up from one table to joins, then modelling and constraints.
- **Task kinds.** Predict the rows a query returns; fix-the-bug (a missing join condition that duplicates rows, `= NULL` instead of `IS NULL`, an off-by-one date range); fill in the `WHERE` clause; arrange the clauses in order; write a query for a new question; design a small schema and justify one constraint in words; a parameterized query that is safe from SQL injection.
- **Checks.** Compare result sets with the reference query on the sample data **and on a second hidden dataset**, so queries that only fit the visible rows fail. Order matters only when the question asks for it.
- **Cautions.** Isolated in-browser or sandboxed databases only, never the application's database (DATA-01, `build.md` section 13).

### 6.6 Working with AI (`ai`), new and proposed

- **Who and why.** Every learner who will use AI assistants, and contributors to this platform, who already work with Claude and ChatGPT (`build.md` section 14). `build.md` section 8 lists "Working with AI" as a developer-tool tutorial: ask for explanations, inspect diffs, verify generated claims, write a handoff. This course expands it.
- **Method.** **Verify, don't trust.** Worked examples are real assistant conversations and diffs, annotated with what was right, what was wrong and how it was checked. Learners predict whether an AI answer is correct before running it, critique answers, and practise turning a vague request into a clear one. Setup is taught as careful, permission-aware steps in a disposable practice repository, never in a real project first.
- **Proposed units.**

  | Unit | Title | Focus | Task kinds |
  | --- | --- | --- | --- |
  | `ai.u01` | What AI assistants are and are not | What a language model does; confident wrong answers; why tests are evidence | Predict whether a given AI answer is right, then run it; spot the made-up function |
  | `ai.u02` | Asking well | Context, goal, constraints, examples; asking for explanations, not just code | Rewrite a vague request; compare two answers to two requests |
  | `ai.u03` | Setting up Claude | Account, privacy settings, what never to paste (passwords, keys, other people's personal data) | Settings checklist; sort examples into "safe to paste" and "never paste" |
  | `ai.u04` | Claude Code in a practice repository | Install, run in a disposable repository, read the plan, approve or deny permission prompts, review the diff before accepting | Explain a diff in your own words; find the bug in an AI-made change; reject an unsafe permission request |
  | `ai.u05` | AI with GitHub | Branches and pull requests for AI changes; checking an AI-written PR description against the diff; CI as the judge | Find the claim in a PR description that the diff does not support |
  | `ai.u06` | Connecting tools safely | Connectors and integrations (for example GitHub access, MCP servers): least privilege, reviewing and revoking access, tokens kept out of code | Choose the narrowest permission for a task; revoke a practice connection |
  | `ai.u07` | Verify and hand off | Tests as evidence, writing a handoff like `docs/handoffs/`, saying what was not verified | Write a handoff for a small change; review someone else's |

- **Checks.** Mostly self-check and rubric evidence, plus a link to the learner's own practice pull request. The platform never grades a conversation with an AI, and never needs access to the learner's AI accounts.
- **Cautions and open questions (decide before building TOOL-03).**
  - **Age.** Many AI services set a minimum age above 13, and some require 18. Our students can be 13 to 17. Before writing `ai.u03` to `ai.u06`, check each provider's current terms. Units 1, 2 and 7 need no account. For the setup units, the likely options are a parent-led setup, an adults-only label, or a recorded walkthrough instead of hands-on setup.
  - **Cost.** Some tools need a paid plan or paid API credits. The course must have a no-cost path (walkthroughs, simulated sessions) and never require payment to earn its badges (owner rule: free options first).
  - **Change.** These tools change quickly. Keep tool-specific steps in short, dated lessons, separate from lasting skills (verifying, reviewing diffs, protecting secrets), and review them each term.

## 7. Video scripts (proposed, backlog EDU-10)

Short optional videos can help some learners, especially for worked examples and Git or setup steps. Proposed rules:
- **Short:** under about 6 minutes, ideally 2 to 4. Engagement drops sharply for longer instructional videos (Guo, Kim and Rubin 2014).
- **One idea per video**, following the lesson's objective and subgoal labels.
- **Narration matches what is shown on screen**, with the code large enough to read on a phone. Signal the important line and leave out decoration (Mayer 2009).
- **Pause-and-predict moments** in the script ("pause and predict what prints").
- **Captions and a full transcript are required**, and the lesson must work without the video.
- No faces or voices of students; no third-party trackers in the player.

Scripts are written and reviewed as text first (EDU-10). Recording, hosting and cost are separate decisions.

## 8. Review process (backlog PLAN-03)

Before this document becomes `ready`:
1. The owner reads sections 2 to 6 and marks anything they disagree with.
2. A second assistant reviews it against `build.md` sections 3, 4 and 12, looking for overclaims about the research and for conflicts.
3. Pilot one new task type (fix-the-bug or fill-in-the-gap) in unit 2 and observe learners (PILOT-01) before adding the rest.
4. Record decisions in `course-catalog.md` section 9 with date and reason.

## 9. How we will know it works

Proposed measures, from `build.md` section 12 product measures. These are not current results:
- Share of first attempts with errors that are fixed within two more attempts.
- How often learners reveal hint 3, and whether that falls across a unit (support fading).
- Prediction accuracy over time on the same skill (misconceptions shrinking).
- Unit check pass rates for learners who did review cards against those who skipped them, read with care because the groups choose themselves.
- "This was confusing" reports per lesson (FB-05).

## 10. References

These are well-known computing-education and learning-science sources, cited from memory for this design; they were not re-read for this pull request. Check each one before quoting it in learner-facing material.

- Becker, B. A., Glanville, G., Iwashima, R., McDonnell, C., Goslin, K. and Mooney, C. (2016). Effective compiler error message enhancement for novice programming students. *Computer Science Education*.
- Becker, B. A. and colleagues (2019). Compiler error messages considered unhelpful: the landscape of text-based programming error message research. ITiCSE Working Group Reports.
- Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T. and Rohrer, D. (2006). Distributed practice in verbal recall tasks: a review and quantitative synthesis. *Psychological Bulletin*.
- Denny, P., Luxton-Reilly, A. and Carpenter, D. (2014). Enhancing syntax error messages appears ineffectual. ITiCSE.
- du Boulay, B. (1986). Some difficulties of learning to program. *Journal of Educational Computing Research*.
- Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J. and Willingham, D. T. (2013). Improving students' learning with effective learning techniques. *Psychological Science in the Public Interest*.
- Ericson, B. J., Margulieux, L. E. and Rick, J. (2017). Solving Parsons problems versus fixing and writing code. Koli Calling.
- Guo, P. J., Kim, J. and Rubin, R. (2014). How video production affects student engagement: an empirical study of MOOC videos. ACM Learning at Scale.
- Hattie, J. and Timperley, H. (2007). The power of feedback. *Review of Educational Research*.
- Kalyuga, S., Ayres, P., Chandler, P. and Sweller, J. (2003). The expertise reversal effect. *Educational Psychologist*.
- Lee, I. and colleagues (2011). Computational thinking for youth in practice. *ACM Inroads*.
- Lister, R. and colleagues (2004). A multi-national study of reading and tracing skills in novice programmers. ITiCSE Working Group Reports.
- Lopez, M., Whalley, J., Robbins, P. and Lister, R. (2008). Relationships between reading, tracing and writing skills in introductory programming. ICER.
- Margulieux, L. E., Guzdial, M. and Catrambone, R. (2012). Subgoal-labeled instructional material improves performance and transfer in learning to develop mobile applications. ICER.
- Mayer, R. E. (2009). *Multimedia Learning* (2nd edition). Cambridge University Press.
- Parsons, D. and Haden, P. (2006). Parson's programming puzzles: a fun and effective learning tool for first programming courses. Australasian Computing Education Conference.
- Renkl, A. and Atkinson, R. K. (2003). Structuring the transition from example study to problem solving in cognitive skill acquisition: a cognitive load perspective. *Educational Psychologist*.
- Roediger, H. L. and Karpicke, J. D. (2006). Test-enhanced learning: taking memory tests improves long-term retention. *Psychological Science*.
- Sentance, S., Waite, J. and Kallia, M. (2019). Teaching computer programming with PRIMM: a sociocultural perspective. *Computer Science Education*.
- Shute, V. J. (2008). Focus on formative feedback. *Review of Educational Research*.
- Sweller, J. and Cooper, G. A. (1985). The use of worked examples as a substitute for problem solving in learning algebra. *Cognition and Instruction*.

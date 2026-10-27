# Lesson feedback engine (specification)

Last updated: 2026-10-26 (America/Toronto)  
Status: **part 1 built** (merged, PR #22, handoff 15) and **part 2a built, in review** (handoff 19, 2026-10-27): named check rules with messages in the content files (section 6), hints tagged to errors and rules, the similar example and "Other ways to do it" (section 7), the hint-button outline after two failed runs (decision 25), and the unit 1 hints reworded into three levels (ASSESS-08). Not built yet (proposed part 2b): predict-first (section 9), measurements and support data (section 10), and calling the ENG-03 runner from the page (UI-05). Decisions 2 and 3 of section 11 were answered on 2026-10-27 (backlog decisions 24 and 25). Appendix A and the hint rules of section 8 were built for unit 1 by ASSESS-07 (2026-10-26, handoff 10).  
Related: [`teaching-design.md`](teaching-design.md) sections 2.5, 2.9 and 2.10; [`build.md`](../../build.md) sections 4 and 12; [`course-catalog.md`](course-catalog.md) section 7.3; [`ai-helper.md`](ai-helper.md); backlog ENG-03, ENG-04 and ASSESS-07.

The feedback engine decides what a learner sees after they run or check code. It has five parts:

1. Friendly translations of common Python errors
2. The offending line highlighted in the editor
3. Check-specific messages
4. Progressive hints beside the error
5. Predict-first tasks

It must **never reveal a full solution** (section 8).

## 1. What exists today

Read from `frontend/app/adventure.tsx`, `frontend/public/python-worker.js` and `backend/app/lesson_checks.py` at `main` `4848d49`:

- **Python errors** are shown as Python's own message in the output panel, as the Pyodide worker returns it (`String(error)`). The full traceback string is expected to include Pyodide's internal frames; capture real samples before building (section 10).
- **One extra sentence** comes from two patterns: `SyntaxError` or `IndentationError` gives "Check matching quotes and parentheses…", `NameError` gives "Check the variable or function name…". Every other error gives "Read the error above, make one change, and try again."
- **No line highlighting.** The editor is a plain `<textarea>`.
- **Check messages** come from the server's bounded checker, one message per failed rule, with result states `passed`, `needs_work`, `execution_error`, `unsupported` and `service_error`. The checker's own syntax message names the line.
- **Hints:** three per challenge, revealed one at a time with "Show next hint". They are not linked to the error shown.
- **Prediction:** only card 3, as a multiple-choice question.
- **Known problems:**
  - Hint 3 of `hello`, and hints 1 and 2 of `input` together, were complete passing answers (section 8). Fixed by ASSESS-07.
  - The `hello` success message claimed something the check did not test (appendix A). Fixed by ASSESS-07.

## 2. Goals and non-goals

**Goals:**
- Every error message says **what happened, where, the likely cause, and one next step**, in words a beginner knows.
- Python's original message stays one click away, so learners also learn to read real errors (Python unit 6 teaches tracebacks properly).
- Feedback is tied to the lesson: an error about something not yet taught gets a gentle message, not jargon.
- Hints become more specific step by step, appear next to the problem, and are chosen by the learner.
- Nothing given to the learner, alone or combined, is a complete solution to the task they are being checked on.

**Non-goals:**
- No grading changes. Result states and XP rules stay as they are.
- No learner code runs on the server. Error translation runs in the browser.
- No AI. The optional AI helper is a separate, deferred design ([`ai-helper.md`](ai-helper.md)).
- Not a general Python tutor. Translations cover the errors our units produce.

## 3. Where it runs and what it uses

- **In the browser**, after the Pyodide worker returns. A pure function takes the error text, the code, the lesson ID and the card, and returns the feedback to show. Because it is a pure function, it is easy to test with saved error samples.
- **The worker change:** besides the message, the worker returns the error **type**, the **line number** in the learner's code (the last traceback frame from `<exec>`), the column when Python gives one, and the message text. Frames inside Pyodide are dropped.
- **Content files** add, per challenge: named check rules with their message IDs (section 6), hint levels tagged with the error types or rules they help with (section 7), and optional misconception notes.
- **Nothing new is logged or stored about code.** If we record anything, it is support data such as "hint level 2 shown" or "NameError translated", with no code or message text, under the same rules as `build.md` section 11 and OPS-04.

## 4. Friendly translations of common Python errors

Each translation has a **title**, an **explanation** of the likely cause, and a **next step**. Use `{line}` and `{name}` from the error. Messages below are for Python 3.12, the version in Pyodide 0.27; they were captured locally with Python 3.12 for this document.

| Python says | Likely cause (unit 1 to 2) | Friendly title | Explanation and next step |
| --- | --- | --- | --- |
| `SyntaxError: unterminated string literal` | A quote was opened and not closed | A message is missing its closing quote | "On line {line}, a text message starts with a quote but does not end with one. Add the matching quote before the closing parenthesis." |
| `SyntaxError: '(' was never closed` | Missing `)` | A parenthesis is still open | "The `(` on line {line} has no matching `)`. Python may notice this on a later line. Add the `)` at the end of that instruction." |
| `SyntaxError: expected ':'` | Missing colon after `if`, `else`, `elif` (later `for`, `while`, `def`) | This line needs a colon | "Lines that start a block, like `if path == \"left\"`, end with `:`. Add a colon at the end of line {line}." |
| `SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?` | `=` used in a comparison | Comparing needs two equals signs | "`=` stores a value; `==` compares two values. On line {line}, use `==` to check whether they are equal." |
| `SyntaxError: invalid syntax. Perhaps you forgot a comma?` (with words but no quotes) | Text without quotes | Words need quotes to be text | "Python read the words on line {line} as names, not text. Put the message inside matching quotes." |
| Other `SyntaxError` | Various | Python cannot read line {line} | "Check the quotes, parentheses and colons on line {line} and the line before it." |
| `IndentationError: expected an indented block after 'if' statement on line N` | Block not indented | The lines inside this `if` need indenting | "Lines that belong to an `if` or `else` start with four spaces. Indent line {line}." |
| `IndentationError: unexpected indent` | Stray spaces at the start of a line | This line has extra spaces at the start | "Line {line} starts with spaces but is not inside a block. Remove the spaces at the start of the line." |
| `TabError` | Mixed tabs and spaces | Tabs and spaces are mixed | "Use four spaces for each indent level, not a tab, on line {line}." |
| `NameError: name 'Print' is not defined` (a different case of a built-in) | Capital letter | Python is case-sensitive | "Python knows `print`, not `{name}`. Use all lowercase on line {line}." |
| `NameError: name 'x' is not defined` (close to a defined name) | Typo | Python does not know `{name}` | "Did you mean `{closest}`? Names must be spelled exactly the same each time." (`{closest}` is a defined name within one or two edits.) |
| `NameError` (no close match) | Used before assigned, or missing quotes | Python does not know `{name}` yet | "Give `{name}` a value earlier in the program, or, if `{name}` is meant to be text, put it in quotes." |
| `TypeError: can only concatenate str (not "int") to str` | Joining text and a number with `+` | Text and numbers cannot be joined with `+` | "On line {line}, one side of `+` is text and the other is a number. Turn the number into text with `str(...)`, or use an f-string." (Unit 2) |
| `ValueError: invalid literal for int() with base 10` | `int()` on text that is not a whole number | That text is not a whole number | "`int()` only turns text like `\"7\"` into a number. Check what was typed." (Unit 2) |
| `ZeroDivisionError` | Dividing by zero | Division by zero | "A number on line {line} was divided by 0. Check the value before dividing." (Unit 2) |
| `EOFError: Add a player reply…` (from our worker) | More `input()` calls than test replies | Not enough player replies | "Your program asked for input more times than there are player replies. Add a reply below, or check the number of `input()` calls." |
| Stopped after 15 seconds (from the app) | Endless loop | Your program kept running | "It did not finish within 15 seconds, usually because a loop never ends. Check that the loop's condition can become false." (Unit 3) |
| Output limit (from the worker) | Very long output | Too much output | "Your program printed more than 20,000 characters. Print less, or check for a loop that never ends." |
| Anything else | — | Python stopped on line {line} | "Read Python's message below, change one thing, and run it again." |

Rules for translations:
- Keep Python's message under a **"Show Python's message"** toggle. From Python unit 6 on, show it first and the friendly version second.
- Code samples in an explanation are **patterns of one line at most**, from the lesson's worked example or a neutral one (`if answer == "yes":`), never the learner's own fixed line and never a whole program (section 8).
- If a translation does not fit the current unit (for example `IndexError` in unit 1), use the "Anything else" message instead of teaching ahead.
- Research on rewritten error messages is mixed ([`teaching-design.md`](teaching-design.md) section 2.9), so we measure it: does the same error repeat less after translation? (section 10).

## 5. Highlighting the offending line

- **Proposed approach, no new dependency:** a line-number gutter, and a highlight layer behind the `<textarea>`, kept aligned with it. A code editor library (for example CodeMirror) would do this better, but it is a new dependency that needs its own justification. Decide when the rich editor is planned, not here.
- **What is shown on the reported line:**
  - a marker in the gutter, with a symbol as well as colour (colour alone fails accessibility)
  - a tinted line background
  - the text "Line {line}" in the message
- **"Go to line {line}" button:** moves the cursor to the start of that line and scrolls to it. Focus is never moved without the learner asking.
- **Syntax errors are often detected after the real mistake,** for example an unclosed parenthesis noticed on the next line. For `SyntaxError`, highlight the reported line and say "on or just before line {line}". For an unclosed `(` or quote, highlight the line where it was opened when Python reports it.
- **Screen readers:** the message is announced through the existing live region. The editor gets `aria-describedby` pointing at it, and the line number is in the text, so nothing depends on seeing the highlight.
- **The highlight clears** when the learner edits that line or runs again.
- **Check messages** (section 6) can also name a line when a rule is about a specific line, for example "line 3 prints the word `hero`, not its value".

## 6. Check-specific messages

Applies to the bounded checker now and to browser behaviour checks later (ENG-03).

- **Each check has named rules**, and each rule has its own message, for example `hello.two-lines`, `hello.different-lines` and `variables.uses-variable`. The content file lists the rules and message IDs, so messages can be reviewed and improved without reading checker code.
- **A failing message says** what was observed, why it matters for this task, and one next step: "Your program printed one line. This challenge needs two: a place, then a surprise. Add a second `print()`."
- **A passing message says only what was verified.** Anything the check cannot judge becomes a self-check question, never a claim. Bad: "Your scene has a setting and a surprise." Good: "Python printed your two different messages in order. Read them back: which one sets the scene, and which is the surprise?" (appendix A).
- **Result states stay distinct** (`build.md` section 11):
  - `needs_work`: the learner can fix something.
  - `execution_error`: the program crashed. Show the error translation, not a check rule.
  - `unsupported`: valid work the checker cannot judge. Say so plainly, without blame.
  - `service_error`: our fault. The code is unchanged, nothing is lost; try again.
- **Behaviour checks with several inputs** say which test input failed, without revealing hidden test values: "With a different player name, the greeting stayed the same, so the name may be typed into the message instead of using the input."
- **Different valid solutions are accepted.** A message never says "wrong" just because code differs from the reference (`build.md` section 4).

## 7. Progressive hints beside the error

| Level | Purpose | Example (`choices`) |
| --- | --- | --- |
| 1. Orient | Names the concept or the step | "You need two branches: one when the reply is `left`, one for anything else." |
| 2. Locate | Points to the part of the learner's program | "Look at the line that starts your `if`. What is being compared?" |
| 3. Pattern | Shows a partial pattern from a **different** context, with blanks | "`if answer == \"yes\":` then an indented line, then `else:` and another indented line." |

- **There is no level 4**, and no "show solution" button.
- **Beside the error.** When an error or a failed rule is shown, the hint panel next to it offers the hint tagged for that error or rule first. For example, a `NameError` brings up the hint about spelling names the same way. Untagged hints follow in order.
- **The learner chooses.** Hints appear only when asked for ("Show a hint"), one level at a time. They are never shown automatically after a number of failures, though after two failed runs the button can be highlighted.
- **No penalty.** Hint use is recorded as support data and never reduces XP or blocks progress (`course-catalog.md` section 12.1).
- **A similar example** may be offered after hint 3: a short worked example of the same idea in another context, never the challenge itself.
- **After passing**, the card can show other valid solutions ("Other ways to do it"). This is allowed because the learner has already solved the task.

## 8. Never reveal a full solution

Rules for content authors and for every feedback source (translations, check messages, hints, examples and, later, the AI helper):

1. **No hint, message or example may pass the card's check, on its own or combined with the other hints on that card.** Before ASSESS-07, two challenges broke this rule. Both combinations below were run through the checker and passed:
   - `hello` hint 3 (`print("You land on Mars.")` then `print("A robot offers you tea.")`)
   - `input` hints 1 and 2 (`player = input("Name? ")`, then `print("Welcome, " + player)`)

   *Correction (2026-10-26, handoff 10):* this list also named `variables` hints 1 and 3. Those only passed once the learner typed their own values for `hero` and `tool`; the starter leaves them empty. They still spelled out the whole `print` line, so ASSESS-07 rewrote them in another context. `backend/tests/test_honest_checks.py` now runs every hint combination through the real checker.
2. **Worked examples use a different context from the challenge**, and a challenge called "Make it your own" rejects the example copied unchanged, with a kind message (appendix A).
3. **Code in feedback is a pattern of one line at most**, not the learner's own line corrected and not a whole program. Feedback describes what to change; it does not rewrite the learner's code.
4. **No "show solution" control before passing.** Reference solutions appear only after passing, as "other ways".
5. **Behaviour-check messages never print hidden test inputs or expected outputs** that would let a learner hard-code the answer.

**Enforced by tests** (proposed under ENG-04):
- **Hint sets:** for every challenge, every hint code block, and every combination of the card's hints assembled in order, is run through the check, which must not pass.
- **Examples:** every worked example and guided-practice starter, submitted as the challenge answer, must not pass where the challenge says "make it your own".
- **Translations:** a snapshot test of every error translation template, so any multi-line code pattern added to one is visible in review.

Today `backend/tests/test_academy.py` (`test_authored_examples_execute_and_pass_checks`) and the Playwright test `real Python executes … with player replies` submit each lesson's **worked example** as its challenge answer and expect a pass. Rule 2 would break those tests on purpose. Each challenge needs its own trusted reference solution, which `build.md` section 4 already asks for ("trusted reference solutions"). The tests then use that instead.

## 9. Predict-first tasks

- **On predict cards (existing):** keep multiple choice, explain the answer either way, and record the choice as misconception data.
- **On code cards (proposed):** an optional "Predict first" step before **Run**. The learner types what they expect to be printed, or picks from two or three options, and then runs the code. The app compares the prediction with the real output (ignoring trailing spaces and blank lines at the end) and shows "As you predicted" or "Different from your prediction: here is the first line that differs", with a short explanation of the difference where the lesson provides one.
- **Rules:**
  - Predicting never blocks running.
  - Wrong predictions are never penalized.
  - Learners can turn predict-first off for a lesson.
  - Content authors pick which cards ask for a prediction: mainly worked examples, guided practice, fix-the-bug and trace tasks.
- **Data:** a matched or not-matched flag per card, as support data with no prediction text stored. That is enough to find the cards where most learners predict wrongly.

## 10. Testing and rollout

- **Fixture corpus:** real error strings captured from the Pyodide 0.27 worker for each translation in section 4. That confirms the traceback format and line numbers, including Pyodide's internal frames. Each fixture has its expected title and line.
- **Unit tests** for the pure translation function, the line-number extraction, and the closest-name suggestion.
- **Solution-leak tests** (section 8).
- **Playwright:**
  - a `NameError` highlights the right line, with text and not just colour
  - "Go to line" moves the cursor
  - the live region announces the message
  - the hint tagged for the error is offered first
  - mobile layout has no horizontal scroll
- **Controls:** break the line extraction on purpose and see the tests fail, as in handoffs 07 and 08.
- **Rollout:** unit 1 first, with the ASSESS-07 fix, then unit 2 is written with tagged hints from the start. Measure the same error repeating on the next run, and hint-3 reveals, before and after (`teaching-design.md` section 9).
- **Order:** ENG-04 and ASSESS-07 come before EDU-04 (unit 2) in the backlog.

## 11. Open decisions

1. **Editor:** keep the plain `<textarea>` with an overlay (proposed now), or adopt an editor library when unit 2 starts. The library is a new dependency.
2. **Order of messages:** show the friendly translation first in every unit, or switch to Python's message first at unit 6 (proposed)?
3. **Highlighting attention:** should the hint button be highlighted after two failed runs (proposed), or never?
4. **Predict-first:** on by default for chosen cards (proposed), or opt-in?
5. **Unit 1 check:** the wording and check choices in appendix A.

## Appendix A. Why `print("hi")` then `print("woah")` passes "Open the story"

**Question.** In unit 1, `print("hi")` followed by `print("woah")` passes the challenge card of the first lesson, `hello` ("Open the story"). The card's heading is "Make it your own". Does the check do what its wording promises?

**What the card asks** (`backend/content/py/u01/hello.json`, task `hello.challenge`): "Write two print statements: describe a location, then introduce a surprise. Choose any two nonempty story messages, each on its own line."

**What the check tests** (`backend/app/lesson_checks.py`, `assess`, branch `lesson_id == 'hello'`), and nothing else:
1. The code parses, and the bounded interpreter's output equals the output the browser reported.
2. The program has exactly **two top-level statements**, and they produce exactly **two printed lines**.
3. Neither line is empty or only spaces, and neither contains a line break.

On success it always says: **"Your scene has a setting and a surprise. Python displays your two messages in order."**

**Read-only investigation** (run on `main` `4848d49` with `assess()`, no code changed):

| Submitted code | Result |
| --- | --- |
| `print("hi")` then `print("woah")` | **passed**, with "Your scene has a setting and a surprise." |
| `print("hi")` twice (the same line) | **passed** |
| `print(".")` twice | **passed** |
| `print(1)` then `print(2)` (numbers, not messages) | **passed** |
| The lesson's worked example, unchanged (castle, dragon) | **passed** |
| Hint 3, copied (`print("You land on Mars.")`, `print("A robot offers you tea.")`) | **passed** |
| `print("hi")` (one line) | needs_work: "Write two print statements with nonempty messages: one location, then one surprise." |

The same `hi`/`woah` code does **not** pass the other four unit 1 challenges. Their checks test what their wording promises: variables used, input used with two different names, two different branches.

**Verdict.**
- The check does what the **second** sentence of the prompt says: two non-empty messages, each on its own line.
- It does **not** do what the **first** sentence or the success message say. It does not, and cannot reliably, judge whether a line describes a location or a surprise; that is a judgment about meaning.
- It also misses three things it *could* check:
  - the two messages are different
  - they are text, not numbers
  - the work is the learner's own, not the example or hint copied unchanged ("Make it your own")
- The success message claims qualities that were never tested, which breaks `build.md` sections 3 and 12 ("does not claim to judge untested qualities").
- Hint 3 is a complete passing answer, which breaks section 8, rule 1.

**Proposal** (backlog ASSESS-07). **Built on 2026-10-26 as written (handoff 10)**, with no word minimum (decision 5). Hint 3 as published before is also refused by name, because learners saw it as an answer.

1. **Reword the success message** (required). It should say only what was checked, plus a self-check: "Python printed your two messages in order. Read them back: does the first set the scene and the second surprise you? That part is your call."
2. **Add three cheap checks that match the wording** (recommended):
   - The two lines are different: "Both lines say the same thing. Change the second one into a surprise."
   - Each line is text containing at least one letter, not a number or only punctuation: "Use words for your story: a place, then something unexpected."
   - Neither the worked example nor a hint is copied unchanged: "That's the example from the card. Make it your own: change the place and the surprise."
3. **Make the prompt match the check:** "Write two print statements with two different story messages: first a place, then a surprise. The check makes sure you print two different messages; whether they make a good scene is up to you."
4. **Replace hint 3** with a partial pattern from another context, for example "One line could be `print(\"You wake up in a ...\")`. What happens next?", so no hint passes the check.
5. **Do not** try to detect "a location" or "a surprise" automatically. Keyword lists or word counts would reject valid creative answers ("Mars." then "Boom!") and accept nonsense, and feedback would become less honest, not more. That human-judgment part belongs in the self-check, and later in rubric-based project evidence.

Under the proposal, `print("hi")` then `print("woah")` **still passes**, deliberately. Both are different, non-empty text, and the check then honestly says what it verified. The alternative, requiring at least two words per line, would reject "hi" and "woah", but also some valid stories. That is decision 5 in section 11. The proposed default is **no word minimum**.

**Compatibility when it is built:**
- The change is a new `hello.challenge` version (content README: increase `version` for a wording or check fix).
- Learners who already passed keep their completion and XP. Existing awards are untouched, and a new task version does not award again (`test_new_task_or_badge_version_does_not_award_again`).
- The `legacy_lessons_v1.json` fixture and the two "example passes the challenge" tests change in the same pull request (section 8).

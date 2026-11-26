# Python Foundations final project (`py.u12`): three projects, built first

Status: **proposed** (2026-11-20). The owner asked to design the final projects before more lessons, "then we know what we have to teach and combine to get there", with three options for different ages and skill sets, the easiest a hangman-style game, then a website, then a full app.

The three reference versions are in `docs/plan/final-projects/`. `backend/tests/test_final_project_references.py` proves that each one runs the way the browser runs learner code (its own folder, typed-in replies, seeded random, the learner's own files importable, only the six allowed modules), that its own test file passes, and that a play-through behaves as its brief says.

## 1. The three projects, easiest first

| | 1. Lockpick | 2. Site Builder | 3. Planner |
| --- | --- | --- | --- |
| What it is | A word game in the style of hangman: guess letters to open a vault before six misses jam the lock | A Python program that turns a data file into a small website, one page per item, with links between them | A to-do app with commands (`add … by 2026-12-01`, `list`, `done 2`, `stats`) that remembers your plan between runs |
| Who it suits | First-timers; about 13 and up | Learners who finished units 1 to 10 comfortably; about 14 to 16 | Confident learners who finished every unit; about 16 and up |
| Time | 6 to 8 hours | 10 to 15 hours | 20 to 30 hours |
| Size of the reference version | 1 file, 85 lines | 1 file and a data file, 87 lines | 4 files, 170 lines |
| What it proves | Loops with state, sets, strings, input validation, functions, reading a file, writing tests | Everything in 1, plus JSON data, string templates, regex, and safe output (escaping) | Everything in 2, plus classes, an app split into modules, saved data that survives a damaged file, and a real test suite |
| Required tests (learner's own) | 5 or more | 8 or more | 10 or more, across modules |

Ages are a guide for the recommendation, never a gate: anyone may pick any project, and placement (`placement.md`) recommends one from what the learner has finished.

**About "a full app".** In Python Foundations, a full app is a real program people can use: it takes commands, keeps its data, survives mistakes, and has tests, like the first versions of many real tools. It is not a graphical app. Buttons and screens need HTML, CSS and JavaScript, which belong to the web and JavaScript courses. The path there is already in the catalog (`web`, `js`, then `fullstack`, whose capstone is a full-stack planner). Planner is deliberately the same idea, so a learner can later give it a graphical front.

**Why these three.** Each uses most of what the course teaches, with less scaffolding as you go up (`teaching-design.md`: "Final project: brief, rubric and tests only"). Each has an honest automated part (the required functions are checked, as lessons check them) and a rubric part that no check can pass on its own (`build.md` section 7).

### Required functions (checked automatically, like ENG-06 lessons)

| Project | Functions the checks call | Everything else |
| --- | --- | --- |
| Lockpick | `mask(word, guessed)`, `problem_with(guess, guessed)`, `is_open(word, guessed)`, `load_words(path)` | The game itself, its messages, extra features |
| Site Builder | `escape(text)`, `slug(name)`, `build(data)` returning `{file name: HTML}` | Page design, extra pages, CSS |
| Planner | `commands.run(planner, line, today)`, `storage.load(path)`, `storage.save(planner, path)`, `Planner.add/complete/remove` | Extra commands, report formats, file layout beyond these |

Hidden cases cover the edges the briefs name: a doubled letter, pressing Enter with no letter, a repeated guess; text containing `<` and `&`, two items that would get the same page name; task 0, task "two", a date that does not exist, a damaged save file.

### Rubric (the existing pilot weights from `fullstack.md`, for all three)

Behaviour 40%, testing and debugging 20%, explanation and design 15%, usability and accessibility 15%, reproducibility and documentation 10%. Evidence is labelled by kind (`build.md` section 7): automated checks, the learner's own tests, and self-review. A final project earns its 500 XP (decision 6) only with the rubric, never from the checks alone.

### Stretch ideas (badge only, no XP, per decision 6)

- **Lockpick:** categories from a CSV file, a hint that costs a try, two-player mode where one types the word.
- **Site Builder:** a page per tag, sorting, a site theme chosen in the data file.
- **Planner:** search with a regex, overdue reports by week (`datetime`), and exporting the plan as a page with Site Builder's `build()`. That last one joins projects 2 and 3.

## 2. What Python Foundations must add to get learners there

Checked against the 52 released lessons (their examples, starters, other ways and prompts): nothing teaches triple-quoted strings, `str.format`, HTML, escaping, a command loop, or keeping data between runs, and no lesson uses ENG-10 (testing your own code against broken versions).

| New lesson (proposed ID) | Unit | Needed by | What it teaches |
| --- | --- | --- | --- |
| `py.game-loop` | 3 or 6 | 1, 3 | A loop that holds state (tries, score) until a win, a loss or a quit; `continue` after a bad turn |
| `py.write-your-tests` | 8 | 1, 2, 3 | Writing tests that catch broken versions of a function (uses ENG-10, already built) |
| `py.save-between-runs` | 9 | 3 | Load at start, save at the end, survive a missing or damaged file |
| `py.multiline-strings` | 10 | 2 | Triple-quoted strings as templates, filled with `format()` |
| `py.html-as-text` | 10 | 2 | Just enough HTML to build a page from Python: tags, links, lists |
| `py.escaping` | 10 | 2 | Why text from data or users must be escaped before it goes into a page, and the order that matters (`&` first). It is the same idea as the site's own text policy |
| `py.command-loop` | 10 | 3 | Reading commands like `done 2`: split, check, dispatch, explain what went wrong |
| `py.app-structure` | 11 | 3 | Splitting an app into data, logic and interface modules; nothing in the data module prints |
| `py.when-not-oop` | 11 | 3 | Already planned (needs ENG-09) |
| `py.final-brief`, `py.final-milestones`, `py.final-review` | 12 | all | Already planned (need ENG-09) |

With these, Lockpick needs only `py.game-loop` and `py.write-your-tests` beyond today's lessons, so it can open first.

## 3. Engineering the projects need

| Item | What | Needed by | Notes |
| --- | --- | --- | --- |
| **ENG-09** rubric and self-review tasks | Already proposed. A task type for the brief, milestone checklist and review, with evidence labelled as self-reported | all | Also unblocks the six lessons waiting on it (units 7, 9, 11 and 12) |
| **E1: project workspace** | Several files per project (code and data), saved for the learner and restored next time, and an opt-in "keep the files my program wrote" so a save file survives between runs | all; essential for 3 | Code and data are stored as text and never run on the server. An additive migration. The project's title goes through `text_policy.problem()` |
| **E2: live play** | Play a program as you go, typing each reply when asked, instead of typing all replies before the run | 1, 3 | Proposed without new headers or dependencies: each reply re-runs the program from the start with all replies so far. Seeded random (ENG-07) makes every re-run identical, and the time limit still applies |
| **E3: page preview** | Show the HTML a program wrote, in a sandboxed frame with no scripts and a strict policy | 2 | The same preview the web course needs (`master-run.md`, `web`). It is a CSP change, so it needs the owner's approval |
| **E4: project checks** | Run the required functions against hidden cases, as lessons do, inside the workspace | all | ENG-06 and ENG-08b as they are |

**Content filters.** Nothing a learner makes here is shown to anyone else; it is seen by the learner and, through the family view, their parent. Even so, a project title, README and site text go through the text policy before they are saved (personal details and blocked words). Site Builder's pages are only ever shown in the sandboxed preview, so a learner's HTML cannot run scripts on the site. Sharing projects publicly would need report-and-review first, and is not proposed.

**Hints and error detection.** Each project gets the same three-step hints per milestone, and the mistake detectors (`app/insights.py`) run on project code too. Three new detectors fit these projects: a loop that never changes its stopping state (already partly built), comparing text from `input()` to a number (built), and building HTML from unescaped data (new, for Site Builder).

## 4. Build order (recommended)

1. **ENG-09** (rubric and self-review), then the three `py.final-*` lessons. This also releases the six lessons waiting on it. *Built in handoff 61: ENG-09, `py.when-not-oop` and `py.final-brief`. `py.final-milestones` and `py.final-review` need the project workspace (step 2).*
2. **E1 project workspace and E2 live play.** All three projects need them, and live play makes Lockpick feel like a game. *E2 built (#72, handoff 62); E1 built (handoff 64): `/projects`, saved files, Run with live play, and kept written files.*
3. `py.game-loop`, `py.write-your-tests`: **Lockpick opens.**
4. `py.multiline-strings`, `py.html-as-text`, `py.escaping`, then **E3 preview**: **Site Builder opens.**
5. `py.save-between-runs`, `py.command-loop`, `py.app-structure`, `py.when-not-oop`: **Planner opens**, and unit 12 is complete.

Each step is one pull request, built after this plan, with the reference versions here as the target the lessons must reach.

## 5. Decisions taken on the owner's behalf (2026-11-20)

The owner asked me to decide these.

- **Release order:** merge #63, #64, #65, #66 in that order. Computer Science Foundations opens with units 1 and 3. Unit 2 (pseudocode, tracing, invariants) follows when ENG-09 adds reasoning task types. Unit 3 needs only unit 1.
- **Creatures for 13+:** all thirteen names stay (Inkling, Sumbat, Loop lynx, Packrat, Callwing, Bugbear, Toolhound, Testudo, Scrollworm, Patternfox, Classaur, Bitmoth, Seekowl). Each is a pun on what its unit teaches, the drawings are simple shapes, and "tame" is used for winning a creature. That suits a 13+ audience, which is where Prodigy's own players were. Nothing in the arena is babyish or punitive: no lives, no streaks, nothing to buy.
- **Home page:** it mentions Computer Science Foundations when CS unit 2 opens, so the course appears there with three units rather than two.

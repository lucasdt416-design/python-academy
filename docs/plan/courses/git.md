# Git and GitHub Essentials (`git`): course design

Status: **proposed**, written 2026-11-02. No code and no catalog change. Sources: `course-catalog.md` section 3.4, `teaching-design.md` section 6.3, `build.md` section 8.

## Audience and prerequisites

Everyone who builds projects, and anyone contributing to this platform.

- **Required:** `py.u01`, so the learner has a file worth versioning.
- **Suggested:** `py.u05`.

## Outline

| Unit | Title | Lessons (proposed IDs) |
| --- | --- | --- |
| `git.u01` | Files, folders and the terminal | `git.paths`, `git.terminal-basics`, `git.run-a-program` |
| `git.u02` | Your first repository | `git.git-vs-github`, `git.status`, `git.first-commit`, `git.read-a-diff` |
| `git.u03` | Sharing your work | `git.clone`, `git.push-and-pull`, `git.credentials` |
| `git.u04` | Branches and pull requests | `git.branches`, `git.pull-request`, `git.review-a-diff`, `git.read-ci` |
| `git.u05` | When things go wrong | `git.conflicts`, `git.revert`, `git.committed-a-secret` |

Recovery with `revert` comes before any command that rewrites history. `git.committed-a-secret` teaches that a pushed secret must be replaced, not just deleted.

## Projects and evidence

| Project | Evidence | Label |
| --- | --- | --- |
| Simulated repository tasks | The simulated repository ends in the right state | Practice (lower label, `build.md` section 8) |
| A README change in a disposable real repository: commit, push, pull request, review the diff | The learner pastes a link to their practice pull request and ticks a checklist | Self-reported. Nothing is verified from their account |
| A planted conflict, resolved | Same | Self-reported |

## Runtime and safety

**The simulation.** A small model of a repository, written for this course, runs in the page: files, staged changes, commits, branches. Learners type a limited set of commands, or choose them. It is a data model and **never a shell**, so typed text is matched against the known commands and nothing is executed.

**Real work.** It happens on the learner's own machine, in their own GitHub account. The platform never runs Git for them.

| Risk | Control |
| --- | --- |
| A learner pastes a token or password | The app never asks for one. Lessons say so, and `git.credentials` teaches why |
| A pasted pull request link | Stored as plain text, shown escaped, and never fetched by the server |
| Accounts for 13 to 17 year olds | GitHub's terms say "You must be age 13 or older" (checked 2026-11-02). Fine for invited students, but a learner should know they are making an outside account |
| A private email in a commit | Taught in `git.first-commit`: GitHub's no-reply address |

## Dependencies

None. A library that runs real Git in the browser exists, but the small model is enough for what is taught, and it is easier to keep honest.

## Checker features required

- **A `simulated_repo` task type:** starting state, allowed commands, expected final state. New, but needs no worker.
- **A reasoning task type,** for "predict what `git status` shows". May come with `predict`, which already exists.
- **ENG-09's self-report type,** for real work.

## Risks

- A simulation teaches the simulation, so the two evidence labels must stay visibly different.
- Terminal differences between Windows, macOS and Linux need per-system steps, and nobody on the project has tested Windows.
- GitHub's interface changes, so keep those steps in short, dated lessons.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. Should the simulation accept typed commands, or only choices? *Recommended: typed, from a small list, because typing is what learners will do for real.*
2. Should a practice repository template be published for learners to copy? *Recommended: yes, but it needs a public repository, which is your call.*
3. Is a link plus a checklist enough, with no check against GitHub? *Recommended: yes for now. Checking accounts needs a separate decision (`teaching-design.md` section 6.3).*

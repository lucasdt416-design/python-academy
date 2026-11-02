# Course design documents

Written 2026-11-02 (America/Toronto) for master run stage S10, handoff 30.  
Status: **proposed**. Nothing here is decided, built or in the catalog because of these documents. Each course's content stays blocked until Lucas reviews its document (master run stage WE12).

| Course | Document | Runtime it needs | New dependency? |
| --- | --- | --- | --- |
| `git` | [git.md](git.md) | A simulated repository in the browser; the learner's own real repository | No |
| `web` | [web.md](web.md) | An isolated HTML and CSS preview | No |
| `js` | [js.md](js.md) | A JavaScript worker, and the preview with scripts | No |
| `sql` | [sql.md](sql.md) | A SQL engine in the browser | **Yes** (box B-D1) |
| `data` | [data.md](data.md) | Python worker with file fixtures (ENG-08) | Not for the core |
| `cs` | [cs.md](cs.md) | The Python worker, and reasoning tasks | No |
| `node` | [node.md](node.md) | The learner's own machine, plus fixtures | No |
| `fullstack` | [fullstack.md](fullstack.md) | The learner's own machine | No |
| `ce` | [ce.md](ce.md) | Python for most; the learner's machine for C | Not at first |
| `ai` | [ai.md](ai.md) | No provider calls from the product | No |

## Rules every document follows

- **Learner code never runs on the server,** in any language. SQL counts as learner code.
- **Hidden expected output never reaches the browser.**
- **Original content only.** Outside courses are links, with terms checked first.
- **No payment, public posting or paid hosting is needed to earn a badge** (`build.md` section 7).
- **IDs are proposed.** Unit IDs follow `<course>.uNN`, and lesson IDs `<course>.<slug>`, as in `course-catalog.md` section 3.2.

## Questions that cut across courses

Each recommendation is **recommended, not yet confirmed**.

1. **Hidden data in the browser.** A hidden case's *data* has to reach the browser for the code to run there: SQL's hidden dataset, Python's hidden function arguments (handoff 29 question 1) and JavaScript's hidden inputs. *Recommended: one rule for every course. Hidden data may reach the browser, and hidden expected results may not.*
2. **`ai` is not in `catalog.json`.** It is in `course-catalog.md` section 3.3 and backlog TOOL-03, but not in the content file, while the other nine courses here are. *Recommended: add it as `coming_soon` when its document is approved.*
3. **Which course first after `py`.** The documents do not decide this. *Recommended: `git`, because it needs no new runtime and every later project uses it.*

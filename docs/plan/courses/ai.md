# Working with AI (`ai`): course design

Status: **proposed**, written 2026-11-02. No code and no catalog change. Backlog TOOL-03. Sources: `teaching-design.md` section 6.6, `build.md` section 8, the providers' pages below. **Not legal advice.** Terms change, so re-check them when building and each term after.

## Audience and prerequisites

Every learner who will use AI assistants, and contributors to this platform. `course-catalog.md` lists no prerequisites yet; *proposed:* `py.u01` to `py.u03`, so a learner can run code to test an answer, and `git` for `ai.u05`.

## Provider ages and costs, checked 2026-11-02

| Service | Minimum age | Cost for what the course needs | Source and confidence |
| --- | --- | --- | --- |
| **Claude** (app) | **18**, or the minimum age to consent in your location, whichever is higher | Free plan exists | [Consumer Terms](https://www.anthropic.com/legal/consumer-terms), section 2, effective 2025-10-08. Read directly |
| **Claude Code** | **18,** same terms | **Not on the free plan.** Pro is USD 20 a month, or USD 17 a month billed yearly | [Pricing](https://claude.com/pricing). Read directly |
| **ChatGPT** | 13, and under 18 needs a parent's or guardian's permission | Free plan; plan details not checked | [Terms of Use](https://openai.com/policies/row-terms-of-use/), [help page](https://help.openai.com/en/articles/8313401-is-chatgpt-safe-for-all-ages). **Seen through search results; the page itself refused the fetch.** Which terms apply in Canada was not confirmed |
| **Gemini** | "13 (or the applicable age in your country)" | Free plan; details not checked | [Google help](https://support.google.com/gemini/answer/13278668?hl=en-CA). Read directly. **Canada's age is not stated there, and one older article said 18,** so this is unconfirmed |
| **GitHub** | 13 | Free account | [Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service), section B.3. Read directly |
| **GitHub Copilot Free** | No separate age rule found | Free plan with limits | [Copilot plans](https://docs.github.com/en/enterprise-cloud%40latest/copilot/get-started/plans-for-github-copilot). Search only; not confirmed |

**What this changes.** `teaching-design.md`'s draft units `ai.u03` "Setting up Claude" and `ai.u04` "Claude Code in a practice repository" cannot be hands-on for students aged 13 to 17, **because Claude's terms require 18**. A parent-led setup does not change that: the terms have no parent exception in the sentence read. The course must not lead a minor to break a provider's terms, and Claude Code also costs money.

## Outline

| Unit | Title | Lessons (proposed IDs) | Account needed? |
| --- | --- | --- | --- |
| `ai.u01` | What AI assistants are and are not | `ai.what-a-model-does`, `ai.confident-and-wrong`, `ai.tests-are-evidence` | No |
| `ai.u02` | Asking well | `ai.context-and-goal`, `ai.ask-for-explanations`, `ai.compare-two-answers` | No |
| `ai.u03` | Using an assistant safely | `ai.what-never-to-paste`, `ai.age-rules-and-terms`, `ai.settings-checklist` | No. Hands-on only where the learner's age allows |
| `ai.u04` | An AI coding tool in a practice repository | `ai.read-the-plan`, `ai.permission-prompts`, `ai.review-the-diff` | **No-cost path is a simulated session.** Hands-on is 18 or older and costs money |
| `ai.u05` | AI with GitHub | `ai.ai-branches`, `ai.check-a-pr-description`, `ai.ci-as-judge` | GitHub only |
| `ai.u06` | Connecting tools safely | `ai.least-privilege`, `ai.revoke-access`, `ai.tokens-out-of-code` | Simulated. Hands-on is 18 or older |
| `ai.u07` | Verify and hand off | `ai.write-a-handoff`, `ai.say-what-was-not-checked` | No |

Lasting skills are separate from tool-specific steps, which stay in short, dated lessons.

**A no-cost path covers every unit and every badge.** It uses annotated transcripts and diffs, and simulated sessions. Examples must be original or our own real sessions, checked for private details.

## Projects and evidence

A handoff for a small change, and a review of someone else's. Evidence is self-check and rubric, optionally with a link to a practice pull request. Simulated work carries the lower label (`build.md` section 8). The platform **never grades a conversation with an AI and never needs access to a learner's AI accounts.**

## Runtime and safety

**No provider calls from the product.** No API key, no spending and no learner text sent anywhere. This course is separate from the optional AI helper ENG-05, which stays deferred.

| Threat | Control |
| --- | --- |
| A learner pastes private data into an outside service | `ai.what-never-to-paste` comes before anything hands-on |
| A learner enters the wrong age to get an account | `ai.age-rules-and-terms` says plainly: don't. Tell them which services they can use |
| An AI tool damages a real project | A disposable practice repository only. Hands-on steps never start in a real project |
| A broad token is granted | `ai.least-privilege` and `ai.revoke-access` |
| "Predict if this AI answer is right" tasks | Static, reviewed text. Code in them is run by the same worker as everything else |

## Dependencies

None in the product.

## Checker features required

- Existing `predict` and browser checks, for "run it and see".
- **ENG-09** for rubric work.
- A **simulated session** task type: a scripted transcript with permission prompts the learner approves or denies. New, needs no runtime.

## Risks

- **Fast change.** Ages, prices and features here may change soon, so every fact has a date.
- **A conflict of interest in the wording.** The project is built with these tools, so lessons must not promote any one provider. Keep them neutral, and say what each costs.
- **Terms in Canada.** Age and consent rules can depend on location, and two of the rows above are unconfirmed.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. Who gets the hands-on units? *Recommended: 18 or older, labelled so; everyone else takes the simulated path with the same badge rules. This changes `teaching-design.md` section 6.6's options: "parent-led setup" is off the table for Claude.*
2. Should the course be provider-neutral? *Recommended: yes. Claude Code can be one dated example, and the skills are general.*
3. Should someone confirm Canadian age rules for ChatGPT and Gemini before writing `ai.u03`? *Recommended: yes, read the live terms then. Worth asking someone qualified if the course is offered to minors.*
4. Add `ai` to `catalog.json`? *Recommended: as `coming_soon`, once this is approved.*

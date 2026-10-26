# Optional AI helper: "Explain my error" (design note)

Last updated: 2026-10-26 (America/Toronto)  
Status: **deferred** (backlog ENG-05). Design note only: **do not build** until the decisions in section 9 are made by the owner. Nothing here is implemented, configured or paid for.  
Related: [`lesson-feedback.md`](lesson-feedback.md) (the non-AI feedback engine, which comes first); [`teaching-design.md`](teaching-design.md) section 6.6; [`feedback-security.md`](feedback-security.md) section 7 (counters with no text); [`build.md`](../../build.md) sections 1, 11, 12 and 14.

`build.md` section 1 says no paid AI integrations are implemented by the plan, and the owner's standing rule is free options first. This note records how an AI helper **could** be done safely, so that the decision, if it is ever taken, is an informed one.

## 1. What it would be

- After a run fails (`execution_error`) or a check says `needs_work`, a signed-in student sees an optional button: **Explain my error**.
- The server sends a minimal request to an AI model: the error, the relevant lines of code, and the lesson's objective. It returns a short explanation in the same shape as the feedback engine: what happened, where, the likely cause, and one next step.
- It sits **beside** the built-in feedback, never instead of it. It only appears after the built-in translation and at least one hint have been shown (proposed), so learners try the non-AI support first. Research on AI help for novices suggests both real benefits and a risk of relying on it, which depends on how it is introduced (Kazemitabaar and colleagues 2023; Liffiton and colleagues 2023, "CodeHelp", which used guardrails much like these; Prather and colleagues 2023).

## 2. What it must never do

- **No grading.** It never decides `passed`, never awards XP or badges, and its output is never treated as evidence of skill. Checks stay deterministic (`build.md` section 14: let deterministic tests judge deterministic behaviour).
- **No full solutions.** It follows [`lesson-feedback.md`](lesson-feedback.md) section 8: it does not write or rewrite the learner's program, and any code in an answer is a pattern of one line at most. This is enforced by a server-side check, not trusted to the model (section 4).
- **No chat.** One question and one answer per press. No open conversation, no memory between requests, no personal topics.
- **Not for parents or signed-out visitors**, and not in preview mode.
- **Never on by default.**

## 3. How it would work (proposed architecture)

- **Server-side key only.**
  - The provider API key lives only in the API service's environment, for example `AI_HELPER_API_KEY`, set by the owner in Render.
  - It is never in source code, the browser, the frontend build, logs, screenshots or handoffs.
  - The browser calls our API, never the provider.
- **Off by default, at three levels.**
  - A server setting, for example `AI_HELPER_ENABLED`, unset means off. The endpoint returns 404 and the button is hidden.
  - A per-family switch that a parent turns on (proposed; section 6).
  - The learner presses the button each time.
- **The endpoint.**
  - `POST /api/explain`, students only.
  - Uses the existing Origin check, the server-side session check (SEC-03) and the rate-limit framework (SEC-01).
- **Per-user daily cap.**
  - For example 10 explanations per student per day (number to be decided).
  - Stored as **database** counters, because they must survive restarts.
  - Counters hold a keyed hash of the user, a day and a count, never code or message text, following `feedback-security.md` section 7.
  - A refused request gets 429 with a friendly message: "You've used today's explanations. The hints and error notes still work."
- **Global daily cap**, for example 200 explanations a day across all users, so one compromised account or a bug cannot spend the budget.
- **Hard spending limit at the provider:**
  - a monthly spend cap set in the provider's billing console, below what the owner is willing to pay
  - prepaid credits with auto-reload **off**, where the provider offers that
  - an app-level kill switch (unset `AI_HELPER_ENABLED`)

  If the provider limit is reached, requests fail and the button says the helper is unavailable; nothing else breaks.
- **Model and limits.** The smallest model that explains beginner errors well (for example Anthropic's Claude Haiku 5.5, `claude-haiku-5-5`). Short maximum output, a short timeout, no tools and no web access. Price per request to be checked at the time of the decision; not estimated here.
- **Failure.** Provider errors, timeouts, caps reached or the feature switched off all hide the button or show "unavailable". The lesson is never blocked.

## 4. Guardrails on the answer

- **Instructions to the model** (a system prompt kept in the repository and reviewed like content):
  - explain, don't solve; one next step; no complete programs
  - stay on the lesson's topic and the unit's vocabulary
  - refuse anything unrelated
- **Server-side checks before anything is shown:**
  1. Extract any code from the answer. If it is more than one line per block, remove it and keep only the explanation.
  2. Run the lesson's own check on the extracted code, never executing it, just as the existing bounded checker works today. If it would pass, refuse the answer and show the built-in hint instead. This is the same solution-leak rule as `lesson-feedback.md` section 8.
  3. Length limit; plain text only, rendered as text, never as HTML (the stored-XSS rules in `feedback-security.md` section 2 apply).
- **Reporting:** a "This explanation was wrong or unhelpful" link opens the tester feedback form (FB-05) with the lesson context, but not the AI answer or the code unless the tester opts in.

## 5. Privacy

- **Minimal data to the provider:** the error type and message, the few lines around the reported line (not the whole program), the lesson ID and objective. Never the student's name, email, account ID, age or birthday. Code can still contain names or personal text that a learner typed; the button's notice says so: "Your code near the error is sent to an AI service to write this explanation. Don't put personal details in your code."
- **Nothing stored by us:** no request or answer text in our database or logs. Only the counters in section 3, and a log line like "explain: ok" or "explain: refused (cap)" with no user ID, code or text.
- **Provider data handling:** choose a provider and account type whose terms say API inputs are not used for training, with the shortest retention available. **Check the current terms at decision time; this note does not rely on any provider's present wording.**
- **Privacy notice:** the app's privacy information must describe the helper, the data sent, the provider, and how to turn it off, before it is switched on for anyone.

## 6. Age considerations: students are 13 and over

- **Minimum ages.** The app only registers students aged 13 and over (`build.md` section 3). Many AI providers set minimum ages for their own consumer products, often 18, and have separate rules for organizations that build products used by minors through their API.
  - Before building, check the chosen provider's current terms and usage policy for products used by 13 to 17 year olds.
  - Record what safeguards it requires; for example, some providers require age-appropriate content filtering and a disclosure to users.
  - If the terms do not allow it, do not build it.
- **Consent.** Students are invited by a parent (account policy, unchanged). Proposed default: the helper is available only if the **parent** turns it on for their family **and** the student chooses to press the button. Privacy law in our likely jurisdictions (for example Canada's PIPEDA, and "meaningful consent" for young people) should be checked by the owner. This note is not legal advice.
- **Content safety:** a narrow topic, short answers, no chat and no memory reduce risk. Add the provider's moderation features where available. Any report of an inappropriate answer switches the helper off until it is reviewed (owner action).
- **Learning:** for younger learners especially, AI explanations must not replace thinking. That is why it appears only after the built-in feedback and a hint, why it is capped, and why it never writes the program.

## 7. Cost

There is no cost while it is not built or is switched off. When on, the cost is bounded by the global daily cap and the provider's hard spending limit (section 3). The owner sets both numbers. Because the helper is optional and paid, it stays **deferred** until the owner chooses to spend on it (owner rule: free options first, costs stated plainly).

## 8. How it would be tested (when built)

- The endpoint returns 404 when switched off; 401 for visitors, 403 for parents; 429 after the per-user and global caps; and works after a restart with the caps still counted.
- The key never appears in any response, page source, log or error. A test greps the build output and the logs.
- Solution-leak tests: a stub provider returns a full solution, and the server refuses it.
- Answers are rendered as text: a stub returning HTML or a script shows as literal text.
- **Mocks:** all automated tests use a stub provider. No test calls a real AI service, and CI never has the key.
- A small pilot with the owner and one tester before any wider use, comparing whether learners fix errors more or less independently with and without it.

## 9. Decisions needed before building

| # | Decision | Proposed default |
| --- | --- | --- |
| 1 | Build it at all, and when | Not before ENG-04 (feedback engine) has been live and measured |
| 2 | Provider and model, after checking terms for 13 to 17 year olds, data use and retention | A provider whose terms allow it; the smallest suitable model |
| 3 | Who pays, and the monthly hard limit | Owner; a small fixed limit set at the provider |
| 4 | Per-user daily cap and global daily cap | 10 per student per day; 200 per day in total |
| 5 | Consent model | Parent turns it on per family; student presses the button each time |
| 6 | Exactly what is sent | Error, nearby lines and lesson objective only |
| 7 | When the button appears | Only after the built-in translation and at least one hint |
| 8 | Who reviews reports of bad answers, and the switch-off rule | Owner; any inappropriate answer switches it off until reviewed |
| 9 | Privacy notice wording | Written and approved before it is switched on |
| 10 | How success is judged | A pilot that measures independent fixes, not just satisfaction |

## 10. References

Cited from memory for this note, not re-read for this pull request; check before quoting.

- Kazemitabaar, M., Chow, J., Ma, C. K. T., Ericson, B. J., Weintrop, D. and Grossman, T. (2023). Studying the effect of AI code generators on supporting novice learners in introductory programming. CHI.
- Liffiton, M., Sheese, B., Savelka, J. and Denny, P. (2023). CodeHelp: using large language models with guardrails for scalable support in programming classes. Koli Calling.
- Prather, J. and colleagues (2023). The robots are here: navigating the generative AI revolution in computing education. ITiCSE Working Group Reports.

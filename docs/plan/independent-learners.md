# Independent learner accounts (ID-01 plan)

Status: **proposed**, a plan only. Nothing here is built. Written 2026-10-27 (America/Toronto), drafted in chat from the code on `main` after PR #27 and checked line by line against it by Claude Code before merging (see the PR's handoff).
Related: [`build.md`](../../build.md), [`backlog.md`](backlog.md) (ID-01, decisions 19, 21, 22, 23), [`course-catalog.md`](course-catalog.md) (goals, recommendations, learner level), [`feedback-security.md`](feedback-security.md), [`../../DEPLOYMENT.md`](../../DEPLOYMENT.md).

This plan is **not legal advice**. Section 5 lists what the owner should read before real strangers' data is stored, and says what could not be confirmed.

## 0. What the owner decided (2026-10-27)

Only these three answers are recorded as decided. Everything else in this document is a proposal or a recommendation, marked as such.

1. **An independent learner account is for people 16 or older.** The age is self-declared, like the existing age gate (never identity verification). Learners under 16 keep the parent-invitation path (13 and up), unchanged.
2. **Anyone with a Google account may sign up** (the owner's choice), once the Google app is published (but see section 6.1: it may already be open).
3. **Level-based recommendations come later.** Older and university learners are pointed to harder courses, younger learners to Python Foundations. A pointer to an outside course (for example Harvard CS50) would be a link only, never copied content, with its terms checked first.

## 1. Goals and non-goals

**Goals**

- Let someone 16 or older learn on their own: for example a university-bound adult who knows little about computers, or a 16 or 17 year old who does not want a parent in the loop.
- Keep every protection that exists today: learner code never runs on the server, server-side sessions, rate limits, anonymous tester feedback, admin only from `ADMIN_EMAILS`.
- Be able to turn sign-ups off at once, and to delete a learner's data on request, **before** strangers are invited.

**Non-goals (for this plan)**

- Identity or age verification. The age stays self-declared.
- Showing an independent learner's data to anyone but themselves (and the admin for support, section 2).
- Any change for existing parents and students.
- A paid plan, a payment flow, teacher or class accounts, or a custom domain (SITE-04 is separate).
- Level-based recommendations (section 8 only says how they would fit).

## 2. Accounts today, and the new one

### 2.1 What exists (checked against the code)

| Fact | Source |
| --- | --- |
| Roles are `pending` (just signed in), `parent` and `student` | `User.role` in `backend/app/db.py`; `current()` in `backend/app/main.py` |
| A new Google sign-in creates a `pending` user with only a verified email and Google subject | `callback()` in `main.py` (a verified Google email is required) |
| Enrolment asks for a date of birth. **With an invitation:** the invitation must be valid, unused, unexpired and for the same email; age must be 13 or more; the user becomes a `student` with the inviting parent as `parent_id` | `enroll()` in `main.py` |
| **Without an invitation:** age must be **over 25**, and the user becomes a `parent`. Anyone 25 or younger is refused ("Parents must be over 25") | `enroll()` in `main.py` |
| Only a parent can create invitations (email-bound, seven days, link copied by hand) | `invite()` in `main.py` |
| Every learning route (`/api/goal`, `/api/recommendation`, `/api/awards`, `/api/attempts`, `/api/progress`) requires role `student`. A parent sees family progress only | `current(request, db, 'student')` in `main.py` |
| A parent sees only their own students: the family view filters on `User.parent_id == u.id` | `family()` in `main.py` |
| The admin is decided from `ADMIN_EMAILS` at sign-in. Testers are `student` accounts only, set by the admin | `admin.py`; `feedback-security.md` section 1 |
| The date of birth is stored in `users.birthday` | `User.birthday` in `db.py` |

### 2.2 What this means today (a gap the new account closes)

- **A 16 to 25 year old cannot sign up by themselves at all.** They can only join if a parent over 25 invites them.
- **Someone over 25 who signs up alone becomes a "parent" and cannot learn.** Every learning route needs the student role.
- So "a university student who knows little about computers" has no way in unless a parent invites them.

### 2.3 The new account: an "independent learner"

**Recommended model (proposal):** keep the role `student` and give the account **no parent** (`parent_id` is already optional in the database). Reasons:

| Option | For | Against |
| --- | --- | --- |
| **A. `student` with no parent** (recommended) | Every learning route, XP, badges, goals, recommendations, testers and the admin student list keep working with no change to their role checks. Smallest change, smallest risk of an access bug | "Student" is a slightly odd word for an adult. Code must never assume a student has a parent. The word can be changed in the interface only |
| B. A new role, for example `learner` | A clearer name | Every `current(request, db, 'student')` check, the tester rule and the admin list must be changed and re-tested. More places for an access mistake |

With option A the rule "a parent never sees an independent learner" holds by construction, because the parent view only lists accounts whose `parent_id` equals that parent. A test must prove it (section 9, stage D).

### 2.4 Who can see what

| Account | Own learning data | A parent's view | Admin (support) | Tester feedback |
| --- | --- | --- | --- | --- |
| Parent | none | their own students only | account list | never (decision 23) |
| Student (invited) | yes | their parent: goal, completed lessons, attempts' pass state | account list; flag testers | if marked a tester |
| **Independent learner** | yes | **nobody** | account list (email, tester flag), nothing else by default | if marked a tester |

**Proposal:** the admin's student list shows an independent learner's ID and email only, as it does for students today. The admin never reads a learner's code or progress without a reason recorded in the account history (section 5.4).

### 2.5 Edge cases (proposals)

| Case | Proposal |
| --- | --- |
| Age 16 or 17 with an invitation | Stays a normal invited student, as the parent chose. They are not converted |
| Age 16 or 17 with no invitation, "learning for myself" | Independent learner (the owner's 16+ rule). They are told plainly that no parent will see their progress |
| Age 13 to 15 with no invitation | Not allowed. The screen explains that a parent or guardian creates an invitation, and what to send them |
| Under 13 | Not allowed, as today |
| A parent (over 25) who also wants to learn | Not possible in one account today. Short term: sign in with a second Google account. Later option: a learner profile attached to the parent account (a separate decision, not part of this plan) |
| Someone already a parent who chose wrongly | An admin can change an account's role by hand until a self-service way exists (section 6.3, an admin tool) |
| A learner who turns 16 | No change. A parent-invited student stays under the parent until the parent or the learner asks otherwise. A "leave my parent's account" flow is a possible later item, not planned here |

## 3. Sign-up and onboarding flow (proposed)

1. **Sign in with Google.** Unchanged. The result is a `pending` account.
2. **One question:** "How will you use Python Academy?"
   - "I'm learning for myself (16 or older)"
   - "I'm a parent or guardian setting up a learner (over 25)"
   - "A parent invited me" (paste the link, as today)
3. **Date of birth** (self-declared), checked against the choice: 16 or more for "myself", over 25 for "parent", 13 or more for an invitation. A refusal says what is allowed, with no blame ("This account is for people 16 or older. Ask a parent or guardian to invite you.").
4. **Goal card** (unchanged), then **level** (section 3.1).
5. First lesson.

The sign-up screen never shows the age rules as a hint for getting around them: it asks the date of birth once and applies the rule on the server.

### 3.1 Level (self-chosen)

Following decision 21, the learner picks **high school** or **university** themselves. It is **never derived from the date of birth**, and the screen never asks for one. It is stored separately (section 4) and used later for unit-check variants (ASSESS-06) and for recommendations (section 8). It is optional: skipping gives the default.

## 4. Data model changes (proposal: additive only)

Every migration follows the existing rules (README, "Database changes"): additive, safe while the old app version is still running during a deploy, tested up and down on SQLite and PostgreSQL.

| Change | Purpose | Notes |
| --- | --- | --- |
| No new role | Option A in section 2.3 | `parent_id` stays nullable. A test lists every query that touches `parent_id` |
| `learner_level` (new small table, or a nullable column) | Section 3.1 | `high_school`, `university`, or none. Changes are recorded as account history events, like goals |
| `app_settings` (new small table, one row per setting) | An instant sign-ups switch the admin can flip without a redeploy (section 6.3) | Read on every enrolment. Default is "open" so nothing changes at deploy |
| No table for the daily cap | Count the existing `events` rows with action `enrolled` created today | Uses data that already exists (`audit(db, u, 'enrolled', ...)` in `enroll()`) |
| Account deletion record | Prove a deletion happened without keeping the data | An account-history style row with no personal data, or a log line with a count. To be decided in the stage that builds it |

**Data minimisation question (open, section 11):** `users.birthday` stores the full date of birth. For independent learners, storing only the fact that they are 16 or older might be enough. The age rules need the date at sign-up, not afterwards. Changing what existing accounts store is a separate migration with its own review.

## 5. Privacy and deletion

### 5.1 What is stored about a learner today (from `backend/app/db.py`)

| Where | What | Personal? |
| --- | --- | --- |
| `users` | Google subject ID, email, role, date of birth, parent link, tester flag | Yes |
| `events` | Account history: signed in, signed out, enrolled, goal changed, tester set | Yes (tied to the user ID) |
| `attempts` | The learner's **code**, its output, pass state | Yes: free text typed by the learner |
| `xp_awards`, `badge_awards` | XP and badge ledger rows | Linked to the user |
| `learner_goals` | The chosen goal | Linked to the user |
| `sessions` | A hashed session ID, times, admin flag | Linked to the user, short-lived |
| `invitations` | The invited email, parent, expiry | Yes for the invited person |
| `feedback` | Anonymous tester feedback, **no user link** | Not linked (50 days, 90 items) |
| Render's request logs | IP address and time of each request (`feedback-security.md` section 8) | Yes, outside our code |

The README and the tests already show that the app's own log lines carry no email, code or message text for the admin and feedback routes. **Not yet checked:** the sign-in and enrolment log lines. The stage that opens sign-up must check them.

### 5.2 What is never stored

Passwords (Google handles sign-in), the Google access token beyond the sign-in, payment details, the learner's IP address in the database, and learner code anywhere but `attempts` (and the anonymous feedback item if they tick "Include my code").

### 5.3 Self-service export and deletion (proposed)

| Item | Proposal |
| --- | --- |
| **Export** | A "Download my data" action: one JSON file with the account row (without internal IDs of others), history events, attempts (code, output, pass state), XP, badges and the goal. Rate-limited, signed-in only, nothing emailed |
| **Delete** | A "Delete my account" action with a confirmation step. It deletes the user's `attempts`, `xp_awards`, `badge_awards`, `learner_goals`, `events`, sessions (they already cascade) and finally the `users` row, in an order that respects the foreign keys. Anonymous feedback is not linked, so it stays until its own 50-day limit |
| **Parents and students** | Deleting an invited student's account is the student's or the parent's request (to be decided). Deleting a parent account that still has students needs a rule: proposed, the parent must first delete or release the students |
| **Admin tool** | An admin way to delete or disable one account by ID, with a reason, recorded without personal data. Needed for requests that arrive by email |

### 5.4 Retention (proposals, not decisions)

| Data | Proposal |
| --- | --- |
| Anonymous feedback | 50 days, at most 90 items (already built, decision 18) |
| Learner code in `attempts` | Keep while the account exists; delete with the account. Consider a limit (for example keeping only the latest N attempts per lesson) |
| Inactive accounts | Delete after a long period without sign-in (for example 24 months), with a warning email only if emailing exists; otherwise decide that none is sent and say so in the notice |
| Account history | Keep while the account exists; a deletion removes it |
| Backups | Deleted data stays in database backups until they expire. The notice must say so. **Not confirmed here:** Render's backup retention for this plan (see the backups stage OPS-02) |
| Admin support access | Any time the admin looks at one learner's code or progress, an account-history row records that it happened and why (without the content) |

### 5.5 Privacy notice (contents)

A page on the site, linked from sign-in and the footer, in plain language, covering: who runs it (an individual, a private student project, with a contact address); what is collected (section 5.1) and why; what is not collected (5.2); where it is stored (**Render's Oregon region in the United States**, per `DEPLOYMENT.md`, so the data leaves Canada); who can see it (section 2.4); how long it is kept (5.4); how to export and delete; that learner code runs only in the browser; that Google processes sign-in; the age rules (16 for independent accounts, 13 to 15 with a parent, under 13 not allowed); what happens to anonymous feedback; and how to contact the owner. It is also the privacy policy link Google needs for a published app (section 6.2).

### 5.6 What the owner should read (not legal advice, not confirmed here)

- **PIPEDA**, Canada's federal private-sector privacy law, and the Office of the Privacy Commissioner's guidance on **children's and teenagers' consent**. As far as this plan can tell there is no single fixed age in the law; the guidance looks at whether a young person can understand what they are agreeing to. **Not confirmed.**
- Whether a small hobby project is covered, or exempt, and when **cross-border storage** (Oregon) needs to be mentioned. **Not confirmed.**
- Provider terms: Google's rules for apps that let under-18s sign in, and Render's terms on personal data.
- A lawyer or a school's privacy officer may answer these in a short conversation. That is the person to ask before inviting anyone outside friends.

## 6. Opening it to anyone safely

### 6.1 Today's situation, and one thing to check now

`DEPLOYMENT.md` and the README say the Google app is in testing and test accounts are added to it. **Google's own help page says that in Testing mode, an app that requests only the basic sign-in scopes (`openid`, email and profile) does not need test users to be listed, and those users see no warning** ([publishing status help](https://support.google.com/cloud/answer/15549945)). This app requests only those scopes. If that applies, **anyone with a Google account can already sign in today**, and anyone who then claims a date of birth over 25 becomes a `parent` (who can only create invitations). **Please check this with a Google account that is not on your list**, and tell the planning session. If it is true, the sign-ups switch and the cap in 6.3 are needed sooner than this plan assumed, and the README line about adding test accounts is out of date. This cannot be confirmed from the repository.

### 6.2 Publishing the Google app (what Google says; confirm in the console)

From the same help pages:

- **Testing:** up to 100 listed test users; tokens expire after seven days, **except** for the basic scopes above, which have no expiry.
- **In production:** any Google account can authorize the app. Verification may be needed before the app's name and logo show, or for sensitive or restricted scopes. The page does not say directly whether an app with only basic scopes needs verification, so **mark this unconfirmed** and read the console's "Verification status" section.
- **For an external production app, Google asks for:** a home page on a verified domain you own that describes the app and is not only a login page, a **privacy policy** and **terms of service** linked from the home page and the consent screen (same URLs), and every domain registered as an authorized domain. **The current address is a `onrender.com` subdomain, which cannot be a verified domain you own.** A custom domain (SITE-04) may therefore be required for a published app, or at least for brand verification. **Mark this as to be confirmed.**
- The 100-new-user lifetime cap applies to unverified apps asking for sensitive or restricted scopes. This app does not ask for them.

### 6.3 Safeguards (all proposals, nothing decided)

| Safeguard | What it does | Notes |
| --- | --- | --- |
| **Sign-ups on/off switch** | When off, a new `pending` account cannot enrol; existing accounts are unaffected. The page says sign-ups are closed for now | Stored in `app_settings` (section 4) and flipped by the admin without a redeploy, because an environment variable change redeploys the API and takes minutes |
| **Daily cap on new accounts** | Refuse enrolment once N new accounts exist today, counted from the existing `enrolled` events. Suggested starting value: 20 a day, easy to raise | One counter, no extra table |
| **Per-address sign-up limits** | The existing `signin` and `enroll` rate limits, counted per visitor address with `CLIENT_IP_HEADER=cf-connecting-ip` | Already in `limits.py`. Still in memory, so they reset on redeploy (known limit) |
| **Admin disable or delete an account** | By ID, with a reason, no personal data in the record | Also used for abuse |
| **Alerts on a spike** | A way to notice many sign-ups or many 429 responses in a short time | Overlaps OPS-03. A simple first version is a daily count the admin can read |
| **Invited-group first** | Invite a small group (friends going into university) before everyone | A process step, not code |

## 7. Cost and capacity

- **Today:** two Render Starter web services and a Basic-256mb PostgreSQL database with 15 GB storage and autoscaling off, about USD 20 a month plus extras (`DEPLOYMENT.md`).
- **Cheap per learner:** Python runs in the learner's browser, not on the server. The server judges reported output and stores small rows.
- **What grows:** the `attempts` table (the learner's code on every run that is saved), sessions, and database connections. The 15 GB database with autoscaling off is a hard limit to watch.
- **When the in-memory rate limits stop being enough:** as soon as more than one API instance runs, each would count separately. The README and `DEPLOYMENT.md` already say to move the counters to the database first.
- **Triggers to review** (suggested): more than about 100 active accounts; database storage over 50 percent; the API's memory or response times near their limits; any need for a second API instance; a spike of 429 responses.
- Tie the first review to the **2026-11-08 cost review (OPS-05)**.

## 8. Level-based recommendations (later; no design change now)

`recommend()` in `backend/app/recommend.py` is a pure function of the goal, the catalog, completed lessons, placement and dismissed courses, with a `RULES_VERSION`. A level would be one more input. The goals already include `university` (Python, git, `cs`, SQL, `ce`). So level could, for example, reorder or add an outside pointer for university learners, without changing the account model. Changing the rules means bumping `RULES_VERSION` and adding tests. Any outside link (for example CS50) is a pointer on a recommendation card, with the course's terms and licence checked first, and the in-house `cs` course remains the planned in-product path. Nothing about this is built or decided beyond the owner's answer in section 0.

## 9. Staged build plan (proposed order)

Each stage is one small reviewable PR with tests, a handoff and a live check, as in `build.md`.

| Stage | What | Depends on | Main risks and tests |
| --- | --- | --- | --- |
| **A. Privacy notice and data inventory** | The notice (5.5) as a page, and a data inventory document. Check the sign-in and enrolment log lines for personal data | None | A claim in the notice that is not true. Verify every sentence against the code |
| **B. Export and delete my account** | Section 5.3, with tests for foreign-key order and that nothing is left behind | A | Deleting too little, or too much (a parent's data). Tests on SQLite and PostgreSQL |
| **C. Switch, cap, admin disable or delete** | Section 6.3: `app_settings`, the daily cap, the admin tools | None (can run before B) | A switch that fails open or closed wrongly. 401 and 403 tests for every new admin route |
| **D. Independent enrolment** | Section 3 and 2.5: the new question, the 16+ rule, the 13 to 15 message | A, B, C | Age boundaries (15, 16, 17, 25, 26, with and without an invitation), a parent seeing an independent learner (must be impossible), an under-16 slipping through, role changes. Existing parents and students must be unchanged |
| **E. Learner level** | Section 3.1 and ASSESS-06 | D | Level never derived from a birthdate. Skipping it works |
| **F. Small invited group, then wider** | A process: invite friends, watch the daily count and logs for a week, then decide on publishing the Google app (and a custom domain if Google requires it) | A to E, OPS-02 (backups and a restore drill), SEC-09 enforced | Findings from real use |
| **G. Level-based recommendations** | Section 8 | E | Rules version, tests |

The backups and restore drill (OPS-02), the enforced nonce policy (SEC-09) and a private API (SEC-02) are listed in the backlog as earlier safety work. They should be done before stage F.

## 10. Backlog rows (to add; not added here)

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| ID-01 | Next | Independent learner accounts: this plan. Decided: 16 or older, self-declared; anyone with a Google account; level-based recommendations later | None | in_review (this plan), then split into ID-01a to ID-01g below |
| ID-01a | Next | Privacy notice and data inventory (stage A) | ID-01 | proposed |
| ID-01b | Next | Export and delete my account (stage B) | ID-01a | proposed |
| ID-01c | Next | Sign-ups switch, daily cap, admin disable or delete (stage C) | None | proposed |
| ID-01d | Next | Independent enrolment, 16 or older (stage D) | ID-01a, ID-01b, ID-01c | proposed |
| ID-01e | Next | Learner level, same as ASSESS-06 (stage E) | ID-01d | proposed |
| ID-01f | Next | Invited group first, then publishing the Google app and domain (stage F) | ID-01a to ID-01e, OPS-02, SEC-09 | proposed |
| ID-01g | Later | Level-based recommendations (stage G) | ID-01e | proposed |
| SEC-10 | Now | Check whether any Google account can sign in today (section 6.1); if so, record it and bring the switch (ID-01c) forward | None | proposed |

## 11. Questions for the owner

Each has a recommended answer. **None is decided until the owner confirms it.**

1. **Check 6.1 now:** can a Google account that is not on your test list sign in? *Recommended: yes, check today; it decides how urgent stage C is.*
2. **Model:** independent learner as a `student` with no parent (section 2.3, option A)? *Recommended: yes.*
3. **Parent who also wants to learn:** use a second Google account for now? *Recommended: yes; revisit later.*
4. **Age data:** keep storing the full date of birth for everyone, or store only "16 or older" for independent learners? *Recommended: keep as is for now; review in stage D.*
5. **Daily cap:** 20 new accounts a day to start? *Recommended: yes, raise as needed.*
6. **Inactive accounts:** delete after 24 months without sign-in? *Recommended: yes, and state it in the notice.*
7. **Deleting an invited student:** the student, the parent, or both may ask? *Recommended: both.*
8. **Contact address** for the privacy notice: which address will you publish? (Not decided here.)
9. **Custom domain:** does it have to come before publishing the Google app (section 6.2)? *Recommended: check the Google console before deciding.*

## 12. Sources

- Code, all on `main`: `backend/app/db.py` (tables), `backend/app/main.py` (`current`, `callback`, `enroll`, `invite`, `family`, `age_on`), `backend/app/admin.py`, `backend/app/recommend.py`, `backend/app/limits.py`.
- `DEPLOYMENT.md`, `README.md`, [`backlog.md`](backlog.md), [`course-catalog.md`](course-catalog.md), [`feedback-security.md`](feedback-security.md).
- Google: [Publishing status help](https://support.google.com/cloud/answer/15549945) and [Branding and verification help](https://support.google.com/cloud/answer/10311615), read on 2026-10-27. Anything not stated there is marked unconfirmed above.

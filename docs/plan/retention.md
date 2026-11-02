# Data retention policy (OPS-04)

Written 2026-11-02 (America/Toronto), checked against the code on `main` at `4b70a28`.  
Status: **proposed**. Only what is marked **decided** was decided by the owner. Box B-I6 (delete inactive accounts) is empty, so that is still open. This is not legal advice.  
Related: [`independent-learners.md`](independent-learners.md) section 5, [`feedback-security.md`](feedback-security.md), [`backlog.md`](backlog.md) decisions 18 and 19.

## 1. The short version

- **Only two kinds of data are ever deleted automatically today:** feedback and expired sessions.
- **Nothing else in the database is ever deleted.** No code deletes accounts, attempts, history, invitations, XP or badges (no such `delete` exists in `backend/app/main.py` or `backend/app/admin.py`).
- **A learner cannot yet export or delete their data** (ID-01b is not built).
- **Do not tell anyone a period below applies until the column "Today" says it does.**

## 2. The table

| Data | Personal? | Today (checked in the code) | Proposed policy | State |
| --- | --- | --- | --- | --- |
| Anonymous feedback | Not linked to a person; free text could still identify one | Deleted 50 days after the day it was sent. At most 90 items; when full, the oldest resolved item goes, or the new item is refused (`feedback.py`: `KEEP_DAYS`, `MAX_ITEMS`, `purge`, `make_room`) | The same | **Decided** (decision 18), built |
| Who sees feedback | | Parents never do (decision 19) | The same | **Decided**, built |
| Sessions | Linked to the user | Normal: 7 days at most, 24 hours idle. Admin: 8 hours, 1 hour idle (`sessions.py`). Logout deletes the row. Expired rows are removed when someone next signs in | The same | Built |
| Rate-limit counters | Keyed hashes and addresses, in memory | Gone on restart, or when the window ends (`limits.py`) | The same until ENG-11; ENG-11 must keep them short-lived | Built |
| Account row (`users`) | **Yes:** email, Google ID, date of birth, role | Kept for ever | Kept while the account is used. **Inactive accounts: see question 1** | Open |
| Accounts that never enrolled (`pending`) | **Yes:** email and Google ID. A row exists for every Google sign-in | Kept for ever | Delete after 30 days without enrolling (question 2) | Open |
| Attempts (`attempts`) | **Yes:** the learner's code and output | Kept for ever | Keep while the account exists, and delete with it. Consider keeping the latest attempts per lesson (question 3) | Open |
| Account history (`events`) | **Yes:** tied to the user | Kept for ever | Keep while the account exists, and delete with it | Open |
| XP and badges | Linked to the user | Kept for ever. Ledgers are append-only by design | Keep while the account exists, and delete with it | Open |
| Goals (`learner_goals`) | Linked to the user | One current row, kept for ever. Changes are also history events | Keep while the account exists, and delete with it | Open |
| Placement answers | Would be | **Not built,** so nothing is stored | Decide with EDU-02. Proposed: latest result only, and delete with the account | Open |
| Learner level (ASSESS-06) | Would be | **Not built** | Keep while the account exists, and delete with it | Open |
| Support data for unit checks (ASSESS-03) | Would be | **Not built** | Decide with ASSESS-03 | Open |
| Measurements (ENG-04c) | Must not be | **Not built.** Box B-P1 is empty | Counts only, with no user ID or code. State the period in that stage | Open |
| Invitations (`invitations`) | **Yes:** the invited person's email, who may never have signed up | Kept for ever, even after expiring at 7 days or being used | Delete 30 days after expiry or use (question 4) | Open |
| Export | | **Not built** (ID-01b) | Made on request, never stored | Open |
| Delete my account | | **Not built** (ID-01b). Box B-I7 is empty | Removes the rows above, in foreign-key order | Open |
| Records of an admin disabling or deleting an account | Must not be | **Not built** (ID-01c) | No personal data; keep while the project runs | Open |
| Database backups | **Yes:** a copy of all of the above | **Not confirmed** (OPS-02) | Deleted data stays until backups expire, and the notice must say so | Open: read Render's setting |
| Render's request logs | **Yes:** IP address and time (`feedback-security.md` section 8) | Outside the code; period **not confirmed** | Read Render's setting and state it in the notice | Open |
| API access log | **Yes:** address, path and query string, **including Google's one-time `code`** (`independent-learners.md` section 5.1) | On, by uvicorn's default | Filter query strings (SEC-11; box B-S1 is empty) | Open |

## 3. Questions for the owner

Each recommendation is **recommended, not yet confirmed**.

1. **Inactive accounts.** Delete after 24 months without sign-in (box B-I6)? *Recommended: yes, and say so in the notice. It needs code that does not exist, and a rule about warnings: without email, none can be sent, so say that too.*
2. **Accounts that never enrolled.** Delete after 30 days? *Recommended: yes. These rows hold an email and a Google ID for someone who may have only looked. If SEC-10 shows sign-in is open to anyone, this matters more. The 30 is the implementer's suggestion.*
3. **Attempts.** Keep every attempt, or only the latest few per lesson? *Recommended: decide after the 2026-11-08 cost review (OPS-05). Code is the main thing that grows, and the most personal.*
4. **Invitations.** Delete 30 days after expiry or use? *Recommended: yes. An invited person never agreed to anything, and the row is no use after that. The 30 is the implementer's suggestion.*
5. **Order.** Should the deletion jobs wait for the privacy notice (ID-01a)? *Recommended: build them with ID-01b, and only state a period in the notice once its code exists.*

## 4. What this policy needs in code

None of this is built here. All of it is proposed:

- A delete-with-the-account routine (ID-01b).
- A scheduled cleanup, or cleanup at sign-in as sessions do, for inactive accounts, `pending` accounts and old invitations.
- A test per table that nothing is left behind.

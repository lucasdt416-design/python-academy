# Feedback and admin inbox: threats and controls

Last updated: 2026-10-25 (America/Toronto)  
Status: **proposed**. Nothing here is implemented. It is the security plan for backlog items FB-01 to FB-07 and the feature in `docs/plan/course-catalog.md` section 11.  
Owner decisions this plan must respect (2026-10-25): testers only (11); stored anonymously, with sign-in only to stop bots (12); deleted after 50 days, at most 90 items, oldest resolved deleted first, otherwise reject (18).

Every control below is enforced **on the server**. The browser can hide a button, but it is never trusted to decide who is an admin, who is a tester, what gets stored, or how often.

## Summary

| # | Threat | Main server-side controls |
| --- | --- | --- |
| 1 | Admin takeover | Admin decided only from a server setting; one guard on every admin route, tested by enumerating routes; no endpoint grants admin; shorter admin sessions; SEC-03 before launch |
| 2 | Stored XSS | Plain text only, rendered as text; strict link validation; control and direction characters removed; CSP (SEC-04) |
| 3 | Spam and bots | Google sign-in plus tester flag; per-account and global rate limits; length limits; the 90-item cap |
| 4 | Optional code leaking | Off by default, shown before sending, size-limited, never run, never logged, excluded from the digest by default, deleted with the item |
| 5 | Personal details in free text | Notice in the form; server-side removal of email addresses and phone numbers; admin-only access; 50-day deletion |
| 6 | CSRF | Existing Origin check on every write; SameSite cookies; JSON bodies only; no state change on GET |
| 7 | Rate-limit counters holding message text | Counters store only a keyed hash, an hourly window and a count; no text, no feedback IDs; deleted within 24 hours |

Two further risks to anonymity are covered in section 8 (logs and timing, and the digest leaving the app).

## 1. Admin takeover

**What could go wrong.** Someone becomes admin and reads every tester's feedback, changes statuses, or marks themselves or others as testers. Routes: a forged request, a guard missing on one admin route, a stolen admin session cookie, or an admin flag set from the browser.

**Controls**

- Admin is decided only from a server setting (for example `ADMIN_EMAILS` in Render's environment), never from source code, the database, or anything the browser sends. Decision 14 (how exactly the admin is identified) is still open; until it is answered, the proposal is: the signed-in user's verified Google email must be in that list.
- Admin status is re-checked on **every** admin request from the session's user on the server. There is no "is admin" value in the cookie.
- All admin endpoints live under one path (for example `/api/admin/…`) behind one guard. A test enumerates every registered route under that path and checks that a student, a parent, a tester, and a signed-out visitor each get 401 or 403. A new route that forgets the guard fails CI.
- No endpoint can grant admin. The only privileged write available to the admin is the tester flag.
- Shorter sessions for admins (for example 8 hours instead of 24), and server-side session revocation (backlog SEC-03) before the inbox ships, so logging out or a lost device ends the session.
- Admin pages get the Content-Security-Policy from SEC-04, which limits what injected script could do.
- Admin actions (tester flag changes, status changes, deletions) are written to the account history under the admin's own account. That is allowed because it records the admin, not a tester.

**Tests:** route enumeration (above); a tester cannot set the tester flag; changing the email in the browser or request body has no effect; an admin session past its lifetime is refused.

## 2. Stored XSS

**What could go wrong.** A tester types HTML or JavaScript into the message, or a `javascript:` link into a field. When the admin opens the inbox, it runs with admin privileges.

**Controls**

- Feedback is **plain text only**. The inbox renders it as text (React escapes it). Never `dangerouslySetInnerHTML`, never Markdown or HTML rendering, never a rich-text editor.
- The only link the inbox shows is the GitHub issue field, which only the admin sets. The server accepts only `https://github.com/torontojohn/python-academy/issues/<number>` or `/pull/<number>`; anything else (including `javascript:`) is rejected. The link opens with `rel="noopener noreferrer"`.
- On input, the server removes control characters (except new lines and tabs) and Unicode direction-override characters, which can make text display differently from what it says.
- Server-side length limits: message at most 2,000 characters, optional code at most 20,000, notes at most 2,000.
- The CSP from SEC-04 blocks inline script on admin pages as a second layer. API responses are JSON with `X-Content-Type-Options: nosniff`, as today.
- "Copy digest" copies plain text to the clipboard; it never builds HTML.

**Tests:** messages containing `<script>`, `<img onerror>`, `javascript:` URLs, emoji, right-to-left text and direction overrides are stored safely and shown as literal text; a `javascript:` issue link is rejected.

## 3. Spam and bots

**What could go wrong.** Automated or abusive submissions bury real feedback or fill the 90-item inbox so nothing new gets in.

**Controls**

- Sign-in with Google is required, and the account must have the tester flag, which only the admin can set (decision 11). Visitors, parents and non-tester students get 403.
- Per-account rate limits, for example 5 per hour and 20 per day, using the counters in section 7. A global limit (for example 60 per day across all testers) protects the cap even if one account is compromised.
- Length limits (section 2), and a type that must be one of the five listed.
- The 90-item cap (decision 18): when full, the oldest resolved item is deleted; if none are resolved, the new item is rejected with a clear message. Trade-off: a flood of unresolved items blocks new feedback until the admin resolves or deletes some. The rate limits bound how fast one tester can cause that.
- Because feedback is anonymous, the admin cannot remove one person's items. The response to abuse is to untick their tester flag, which stops new submissions immediately.
- Depends on SEC-01 (rate limiting across the app).

**Tests:** non-testers get 403; the sixth item in an hour is rejected; the global limit applies; a full inbox with nothing resolved rejects new items; a full inbox with resolved items deletes the oldest resolved one.

## 4. Optional code leaking

**What could go wrong.** A learner's code can contain names, messages to friends, or pasted secrets. It might be attached without them realising, kept too long, shown in logs, run by mistake, or copied into an outside assistant.

**Controls**

- "Include my code" is **off by default** (decision 17, proposed). When ticked, the form shows exactly the code that will be sent.
- The server stores code only when the request says the box was ticked, and only up to 20,000 characters.
- Code is stored only in its feedback row and deleted with it (50 days at most). It is never written to logs, events or counters.
- The inbox shows code as plain text in a code block. It is **never run**: no "Run" button, never passed to the checker, never sent to Pyodide. This keeps `build.md`'s rule that learner code never runs on the server.
- "Copy digest" leaves code out unless the admin explicitly includes it for that item.

**Tests:** without the box ticked, no code is stored even if the request includes some; code containing HTML is shown as text; the digest excludes code by default.

## 5. Personal details typed into the free text

**What could go wrong.** A tester types their name, a classmate's name, an email address, a phone number or a password. That turns anonymous feedback into personal data, and it might be copied into an outside assistant through the digest.

**Controls**

- The form says, next to the message box: do not include passwords, names, or other personal details.
- Before storing, the server replaces anything that looks like an email address or phone number with `[email removed]` or `[number removed]`. This is best-effort: it cannot reliably detect names or addresses.
- Only the admin can read feedback; parents cannot (decision 19, proposed). The inbox never shows account data alongside feedback.
- Everything is deleted within 50 days, and the admin can delete an item immediately.
- The admin reviews a digest before pasting it into any assistant (section 8).

**Tests:** email addresses and phone numbers in a message are replaced before storage; the stored row contains no account fields.

## 6. CSRF

**What could go wrong.** A malicious website makes a signed-in tester's browser send feedback, or makes the admin's browser change statuses or tester flags.

**Controls**

- The app already rejects every POST, PUT, PATCH and DELETE whose `Origin` header is not the app's own (`backend/app/main.py`, `security` middleware). Feedback and admin endpoints are covered automatically, with no exceptions.
- Session cookies are `SameSite=Lax` and `HttpOnly`, and `Secure` in production.
- Bodies must be JSON matching a schema, so plain HTML form posts are rejected.
- No state change happens on a GET request.

**Tests:** feedback and admin writes from another origin, or with no Origin header, get 403; a GET to an admin write path changes nothing.

## 7. Rate-limit counters must not hold message text

**What could go wrong.** Per-user rate limits need to know who sent how many items. If the counters held the message, a feedback ID or an exact time, they would undo the anonymity of the feedback table.

**Controls**

- A separate table, for example `feedback_rate`, holds only:
  - a keyed hash of the user ID (HMAC with a server secret, so the table alone does not reveal user IDs)
  - the start of an hourly window
  - a count
- It holds no message text, length, type, lesson, code, hash of the message, or feedback ID, and it is not joined to the feedback table in any query.
- Rows older than 24 hours are deleted in the same request that writes them.
- Feedback rows store only the **date** they were created, not the time, so counters cannot be matched to items by timestamp.
- Feedback submissions are **not** written to the account history (events table). Today every important action is recorded there with the user's ID and an exact time, which would identify the sender. A test checks that sending feedback adds no event.
- The app never logs feedback bodies. Its log line for a submission says only "accepted" or "rejected" and why, with no user ID.

**Tests:** after a submission, the counter table holds only hash, window and count; no event row is added; no feedback row has a time more precise than the date; counters older than 24 hours are gone.

## 8. Other risks to anonymity

- **Infrastructure logs.** Render's request logs record the IP address and time of each request, including feedback submissions, outside the app's control. Someone with access to those logs (the owner) could match a submission to a person by time. The app cannot remove this; it is stated here so nobody overstates the anonymity.
- **Very few testers.** With one tester, every item is obviously theirs. Anonymity protects testers mainly once several of them are active.
- **The digest leaves the app.** Pasting a digest into ChatGPT or Claude sends it to an outside service. The digest contains no account data and no code by default, but free text may still contain personal details. The admin reviews it first.

## 9. Trade-offs of anonymous feedback

| Trade-off | Consequence | Mitigation |
| --- | --- | --- |
| No replies to testers | The admin cannot ask a follow-up question or say thank you to a specific person | The form asks for enough detail to act on; the admin can talk to testers in person or by a general announcement |
| No status view for testers | Testers cannot see whether their report was fixed (backlog FB-08 is dropped) | Release notes or a "recently fixed" list could be shared with all testers |
| No per-person view | The admin cannot spot that one person sent five related reports, or merge them | Context (lesson, card) groups related reports instead |
| Abuse handling is blunt | One person's items cannot be removed as a group | Untick their tester flag; rate limits and the cap bound the damage |
| Anonymity is limited | Few testers, and hosting logs (section 8) | Stated plainly in the form: "sent without your name or email", not "untraceable" |

## 10. Order of work

1. SEC-01 (rate limiting) and SEC-04 (CSP and HSTS).
2. SEC-03 (server-side session revocation), before the admin inbox ships.
3. FB-01 (decisions 14, 17, 19).
4. FB-02 and FB-03, with the route-enumeration test and the "no user data in feedback rows" test.
5. FB-04 to FB-07.

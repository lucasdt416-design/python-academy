# Manual test sheet: real screen readers and browsers (QA-01)

Written 2026-11-02 for master run stage WE6. Status: **ready to use, not yet run by anyone.** Automated checks can't tell you whether a screen reader makes sense, so a person has to do this.

## Setup

| Screen reader | Browser | Cost | Start it |
| --- | --- | --- | --- |
| VoiceOver | Safari on a Mac | Free, built in | Cmd + F5 |
| VoiceOver | Safari on an iPhone or iPad | Free, built in | Settings → Accessibility → VoiceOver |
| NVDA | Firefox or Chrome on Windows | Free download | Ctrl + Alt + N |
| TalkBack | Chrome on Android | Free, built in | Settings → Accessibility → TalkBack |

Use a test student account. Put the mouse away, or use touch gestures only on a phone. Record every problem, however small.

## Tests

Mark each one **Pass**, **Fail** or **Not run**.

| # | Do this | It passes if you hear or can do this | Result |
| --- | --- | --- | --- |
| 1 | Open the home page and press Tab once | "Skip to content" is announced, and Enter moves past the navigation | |
| 2 | List the headings on a lesson page | The current card's heading is there, and the order makes sense | |
| 3 | Press Continue | Focus moves, and the new card's heading is read out | |
| 4 | Choose a wrong answer on a Predict card, then the right one | Each result is read out without you having to look for it | |
| 5 | Move into the code editor | Its name, "Your Python code", and the instructions on how to leave it are read out | |
| 6 | In the editor, press Tab, then Esc and Tab | Tab adds four spaces. Esc then Tab moves to "Run" | |
| 7 | Run a program with wrong output | The result is read out once, not repeated, and you can find the output | |
| 8 | Run a program with an error, then choose "Go to line" | The explanation is read out, and focus lands in the editor on that line | |
| 9 | Open each hint | Each one is read out as it opens, and nothing else moves | |
| 10 | Pass a challenge | The pass and any badge are read out, and you can reach "Next" | |
| 11 | Use the lesson list in the sidebar | Done, current and not started can be told apart by hearing alone | |
| 12 | Answer an input card's replies, then run | Each reply box has a name that says what it is for | |
| 13 | Turn on "reduce motion" in the system settings | Nothing slides or fades in a way that delays what is read | |
| 14 | Zoom the browser to 200% on a computer | Nothing is cut off, and everything can still be reached | |

## Recording a problem

For each failure, write down the test number, the screen reader and browser with versions, what you did, what you heard, and what you expected. Open a GitHub issue, or send it to whoever is running the audit. Then retest after the fix, and record that too. QA-01 asks for reproducible defects and retest evidence.

## Results

| Date | Who | Setup | Tests run | Problems found |
| --- | --- | --- | --- | --- |
| | | | | |

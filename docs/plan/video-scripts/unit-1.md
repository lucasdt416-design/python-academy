# Video scripts: Python unit 1, Build Your Own Adventure (EDU-10)

Written 2026-11-09 (America/Toronto) for master run stage WE10. Status: **proposed: scripts only.** Nothing is recorded, hosted or linked from a lesson. Recording, hosting and cost are separate decisions (`teaching-design.md` section 7).  
Related: [`../teaching-design.md`](../teaching-design.md) section 7 (the rules these follow), the unit 1 lessons in `backend/content/py/u01/`.

## How these scripts work

- **One video per lesson, one idea each,** following the lesson's own example, words and order. A video never shows the challenge's answer: it stops where the lesson's "Try it" card starts.
- **Each one is about 2 minutes,** well under the 6-minute limit: about one minute of narration, at roughly 140 words a minute, and the rest typing, running and the pauses. The Time column adds this up; word counts are in section 7.
- **Pause and predict:** each script has one or two places where the video says "pause and predict", then waits two seconds on a still frame before the answer.
- **On screen:** the editor and Output, nothing else. Code at least 24 px high at 1080p, so it is readable on a phone. The line being talked about is highlighted. No music, no faces, no students' voices, no mascots.
- **Captions and transcripts:** the **Narration** column is the transcript. Captions follow it word for word, with code read as written: "print, open bracket, quote", and so on, only the first time. Afterwards the code is described in words.
- **The lesson works without the video.** A video adds nothing the cards don't already say.

Each script has a table: **Screen** (what is shown), **Narration** (what is said). Times are approximate.

## 1. Open the story (`hello`): `print()`

Objective: a program is instructions, run from top to bottom; `print()` shows text.

| Time | Screen | Narration |
| --- | --- | --- |
| 0:00 | An empty editor, titled `story.py` | A program is a list of instructions. Python reads them from the top to the bottom, one at a time. Our first instruction shows words on the screen. |
| 0:15 | Typing `print("You arrive at a moonlit castle.")` | This is print. Lowercase p. Then brackets, and inside them, our words, between matching quotation marks. Text in quotes is called a string. |
| 0:35 | The quotes and brackets highlighted in turn | Every opening quote needs a closing quote, and every opening bracket needs a closing bracket. If one is missing, Python stops and tells you. |
| 0:50 | Run. Output: `You arrive at a moonlit castle.` | When we run it, the words appear. Notice the quotation marks don't. They only tell Python where the text starts and ends. |
| 1:05 | Typing a second line, `print("A tiny dragon opens the gate.")` | Now a second instruction. **Pause and predict: when we run this, which message appears first?** |
| 1:15 | Still frame, 2 seconds | |
| 1:20 | Run. Output shows the castle line, then the dragon line | The castle message first. Python runs the first print before the second, and each print starts a new line. Two instructions, two lines of story. |
| 1:40 | The two lines swapped in the editor; run | If we swap the two lines, the messages swap too. Order matters. |
| 1:55 | The lesson's "Try it" card | Your turn. On the next card, change the dragon into a different creature. Keep the quotes and brackets matching, and run your story. |

## 2. Create your hero (`variables`): variables

Objective: a variable is a name that refers to a value; use it without quotes.

| Time | Screen | Narration |
| --- | --- | --- |
| 0:00 | Typing `hero = "Nova"` | Programs need to remember things. A variable is a name that refers to a value. Here, the name hero refers to the string Nova. |
| 0:20 | The equals sign highlighted | This equals sign doesn't mean "is equal to". It means "store this value under this name". And it prints nothing. |
| 0:35 | Typing `tool = "lantern"`, then `print(hero)` and `print(tool)` | A second variable, tool. Then two prints. Notice there are no quotation marks around hero this time. **Pause and predict: what does print hero show?** |
| 0:55 | Still frame, 2 seconds | |
| 1:00 | Run. Output: `Nova`, then `lantern` | Nova. Without quotes, hero means "use the value stored under this name". |
| 1:15 | Changing one line to `print("hero")`; run. Output: `hero` | With quotes, it's just the word hero. That one pair of quotation marks changes everything. |
| 1:35 | Changing `"Nova"` to `"Kai"` in the first line; run | And here's why variables are useful: change the value in one place, and every print that uses it changes too. |
| 1:50 | `print(pet)` added above any `pet = ...`; run. A `NameError` | One rule: a variable must have a value before you use it. Python reads from the top, so a name it hasn't seen yet is an error. |
| 2:05 | The "Try it" card | Your turn: give your hero a name and a tool of your choice, and run it. |

## 3. Meet the player (`input`): `input()`

Objective: `input()` asks a question and gives back what the player types; store it in a variable.

| Time | Screen | Narration |
| --- | --- | --- |
| 0:00 | Typing `player = input("What is your name? ")` | Now the story can ask the player something. input shows a question, called a prompt, and waits. Whatever the player types comes back as a string, and here we store it in the variable player. |
| 0:25 | The academy's "Player replies" box, with `Nova` typed in | In this academy, you type the player's replies in this box before you run. Python reads them in order. The prompt itself doesn't appear in Output here. |
| 0:40 | Typing `print("Welcome, " + player + "!")` | A plus sign joins strings together. "Welcome, comma, space", then the player's name, then an exclamation mark. **Pause and predict: with Nova as the reply, what appears?** |
| 1:00 | Still frame, 2 seconds | |
| 1:05 | Run. Output: `Welcome, Nova!` | Welcome, Nova! Notice the space after the comma comes from our string. Python doesn't add one when it joins. |
| 1:20 | The reply changed to `Kai`; run. Output: `Welcome, Kai!` | Change the reply, and the story changes, without touching the code. That's what makes a program interactive. |
| 1:40 | The "Try it" card | Your turn: change the welcome, run it with Nova, then with Kai. |

## 4. Choose a path (`choices`): `if` and `else`

Objective: `if` runs its block only when the condition is true; `else` runs otherwise.

| Time | Screen | Narration |
| --- | --- | --- |
| 0:00 | Typing `path = input("Left or right? ")` | A story is better with choices. First, we ask the player: left or right? |
| 0:15 | Typing `if path == "left":` | if checks a condition. Two equals signs compare two values. One equals sign stores a value; two compare. Then a colon. |
| 0:35 | Typing the indented `print("You discover a waterfall.")` | The next line is indented four spaces. Indented lines belong to the if, and run only when the condition is true. |
| 0:50 | Typing `else:` and the indented `print("You find a hidden library.")` | else, with its own colon and its own indented block, runs when the condition is false. Only one of the two blocks ever runs. |
| 1:10 | The reply box: `left`; run. Output: `You discover a waterfall.` | With left, path equals "left" is true, so the waterfall. |
| 1:25 | The reply box: `right` | **Pause and predict: with right, which block runs?** |
| 1:30 | Still frame, 2 seconds | |
| 1:35 | Run. Output: `You find a hidden library.` | The else block. "right" equals "left" is false, so Python skips the if block. |
| 1:50 | The reply box: `Left`, with a capital L; run. Output: the library | Careful: Left with a capital L is not the same text as left, so it takes the else path too. The comparison is exact. |
| 2:10 | The "Try it" card | Your turn: give both paths new discoveries, and run it with left, then with right. |

## 5. Launch your adventure (`adventure`): putting it together

Objective: combine a scene, a name, a choice and two endings, in order, and test every path.

| Time | Screen | Narration |
| --- | --- | --- |
| 0:00 | The full example, appearing line by line | You know four things now: print a scene, store a value, ask a question, choose a path. A game puts them in order. |
| 0:15 | `print("A floating island appears.")` highlighted | First, the scene. |
| 0:22 | `hero = input("Your name? ")` and the welcome line highlighted | Then ask for a name, store it, and use it in a welcome. |
| 0:35 | `path = input("Left or right? ")` and the `if`/`else` highlighted | Then the choice, in its own variable, and two endings. Each reply has its own variable, so they never get mixed up. |
| 0:50 | Replies `Nova` and `left`; run | Let's play. Nova, and left. |
| 0:55 | Output: `A floating island appears.`, `Welcome aboard, Nova`, `You befriend a cloud dragon.` | Three lines: the scene, the welcome, and the cloud dragon. |
| 1:10 | The replies box | **Pause and predict: what's the least you need to test before sharing this game?** |
| 1:15 | Still frame, 2 seconds | |
| 1:20 | Runs with `Kai` and `right`, then `Mira` and `left` | Different names and both paths. One run only tests one path. A mistake in the other ending would only show up when a friend plays it. |
| 1:45 | The "Try it" card | Your turn: remix the floating island into your own world, change both endings, and try different replies. |

## 6. Accessibility and privacy checklist (for whoever records them)

- Captions are the narration, edited only for timing. A full transcript is published under each video.
- Nothing is shown only by colour: the highlight is also a box or an underline.
- The pause-and-predict stills say "Pause and predict" in words on screen.
- No third-party trackers in the player, and no autoplay. If hosting is chosen later, it must allow both.
- No learner work, names or accounts appear. The names used (Nova, Kai, Mira) are the lessons' own.

## 7. Lengths, and how the code was checked

| Script | Narration words | At 140 words a minute |
| --- | --- | --- |
| Open the story | 172 | about 74 seconds |
| Create your hero | 159 | about 68 seconds |
| Meet the player | 137 | about 59 seconds |
| Choose a path | 151 | about 65 seconds |
| Launch your adventure | 133 | about 57 seconds |

Every code sample above was run in Python 3.12.14, with the replies shown, and printed exactly the Output shown in its row.

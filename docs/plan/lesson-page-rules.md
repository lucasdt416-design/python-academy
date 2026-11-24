# Lesson page rules

Status: **in force** from 2026-11-20 (handoff 60). The owner asked for every lesson to be looked at as a learner sees it, and for the page to stay readable "for every lesson so far and forever". These rules come from that review. Each one is checked by a test, named after the rule, so a lesson or scene that breaks one fails CI.

## The page (frontend/tests/lesson-layout.spec.ts, every released lesson)

| Rule | What | Why |
| --- | --- | --- |
| **L1** | On **See it work**, the code is full width; under it, what the run printed and its note sit **beside** the scene. On a phone the scene comes straight after the output. | The picture explains the output, so they are read together. Before, the scene was at the bottom, 800 px wide, far from the code. |
| **L2** | Every label in a scene is **inside its frame** and at least **9 px** on screen. | Labels of 6 to 7 px and text running off the frame were found in several scenes. |
| **L3** | Nothing on the page **scrolls sideways**, at desktop or phone width. | |
| **L4** | **No placeholder pictures.** A lesson with a drawing of its own shows it; others show none, and the layout closes up. | The same "py" hills on 43 lessons said nothing, and on a phone pushed the lesson a screen down. |
| **L5** | On **Your challenge**, the task, **Done when** and the **hints** are together on the left; the editor, run buttons, result and output on the right. Each case's description reads on one line, its expected output under it. | Hints sat at the bottom of the editor column, below the scene, and the description of each case was squeezed to one word per line. |
| **L6** | **No empty scene** in Try it or Your challenge before something has run. | An empty frame saying "Run the code to fill this scene" added nothing. |

## Scenes (reviewed by eye; L1 and L2 are tested)

| Rule | What |
| --- | --- |
| **S1** | A scene **never repeats the output** that is printed beside it. It shows what the output cannot: what is stored, where things move, what was compared, what was skipped. (Exception: a scene whose point is the contrast between printing and something else, like *Print or return?*.) |
| **S2** | A scene **fills its frame**: one main drawing, centred and sized to what it holds, not a small drawing in a corner of an empty box. |
| **S3** | A scene reads its numbers from the **program itself** when the output alone is not enough (the maths scene reads `hypot(3, 4)`; the calendar rings the dates written in the code), and says only what the run showed. |

## Content (backend/tests/test_lesson_clarity.py, every released lesson in course order)

| Rule | What |
| --- | --- |
| **C1** | A function or method the challenge, Try it or a hint names must already be known: used in this lesson's Discover, example or note, or an earlier lesson, or written by the learner, or **explained in the same sentence** ("`abs()` gives a number without its minus sign"). |
| **C2** | A Discover card brings in **at most six** new functions or methods, so each gets its own example. |
| **C3** | A Discover card is **at most 130 words**. Longer means two lessons. |
| **C4** | No paragraph, and no step of a list, in a Discover card, Try it or challenge is **over 45 words**. A longer task is a one-line goal, then numbered steps (`1. `), then what the check does. A blank line starts a paragraph; `- ` starts a list item (`frontend/app/prose.tsx`). (2026-11-24, handoff 63) |

Code in lesson text is shown as code automatically (`frontend/app/prose-runs.ts`): authors keep writing plain sentences, and unit 1's text stays frozen.

## The whole site (2026-11-23, handoff 62)

The owner asked for every page to be questioned: "is this actually good, or is it AI slop?" These came from looking at the home, course, practice, profile and lesson pages at desktop and phone width.

| Rule | What | Found and fixed |
| --- | --- | --- |
| **D1** | **No icon in a coloured square** next to a label that already says it. | The five lesson steps on the home page and the tab of every lesson card repeated the stepper's icon in a coloured box. Now a numbered row with a coloured rule, and a plain tab. |
| **D2** | **No box inside a box.** Inside a panel, items are divided by a rule, not given cards of their own. | The self-review parts, and the parents' list on the home page. |
| **D3** | **No drop shadows** on cards and panels; a border is enough. | The lesson card and the home page's code preview. |
| **D4** | **No slogans.** Every line of text tells the reader something they can use or check. | "Built for curious minds. Designed for room to grow." (every footer), "One idea at a time." and "Your story. Your pace." (every lesson card). The card footer now says why Continue is waiting, when it is. |
| **D5** | **Every claim is true today**, and counts come from the data. | "Eleven of the twelve units are open" (now twelve), "twelve units open, no on the way", "1 lessons", and "your brief is kept so you can read it back", which had no way to read it back. It now comes back into the form. |
| **D6** | **A page is never just a heading and a button.** If it is for signed-in learners, it shows what is behind the sign-in. | The signed-out Practice arena now shows a creature and how taming works. |

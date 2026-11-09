# Lesson pictures: how they are drawn

Every lesson has one picture that shows **the idea the lesson teaches**, set in the adventure's world. The pictures live in `frontend/app/lesson-art.tsx`, keyed by lesson id (`LESSON_ART`). A lesson with no picture of its own gets the plain fallback: green hills under a small `py` sign. The originals are the `<symbol>` elements in `docs/design/prototype/index.html`.

## The frame

- **320 × 180** (`viewBox="0 0 320 180"`, 16:9). One picture serves every size: the lesson heading, course rows (96 px wide), the unit list beside a lesson (52 px wide) and the student home.
- **Rounded background**, `<rect width="320" height="180" rx="16"/>`, tinted by unit:

  | Unit | Background class | Colour |
  | --- | --- | --- |
  | 1, Build Your Own Adventure | `bg1` | mint `#dcebe2` |
  | 2, Numbers and decisions | `bg2` | sand `#f1e6c8` |
  | 3, Repeat and explore | `bg3` | blue-grey `#d3e3e6` |
  | 4 and later | Pick a new pale tint, add a `bg4` class to `style.css`, and add a row here | |

- **Ground:** one or two soft hills along the bottom, a quadratic path such as `M0 146Q90 126 170 142T320 134V180H0Z`, in `f-moss-l` (light) with an optional `f-moss` hill in front.

## Shapes and lines

- **Flat shapes, one outline weight.** No gradients, shadows, filters, patterns or images.
- **Outlines** use the stroke classes: `s-ink` (2.5 px, the default), `s-ink-s` (1.6 px, for small things such as coins), `s-ink-w` (6 px, beams and poles), `s-moss`/`s-moss-s`/`s-moss-w` (the same in moss green), `s-clay-w` (4 px clay, for a path or an arrow that matters), `s-cream-w` (16 px, a road), `s-slate-d` (dashed, for "and so on"). All have round caps and joins.
- **Fills** use only the palette classes: `f-white`, `f-cream`, `f-amber`, `f-amber-l`, `f-moss-l`, `f-moss`, `f-plum`, `f-slate`, `f-clay`, `f-ink`. A shape can carry one fill and one stroke class (`class="f-cream s-ink"`); the fill wins because the fill rules come later in `style.css`.
- **Sparkles:** four-point stars in `f-amber` (`M270 30l4 10 10 4-10 4-4 10-4-10-10-4 10-4z`), at most two per picture.
- **People** are simple: a circle head (`f-cream` or `f-amber-l` with `s-ink`) on a rounded plum body. No faces, no hands, no hair, no skin tones.

## Words in pictures

- **Only code, in the mono font**: `<text class="mono f-ink" font-size="12–18">`. Use `f-moss` for a line of code that names the idea (`hero = "Kai"`, `range(0, 10, 2)`), `f-clay` for the value that changes or is wrong.
- **Code shown must be true Python** and match the lesson: `17 // 5 = 3` is fine as a caption; `while guess != secret:` must be valid if run.
- Text at least 11 at this scale, so it stays legible at 280 px wide. In the 52 px thumbnails it is decoration only; the lesson title sits beside it.
- `sans` text only for one-word labels (`text`, `number`).

## Accessibility

- In the lesson heading and on the home page, the picture is an image with a description (`role="img"`, `aria-label`). **Write the description in `LESSON_ART`**: what is shown, in one sentence, naming the idea ("Five pouches with three coins each and two coins left over in a chest").
- Beside a lesson's own title (course rows, the unit list, the student home strips) pass `label={false}`: the picture is hidden from screen readers so the title is not read twice.
- Nothing in a picture is the only place a fact appears. Colour never carries meaning on its own.
- Pictures never move. If one ever animates, it must be under `@media (prefers-reduced-motion: no-preference)` only.

## Adding a picture

1. Draw it in the frame above, using only the classes listed (no `style` attributes and no `fill="#…"`: the page's Content-Security-Policy and the palette both depend on that).
2. Add it to `PICTURES` in `lesson-art.tsx` under a new `art-…` id, in JSX (`className`, `fontSize`, `fontWeight`).
3. Map the lesson id to it in `LESSON_ART`, with its description.
4. Add the lesson id to `PICTURES` in `frontend/tests/redesign.spec.ts`. The test fails if a released lesson's row shows any other picture.
5. Optionally add a `<symbol>` copy to the prototype so the gallery (`#art`) stays complete.

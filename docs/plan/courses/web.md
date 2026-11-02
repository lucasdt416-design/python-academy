# Web Foundations: HTML and CSS (`web`): course design

Status: **proposed**, written 2026-11-02. No code and no catalog change. Sources: `course-catalog.md` section 3.4, `teaching-design.md` section 6.4, `build.md` sections 5 and 7, backlog WEB-01.

## Audience and prerequisites

Practical builders, on the way to full-stack work.

- **Required:** `py.u01` to `py.u03`. `build.md` notes HTML may start earlier.
- **Suggested:** `git`.

## Outline

| Unit | Title | Lessons (proposed IDs) |
| --- | --- | --- |
| `web.u01` | Structure | `web.elements`, `web.headings-and-text`, `web.links-and-images`, `web.lists-and-tables` |
| `web.u02` | Forms and meaning | `web.semantic-sections`, `web.forms-and-labels`, `web.keyboard-and-screen-readers` |
| `web.u03` | Style | `web.selectors`, `web.box-model`, `web.colour-and-contrast`, `web.fonts-and-units` |
| `web.u04` | Layout | `web.flexbox`, `web.grid`, `web.responsive`, `web.reduced-motion` |
| `web.u05` | Your site | `web.plan-a-site`, `web.several-pages`, `web.check-your-site` |

Accessibility is part of every lesson, and `web.u02` only names it directly.

## Projects and evidence

**Personal website** (`build.md` section 7): a responsive site with semantic navigation. Guided build, independent brief, stretch extensions. No public posting or paid hosting is needed.

| Evidence | Label |
| --- | --- |
| Structural checks pass | Practice |
| Automated accessibility rules pass | Practice. It finds some problems, and it does not prove a page is accessible, so messages must say that |
| Visual design | Self-assessed or reviewed against a published rubric, never automated |

## Runtime and safety

**An isolated preview:** a sandboxed `iframe` with **no** `allow-scripts` and **no** `allow-same-origin`, holding the learner's HTML and CSS.

| Threat | Control |
| --- | --- |
| Learner HTML runs a script | No `allow-scripts`; an inline policy of `default-src 'none'; style-src 'unsafe-inline'; img-src data:` as a second layer |
| The page reads the app's session | No `allow-same-origin`, so it has an opaque origin. Session cookies are `HttpOnly` as well |
| The preview loads outside content, leaking the visitor's address | `default-src 'none'`, so no outside images, fonts or stylesheets. Lessons supply images as embedded data |
| A link or form navigates away | No `allow-top-navigation` or `allow-forms`; form submission is shown as text instead |
| A tracker in copied HTML | Blocked by the same policy |

**To test before relying on this:** how the preview fits the app's page policy (a `frame-src` entry may be needed), that `frame-ancestors 'none'` does not stop it, and that the preview works on Safari and Firefox, which the project has not tested. Any change to the page policy gets its own security note.

Nothing is sent to the server except, as today, the code and the reported results.

## Dependencies

None for the preview. An accessibility rules engine is the one candidate: axe-core is already used in scratch runs but is not a dependency of the app. If shipped to learners it would be a new dependency, so the first version uses a small hand-written rule list. Its name, size, licence and integrity would be checked first if that changes.

## Checker features required

- **A `web_preview` task type:** source, a preview, reported facts.
- **Structural checks.** The browser parses the HTML into a detached document with `DOMParser`, which runs no scripts, and reports facts: heading order, labels on inputs, `alt` on images. The API judges those facts.
- **Computed style checks,** only where the result is objective, such as "this colour pair has enough contrast".

## Risks

- **Reports can be faked,** as with all browser checks. Practice evidence only.
- **Checking the wrong thing.** Two correct pages can have very different markup, so rules must be about behaviour and meaning, not exact tags.
- **A message may only claim what was checked.** "No problems found by this check" is honest, and "your page is accessible" is not.

## Open questions for Lucas

Each recommendation is **recommended, not yet confirmed**.

1. Is it fine that previews allow no outside images? *Recommended: yes. It is the simplest way to protect the visitor's address.*
2. Should the course show how to publish a site? *Recommended: as an optional free local-first tutorial, with no badge tied to it.*
3. Should the preview use a separate origin, not just a sandbox? *Recommended: not for `web`, since no scripts run. Revisit in `js`.*

# Public website and product design direction (SITE-01)

Last updated: 2026-10-26 (America/Toronto)  
Status: **proposed**. Design direction only: no application code changes. The owner chooses a story concept (section 1) and an architecture (section 5) before anything is built.  
Related: [`build.md`](../../build.md) sections 1, 3 and 4; [`course-catalog.md`](course-catalog.md) sections 2 and 3; [`teaching-design.md`](teaching-design.md); handoff 08 (the nonce-based Content-Security-Policy and its cost).

**The owner's vision.** A top-tier "wow" public website that tells the story of the mission and ends in a button into the product, as some companies keep a storytelling site apart from their product. The landing page is a scroll-driven, illustrated story with a short intro, scenes that change as you scroll, and small interactive moments. The product stays simple, calm and fast, in today's colours, with more polish.

**Inspiration, not a source.** hackcanada.org was named as inspiration for the *idea* of an illustrated scroll story. Nothing here copies its art, mascot, layout, text or code; the concepts below are built from our own unit 1 world.

## 0. What we have today

Read from `frontend/app/` at `main` `27ab31b`:

- **Colours:**
  - deep forest greens for headings and buttons, for example `#1d4532` and `#244532`
  - sage and mint backgrounds, for example `#f3f7f2` and `#eaf2e5`
  - warm parchment and gold accents for "Coming soon" and the Continue button, for example `#f9f0d6`, `#e6d7ad` and `#85651c`
  - a blue for links, `#2867c8`
- **Type:** Arial and Helvetica, with large, tight headlines ("Build Your Own **Adventure.**", the last word in green).
- **Illustration:** one hand-written inline SVG scene in `adventure.tsx`: a moonlit castle, rolling hills, a path, a moon and sparkles. It has five variants, one per lesson (castle, backpack and lantern, a welcome message, two paths, a floating island), each with a text description. Small CSS animations (`twinkle`, `moon-glow`, `card-arrive`) are already turned off under `prefers-reduced-motion`.
- **Tone:** "Small steps. Real skills." · "Built for curious minds. Designed for room to grow." · "One idea at a time."
- **Rendering:** every page renders per request, because of the per-request nonce (handoff 08). Cloudflare does not cache pages (`cf-cache-status: DYNAMIC`).
- **Something to tidy:** the stylesheet has about 70 different hard-coded colour values, many of them near-duplicate greens. SITE-03 would replace them with about a dozen named colours (CSS custom properties). That is the cheapest way to make the product look more polished and consistent.

The story site should feel like it belongs to that world: the same greens, parchment and gold, the same moonlit castle language, drawn bigger and with more depth.

**The mission,** in one line from `build.md` section 1: *help someone go from their first program to independently designing, testing, explaining and shipping useful software.* The landing page says this in a grade 9 voice: **"From your first line of code to something real you built yourself."**

## 1. Three story concepts

Each concept is a single page of 6 to 8 "scenes". Every scene works as plain text and a still picture first, and motion is added on top (section 3).

**Calls to action used in every concept:**
- **Primary:** "Try the first lesson, no account needed" → `/preview?lesson=hello`. This already exists, saves nothing and needs no sign-in.
- **Secondary:** "Sign in to save your progress" → the product's welcome page.
- **For teams:** "Hackathon Ready is coming" → the catalog.

### Concept A: The Lantern Path (a journey)

You walk a path at night with a lantern, from a small cottage to the moonlit castle. Each step on the path is one of the skills of unit 1.

| # | Scene | What scrolling does | Interactive moment |
| --- | --- | --- | --- |
| 1 | **Intro:** a dark hillside; a lantern flickers on and the title appears, "Every adventure starts with one line." | The lantern lights the path ahead as you start scrolling | None; skipped entirely if reduced motion is set |
| 2 | **The first line:** a signpost reads `print("You arrive at a moonlit castle.")`, and the castle appears on the horizon | The words appear as the castle fades in | A "predict" button: "What do you think this prints?" with two choices, then the answer |
| 3 | **Your hero:** a backpack and lantern; `hero = "…"` | The backpack opens as the scene arrives | Type a hero name; the signpost and later scenes use it. It runs in JavaScript only, and is labelled "a preview of what you'll write" |
| 4 | **Meeting someone:** a figure at the gate asks your name (`input()`) | A speech bubble appears | None, so the story keeps moving |
| 5 | **The fork:** two paths, left to the waterfall and right to the library (`if` / `else`) | The path splits as you scroll | Choose left or right; the next scene shows that path |
| 6 | **The mission:** the path climbs and the lands beyond appear: a lake of data (SQL), a town of web pages, bridges (Git), a festival of tents (hackathons), a lighthouse (working with AI). "From your first line of code to something real you built yourself." | A slow pan across the horizon | Tap a land to read one sentence about what you'll build there (coming-soon lands are marked) |
| 7 | **How it feels:** three small cards: "One idea at a time", "Your code runs in your browser", "Hints, never answers" | Cards settle in | None |
| 8 | **The gate (call to action):** the castle gate opens | The gate opens at the end of the scroll | **Try the first lesson** (primary) · Sign in · For teams |

- **Where the mission sits:** scene 6, after the reader has "written" four lines, so the big promise lands once they have felt the small one.
- **Strengths:** the most emotional; a direct continuation of the unit 1 art.
- **Risks:** the most illustration work (8 scenes); the mission arrives late for teachers and team leads who skim.

### Concept B: Your Code Builds the World (code and picture side by side)

A blank page splits in two. On the left, a short Python program grows one line per scene. On the right, the world draws itself from that line. At the end the reader sees the complete program and the world it made, which is exactly what the first unit teaches.

| # | Scene | What scrolling does | Interactive moment |
| --- | --- | --- | --- |
| 1 | **Intro:** an empty editor with a blinking cursor; "What would you build?" | The cursor types the first character as you begin | None; under reduced motion the full first line is simply there |
| 2 | `print("You arrive at a moonlit castle.")` | The sky, hills and castle appear | **Predict first:** "What will this print?" Pick, then reveal (`teaching-design.md` section 2.2) |
| 3 | `hero = "Nova"` and `print(hero + " carries a lantern.")` | A small hero appears with a lantern | **Rename the hero:** type a name; the code and picture update together |
| 4 | `name = input("Who goes there? ")` | A speech bubble appears at the gate | Type a reply; the greeting line uses it |
| 5 | `if path == "left":` … `else:` … | The path forks, and the chosen branch lights up | **Left or right:** a toggle switches which branch of the code is highlighted and which scene shows |
| 6 | **The mission:** the code panel zooms out to show the whole program; the world zooms out to show the lands beyond. "This is unit 1. It's where everything starts: from your first line of code to something real you built yourself." | A zoom out | None |
| 7 | **Honest promises:** "Runs in your browser" · "Hints, never answers" · "Checks tell you what they checked" · "Free to start" | Each line arrives with a small icon | None |
| 8 | **Call to action:** "Write your first line" | The editor cursor blinks under the button | **Try the first lesson** (primary) · Sign in · For teams |

- **Where the mission sits:** scene 6, after the reader has watched four lines of code make a world.
- **Strengths:**
  - It shows the product honestly; this is literally what unit 1 teaches.
  - It teaches as it markets (predict first; code changes the picture).
  - It needs the fewest illustrations (one world built in layers).
  - It speaks to grade 9 beginners and to developers.
- **Risks:**
  - Code on a landing page can scare some beginners, so the lines must be short and friendly.
  - It must say plainly that the interactive bits are a preview: they run in JavaScript, not Python, and real Python runs in the lesson.

### Concept C: The Map (the whole academy)

A hand-drawn map unrolls as you scroll. You start in Python Valley (the unit 1 castle), and the map widens to show every course as a region, with a dotted trail between them.

| # | Scene | What scrolling does | Interactive moment |
| --- | --- | --- | --- |
| 1 | **Intro:** a rolled-up map; "Where do you want to go?" | The map unrolls | None; under reduced motion the map is simply open |
| 2 | **Python Valley:** the castle and two paths, "Start here: five small quests" | The valley comes into focus | A tiny `print` preview, as in concept B scene 2 |
| 3 | **Choose your goal:** the six goals from the goal card (learn from scratch, hackathons, university, websites, data, explore) | The trail for the chosen goal lights up | **Pick a goal;** the trail redraws, mirroring the real recommendation rules |
| 4 | **The regions:** Git Bridges, Web Town, SQL Lake, Node Workshop, Hackathon Camp, the AI Lighthouse | A pan across the map | Tap a region for what you'll build; "Coming soon" regions are drawn in pencil, not ink |
| 5 | **The mission,** as the map's legend | The legend settles in a corner | None |
| 6 | **For teams:** Hackathon Camp up close: scope, time-box, branches, demo | Tents appear | None |
| 7 | **Call to action:** "Begin at the trailhead" | The trail glows to the trailhead | **Try the first lesson** · Sign in · For teams |

- **Where the mission sits:** scene 5, as the map's legend; the whole page is effectively the mission.
- **Strengths:**
  - It shows growth beyond Python, which fits a future rename (section 5.3).
  - It is the best concept for teams and teachers.
  - It reuses the real goals and paths.
- **Risks:**
  - The least about writing code, so the "small steps" feeling is weaker.
  - A big map is hard on phones.
  - Showing many coming-soon regions could over-promise.

### Comparison and a suggestion

| | A: Lantern Path | B: Code Builds the World | C: The Map |
| --- | --- | --- | --- |
| For a grade 9 beginner | Strong (story) | Strong (they see that they can do it) | Medium |
| For other students and teams | Medium | Medium | Strong |
| Honesty about today's product | Medium | **Strongest** (it is unit 1) | Risk of over-promising |
| Illustration work | Most (about 8 scenes) | Least (one world in layers) | Medium (one large map) |
| Works on a phone | Good | Good (code above, world below) | Hardest |
| Fit with a future rename | Medium | Medium | Strongest |

**Suggested default: Concept B,** ending with a small version of C's map in its mission scene (scene 6). This shows the real product honestly, teaches as it markets, needs the least art, and still shows where the academy is going. The owner chooses (question 1).

## 2. Illustrations: options and cost

| Option | Cost | Consistency | Animation | Weight and speed | Rights | Fit |
| --- | --- | --- | --- | --- | --- | --- |
| **Commissioned art** (a human illustrator) | Paid: quotes vary widely by artist and scope, so get two or three quotes for 8 to 12 scenes. Not estimated here | Excellent | Only if delivered as layered SVG, or with separate parts | Depends on format; raster images need care | Clear, with a written licence covering the website, the course and the book | Best quality, but conflicts with the free-first rule; slower |
| **AI-generated art in one style** | Low (a tool subscription or a free tier) | Hard: characters and details drift between images; needs careful curation | Poor: flat images cannot move their parts | Heavy raster files; needs WebP or AVIF in several sizes | Tool terms vary; AI images may not be protectable by copyright; some families and teachers dislike AI art on a children's learning site | Fastest first draft, weakest fit |
| **Hand-written SVG scenes** (extending today's castle style) | Free (time only) | Excellent: one palette, one shape language, already used in the product | Excellent: every hill, star and gate can move separately with CSS | Tiny (a scene is a few kilobytes); sharp at any size | Ours, in the repository, reviewable like code | Matches the product exactly; simpler, flatter style |

**Recommendation: hand-written SVG scenes,** in the style of the existing castle:
- It is free, the shapes can be animated separately, it is tiny and fast on school laptops, it is accessible (each scene has a text description), and it is reviewed in pull requests like code.
- It also makes the landing page and product look like one family, which is half of "polish".
- Claude Code can draft scenes as SVG code, and a person refines them. If the owner later wants one "hero" illustration by an artist, it can be commissioned as layered SVG and dropped in without changing anything else.
- **Rules:** use the palette in section 0; flat shapes with soft gradients; no text inside images (text stays real text, so it can be translated and read aloud); every scene has `role="img"` and a description; and no copying of any other site's characters or art.

## 3. Motion principles

**Motion explains; it never decorates the reading.** Every scene must make sense as text and a still picture.

| Animates | Never animates |
| --- | --- |
| Scenes fading or sliding a short distance as they arrive (opacity and transform only) | **Scroll speed or direction:** no "scroll-jacking", no smooth-scroll libraries that take over the wheel or trackpad |
| Gentle depth: background hills moving a little slower than the foreground (a few percent) | Text while someone is reading it; no parallax on paragraphs |
| The code panel "typing" a line, and the world drawing that line (concept B) | Anything that flashes more than three times a second (WCAG 2.3.1) |
| Small idle loops (twinkling stars, a flickering lantern), each stopping after a few seconds | Auto-advancing carousels, auto-playing video or sound |
| Feedback on interactive moments (a toggle sliding, the path lighting up) | Anything needed to understand the content |
| A short intro, at most about 1.2 seconds, over content that is already on the page | **A loading screen that hides content.** The intro never blocks reading or the buttons, and is skipped on later visits in the same session |

**Reduced motion** (`prefers-reduced-motion: reduce`, set in the operating system):
- All scroll-linked and idle animation is off.
- Scenes appear as a simple column of still pictures with their text, and the intro is skipped.
- The interactive moments still work; their results appear instantly.

**A visible "Pause animations" button** also stops all motion for people who have not set the system option (WCAG 2.2.2). It is remembered in the browser only (`localStorage`), never on a server.

**Performance budget.** Targets are measured on a throttled profile (DevTools: 4× CPU slowdown, "Slow 4G") as a stand-in for a school Chromebook, and on a real mid-range phone:

| Measure | Budget |
| --- | --- |
| Largest Contentful Paint (when the main picture or heading appears) | ≤ 2.5 s on the throttled profile |
| Interaction to Next Paint (how quickly a tap responds) | ≤ 200 ms |
| Cumulative Layout Shift (things jumping around) | ≤ 0.1 |
| Data for the first screen | ≤ 600 KB on a phone; ≤ 1 MB for the whole page |
| JavaScript for the story itself | ≤ 30 KB compressed if it is a separate static site; ≤ 60 KB extra if it is inside the Next.js app |
| All illustrations together | ≤ 150 KB compressed |
| Scrolling | No task longer than 50 ms while scrolling; about 60 frames per second on a laptop, at least 50 on the phone |
| Render memory (only if it lives in the app) | At least 150 MB free on the 512 MB Starter instance at peak |

## 4. Technical approach

### 4.1 Animation tools

| Option | What it is | Dependency | Works with our Content-Security-Policy | Verdict |
| --- | --- | --- | --- | --- |
| **CSS only:** scroll-driven animations (`animation-timeline: view()`), plus a small `IntersectionObserver` script that adds a class when a scene arrives | Built into browsers | None | Yes: no inline script, no `eval` | **Recommended to start.** Scroll-driven CSS is supported in Chromium-based browsers and recent Safari, but not everywhere (Firefox has had it only behind a setting), so the observer script is the fallback. Check browser support again when building |
| Motion (motion.dev, MIT licence) | A JavaScript animation library with scroll helpers | One npm package, bundled with the app (no CDN) | Yes, if we never rely on style attributes in the server's HTML (see below) | Only if CSS cannot do a moment well; measure its size first |
| GSAP with ScrollTrigger | A popular animation library | One npm package, bundled | Yes, with the same caution | Free to use, but under its own licence, not an open-source one; read the terms before choosing |
| Lottie | Animations exported from design tools as JSON | Package plus JSON files | The full player has used `eval` for expressions, which our policy forbids | Avoid |
| Smooth-scroll libraries (for example Lenis) | Take over scrolling | Package | Yes | **Avoid:** scroll-jacking hurts accessibility |
| 3D (for example three.js) | WebGL scenes | Large package | Yes | Avoid: too heavy for school laptops |

**Content-Security-Policy rules that any choice must follow:**

- Scripts are **bundled and served from our own site**: no CDN for the page, as the policy requires (`script-src 'self'` plus the nonce). Nothing may need `'unsafe-eval'`.
- **No `style="…"` attributes in the HTML the server sends.** Our page policy is `style-src 'self'`, which blocks inline style attributes, and a nonce cannot allow them. Some React animation helpers write starting positions as `style` attributes during server rendering, which would be reported (Report-Only now) or blocked (once enforced). The safe pattern:
  - put starting states in CSS classes in the stylesheet
  - change values only from JavaScript after the page loads, through the CSS object model, for example `element.style.setProperty('--progress', value)`, which the policy allows
  - a Playwright test fails on any CSP report, so this rule is enforced by tests
- **SVG:** use presentation attributes (`fill="…"`) and classes, not `style` attributes or `<style>` blocks inside the SVG.
- **The proxy:** in the Next.js app, `frontend/proxy.ts` gives every page request a nonce. A story page inside the app is rendered per request like every other page. A separate static site (5b) has no proxy and needs no nonce, because it has no inline scripts at all.

### 4.2 Rendering, memory and cost today

- Every app page is rendered per request (`connection()` in the root layout), because the nonce must be new each time.
- Measured in handoff 08 on a laptop: about 0.5 ms more CPU per page than a static page, and about 57 MB more server memory after a load test.
- The frontend runs on Render **Starter** (512 MB, 0.5 CPU, flat monthly price). There is no per-request charge, but a traffic spike to the landing page (for example a hackathon sharing the link) would use the same small instance that serves learners.
- A story page inside the app would be heavier than today's pages (big SVG, more markup), and is the page most likely to get bursts of visitors.

### 4.3 What must be measured, before and after

- **Speed** (section 3 budget): Lighthouse in Chrome DevTools (free, built in) on the throttled profile and on a real phone, for the landing page and for `/learn/hello`.
- **Scroll smoothness:** Chrome DevTools → Performance, recording a full scroll: long tasks, dropped frames, layout shifts.
- **Weight:** bytes transferred and JavaScript size (DevTools → Network).
- **Server (only if inside the app):** Render → python-academy → Metrics, memory and CPU before and after launch, plus time to first byte for `/` under a short burst (for example 200 requests, 10 at a time, as in handoff 08).
- **Policy:** zero CSP reports in the console and in the Playwright listener.

## 5. Architecture: where the story lives

### 5.1 The two options

**(a) Same Next.js app.** The story at `/`, and the product's signed-out home moves to `/app`.
**(b) Separate static site.** Plain files on a CDN, with no login and no cookies, linking into the app. Today's app stays exactly where it is.

| | (a) Same app, story at `/` | (b) Separate static site |
| --- | --- | --- |
| **Render cost** | No new service. Uses the Starter instance's CPU and memory for every visitor | A new **Render static site**, which Render lists as free (confirm current limits at decision time). The app's instance is untouched by landing-page traffic |
| **Security** | Same origin as the app and its session cookie; the story must follow the nonce policy and has no extra isolation | **No login, no cookies, no API**, so there is nothing to steal there. A strict policy with no inline script at all (`script-src 'self'`), and no nonce needed |
| **Performance** | Rendered per request on 0.5 CPU, not cacheable | Static files served from Render's CDN, cacheable, fastest for the first visit |
| **Changes to the app** | Moving the product's home to `/app` touches: the redirect after Google sign-in (to `/` today); invitation links (`/#invite=…`, and `/?invite=…` from before SEC-06); old links and bookmarks (need redirects); tests | **None.** The app's welcome page stays as it is; the story just links to it |
| **Maintenance** | One codebase and one deploy; can reuse React components | A second, small build, kept in the same repository (for example a `site/` folder and one more entry in `render.yaml`). Colours and type shared through a small tokens file |
| **Tooling** | React, already here | **Plain HTML, CSS and a small amount of JavaScript, with no build step and no new dependencies** (proposed), or a static-site tool if it grows |

**Recommendation: (b), a separate static site** in the same repository:
- It costs nothing extra.
- Landing-page traffic can never slow down learners.
- It holds nothing worth attacking.
- It is the fastest possible "wow" on a school laptop.
- It needs **no changes** to sign-in, invitations or the app's routes.

The price is a second small deploy, and colours kept in step between two places. Choose (a) only if one URL with no custom domain matters more than speed and isolation.

### 5.2 Without a custom domain

Without one, the two sites live at two `onrender.com` addresses: the existing `python-academy-dji8.onrender.com`, and a new one Render assigns to the static site. That works, but looks less polished. Nothing else depends on a domain.

### 5.3 A custom domain and a possible rename

The product is growing beyond Python (SQL, Node.js, Git, hackathons, AI), so "Python Academy" may become too narrow. `build.md` section 16 already lists the brand as an open decision.

**A custom domain** (for example `www.<name>` for the story and `app.<name>` for the product) would involve:

1. **Buying a domain:** a yearly fee at a registrar, an owner decision and a paid item.
2. **DNS records** at the registrar pointing both names to Render. Render issues the HTTPS certificates. Custom domains are available on Render's plans; confirm at decision time.
3. **App settings (owner actions in Render):**
   - `APP_ORIGIN` and `API_ORIGIN` change to the new address
   - every **Google OAuth** authorized redirect URI and JavaScript origin is updated in Google Cloud
   - the static site's links are updated
4. **Sign-in:** session cookies belong to the old address, so everyone signs in once after the move. Old `onrender.com` links should redirect.
5. **HSTS:** our header includes `includeSubDomains`. Once it is served on the main domain, every subdomain must use HTTPS too. That is fine, but should be decided knowingly.

**A rename** would also touch:
- the header's "py" logo and name, page titles and metadata
- the Google sign-in consent screen's app name, which may need Google's review if the app is published beyond testing
- `DEPLOYMENT.md`, `README.md` and handoff references
- optionally the GitHub repository name (GitHub redirects old links)

It would **not** change course, unit, lesson or badge IDs (they are stable by design), saved progress, or the database.

**Suggestion:** decide the name before buying a domain and before drawing the logo into the story. Until then, build the story site at its free `onrender.com` address with the name written in one place, so a rename is a one-line change.

## 6. Accessibility

| Area | What we commit to | How we test |
| --- | --- | --- |
| Reduced motion | Section 3: all motion off, scenes stacked, intro skipped; plus a visible pause button | Playwright with `reducedMotion: 'reduce'` checks that no animation runs and all text is visible; a manual check with the operating-system setting on |
| Keyboard | Every interactive moment is a real `<button>`, `<input>` or radio group; visible focus; a "Skip the story" link to the call to action; no keyboard traps; scrolling works with the keyboard | Playwright keyboard tests: tab through the whole page, use each moment, reach the call to action |
| Screen readers | One `<h1>`; each scene is a section with a heading and real text; pictures have short descriptions; decorative motion is hidden from assistive technology; results of interactions announced politely | Automated checks with **axe-core** (used since stage 3); manual checks with **VoiceOver** (built into macOS and iOS) and **NVDA** (free, Windows), as QA-01 asks |
| Contrast | Text meets WCAG AA (4.5:1, or 3:1 for large text), including text over illustrations, which gets a solid panel behind it | axe-core, plus a manual check of every text-over-picture spot in both states of each animation |
| Text size and zoom | Works at 200% zoom and with larger default text; reflows at 320 px wide without horizontal scrolling (WCAG 1.4.10) | Playwright at 320 px and at 200% zoom; manual browser zoom |
| Phones | Concept layouts stack (code above the world in concept B); touch targets at least 44 px; no hover-only content | Playwright at 375 px (as today) and a real phone |
| Language and reading level | Short sentences a grade 9 reader understands; the meaning of code explained in words | Human review; read aloud |

## 7. How the product should evolve (SITE-03: polish, not a redesign)

The product stays calm: one idea at a time, the same layout and the same colours. SITE-03 makes it feel like the same family as the story, without adding busyness.

- **Everywhere:**
  - replace the ~70 hard-coded colours with about a dozen named colour variables
  - one spacing scale and one corner radius
  - a slightly warmer system font stack instead of Arial (no web font download), keeping the large headings
  - the same small "py" mark, or the new logo after a rename
- **Catalog:**
  - Show available courses first, with a small SVG emblem for each course in the story's style (a castle for Python, a bridge for Git, a lake for SQL, a lighthouse for AI).
  - Group the ten "Coming soon" courses into a quieter, compact "Coming later" list. Today they fill most of the page; see handoff 04's screenshot.
  - Keep the Recommended chip and the progress bars.
- **Course page:**
  - A wide, short header illustration (the course's scene, drawn in the story's style), the title and progress.
  - Units below exactly as now.
  - No new animation beyond a gentle fade-in, which stops under reduced motion.
- **Lesson page:**
  - Unchanged structure (sidebar, one card, the editor).
  - The existing scene gains small story details matching the landing page.
  - Passing a challenge shows the badge with a short, single celebration (a few sparkles, under a second, off under reduced motion), replacing nothing that exists.
  - No motion while the learner is reading or typing.
- **Measured:** the same budgets and accessibility checks as section 6, and no layout changes that break existing tests.

## 8. Plan in stages (one PR each)

| Stage | Delivers | Live check |
| --- | --- | --- |
| **1. SITE-01** (this PR) | This design direction | The owner reads it and answers section 10 |
| **2. Static story skeleton** (SITE-02, part 1) | The chosen concept as **plain text and still SVG scenes**, no motion: headings, the mission and the calls to action into `/preview?lesson=hello`. Plus security headers and a strict policy, deployed as a new static site (the owner creates the Render static site from `render.yaml`) | The page loads at its new address; all links work; `curl -I` shows the headers; axe shows 0 violations; Lighthouse within budget |
| **3. Scenes and motion** (SITE-02, part 2) | Scroll-driven scene transitions in CSS, the pause button, reduced-motion behaviour, and the short intro | Scroll on a laptop and a phone; turn on reduced motion and see a still page; DevTools Performance shows no long tasks during scrolling |
| **4. Interactive moments** (SITE-02, part 3) | Predict, rename the hero, left or right, tap a region: all keyboard-accessible, labelled as previews | Do each moment with a mouse, a keyboard and VoiceOver |
| **5. Product tokens** (SITE-03, part 1) | Named colour variables and the spacing and type scale in the app, with **no visible change** beyond tidier colours | All existing Playwright tests pass; screenshots compared before and after |
| **6. Product polish** (SITE-03, part 2) | Catalog grouping and course emblems, course header art, the lesson celebration | Catalog, a course and a lesson on a laptop and a phone; reduced motion; no new CSP reports |
| **7. Domain and name** (SITE-04, only if the owner decides) | The custom domain on both sites, updated origins and OAuth settings (owner actions), redirects, and any rename | Sign in on the new domain; old links redirect; headers and HSTS are correct |

## 9. Backlog rows to add

In the `build.md` format; not added to `docs/plan/backlog.md` in this PR.

| ID | Priority | Item | Depends on | Status |
| --- | --- | --- | --- | --- |
| SITE-01 | Next | Design direction for the public story site and the product's look (`docs/plan/site-design.md`): three story concepts, illustration approach, motion and performance budget, architecture, accessibility, staged plan | None | in_review (handoff 13) |
| SITE-02 | Next | Public landing story site: the chosen concept as a separate static site (proposed), built in three PRs: skeleton with still scenes and strict headers; scroll motion with reduced motion and a pause button; interactive moments. Within the section 3 budget, 0 axe violations | SITE-01 decisions (concept, architecture) | proposed |
| SITE-03 | Later | Product polish to match the story, not a redesign: colour and spacing tokens, catalog grouping with course emblems, course header art, a short lesson celebration; calm and fast | SITE-02 (shared style) | proposed |
| SITE-04 | Later | Custom domain and possible rename: choose a name, buy a domain (paid, owner decision), DNS, `APP_ORIGIN` and `API_ORIGIN`, Google OAuth settings, redirects, one-time sign-in again | Owner decision on name and cost; `build.md` section 16 (brand) | proposed |

## 10. Questions for the owner

1. **Concept:** A (Lantern Path), B (Code Builds the World), C (The Map), or B with a small map in its mission scene (the suggested default)?
2. **Architecture:** a separate static site (recommended) or the story inside the app at `/`, with the product moved to `/app`?
3. **Illustrations:** hand-written SVG (recommended, free), or do you want quotes from an illustrator for a hero image?
4. **Name and domain:** keep "Python Academy" for now, or choose a broader name before the story site is built? Are you willing to pay for a domain, and if so, when?
5. **Launch timing:** publish the story site soon, or wait until unit 2 exists, so visitors find more than five lessons behind the button?
6. **The intro:** is a short animation over visible content (at most about 1.2 seconds, never blocking) close enough to the "loading screen" you liked? A real loading screen that hides the page would hurt speed and accessibility.
7. **Audience order:** the concepts put a grade 9 beginner first. Should teams and teachers get their own short section, or a separate page later?

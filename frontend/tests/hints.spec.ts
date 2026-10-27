import {test, expect, Page} from '@playwright/test';
import {HINT_BUTTONS,HINT_LEVELS,HINT_TEXT,OUTLINE_AFTER,nextHint} from '../app/feedback';
// Same JSON that /api/lessons serves; backend tests assert they are identical.
import lessons from '../../backend/tests/fixtures/legacy_lessons_v1.json';
import catalog from '../../backend/tests/fixtures/catalog_v1.json';

/* ENG-04 part 2a (docs/plan/lesson-feedback.md section 7): hints tagged to an error or check rule,
 * the similar example after the approach, "Other ways to do it" after passing, and the gentle
 * outline on the hint button after two failed runs. Unit tests of nextHint first, then the page
 * with real Python and a mocked API. */

const lesson = (id: string) => lessons.find(l => l.id === id)!;
const shownKeys = (steps: {key: string}[]) => steps.map(s => s.key);
function walk(id: string, active: string | null) {
 const l = lesson(id), steps = [];
 for (let step = nextHint(l.hints, l.errorHints, active, [], l.similarExample); step; step = nextHint(l.hints, l.errorHints, active, shownKeys(steps), l.similarExample)) steps.push(step);
 return steps;
}

test('with no error, the ladder comes in order, then the similar example, then nothing', () => {
 const steps = walk('variables', null);
 expect(steps.map(s => s.label)).toEqual([...HINT_LEVELS, HINT_TEXT.similar]);
 expect(steps.map(s => s.button)).toEqual([...HINT_BUTTONS, HINT_TEXT.similarButton]);
 expect(steps.slice(0, 3).map(s => s.text)).toEqual(lesson('variables').hints);
 expect(steps[3]).toMatchObject({text: lesson('variables').similarExample!.note, code: lesson('variables').similarExample!.code});
});

test('a NameError offers the spelling hint first, then the ladder in its usual order', () => {
 const steps = walk('variables', 'NameError');
 expect(steps[0]).toMatchObject({label: 'About this error', button: 'Show a hint about this error'});
 expect(steps[0].text).toMatch(/^Names must be spelled exactly the same each time/);
 expect(steps.slice(1).map(s => s.label)).toEqual([...HINT_LEVELS, HINT_TEXT.similar]);
});

test('every tagged hint is offered first for its own error or rule, and only then', () => {
 for (const l of lessons) for (const hint of l.errorHints) for (const tag of hint.tags) {
  const first = nextHint(l.hints, l.errorHints, tag, [], l.similarExample)!;
  expect(first.text, `${l.id} ${tag}`).toBe(hint.text);
  expect(first.label).toBe(/Error$/.test(tag) ? 'About this error' : 'About this check');
  // Another lesson's rule, or an error with no tagged hint, changes nothing.
  expect(nextHint(l.hints, l.errorHints, 'ZeroDivisionError', [], l.similarExample)!.label).toBe(HINT_LEVELS[0]);
 }
});

test('a tagged hint already shown is not offered again; the ladder carries on', () => {
 const l = lesson('choices');
 const tagged = nextHint(l.hints, l.errorHints, 'IndentationError', [], null)!;
 expect(nextHint(l.hints, l.errorHints, 'IndentationError', [tagged.key], null)!.label).toBe(HINT_LEVELS[0]);
 // A lesson with no similar example ends after the approach.
 expect(nextHint(l.hints, l.errorHints, null, ['level:0', 'level:1', 'level:2'], null)).toBeNull();
});

test('every unit 1 challenge has three ladder hints, tagged hints and a similar example', () => {
 for (const l of lessons) {
  expect(l.hints, l.id).toHaveLength(3);
  expect(l.errorHints.length, l.id).toBeGreaterThan(0);
  expect(l.similarExample, l.id).not.toBeNull();
 }
 expect(OUTLINE_AFTER).toBe(2);
});

// The lesson page

async function mockApi(page: Page, check: () => unknown) {
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  const body = path === '/api/lessons' ? lessons : path === '/api/catalog' ? catalog : path === '/api/check' ? check() : {};
  await route.fulfill({contentType: 'application/json', body: JSON.stringify(body)});
 });
}
const passed = (rule: string) => ({passed: true, result: 'passed', feedback: 'Checked.', rule, assessment: 'browser_practice'});
const needsWork = (rule: string, feedback = 'Not yet.') => ({passed: false, result: 'needs_work', feedback, rule, assessment: 'browser_practice'});
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

const hintsPanel = (page: Page) => page.getByRole('region', {name: 'Hints'});
const hintButton = (page: Page) => hintsPanel(page).getByRole('button');
async function runChallenge(page: Page, code: string) {
 await page.getByLabel('Your Python code').fill(code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeEnabled({timeout: 25000});
 await expect(page.locator('#code-feedback')).not.toBeEmpty();
}

test('a NameError shows the spelling hint first, beside the error', async ({page}) => {
 await mockApi(page, () => passed('variables.passed'));
 await page.goto('/preview?lesson=variables&card=5');
 await expect(hintButton(page)).toHaveText(HINT_BUTTONS[0]);
 await runChallenge(page, 'hero = "Kai"\ntool = "map"\nprint(heor)');
 await expect(hintButton(page)).toHaveText('Show a hint about this error');
 await hintButton(page).click();
 await expect(hintsPanel(page).getByRole('listitem')).toHaveText([`About this error. ${lesson('variables').errorHints.find(h => h.tags.includes('NameError'))!.text}`]);
 // Then the ladder, from its first step.
 await expect(hintButton(page)).toHaveText(HINT_BUTTONS[0]);
});

test('a failed check rule shows the hint tagged for that rule first', async ({page}) => {
 await mockApi(page, () => needsWork('hello.different-lines', 'Both lines say the same thing. Change the second one into a surprise.'));
 await page.goto('/preview?lesson=hello&card=5');
 await runChallenge(page, 'print("hi")\nprint("hi")');
 await expect(hintButton(page)).toHaveText('Show a hint about this check');
 await hintButton(page).click();
 const tagged = lesson('hello').errorHints.find(h => h.tags.includes('hello.different-lines'))!;
 await expect(hintsPanel(page).getByRole('listitem')).toHaveText([`About this check. ${tagged.text}`]);
});

test('the similar example comes only after the approach, and other ways only after passing', async ({page}) => {
 let next: unknown = needsWork('variables.uses-variables');
 await mockApi(page, () => next);
 await page.goto('/preview?lesson=variables&card=5');
 const l = lesson('variables');
 for (let level = 0; level < 3; level++) {
  await expect(hintsPanel(page).getByText(HINT_TEXT.similar)).toHaveCount(0);
  await hintButton(page).click();
 }
 await expect(hintButton(page)).toHaveText(HINT_TEXT.similarButton);
 await hintButton(page).click();
 const similar = hintsPanel(page).getByRole('listitem').last();
 await expect(similar).toContainText(`${HINT_TEXT.similar}. ${l.similarExample!.note}`);
 await expect(similar.locator('code')).toHaveText(l.similarExample!.code);
 await expect(hintButton(page)).toHaveText(HINT_TEXT.done);
 // Not before passing: not on load, and not after a run that did not pass.
 const otherWays = page.getByRole('region', {name: HINT_TEXT.otherWays});
 await expect(otherWays).toHaveCount(0);
 await runChallenge(page, 'hero = "Kai"\ntool = "rope"\nprint("hero")');
 await expect(otherWays).toHaveCount(0);
 next = passed('variables.passed');
 await runChallenge(page, 'hero = "Kai"\ntool = "rope"\nprint(hero, tool)');
 await expect(otherWays).toBeVisible();
 await expect(otherWays.locator('code')).toHaveText(l.otherWays.map(w => w.code));
 // Editing the code means it is no longer the passing version, so the panel goes.
 await page.getByLabel('Your Python code').press('End');
 await page.keyboard.type(' ');
 await expect(otherWays).toHaveCount(0);
});

test('the hint button gets a gentle outline after exactly two failed runs, and not before', async ({page}) => {
 let next: unknown = needsWork('hello.words');
 await mockApi(page, () => next);
 await page.goto('/preview?lesson=hello&card=5');
 const outlined = page.locator('.hint-ladder button.suggested');
 await expect(outlined).toHaveCount(0);
 await runChallenge(page, 'print(1)\nprint(2)');               // failed run 1: the check says needs work
 await expect(outlined).toHaveCount(0);
 await runChallenge(page, 'print("A forest."');               // failed run 2: Python stopped
 await expect(outlined).toHaveCount(1);
 await expect(outlined).toHaveAttribute('aria-describedby', 'hint-suggested');
 await expect(page.locator('#hint-suggested')).toHaveText(HINT_TEXT.suggested);
 const style = await outlined.evaluate(el => { const s = getComputedStyle(el); return [s.outlineStyle, s.animationName, s.transitionDuration]; });
 expect(style).toEqual(['dashed', 'none', '0s']);
 // No popup and nothing moves: the button stays where it was.
 await expect(page.getByRole('dialog')).toHaveCount(0);
 // A pass starts the count again.
 next = passed('hello.passed');
 await runChallenge(page, 'print("A forest.")\nprint("A dragon!")');
 await expect(outlined).toHaveCount(0);
});

test('a "Try it" run that fails never outlines the hint button, and with reduced motion nothing animates', async ({page}) => {
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page, () => needsWork('hello.words'));
 await page.goto('/preview?lesson=hello&card=4');
 for (let i = 0; i < 2; i++) {
  await page.getByLabel('Your Python code').fill('print(');
  await page.getByRole('button', {name: 'Run Python →'}).click();
  await expect(page.locator('#code-feedback')).toContainText('Python stopped', {timeout: 25000});
 }
 await page.getByRole('button', {name: 'Start my challenge'}).click();
 await expect(page.locator('.hint-ladder button.suggested')).toHaveCount(0);
 for (let i = 0; i < 2; i++) await runChallenge(page, 'print(1)\nprint(2)');
 const button = page.locator('.hint-ladder button.suggested');
 await expect(button).toHaveCount(1);
 expect(await button.evaluate(el => [getComputedStyle(el).animationName, getComputedStyle(el).transitionDuration])).toEqual(['none', '0s']);
});

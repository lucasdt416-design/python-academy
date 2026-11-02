import {test, expect, Page} from '@playwright/test';
import {HINT_BUTTONS,HINT_LEVELS,HINT_TEXT,OTHER,STOPS,TRANSLATIONS,checkLine,closestName,definedNames,explain,parseError,pythonMessage} from '../app/feedback';
// Real error text from the Pyodide worker; the last test below checks it still matches.
import errors from './fixtures/pyodide-errors.json';
// The real API answer for print("hi") then print("woah"); backend/tests/test_honest_checks.py checks it.
import hiWoah from './fixtures/hello-hi-woah.json';
import snapshot from './fixtures/translations.snapshot.json';
import lessons from '../../backend/tests/fixtures/legacy_lessons_v1.json';
import catalog from '../../backend/tests/fixtures/catalog_v1.json';

/* The lesson feedback engine, first part (ENG-04, docs/plan/lesson-feedback.md). The first tests
 * are unit tests of app/feedback.ts and need no browser; the rest drive the lesson page with real
 * Python in Pyodide and a mocked API. */

const sample = (id: string) => {
 const found = errors.samples.find(s => s.id === id);
 if (!found) throw Error(`no fixture ${id}`);
 return found;
};
function explainSample(id: string, unit = 1) {
 const s = sample(id);
 return explain(s.outputLimit ? {stop: 'output_limit'} : parseError(s.raw!, s.errorType), {code: s.code, unit});
}

// One row per translation in section 4 of the specification, each from a real Pyodide error.
const EXPECTED: [string, number, {id: string; title: string; line: number | null; where: string | null; text?: string}][] = [
 ['unterminated-string', 1, {id: 'unterminated-string', title: 'A message is missing its closing quote', line: 1, where: 'Line 1'}],
 ['never-closed', 1, {id: 'never-closed', title: 'A parenthesis is still open', line: 1, where: 'Line 1'}],
 ['never-closed-last-line', 1, {id: 'never-closed', title: 'A parenthesis is still open', line: 2, where: 'Line 2'}],
 ['colon', 1, {id: 'colon', title: 'This line needs a colon', line: 2, where: 'On or just before line 2'}],
 ['equals', 1, {id: 'equals', title: 'Comparing needs two equals signs', line: 2, where: 'On or just before line 2'}],
 ['forgot-quotes', 1, {id: 'quotes', title: 'Words need quotes to be text', line: 1, where: 'On or just before line 1'}],
 ['syntax-other', 1, {id: 'syntax', title: 'Python cannot read line 1', line: 1, where: 'On or just before line 1'}],
 // "Perhaps you forgot a comma" on a line that has quotes may really be a missing comma.
 ['syntax-later-line', 1, {id: 'syntax', title: 'Python cannot read line 2', line: 2, where: 'On or just before line 2'}],
 ['indent-block', 1, {id: 'indent-block', title: 'The lines inside this `if` need indenting', line: 3, where: 'Line 3'}],
 ['indent-block-else', 1, {id: 'indent-block', title: 'The lines inside this `else` need indenting', line: 5, where: 'Line 5'}],
 // A loop block (unit 3 onwards): while and for.
 ['indent-loop', 3, {id: 'indent-loop', title: 'The lines inside this `for` loop need indenting', line: 2, where: 'Line 2'}],
 ['unexpected-indent', 1, {id: 'unexpected-indent', title: 'This line has extra spaces at the start', line: 2, where: 'Line 2'}],
 ['tabs', 1, {id: 'tabs', title: 'Tabs and spaces are mixed', line: 3, where: 'Line 3'}],
 ['name-case', 1, {id: 'name-case', title: 'Python is case-sensitive', line: 1, where: 'Line 1', text: 'Python knows `print`, not `Print`. Use all lowercase on line 1.'}],
 ['name-typo', 1, {id: 'name-typo', title: 'Python does not know `heor`', line: 2, where: 'Line 2', text: 'Did you mean `hero`? Names must be spelled exactly the same each time.'}],
 // Python suggests help, which learners have not met; the general NameError message is kinder.
 ['name-unknown', 1, {id: 'name-unknown', title: 'Python does not know `hello` yet', line: 2, where: 'Line 2'}],
 // Inside a function: the line in the function, not the line that called it.
 ['name-in-function', 1, {id: 'name-unknown', title: 'Python does not know `nam` yet', line: 3, where: 'Line 3'}],
 ['concat', 2, {id: 'concat', title: 'Text and numbers cannot be joined with `+`', line: 2, where: 'Line 2'}],
 ['int-text', 2, {id: 'int-text', title: 'That text is not a whole number', line: 1, where: 'Line 1'}],
 ['zero', 2, {id: 'zero', title: 'Division by zero', line: 2, where: 'Line 2'}],
 // The input() call in the learner's code, not the line inside our input() replacement.
 ['replies', 1, {id: 'replies', title: 'Not enough player replies', line: 2, where: 'Line 2'}],
 ['output-limit', 1, {id: 'output-limit', title: 'Too much output', line: null, where: null}],
 ['other', 1, {id: 'other', title: 'Python stopped on line 2', line: 2, where: 'Line 2'}],
];

for (const [id, unit, want] of EXPECTED) test(`translation: ${id}`, () => {
 const got = explainSample(id, unit);
 expect({id: got.id, title: got.title, line: got.line, where: got.where, ...(want.text ? {text: got.text} : {})}).toEqual(want);
});

test('translation: the endless-loop stop needs no Python message', () => {
 expect(explain({stop: 'timeout'}, {code: 'while True:\n    pass', unit: 1})).toEqual({id: 'timeout', title: 'Your program kept running',
  text: 'It did not finish within 15 seconds, usually because a loop never ends. Check that something inside the loop changes, so that the loop can stop.', line: null, where: null});
});

test('every translation in the specification is tested with a real error, 20 in all', () => {
 const tested = new Set([...EXPECTED.map(([, , want]) => want.id), 'timeout']);
 const all = [...TRANSLATIONS.map(t => t.id), ...Object.values(STOPS).map(s => s.id), OTHER.id];
 expect(all).toHaveLength(20);
 expect([...tested].sort()).toEqual([...all].sort());
});

test('a loop translation is not used before unit 3, which teaches loops', () => {
 expect(explainSample('indent-loop', 2)).toMatchObject({id: 'other', title: 'Python stopped on line 2', line: 2});
});

test('a translation for a later unit is not used in unit 1', () => {
 // Unit 1 has not taught numbers yet, so these get the general message, still with the line.
 for (const [id, line] of [['concat', 2], ['int-text', 1], ['zero', 2]] as const) {
  expect(explainSample(id, 1)).toMatchObject({id: 'other', title: `Python stopped on line ${line}`, line});
 }
});

test('the output limit is known from the worker flag, because Python only says OSError', () => {
 const s = sample('output-limit');
 expect(s.raw!.trimEnd().split('\n').pop()).toBe('OSError: [Errno 29] I/O error');
 expect(explain(parseError(s.raw!, s.errorType), {code: s.code, unit: 1}).id).toBe('other');
 expect(explainSample('output-limit').id).toBe('output-limit');
});

test('line numbers come from the learner’s code, never from Pyodide’s own frames', () => {
 for (const s of errors.samples) {
  expect(s.raw).toContain('/lib/python312.zip/_pyodide/_base.py');
  const {line, type} = parseError(s.raw!, s.errorType);
  const ours = [...s.raw!.matchAll(/File "<exec>", line (\d+)/g)].map(m => Number(m[1]));
  expect(line, s.id).toBe(ours.at(-1));
  expect(type, s.id).toBe(s.errorType);
  expect(line! <= s.code.split('\n').length, s.id).toBe(true);
 }
 // Without the type from the worker, it is read from Python's last line.
 expect(parseError(sample('name-typo').raw!).type).toBe('NameError');
});

test('Python’s own message is one click away, without Pyodide’s frames', () => {
 expect(pythonMessage(sample('name-typo').raw!)).toBe('Traceback (most recent call last):\n  File "<exec>", line 2, in <module>\nNameError: name \'heor\' is not defined');
 expect(pythonMessage(sample('unterminated-string').raw!)).toBe('  File "<exec>", line 1\n    print("You arrive at a castle.)\n          ^\nSyntaxError: unterminated string literal (detected at line 1)');
 expect(pythonMessage(sample('replies').raw!)).not.toContain('<academy>');
 for (const s of errors.samples) expect(pythonMessage(s.raw!), s.id).not.toContain('_pyodide');
});

test('name suggestions: defined names one or two edits away, or a built-in Python suggested', () => {
 expect(definedNames('hero = "Kai"\ntool == x\ndef greet(name, times=2):\n    pass\nfor step in steps:\n    pass')).toEqual(['hero', 'greet', 'name', 'times', 'step']);
 expect(closestName('heor', 'hero = "Kai"')).toBe('hero');
 expect(closestName('hero', 'hero = "Kai"')).toBeNull();
 expect(closestName('x', 'y = 1')).toBeNull();
 expect(closestName('villain', 'hero = "Kai"')).toBeNull();
 expect(closestName('prnt', '', "NameError: name 'prnt' is not defined. Did you mean: 'print'?")).toBe('print');
 expect(closestName('hello', '', "NameError: name 'hello' is not defined. Did you mean: 'help'?")).toBeNull();
});

test('a behaviour-check error (ENG-03 runner report) is translated the same way', () => {
 // The runner reports the type, the line and only Python's last line (public/check-runner.js).
 const report = {errorType: 'NameError', line: 2, message: "NameError: name 'missing' is not defined"};
 expect(explain({type: report.errorType, line: report.line, message: report.message}, {code: 'a = int(input())\nprint(a + missing)', unit: 2}))
  .toMatchObject({id: 'name-unknown', line: 2, where: 'Line 2'});
});

test('only a Python error in a check result highlights a line of code', () => {
 expect(checkLine({failed: {reason: 'error', line: 3}})).toBe(3);
 // line_number in a wrong_output result counts lines of output, not lines of code.
 expect(checkLine({failed: {reason: 'wrong_output', line: null}})).toBeNull();
 expect(checkLine({failed: null})).toBeNull();
 expect(checkLine({})).toBeNull();
});

test('translation templates and hint panel wording match the reviewed snapshot, with code patterns of one line at most', () => {
 // A changed or new message must be updated here too, so every change is visible in review (section 8).
 const now = [...TRANSLATIONS.map(({id, unit, title, text}) => ({id, unit, title, text})), ...Object.values(STOPS).map(({id, title, text}) => ({id, title, text})), {id: OTHER.id, title: OTHER.title, text: OTHER.text}];
 const panel = {id: 'hint-panel', levels: [...HINT_LEVELS], buttons: [...HINT_BUTTONS], ...HINT_TEXT};
 expect([...now, panel]).toEqual(snapshot);
 for (const {text, title} of now) for (const part of [text, title]) {
  expect(part).not.toContain('\n');
  for (const code of part.split('`').filter((_, i) => i % 2)) expect(code.length, code).toBeLessThanOrEqual(24);
 }
});

test('the hint ladder has three levels and nothing after them', () => {
 expect(HINT_LEVELS).toEqual(['A nudge', 'A bigger hint', 'The approach']);
 expect(HINT_BUTTONS).toHaveLength(3);
 // Every unit 1 challenge has exactly three hints, which the backend runs through the real checker,
 // alone and combined, and none passes (backend/tests/test_honest_checks.py).
 for (const lesson of lessons) expect(lesson.hints, lesson.id).toHaveLength(3);
});

// The lesson page

async function mockApi(page: Page, check: (body: Record<string, unknown>) => unknown = () => ({passed: true, result: 'passed', feedback: 'Checked.', assessment: 'browser_practice'})) {
 const checked: Record<string, unknown>[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  let body: unknown = {};
  if (path === '/api/lessons') body = lessons;
  else if (path === '/api/catalog') body = catalog;
  else if (path === '/api/check') { const data = route.request().postDataJSON(); checked.push(data); body = check(data); }
  await route.fulfill({contentType: 'application/json', body: JSON.stringify(body)});
 });
 return checked;
}
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

const editor = (page: Page) => page.getByLabel('Your Python code');
const result = (page: Page) => page.locator('#code-feedback');
async function runChallenge(page: Page, code: string) {
 await editor(page).fill(code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeEnabled({timeout: 25000});
}
const highlighted = (page: Page) => page.locator('.code-gutter .gutter-line.error');

test('a NameError is explained, its line highlighted with a marker and text, and Go to line moves the cursor', async ({page}) => {
 const checked = await mockApi(page);
 await page.goto('/preview?lesson=variables&card=5');
 await runChallenge(page, 'hero = "Kai"\ntool = "map"\nprint(heor)');
 // Announced through the status live region; the line is in the text, not only in colour.
 await expect(page.getByRole('status').filter({hasText: 'Python does not know heor'})).toContainText('Line 3');
 await expect(result(page)).toContainText('Python stopped');
 await expect(result(page)).toContainText('Did you mean hero? Names must be spelled exactly the same each time.');
 await expect(highlighted(page)).toHaveText('▶3');
 await expect(page.locator('.code-highlight .code-line.error')).toHaveCount(1);
 expect(await page.locator('.code-highlight .code-line').evaluateAll(lines => lines.findIndex(l => l.classList.contains('error')))).toBe(2);
 await expect(editor(page)).toHaveAttribute('aria-describedby', 'editor-help code-feedback');
 // A crash is not sent to be checked, and focus stays where it was until the learner asks.
 expect(checked).toEqual([]);
 await expect(editor(page)).not.toBeFocused();
 await page.getByRole('button', {name: 'Go to line 3'}).click();
 await expect(editor(page)).toBeFocused();
 expect(await editor(page).evaluate((t: HTMLTextAreaElement) => [t.selectionStart, t.selectionEnd])).toEqual([26, 26]);
 // Python's own message, one click away, without Pyodide's internal frames.
 const raw = page.locator('.python-message');
 await expect(raw).toBeHidden();
 await page.getByText('Show Python’s message').click();
 await expect(raw).toHaveText('Traceback (most recent call last):\n  File "<exec>", line 3, in <module>\nNameError: name \'heor\' is not defined');
});

test('syntax errors highlight the reported line and say it may be just before', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=choices&card=5');
 await runChallenge(page, 'path = input("Path? ")\nif path == "left"\n    print("A cave.")\nelse:\n    print("A bridge.")');
 await expect(result(page)).toContainText('This line needs a colon');
 await expect(result(page)).toContainText('On or just before line 2');
 await expect(highlighted(page)).toHaveText('▶2');
 // An unclosed parenthesis is shown where it was opened, as Python reports it.
 await runChallenge(page, 'print("A forest.")\nprint("A dragon!"\nprint("The end.")');
 await expect(result(page)).toContainText('A parenthesis is still open');
 await expect(highlighted(page)).toHaveText('▶2');
});

test('an error inside a function highlights the line in the function', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=hello&card=5');
 await runChallenge(page, 'def scene():\n    print("A forest.")\n    print(dragon)\n\nscene()');
 await expect(result(page)).toContainText('Python does not know dragon yet');
 await expect(highlighted(page)).toHaveText('▶3');
 // What printed before the error stays visible.
 await expect(page.locator('.execution-output')).toHaveText('A forest.');
});

test('the highlight clears when that line is edited, and the message stays until the next run', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=hello&card=5');
 await runChallenge(page, 'print("A forest.")\nPrint("A dragon!")');
 await expect(highlighted(page)).toHaveText('▶2');
 // Editing another line keeps it; editing line 2 clears it.
 await editor(page).evaluate((t: HTMLTextAreaElement) => { t.focus(); t.setSelectionRange(5, 5); });
 await page.keyboard.type('x');
 await expect(highlighted(page)).toHaveText('▶2');
 await editor(page).evaluate((t: HTMLTextAreaElement) => { t.setSelectionRange(t.value.length, t.value.length); });
 await page.keyboard.press('Backspace');
 await expect(highlighted(page)).toHaveCount(0);
 await expect(result(page)).toContainText('Python is case-sensitive');
 // Running again starts over: the deleted ")" is the new mistake.
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(result(page)).toContainText('A parenthesis is still open', {timeout: 25000});
 await expect(highlighted(page)).toHaveText('▶2');
});

test('print("hi") then print("woah") shows an honest pass, not a claim about the story', async ({page}) => {
 // Decision 5: no word minimum, so it passes; the message says only what was checked.
 const checked = await mockApi(page, () => hiWoah.response);
 await page.goto('/preview?lesson=hello&card=4');
 // On the "Try it" card a run is not a check, so it must not look like a pass.
 await editor(page).fill(hiWoah.request.code);
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(result(page)).toContainText('Ran · not checked', {timeout: 25000});
 await expect(result(page)).toContainText('This card has no check');
 await expect(result(page)).not.toHaveClass(/passed/);
 expect(checked).toEqual([]);
 await page.getByRole('button', {name: 'Start my challenge'}).click();
 await runChallenge(page, hiWoah.request.code);
 expect(checked.map(({lesson_id, code, output}) => ({lesson_id, code, output}))).toEqual([{lesson_id: 'hello', code: hiWoah.request.code, output: hiWoah.request.output}]);
 await expect(result(page)).toHaveText('Check passed' + hiWoah.response.feedback);
 await expect(result(page)).toContainText('That part is your call.');
 await expect(page.getByText(/setting and a surprise/)).toHaveCount(0);
});

test('a result is a pass only when the check says passed', async ({page}) => {
 let next: unknown = {passed: false, result: 'needs_work', feedback: 'Both lines say the same thing. Change the second one into a surprise.', assessment: 'browser_practice'};
 await mockApi(page, () => next);
 await page.goto('/preview?lesson=hello&card=5');
 await runChallenge(page, 'print("hi")\nprint("hi")');
 await expect(result(page)).toHaveText('Not yetBoth lines say the same thing. Change the second one into a surprise.');
 await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 await expect(page.getByRole('button', {name: 'Revisit this quest'})).toHaveCount(0);
 await expect(page.getByRole('button', {name: 'Next quest →'})).toBeDisabled();
 // "passed: true" with any other state, or a missing state, is not a pass.
 for (const response of [{passed: true, result: 'needs_work', feedback: 'Not this time.'}, {passed: true, feedback: 'No state.'}]) {
  next = response;
  await runChallenge(page, 'print("A forest.")\nprint("A dragon!")');
  await expect(page.getByText(/badge earned!/)).toHaveCount(0);
  await expect(page.getByRole('button', {name: 'Next quest →'})).toBeDisabled();
 }
 await expect(result(page)).toContainText('Check unavailable');
});

test('a behaviour-check result (ENG-03) highlights a Python error line, but not an output line', async ({page}) => {
 let next: unknown = {passed: false, result: 'execution_error', feedback: 'Python stopped with NameError on line 2 while running the numbers 2 and 3. Read the error, change one thing, and run it again.',
  assessment: 'browser_tests', cases: [], failed: {id: 'small', visibility: 'visible', description: 'the numbers 2 and 3', reason: 'error', error_type: 'NameError', line: 2}};
 await mockApi(page, () => next);
 await page.goto('/preview?lesson=hello&card=5');
 await runChallenge(page, 'print("A forest.")\nprint("A dragon!")');
 await expect(result(page)).toContainText('Python stoppedPython stopped with NameError on line 2');
 await expect(highlighted(page)).toHaveText('▶2');
 next = {passed: false, result: 'needs_work', feedback: 'For the numbers 2 and 3, line 1 should be "5", but your program printed "-1".', assessment: 'browser_tests', cases: [],
  failed: {id: 'small', visibility: 'visible', description: 'the numbers 2 and 3', reason: 'wrong_output', error_type: null, line: null, line_number: 1, expected_line: '5', actual_line: '-1'}};
 await runChallenge(page, 'print("A forest.")\nprint("A dragon!")');
 await expect(result(page)).toContainText('Not yet');
 await expect(highlighted(page)).toHaveCount(0);
});

test('hints appear beside the code one level at a time, in order, with no solution button', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=input&card=5');
 const hints = page.getByRole('region', {name: 'Hints'});
 // Beside the code: in the editor panel, after the result.
 await expect(page.getByRole('region', {name: 'Python playground'}).getByRole('region', {name: 'Hints'})).toHaveCount(1);
 await expect(hints.getByRole('listitem')).toHaveCount(0);
 const lesson = lessons.find(l => l.id === 'input')!;
 for (let level = 0; level < 3; level++) {
  await hints.getByRole('button', {name: HINT_BUTTONS[level]}).click();
  await expect(hints.getByRole('listitem')).toHaveText(lesson.hints.slice(0, level + 1).map((hint, i) => `${HINT_LEVELS[i]}. ${hint}`));
 }
 // After the approach comes the similar example (ENG-04 part 2a; tests/hints.spec.ts covers it).
 await hints.getByRole('button', {name: 'Show a similar example'}).click();
 // The button stays, so keyboard focus is not lost, but it reveals nothing more.
 const last = hints.getByRole('button', {name: 'That is every hint'});
 await expect(last).toBeFocused();
 await expect(last).toHaveAttribute('aria-disabled', 'true');
 await page.keyboard.press('Enter');
 await expect(hints.getByRole('listitem')).toHaveCount(4);
 await expect(hints).toContainText('There is no answer to reveal');
 await expect(page.getByRole('button', {name: /solution|answer/i})).toHaveCount(0);
});

test('the explained error fits a phone, and nothing new animates with reduced motion', async ({page}) => {
 await page.setViewportSize({width: 375, height: 812});
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page);
 await page.goto('/preview?lesson=hello&card=5');
 await runChallenge(page, 'print("A very long opening line for a story that goes on and on past the edge of a small phone screen.")\nprint(dragon)');
 await page.getByText('Show Python’s message').click();
 await expect(highlighted(page)).toHaveText('▶2');
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 expect(await page.locator('.result, .result *, .code-editor, .code-editor *, .hint-ladder').evaluateAll(els => els.every(el => getComputedStyle(el).animationName === 'none' && getComputedStyle(el).transitionDuration === '0s'))).toBe(true);
});

test('the result, the hints and the editor have accessible names and descriptions', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=hello&card=5');
 await runChallenge(page, 'print("A forest."');
 const described = (await editor(page).getAttribute('aria-describedby'))!.split(' ');
 for (const id of described) await expect(page.locator(`#${id}`)).toHaveCount(1);
 // The gutter and highlight repeat what the text says, so screen readers skip them.
 for (const layer of ['.code-gutter', '.code-highlight']) await expect(page.locator(layer)).toHaveAttribute('aria-hidden', 'true');
 await expect(page.getByRole('status').filter({hasText: 'A parenthesis is still open'})).toHaveCount(1);
 // The toggle works from the keyboard.
 await page.getByText('Show Python’s message').focus();
 await page.keyboard.press('Enter');
 await expect(page.locator('.python-message')).toBeVisible();
});

test('every fixture matches what the worker reports today', async ({page}) => {
 test.setTimeout(300000);
 await page.goto('/no-such-page');
 for (const s of errors.samples) {
  const data = await page.evaluate(({code, inputs}) => new Promise<{error?: string; errorType?: string; outputLimit?: boolean}>(resolve => {
   const w = new Worker('/python-worker.js');
   w.onmessage = ({data}) => { w.terminate(); resolve(data); };
   w.postMessage({code, inputs});
  }), s);
  expect({raw: data.error, errorType: data.errorType, outputLimit: !!data.outputLimit}, s.id).toEqual({raw: s.raw, errorType: s.errorType, outputLimit: s.outputLimit});
 }
});

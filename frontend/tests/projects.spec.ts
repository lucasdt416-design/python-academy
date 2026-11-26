import {test, expect, Page} from '@playwright/test';
import fs from 'fs';
import path from 'path';
// The project workspace (E1, app/projects.tsx and app/workspace.tsx) with real Pyodide. The API is a
// small in-memory copy of backend/app/projects.py: the same starters (read from backend/content/projects),
// the same revision rule, and the same answers for a stale save. backend/tests/test_projects.py covers
// the real routes.
const STARTERS_DIR = path.join(__dirname, '../../backend/content/projects');
const starterFiles = (id: string) => Object.fromEntries(fs.readdirSync(path.join(STARTERS_DIR, id)).sort().map(f => [f, fs.readFileSync(path.join(STARTERS_DIR, id, f), 'utf8')]));
const STARTERS = [
 {id: 'blank', title: 'Empty project', about: 'Just main.py, for anything you want to build.', final: false},
 {id: 'lockpick', title: 'Lockpick', about: 'A word game.', final: true},
 {id: 'site-builder', title: 'Site Builder', about: 'A website from a data file.', final: true},
 {id: 'planner', title: 'Planner', about: 'A to-do app.', final: true},
].map(s => ({...s, files: Object.keys(starterFiles(s.id)).sort((a, b) => (a !== 'main.py' ? 1 : 0) - (b !== 'main.py' ? 1 : 0) || a.localeCompare(b))}));

type Project = {id: number; title: string; starter: string; files: Record<string, string>; keep_written: boolean; updated: string; revision: number};
async function mockApi(page: Page, {role = 'student' as string | null, projects = [] as Project[]} = {}) {
 const saves: {revision: number; files?: Record<string, string>; keep_written?: boolean; title?: string}[] = [];
 const store = new Map(projects.map(p => [p.id, p]));
 const state = {nextId: 100, conflict: false};
 await page.route('**/api/**', async route => {
  const req = route.request(), where = new URL(req.url()).pathname, method = req.method();
  let status = 200, json: unknown = {};
  const one = /^\/api\/projects\/(\d+)$/.exec(where), p = one ? store.get(Number(one[1])) : undefined;
  if (where === '/api/me') ({status, json} = role ? {status: 200, json: {id: 1, email: 'learner@example.com', role}} : {status: 401, json: {detail: 'Sign in to continue'}});
  else if (where === '/api/awards') json = {xp: 0, completed: [], badges: []};
  else if (where === '/api/recommendation') json = {kind: 'continue', reason: '', course: 'py', unit: 'py.u01', lesson: 'hello', options: [], notes: [], rules_version: 2};
  else if (where === '/api/project-starters') json = STARTERS;
  else if (where === '/api/projects' && method === 'GET') json = {most: 20, projects: [...store.values()].map(x => ({id: x.id, title: x.title, starter: x.starter, files: Object.keys(x.files).length, updated: x.updated, revision: x.revision}))};
  else if (where === '/api/projects' && method === 'POST') {
   const {starter} = req.postDataJSON(), s = STARTERS.find(x => x.id === starter)!;
   const made = {id: state.nextId++, title: s.title, starter, files: starterFiles(starter), keep_written: false, updated: new Date().toISOString(), revision: 1};
   store.set(made.id, made); json = made;
  }
  else if (one && !p) ({status, json} = {status: 404, json: {detail: 'That project is not in your account'}});
  else if (one && method === 'GET') json = p;
  else if (one && method === 'DELETE') { store.delete(p!.id); json = {deleted: true}; }
  else if (one && method === 'PUT') {
   const body = req.postDataJSON(); saves.push(body);
   if (state.conflict || body.revision !== p!.revision) ({status, json} = {status: 409, json: {detail: 'This project was saved from another tab or window since you opened it. Reload to get the newest copy, after copying anything you need from here.'}});
   else if (body.files && Object.keys(body.files).some(n => n === 'random.py')) ({status, json} = {status: 422, json: {detail: "random.py would hide Python's own random module, so choose another name."}});
   else { Object.assign(p!, {title: body.title ?? p!.title, files: body.files ?? p!.files, keep_written: body.keep_written ?? p!.keep_written, revision: p!.revision + 1, updated: new Date().toISOString()}); json = p; }
  }
  await route.fulfill({status, contentType: 'application/json', body: JSON.stringify(json)});
 });
 return {saves, store, state};
}
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 page.on('pageerror', e => found.push(`page error: ${e.message}`));
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

const project = (files: Record<string, string>, extra: Partial<Project> = {}): Project => ({id: 7, title: 'My game', starter: 'blank', files, keep_written: false, updated: new Date().toISOString(), revision: 1, ...extra});
const editor = (page: Page) => page.getByRole('textbox', {name: /^Editing /});
const run = (page: Page) => page.getByRole('region', {name: 'Output'});
const screen = (page: Page) => run(page).locator('.live-screen');
const file = (page: Page, name: string) => page.getByRole('navigation', {name: 'Files'}).getByRole('button', {name, exact: true});
async function shot(page: Page, name: string) {
 if (process.env.SHOTS) await page.screenshot({path: path.join(process.env.SHOTS, name + '.png'), fullPage: true});
}

test('signed out, the projects page says what a project is before asking to sign in', async ({page}) => {
 await mockApi(page, {role: null});
 await page.goto('/projects');
 await expect(page.getByRole('heading', {name: 'Projects', level: 1})).toBeVisible();
 await expect(page.getByText('Saved as you type')).toBeVisible();
 await expect(page.getByRole('link', {name: 'Sign in with Google'})).toBeVisible();
 await expect(page.getByRole('navigation', {name: 'Main'}).getByRole('link', {name: 'Projects'})).toHaveCount(0);
 await shot(page, 'projects-signed-out');
});

test('a learner starts Lockpick from the list, and it opens with its files', async ({page}) => {
 await mockApi(page);
 await page.goto('/projects');
 await expect(page.getByRole('navigation', {name: 'Main'}).getByRole('link', {name: 'Projects'})).toBeVisible();
 await expect(page.getByRole('heading', {name: 'Final projects for Python Foundations'})).toBeVisible();
 await shot(page, 'projects-empty');
 await page.getByRole('button', {name: 'Start Lockpick'}).click();
 await expect(page).toHaveURL(/\/projects\/100$/);
 await expect(page.getByLabel('Project name')).toHaveValue('Lockpick');
 await expect(file(page, 'main.py')).toHaveAttribute('aria-current', 'true');
 await expect(file(page, 'words.txt')).toBeVisible();
 await expect(editor(page)).toHaveValue(/def mask\(word, guessed\):/);
 await file(page, 'words.txt').click();
 await expect(editor(page)).toHaveValue(/^vault\n/);
 await expect(page.getByText('Your program can read it with open("words.txt").')).toBeVisible();
 await shot(page, 'workspace-lockpick');
});

test('changes save a moment after typing stops, with the revision the page last saw', async ({page}) => {
 const {saves} = await mockApi(page, {projects: [project({'main.py': 'print("hi")'})]});
 await page.goto('/projects/7');
 await editor(page).fill('print("hello")');
 await expect(page.getByText('Changes not saved yet')).toBeVisible();
 await expect(page.getByText(/^Saved just now/)).toBeVisible({timeout: 5000});
 await page.getByLabel('Project name').fill('Vault game');
 await expect.poll(() => saves.length).toBe(2);
 expect(saves[0]).toEqual({revision: 1, title: 'My game', files: {'main.py': 'print("hello")'}, keep_written: false});
 expect(saves[1]).toMatchObject({revision: 2, title: 'Vault game'});
 await page.reload();
 await expect(editor(page)).toHaveValue('print("hello")');
 await expect(page.getByLabel('Project name')).toHaveValue('Vault game');
});

test('main.py runs with the other files: a module it imports and a data file it opens', async ({page}) => {
 await mockApi(page, {projects: [project({'main.py': 'import helpers\nwith open("words.txt") as f:\n    words = f.read().split()\nprint(helpers.shout(words[0]))', 'helpers.py': 'def shout(word):\n    return word.upper() + "!"', 'words.txt': 'vault\nlantern\n'})]});
 await page.goto('/projects/7');
 await page.getByRole('button', {name: 'Run', exact: true}).click();
 await expect(screen(page)).toHaveText('VAULT!\n', {timeout: 45000});
 await expect(run(page).getByText('The program finished.')).toBeVisible();
 await expect(page.getByRole('button', {name: 'Run again'})).toBeVisible();
 // The page's Run again starts over, so the panel adds no second button and no count of zero replies.
 await expect(run(page).getByRole('button', {name: 'Start over'})).toHaveCount(0);
 await expect(run(page).getByText('0 replies')).toHaveCount(0);
 await shot(page, 'workspace-run');
});

test('a program that asks questions is played as it runs', async ({page}) => {
 await mockApi(page, {projects: [project({'main.py': 'name = input("Name? ")\nprint("Hi " + name)'})]});
 await page.goto('/projects/7');
 await page.getByRole('button', {name: 'Run', exact: true}).click();
 await expect(run(page).getByText('Your program asks: Name?')).toBeVisible({timeout: 45000});
 await run(page).getByRole('textbox').fill('Ada');
 await run(page).getByRole('button', {name: 'Reply'}).click();
 await expect(screen(page)).toHaveText('Name? Ada\nHi Ada\n', {timeout: 45000});
});

test('files a program writes are gone unless kept; when kept they are saved and the next run reads them', async ({page}) => {
 const program = 'try:\n    with open("count.txt") as f:\n        n = int(f.read())\nexcept FileNotFoundError:\n    n = 0\nn = n + 1\nwith open("count.txt", "w") as f:\n    f.write(str(n))\nwith open("notes.py", "w") as f:\n    f.write("x = 1")\nprint("Run number", n)';
 const {saves, store} = await mockApi(page, {projects: [project({'main.py': program})]});
 await page.goto('/projects/7');
 await page.getByRole('button', {name: 'Run', exact: true}).click();
 await expect(screen(page)).toHaveText('Run number 1\n', {timeout: 45000});
 await expect(page.getByText('Your program wrote count.txt. It is gone now.')).toBeVisible();
 await expect(page.getByText('Not kept, because only text files ending .txt')).toContainText('notes.py');
 await expect(file(page, 'count.txt')).toHaveCount(0);

 await page.getByLabel('Keep files my program writes').check();
 await expect.poll(() => saves.at(-1)?.keep_written).toBe(true);
 await page.getByRole('button', {name: 'Run again'}).click();
 await expect(screen(page)).toHaveText('Run number 1\n', {timeout: 45000});
 await expect(page.getByText('Kept what your program wrote: count.txt.')).toBeVisible();
 await expect(file(page, 'count.txt')).toBeVisible();
 await expect.poll(() => store.get(7)!.files['count.txt']).toBe('1');
 await shot(page, 'workspace-kept');
 await page.getByRole('button', {name: 'Run again'}).click();
 await expect(screen(page)).toHaveText('Run number 2\n', {timeout: 45000});
 await expect.poll(() => store.get(7)!.files['count.txt']).toBe('2');
});

test('an error inside another file says which file and line, and Show me opens it there', async ({page}) => {
 await mockApi(page, {projects: [project({'main.py': 'import tools\nprint(tools.half(4))', 'tools.py': 'def half(n):\n    return n / zero'})]});
 await page.goto('/projects/7');
 await page.getByRole('button', {name: 'Run', exact: true}).click();
 await expect(run(page).locator('.result-where')).toHaveText('tools.py, line 2', {timeout: 45000});
 await page.getByRole('button', {name: 'Show tools.py, line 2'}).click();
 await expect(page.getByRole('button', {name: 'Show tools.py, line 2'})).toHaveCount(0);
 await expect(file(page, 'tools.py')).toHaveAttribute('aria-current', 'true');
 await expect(page.locator('.gutter-line.error')).toHaveText(/2/);
 await shot(page, 'workspace-error');
});

test('new files are named with care, and can be renamed and deleted', async ({page}) => {
 const {store} = await mockApi(page, {projects: [project({'main.py': ''})]});
 await page.goto('/projects/7');
 await page.getByRole('button', {name: 'New file'}).click();
 await page.getByLabel('New file name').fill('my-tools.py');
 await page.getByRole('button', {name: 'Add'}).click();
 await expect(page.getByText('Python can’t import a name with - in it. Try my_tools.py.')).toBeVisible();
 await page.getByLabel('New file name').fill('main.py');
 await page.getByRole('button', {name: 'Add'}).click();
 await expect(page.getByText('There is already a file called main.py.')).toBeVisible();
 await page.getByLabel('New file name').fill('tools.py');
 await page.getByRole('button', {name: 'Add'}).click();
 await expect(file(page, 'tools.py')).toHaveAttribute('aria-current', 'true');
 await expect(page.getByText('import tools', {exact: true})).toBeVisible();
 await expect.poll(() => Object.keys(store.get(7)!.files)).toEqual(['main.py', 'tools.py']);

 await page.getByRole('button', {name: 'Rename'}).click();
 await page.getByLabel('New name for tools.py').fill('helpers.py');
 await page.getByRole('button', {name: 'Rename'}).click();
 await expect(file(page, 'helpers.py')).toBeVisible();
 await expect.poll(() => Object.keys(store.get(7)!.files).sort()).toEqual(['helpers.py', 'main.py']);
 await page.getByRole('button', {name: 'Delete'}).click();
 await page.getByRole('group', {name: 'Delete helpers.py?'}).getByRole('button', {name: 'Delete'}).click();
 await expect(file(page, 'helpers.py')).toHaveCount(0);
 await expect(file(page, 'main.py')).toHaveAttribute('aria-current', 'true');
 await expect.poll(() => Object.keys(store.get(7)!.files)).toEqual(['main.py']);
 // main.py runs, so it is never renamed or deleted.
 await expect(page.getByRole('button', {name: 'Rename'})).toHaveCount(0);
});

test('a name the server refuses says why, and the work stays on the page', async ({page}) => {
 await mockApi(page, {projects: [project({'main.py': ''})]});
 await page.goto('/projects/7');
 await page.getByRole('button', {name: 'New file'}).click();
 await page.getByLabel('New file name').fill('random.py');
 await page.getByRole('button', {name: 'Add'}).click();
 await expect(page.getByText("random.py would hide Python's own random module")).toBeVisible();
 await expect(file(page, 'random.py')).toBeVisible();
});

test('a save from an older copy of the page is refused, and the page stops saving and offers a reload', async ({page}) => {
 const {state, store} = await mockApi(page, {projects: [project({'main.py': 'print(1)'})]});
 await page.goto('/projects/7');
 state.conflict = true;
 await editor(page).fill('print("old tab")');
 await expect(page.getByText(/saved from another tab or window/)).toBeVisible({timeout: 5000});
 await expect(page.getByRole('button', {name: 'Reload'})).toBeVisible();
 await expect(editor(page)).toBeDisabled();
 expect(store.get(7)!.files['main.py']).toBe('print(1)');
});

test('a project is deleted from the list only after a second, clear step', async ({page}) => {
 const {store} = await mockApi(page, {projects: [project({'main.py': ''}), project({'main.py': '', 'a.txt': ''}, {id: 8, title: 'Second'})]});
 await page.goto('/projects');
 await expect(page.getByText('2 files · changed just now')).toBeVisible();
 await page.getByRole('button', {name: 'Delete Second'}).click();
 await expect(page.getByText('Delete it and all its files? This can’t be undone.')).toBeVisible();
 await shot(page, 'projects-list-confirm');
 await page.getByRole('group', {name: 'Delete Second?'}).getByRole('button', {name: 'Delete'}).click();
 await expect(page.getByRole('link', {name: 'Second'})).toHaveCount(0);
 expect([...store.keys()]).toEqual([7]);
});

for (const width of [390, 1280]) {
 test(`the workspace fits a ${width}px screen without sideways scrolling`, async ({page}) => {
  await page.setViewportSize({width, height: 900});
  await mockApi(page, {projects: [project({'main.py': 'print("hi")', 'helpers.py': '', 'words.txt': 'a', 'notes.md': '', 'site.json': '{}'})]});
  await page.goto('/projects/7');
  await expect(editor(page)).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(width);
  await shot(page, `workspace-${width}`);
 });
}

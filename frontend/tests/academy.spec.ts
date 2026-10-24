import {test, expect, Page} from '@playwright/test';

const lessons = [
  {id:'hello', title:'Say hello', concept:'print()', description:'Display Hello, Python!', starter:'print("Hello, Python!")', expected:'Hello, Python!\n'},
  {id:'variables', title:'Your first variable', concept:'Variables', description:'Print stars multiplied by 3.', starter:'stars = 7', expected:'21\n'},
  {id:'loop', title:'Make a loop', concept:'Loops', description:'Print 1 through 5.', starter:'for number in range(1, 6):\n    pass', expected:'1\n2\n3\n4\n5\n'},
];

async function mockApi(page: Page, initialRole: string|null) {
  let role = initialRole;
  await page.route('**/api/**', async route => {
    const path = new URL(route.request().url()).pathname;
    let body: unknown = {};
    let status = 200;
    if (path === '/api/lessons') body = lessons;
    else if (path === '/api/me') {status = role ? 200 : 401; body = role ? {id:1,email:'test@example.com',role} : {detail:'Sign in to continue'};}
    else if (path === '/api/history' || path === '/api/family') body = [];
    else if (path === '/api/enroll') {role = route.request().postDataJSON().invitation ? 'student' : 'parent';body = {role};}
    else if (path === '/api/invitations') body = {url:'https://academy.example/?invite=test',expires_in_days:7};
    else if (path === '/api/logout') role = null;
    else if (path === '/api/attempts') {
      const data = route.request().postDataJSON();
      body = {passed: data.output === lessons.find(l => l.id === data.lesson_id)?.expected};
    }
    await route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
  });
}

test('welcome offers Google sign-in and keyboard skip navigation', async ({page}) => {
  await mockApi(page, null);
  await page.goto('/');
  await expect(page.getByRole('link',{name:/Continue with Google/})).toHaveAttribute('href','/auth/google');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link',{name:/Skip/})).toBeFocused();
});

test('invitation survives redirect and enrolls as a student', async ({page}) => {
  await mockApi(page,'pending');
  await page.goto('/?invite=private-token');
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem('academy-invite'))).toBe('private-token');
  await page.reload();
  await expect(page.getByText('Join your family as a student aged 13 or above.')).toBeVisible();
  await page.getByLabel('Date of birth').fill('2010-01-01');
  const request = page.waitForRequest(r => r.url().endsWith('/api/enroll'));
  await page.getByRole('button',{name:'Complete registration'}).click();
  expect((await request).postDataJSON().invitation).toBe('private-token');
  await expect(page.getByLabel('Your Python code')).toBeVisible();
  expect(await page.evaluate(() => sessionStorage.getItem('academy-invite'))).toBeNull();
});

test('parent creates a shareable invitation and signs out', async ({page}) => {
  await mockApi(page,'parent');
  await page.goto('/');
  await page.getByLabel('Student’s Google email').fill('student@example.com');
  await page.getByRole('button',{name:'Create invitation'}).click();
  await expect(page.getByLabel('Invitation link')).toHaveValue('https://academy.example/?invite=test');
  await page.getByRole('button',{name:'Sign out'}).click();
  await expect(page.getByRole('link',{name:/Continue with Google/})).toBeVisible();
});

test('editor supports indentation and reset', async ({page}) => {
  await mockApi(page,'student');
  await page.goto('/');
  await page.getByRole('button',{name:/Make a loop/}).click();
  const editor = page.getByLabel('Your Python code');
  await editor.fill('');
  await editor.press('Tab');
  await expect(editor).toHaveValue('    ');
  await editor.press('Shift+Tab');
  await expect(editor).not.toBeFocused();
  await page.getByRole('button',{name:'Reset code'}).click();
  await expect(editor).toHaveValue(lessons[2].starter);
});

// Run real learner Python in Pyodide; only account endpoints above are mocked.
test('real Python returns correct output and useful syntax errors', async ({page}) => {
  await mockApi(page,'student');
  await page.goto('/');
  for (const [lesson, code, expected] of [
    ['Say hello','print("Hello, Python!")','Hello, Python!'],
    ['Your first variable','stars = 7\nprint(stars * 3)','21'],
    ['Make a loop','for number in range(1, 6):\n    print(number)','1\n2\n3\n4\n5'],
  ]) {
    await page.getByRole('button',{name:new RegExp(lesson)}).click();
    await page.getByLabel('Your Python code').fill(code);
    await page.getByRole('button',{name:/Run Python/}).click();
    await expect(page.locator('.output[aria-live]')).toHaveText(expected,{timeout:20000});
    await expect(page.getByText('Your output matches. Nicely done!')).toBeVisible();
  }
  await page.getByLabel('Your Python code').fill('print(');
  await page.getByRole('button',{name:/Run Python/}).click();
  await expect(page.locator('.output[aria-live]')).toContainText('SyntaxError',{timeout:20000});
});

test('endless Python loop can be stopped and editor stays responsive', async ({page}) => {
  await mockApi(page,'student');
  await page.goto('/');
  await page.getByLabel('Your Python code').fill('while True:\n    pass');
  await page.getByRole('button',{name:/Run Python/}).click();
  await page.getByRole('button',{name:'Stop',exact:true}).click();
  await expect(page.locator('.output[aria-live]')).toHaveText('Execution stopped.');
  await expect(page.getByRole('button',{name:/Run Python/})).toBeEnabled();
});


test('endless loop automatically times out without freezing the page', async ({page}) => {
  await mockApi(page,'student');
  await page.goto('/');
  await page.getByLabel('Your Python code').fill('while True:\n    pass');
  await page.getByRole('button',{name:/Run Python/}).click();
  await expect(page.locator('.output[aria-live]')).toContainText('Execution stopped after 15 seconds',{timeout:20000});
  await expect(page.getByRole('button',{name:/Run Python/})).toBeEnabled();
});

test('mobile welcome fits the viewport', async ({page}) => {
  await page.setViewportSize({width:375,height:812});
  await mockApi(page,null);
  await page.goto('/');
  await expect(page.getByRole('link',{name:/Continue with Google/})).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});


test('opening lesson teaches prediction, editing, hints and execution order', async ({page}) => {
  await mockApi(page,'student');
  await page.goto('/');
  await expect(page.getByRole('region',{name:'Lesson one guide'})).toBeVisible();
  await page.getByRole('button',{name:'The dragon message',exact:true}).click();
  await expect(page.getByText(/castle message appears first because/)).toBeVisible();
  await page.getByRole('button',{name:'Try the example in the editor'}).click();
  await expect(page.getByLabel('Your Python code')).toHaveValue('print("You stand outside a mysterious castle.")\nprint("A tiny dragon opens the gate.")');
  for(let i=0;i<3;i++) await page.getByRole('button',{name:'Show next hint',exact:true}).click();
  await expect(page.getByRole('button',{name:'All hints shown'})).toBeDisabled();
  await page.getByRole('button',{name:'Both at once',exact:true}).click();
  await expect(page.getByText(/These two statements run one after the other/)).toBeVisible();
  await expect(page.getByText('Your output should contain your two story messages in order. Your wording is your choice.')).toBeVisible();
});


test('public preview jumps to lessons without account access', async ({page}) => {
 const privateRequests:string[]=[];
 page.on('request', r=>{if(/\/api\/(me|history|family|attempts)$/.test(new URL(r.url()).pathname))privateRequests.push(r.url());});
 await mockApi(page,null);
 await page.goto('/preview?lesson=loop');
 await expect(page.getByText('Content preview',{exact:true})).toBeVisible();
 await expect(page.getByLabel('Your Python code')).toHaveValue(lessons[2].starter);
 await page.getByRole('button',{name:/Say hello/}).click();
 await expect(page.getByRole('region',{name:'Lesson one guide'})).toBeVisible();
 await expect(page).toHaveURL(/lesson=hello/);
 await expect(page.getByRole('button',{name:'Sign out'})).toHaveCount(0);
 expect(privateRequests).toEqual([]);
});

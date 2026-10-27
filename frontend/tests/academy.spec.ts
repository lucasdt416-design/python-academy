import {test, expect, Page} from '@playwright/test';
// Same JSON that /api/lessons serves; backend tests assert they are identical.
import lessons from '../../backend/tests/fixtures/legacy_lessons_v1.json';
import catalog from '../../backend/tests/fixtures/catalog_v1.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';
const PATH_NAMES:Record<string,string>={scratch:'Learn to code',hackathon:'hackathon',university:'university',websites:'websites and apps',data:'data',explore:'explore'};
async function mockApi(page:Page,initialRole:string|null,done:string[]=[],initialGoal={goal:'scratch' as string|null,chosen:true,asked:true}){
 let role=initialRole;const completed:string[]=[...done];let goal={...initialGoal};
 await page.route('**/api/**',async route=>{
  const path=new URL(route.request().url()).pathname;let body:unknown={},status=200;
  if(path==='/api/lessons')body=lessons;
  else if(path==='/api/catalog')body=catalog;
  else if(path==='/api/awards')body={xp:completed.length*100,completed,badges:[]};
  else if(path==='/api/goals')body=goals;
  else if(path==='/api/goal'){if(route.request().method()==='POST'){const chosen=route.request().postDataJSON().goal??null;goal={goal:chosen??'scratch',chosen:!!chosen,asked:true};}body=goal;}
  else if(path==='/api/recommendation'){
   // Mirrors the backend rules for the one released unit; backend tests cover the rules themselves.
   const next=lessons.find(l=>!completed.includes(l.id));
   body=next?{kind:completed.length?'continue':'start',reason:completed.length?"You're partway through Python Foundations.":`Start of your ${PATH_NAMES[goal.goal??'scratch']} path.`,course:'py',unit:'py.u01',lesson:next.id,options:[],notes:[],rules_version:1}
    :{kind:'caught_up',reason:"You've finished everything available on your path so far.",course:null,unit:null,lesson:null,options:[],notes:['Python Foundations unit 2 is next on your path and is coming soon.'],rules_version:1};
  }
  else if(path==='/api/me'){status=role?200:401;body=role?{id:1,email:'test@example.com',role}:{detail:'Sign in to continue'};}
  else if(path==='/api/history'||path==='/api/family')body=[];
  else if(path==='/api/progress')body=completed;
  else if(path==='/api/enroll'){role=route.request().postDataJSON().invitation?'student':'parent';body={role};}
  else if(path==='/api/invitations')body={url:'https://academy.example/?invite=test'};
  else if(path==='/api/logout')role=null;
  else if(path==='/api/check'||path==='/api/attempts'){
   const data=route.request().postDataJSON();if(path==='/api/attempts'&&!completed.includes(data.lesson_id))completed.push(data.lesson_id);
   body={passed:true,result:'passed',feedback:'Your adventure works with different player replies.',assessment:'browser_practice'};
  }
  await route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
 });
}
// Every test also checks the Report-Only page policy (SEC-04): anything it would block fails the test,
// so the policy can be switched to enforce mode without breaking these flows.
const violations=new WeakMap<Page,string[]>();
test.beforeEach(async({page})=>{
 const found:string[]=[];violations.set(page,found);
 await page.exposeFunction('reportCspViolation',(v:string)=>found.push(v));
 await page.addInitScript(()=>document.addEventListener('securitypolicyviolation',e=>(window as unknown as {reportCspViolation:(v:string)=>void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI||'inline'} on ${location.pathname}`)));
});
test.afterEach(async({page})=>{expect(violations.get(page)).toEqual([]);});
test('welcome provides Google sign-in and keyboard skip navigation',async({page})=>{
 await mockApi(page,null);await page.goto('/');
 await expect(page.getByRole('link',{name:/Continue with Google/})).toHaveAttribute('href','/auth/google');
 await page.keyboard.press('Tab');await expect(page.getByRole('link',{name:/Skip/})).toBeFocused();
});
test('invitation survives redirect and enrolls a student',async({page})=>{
 await mockApi(page,'pending',[],{goal:null,chosen:false,asked:false});await page.goto('/?invite=private-token');await page.reload();
 await page.getByLabel('Date of birth').fill('2010-01-01');
 const request=page.waitForRequest(r=>r.url().endsWith('/api/enroll'));
 await page.getByRole('button',{name:'Complete registration'}).click();
 expect((await request).postDataJSON().invitation).toBe('private-token');
 await expect(page.getByRole('heading',{name:'What would you like to do first?'})).toBeFocused();
 const skip=page.waitForRequest(r=>r.url().endsWith('/api/goal')&&r.method()==='POST');await page.getByRole('button',{name:'Skip for now'}).click();expect((await skip).postDataJSON()).toEqual({});
 await expect(page.getByRole('heading',{name:'Your first course is ready.'})).toBeVisible();await expect(page.getByRole('link',{name:/^Start/})).toHaveAttribute('href','/learn/hello');
 await expect(page.getByText('Learn to code from scratch (default)')).toBeVisible();
 expect(await page.evaluate(()=>sessionStorage.getItem('academy-invite'))).toBeNull();
});
test('parent creates an invitation, previews lessons, and returns to family',async({page})=>{
 await mockApi(page,'parent');await page.goto('/');
 await page.getByLabel('Student’s Google email').fill('learner@example.com');await page.getByRole('button',{name:'Create invitation'}).click();
 await expect(page.getByLabel('Invitation link')).toHaveValue('https://academy.example/?invite=test');
 await page.getByRole('link',{name:/Try the lessons/}).click();
 await expect(page.getByRole('article',{name:'Current learning card'})).toHaveCount(1);
 await page.getByRole('link',{name:'Return to your account'}).click();
 await expect(page.getByRole('heading',{name:'Help their curiosity grow.'})).toBeVisible();
 await page.getByRole('button',{name:'Sign out'}).click();await expect(page.getByRole('link',{name:/Continue with Google/})).toBeVisible();
});
test('student sees one card at a time and predicts before coding',async({page})=>{
 await mockApi(page,'student');await page.goto('/learn/hello');
 await expect(page.getByRole('article',{name:'Current learning card'})).toHaveCount(1);
 await expect(page.getByLabel('Your Python code')).toHaveCount(0);await expect(page.getByText('Card 1 of 5')).toBeVisible();
 await page.getByRole('button',{name:'Continue →',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Watch the story take shape'})).toBeVisible();
 await expect(page.getByRole('heading',{name:'Your story starts with one instruction'})).toHaveCount(0);
 await page.getByRole('button',{name:'Continue →',exact:true}).click();
 await expect(page.getByRole('button',{name:'Continue →',exact:true})).toBeDisabled();
 await page.getByRole('button',{name:'The dragon message',exact:true}).click();await expect(page.getByText(/Let’s look again/)).toBeVisible();
 await expect(page.getByRole('button',{name:'Continue →',exact:true})).toBeDisabled();
 await page.getByRole('button',{name:'The castle message',exact:true}).click();await page.getByRole('button',{name:'Continue →',exact:true}).click();
 await expect(page.getByLabel('Your Python code')).toHaveValue(lessons[0].example);
 await expect(page.getByRole('heading',{name:'Make one small change'})).toBeFocused();
 await page.getByRole('button',{name:'Start my challenge'}).click();await expect(page.getByLabel('Your Python code')).toHaveValue(lessons[0].starter);
 await expect(page.getByRole('button',{name:'Next quest →'})).toBeDisabled();
});
test('preview jumps to any card without private API requests',async({page})=>{
 const requests:string[]=[];page.on('request',r=>{if(/\/api\/(me|history|family|attempts|progress)$/.test(new URL(r.url()).pathname))requests.push(r.url());});
 await mockApi(page,null);await page.goto('/preview?lesson=choices&card=5');
 await expect(page.getByText('Card 5 of 5')).toBeVisible();await expect(page.getByLabel('Your Python code')).toHaveValue(lessons[3].starter);
 await page.getByRole('button',{name:'1. Discover',exact:true}).click();await expect(page.getByLabel('Your Python code')).toHaveCount(0);
 await page.getByRole('link',{name:/Launch your adventure/}).click();await expect(page.getByRole('heading',{name:'Connect the pieces into a game'})).toBeVisible();expect(requests).toEqual([]);
});
test('drafts survive card navigation and hints are gradual',async({page})=>{
 await mockApi(page,null);await page.goto('/preview?lesson=variables&card=5');
 const editor=page.getByLabel('Your Python code');await editor.fill('hero = "Kai"');await page.getByRole('button',{name:'Show a nudge'}).click();
 await expect(page.getByText(/A nudge\./)).toBeVisible();await expect(page.getByText(/A bigger hint\./)).toHaveCount(0);
 await page.getByRole('button',{name:'4. Try it',exact:true}).click();await page.getByRole('button',{name:'5. Your challenge',exact:true}).click();
 await expect(editor).toHaveValue('hero = "Kai"');await editor.fill('');await editor.press('Tab');await expect(editor).toHaveValue('    ');await editor.press('Shift+Tab');await expect(editor).not.toBeFocused();
});
// Actual Python runs in Pyodide. Account/check API responses are mocked here; backend checks have separate tests.
for(const lesson of lessons){test(`real Python executes ${lesson.id} with player replies`,async({page})=>{
 await mockApi(page,null);await page.goto(`/preview?lesson=${lesson.id}&card=5`);await page.getByLabel('Your Python code').fill(lesson.example);
 const request=page.waitForRequest(r=>r.url().endsWith('/api/check'));await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('.execution-output')).toHaveText(lesson.exampleOutput,{timeout:25000});expect((await request).postDataJSON().inputs).toEqual(lesson.exampleInputs);
 await expect(page.getByText(lesson.badge+' badge earned!',{exact:true})).toBeVisible();await expect(page.getByText('100 XP',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Run & check challenge'}).click();await expect(page.getByRole('button',{name:'Run & check challenge'})).toBeEnabled({timeout:25000});await expect(page.getByText('100 XP',{exact:true})).toBeVisible();
});}
test('different player replies change the actual Python story',async({page})=>{
 await mockApi(page,null);await page.goto('/preview?lesson=adventure&card=5');await page.getByLabel('Your Python code').fill(lessons[4].example);
 await page.getByLabel('Player name',{exact:true}).fill('Kai');await page.getByLabel('Path: left or right').fill('right');await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('.execution-output')).toContainText('Welcome aboard, Kai',{timeout:25000});await expect(page.locator('.execution-output')).toContainText('sky garden');
});
test('Python errors and endless loops stay recoverable',async({page})=>{
 await mockApi(page,null);await page.goto('/preview?lesson=hello&card=5');await page.getByLabel('Your Python code').fill('print(');await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('#code-feedback')).toContainText('Python stoppedA parenthesis is still open',{timeout:25000});await page.getByLabel('Your Python code').fill('while True:\n    pass');await page.getByRole('button',{name:'Run & check challenge'}).click();
 await page.getByRole('button',{name:'Stop',exact:true}).click();await expect(page.locator('.execution-output')).toHaveText('Execution stopped.');await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('.execution-output')).toContainText('Execution stopped after 15 seconds',{timeout:20000});await expect(page.locator('#code-feedback')).toContainText('Your program kept running');await expect(page.getByRole('button',{name:'Run & check challenge'})).toBeEnabled();
});
test('checker service errors keep the draft, award nothing, and allow a retry',async({page})=>{
 await mockApi(page,null);await page.route('**/api/check',route=>route.fulfill({contentType:'application/json',body:JSON.stringify({passed:false,result:'service_error',feedback:'Unable to assess this right now. Your code is unchanged; please try again in a moment.',assessment:'browser_practice'})}));
 const code='print("A forest.")\nprint("A dragon!")';await page.goto('/preview?lesson=hello&card=5');await page.getByLabel('Your Python code').fill(code);await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.getByRole('status').filter({hasText:'Unable to assess this right now'})).toBeVisible({timeout:25000});await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 await expect(page.getByLabel('Your Python code')).toHaveValue(code);await expect(page.getByRole('button',{name:'Run & check challenge'})).toBeEnabled();await expect(page.getByText('0 XP',{exact:true})).toBeVisible();
});
test('mobile classroom fits, collapses the unit menu, and respects reduced motion',async({page})=>{
 await page.setViewportSize({width:375,height:812});await page.emulateMedia({reducedMotion:'reduce'});await mockApi(page,null);await page.goto('/preview?lesson=adventure&card=4');
 await expect(page.getByLabel('Your Python code')).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 const toggle=page.getByRole('button',{name:/Lesson 5 of 5/});await expect(toggle).toHaveAttribute('aria-expanded','false');await expect(page.getByRole('link',{name:/Launch your adventure/})).toBeHidden();
 await toggle.click();await expect(toggle).toHaveAttribute('aria-expanded','true');const current=page.getByRole('link',{name:/Launch your adventure/});await expect(current).toHaveAttribute('aria-current','page');
 const box=await current.boundingBox();expect(box!.x).toBeGreaterThanOrEqual(0);expect(box!.x+box!.width).toBeLessThanOrEqual(375);
 await page.getByRole('link',{name:/Open the story/}).click();await expect(toggle).toHaveCount(0);await expect(page.getByRole('button',{name:/Lesson 1 of 5/})).toHaveAttribute('aria-expanded','false');
 expect(await page.locator('.world-spark').evaluateAll(elements=>elements.every(el=>getComputedStyle(el).animationName==='none'))).toBe(true);
});
test('catalog shows every course, with coming-soon courses labelled and not startable',async({page})=>{
 await mockApi(page,null);await page.goto('/courses');
 const courses=page.getByRole('list',{name:'Courses'}).getByRole('listitem');await expect(courses).toHaveCount(catalog.courses.length);
 const python=page.getByRole('article',{name:'Python Foundations'});await expect(python.getByText('Available',{exact:true})).toBeVisible();await expect(python.getByText('8 lessons ready to try')).toBeVisible();
 await expect(page.getByText('Coming soon',{exact:true})).toHaveCount(catalog.courses.length-1);
 await expect(page.getByRole('article',{name:'Hackathon Ready'}).getByText('Builds on Python Foundations units 1–7.')).toBeVisible();
 await page.getByRole('link',{name:'Hackathon Ready'}).click();await expect(page).toHaveURL('/courses/hack');
 await expect(page.getByText('This course is coming soon and cannot be started yet.')).toBeVisible();await expect(page.getByRole('link',{name:/^(Start|Continue)/})).toHaveCount(0);
 await expect(page.getByRole('list',{name:'Units'}).getByRole('listitem')).toHaveCount(7);await expect(page.locator('.unit-card a')).toHaveCount(0);
});
test('course page shows unit progress and continues where the student left off',async({page})=>{
 await mockApi(page,'student',['hello']);await page.goto('/courses/py');
 await expect(page.getByRole('heading',{level:1,name:'Python Foundations'})).toBeVisible();await expect(page.getByText('1 of 8 available lessons complete')).toBeVisible();
 const unit=page.getByRole('article',{name:'Build Your Own Adventure'});
 await expect(unit.getByRole('link',{name:/Open the story.*Completed/})).toHaveAttribute('href','/learn/hello');
 await expect(unit.getByRole('link',{name:/Create your hero.*Up next/})).toBeVisible();await expect(unit.getByRole('link',{name:/Choose a path.*Not started/})).toBeVisible();
 await expect(page.getByRole('article',{name:'Repeat and explore'}).getByText('Coming soon')).toBeVisible();
 await page.getByRole('link',{name:/Continue: Create your hero/}).click();await expect(page).toHaveURL('/learn/variables');
 await expect(page.getByRole('heading',{name:'Remember a detail with a variable'})).toBeVisible();
});
test('lesson sidebar shows done, current, and not started, and works from the keyboard',async({page})=>{
 await mockApi(page,'student',['hello']);await page.goto('/learn/choices');
 const nav=page.getByRole('navigation',{name:'Lessons in this unit'});await expect(nav.getByText('1 of 5 lessons complete')).toBeVisible();
 await expect(nav.getByRole('link',{name:/Open the story.*Completed/})).toBeVisible();await expect(nav.getByRole('link',{name:/Choose a path.*Current lesson/})).toHaveAttribute('aria-current','page');
 await expect(nav.getByRole('link',{name:/Launch your adventure.*Not started/})).toBeVisible();
 await expect(page.getByRole('navigation',{name:'Breadcrumb'}).getByRole('link',{name:'Python Foundations'})).toHaveAttribute('href','/courses/py');
 await nav.getByRole('link',{name:/Create your hero/}).focus();await page.keyboard.press('Enter');
 await expect(page).toHaveURL('/learn/variables');await expect(nav.getByRole('link',{name:/Create your hero/})).toHaveAttribute('aria-current','page');
 await expect(page.getByRole('heading',{name:'Remember a detail with a variable'})).toBeFocused();
});
test('student home offers the next lesson and shows XP',async({page})=>{
 await mockApi(page,'student',['hello','variables']);await page.goto('/');
 await expect(page.getByRole('heading',{name:'Welcome back. Keep building.'})).toBeVisible();
 const next=page.getByRole('region',{name:'Meet the player'});await expect(next.getByText('200 XP')).toBeVisible();
 await expect(next.getByRole('link',{name:/Continue/})).toHaveAttribute('href','/learn/input');
 await expect(page.getByRole('article',{name:'Python Foundations'}).getByText('2 of 8 lessons complete')).toBeVisible();
});
test('a new student chooses a goal from the keyboard and sees why the next lesson is suggested',async({page})=>{
 await mockApi(page,'student',[],{goal:null,chosen:false,asked:false});await page.goto('/');
 await expect(page.getByRole('heading',{name:'What would you like to do first?'})).toBeFocused();await expect(page.getByRole('button',{name:'Continue'})).toBeDisabled();
 await expect(page.getByRole('radio')).toHaveCount(goals.length);
 await page.getByRole('radio',{name:/Learn to code from scratch/}).focus();await page.keyboard.press('ArrowDown');
 await expect(page.getByRole('radio',{name:/Get ready for hackathons/})).toBeChecked();
 const saved=page.waitForRequest(r=>r.url().endsWith('/api/goal')&&r.method()==='POST');await page.getByRole('button',{name:'Continue'}).click();
 expect((await saved).postDataJSON()).toEqual({goal:'hackathon'});
 const next=page.getByRole('region',{name:'Open the story'});await expect(next.getByText('Start of your hackathon path.')).toBeVisible();
 await expect(next.getByText('Get ready for hackathons')).toBeVisible();await expect(next.getByRole('link',{name:/^Start/})).toHaveAttribute('href','/learn/hello');
 await expect(page.getByRole('article',{name:'Python Foundations'}).getByText('Recommended')).toBeVisible();
 await expect(page.getByText('Recommended',{exact:true})).toHaveCount(1);
});
test('students can change their goal, or cancel without changing it',async({page})=>{
 await mockApi(page,'student',['hello'],{goal:'data',chosen:true,asked:true});await page.goto('/');
 await expect(page.getByText("You're partway through Python Foundations.")).toBeVisible();await expect(page.getByText('Work with data',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Change goal'}).click();await expect(page.getByRole('radio',{name:/Work with data/})).toBeChecked();
 await page.getByRole('button',{name:'Cancel'}).click();await expect(page.getByText('Work with data',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Change goal'}).click();await page.getByRole('radio',{name:/Just explore/}).check();
 await page.getByRole('button',{name:'Save my goal'}).click();await expect(page.getByText('Just explore',{exact:true})).toBeVisible();
});
test('students who finished everything available see what is coming soon',async({page})=>{
 await mockApi(page,'student',lessons.map(l=>l.id));await page.goto('/');
 const card=page.getByRole('region',{name:'More lessons are on the way'});await expect(card.getByText("You've finished everything available on your path so far.")).toBeVisible();
 await expect(card.getByText('Python Foundations unit 2 is next on your path and is coming soon.')).toBeVisible();await expect(card.getByRole('link',{name:/^(Start|Continue)/})).toHaveCount(0);
 await expect(page.getByText('Recommended',{exact:true})).toHaveCount(0);
});
test('parents see each learner\'s goal',async({page})=>{
 await mockApi(page,'parent');await page.route('**/api/family',route=>route.fulfill({contentType:'application/json',body:JSON.stringify([{id:2,email:'ava@example.com',attempts:[],completed:['hello'],goal:'Get ready for hackathons'}])}));
 await page.goto('/');await expect(page.getByRole('heading',{name:'ava@example.com'})).toBeVisible();
 await expect(page.getByText('Goal: Get ready for hackathons')).toBeVisible();await expect(page.getByText('1 quests completed',{exact:false})).toBeVisible();
});
test('goal card fits a phone',async({page})=>{
 await page.setViewportSize({width:375,height:812});await mockApi(page,'student',[],{goal:null,chosen:false,asked:false});await page.goto('/');
 await expect(page.getByRole('radio',{name:/Just explore/})).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 const [a,b]=await Promise.all([page.locator('.goal-option').nth(0).boundingBox(),page.locator('.goal-option').nth(1).boundingBox()]);expect(b!.y).toBeGreaterThan(a!.y);
});
test('the lesson page runs Python with the security headers on',async({page})=>{
 await mockApi(page,null);const response=await page.goto('/preview?lesson=hello&card=5');const headers=response!.headers();
 expect(headers['strict-transport-security']).toBe('max-age=31536000; includeSubDomains');expect(headers['x-content-type-options']).toBe('nosniff');
 expect(headers['referrer-policy']).toBe('no-referrer');expect(headers['content-security-policy']).toContain("frame-ancestors 'none'");
 // Passes in Report-Only mode now and after the switch to enforce mode (handoff 08 section 5).
 const policy=noncePolicy(headers);expect(policy).toMatch(/^default-src 'self'; script-src 'self' 'nonce-[A-Za-z0-9+/]{22}==';/);expect(policy).not.toContain('unsafe-inline');
 const worker=await page.request.get('/python-worker.js');expect(worker.headers()['content-security-policy']).toContain('https://cdn.jsdelivr.net');
 await page.getByLabel('Your Python code').fill('print("A forest.")\nprint("A dragon!")');await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('.execution-output')).toHaveText('A forest.\nA dragon!',{timeout:25000});await expect(page.getByText('Story spark badge earned!',{exact:true})).toBeVisible();
});
test('the app refuses to be shown inside a frame',async({page})=>{
 // frame-ancestors 'none' blocks every framing page, even our own origin (Chromium blocks a fake outside site earlier, for other reasons).
 await page.route('**/framing-test',route=>route.fulfill({contentType:'text/html',body:'<iframe src="/"></iframe>'}));
 const refused=page.waitForEvent('console',m=>m.text().includes(`violates the following Content Security Policy directive: "frame-ancestors 'none'"`));
 await page.goto('/framing-test');await refused;await expect.poll(()=>page.frames()[1]?.url()).toMatch(/^chrome-error:/);
});
test('rate-limited checks explain the wait and keep the draft',async({page})=>{
 await mockApi(page,null);await page.route('**/api/check',route=>route.fulfill({status:429,headers:{'Retry-After':'42'},contentType:'application/json',body:JSON.stringify({detail:'Too many checks for now. Please wait 42 seconds and try again. Your code is unchanged.'})}));
 const code='print("A forest.")\nprint("A dragon!")';await page.goto('/preview?lesson=hello&card=5');await page.getByLabel('Your Python code').fill(code);await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('.notice[role=alert]')).toHaveText('Too many checks for now. Please wait 42 seconds and try again. Your code is unchanged.',{timeout:25000});
 await expect(page.getByLabel('Your Python code')).toHaveValue(code);await expect(page.getByRole('button',{name:'Run & check challenge'})).toBeEnabled();await expect(page.getByText(/badge earned!/)).toHaveCount(0);
});
// SEC-09: inline scripts run only if they carry the nonce made for this response (proxy.ts).
// The nonce policy is found in either header, so these pass in Report-Only and enforce mode.
const PAGES=['/','/courses','/courses/py','/learn/hello','/preview?lesson=hello','/no-such-page'];
function noncePolicy(headers:Record<string,string>){return [headers['content-security-policy-report-only'],headers['content-security-policy']].filter(Boolean).join(',').split(',').map(p=>p.trim()).find(p=>p.includes("'nonce-"))??'';}
function nonceOf(policy:string){return /'nonce-([^']+)'/.exec(policy)?.[1]??'';}
test('every page request gets a new nonce, and every script on the page carries it',async({request})=>{
 const seen=new Set<string>();
 for(const path of PAGES)for(let i=0;i<2;i++){
  const response=await request.get(path);const policy=noncePolicy(response.headers());const nonce=nonceOf(policy);
  expect(nonce).toMatch(/^[A-Za-z0-9+/]{22}==$/);expect(policy).toContain(`script-src 'self' 'nonce-${nonce}';`);expect(policy).not.toContain('unsafe-inline');
  expect(seen.has(nonce),`${path} reused a nonce`).toBe(false);seen.add(nonce);
  const scripts=(await response.text()).match(/<script\b[^>]*>/g)??[];expect(scripts.length).toBeGreaterThan(0);
  for(const script of scripts)expect(script,path).toContain(`nonce="${nonce}"`);
 }
 // Pages are rendered per request, so no shared cache may keep one nonce for everyone.
 expect((await request.get('/courses')).headers()['cache-control']).toContain('no-store');
});
test('every page loads with no CSP reports under the nonce policy',async({page})=>{
 for(const role of [null,'student','parent']){
  await page.unrouteAll();await mockApi(page,role);
  for(const path of PAGES){const response=await page.goto(path);expect(nonceOf(noncePolicy(response!.headers()))).not.toBe('');await page.waitForLoadState('networkidle');await expect(page.locator('main')).toBeVisible();}
 }
 // The afterEach check fails the test if any page reported a violation.
});
test('an injected inline script without the nonce is reported as blocked',async({page})=>{
 await mockApi(page,null);let enforced=false;
 // Plays the part of stored XSS: the page HTML arrives with extra inline scripts in it.
 await page.route('**/preview?lesson=hello',async route=>{
  const response=await route.fetch();const nonce=nonceOf(noncePolicy(response.headers()));enforced=(response.headers()['content-security-policy']??'').includes("'nonce-");
  const injected=`<script>window.injected=true</script><script nonce="${btoa('guessed-nonce!!!')}">window.guessed=true</script><script nonce="${nonce}">window.trusted=true</script>`;
  await route.fulfill({response,body:(await response.text()).replace('</head>',injected+'</head>')});
 });
 await page.goto('/preview?lesson=hello');await expect(page.getByRole('article',{name:'Current learning card'})).toHaveCount(1);
 const found=violations.get(page)!;
 // One report each for the script with no nonce and the one with a guessed nonce; none for the real nonce.
 await expect.poll(()=>found.length).toBe(2);expect(found).toEqual(Array(2).fill('script-src-elem blocked inline on /preview'));
 const ran=await page.evaluate(()=>{const w=window as unknown as Record<string,boolean>;return {injected:!!w.injected,guessed:!!w.guessed,trusted:!!w.trusted};});
 // Report-Only reports but still runs them; enforce mode blocks them.
 expect(ran).toEqual({injected:!enforced,guessed:!enforced,trusted:true});
 found.length=0;// expected reports, checked above
});

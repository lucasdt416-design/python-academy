'use client';
import {useState} from 'react';
import {type Awards,type Catalog,type Course,type Recommendation,lessonHref,locate,nextLesson,prerequisiteText,unitNumber,useCatalog} from './catalog-data';
import LessonArt,{CARD_TYPES,Icon} from './lesson-art';


/** Each released unit's picture: the lesson that best shows the whole unit. */
const UNIT_ART:Record<string,string>={'py.u01':'adventure','py.u02':'py.arithmetic','py.u03':'py.nested-loops'};
/** The home page's own words for each unit (prototype copy); a unit without them shows its catalog summary. */
const UNIT_BLURB:Record<string,string>={'py.u01':'Print, variables, input and choices, ending in a small game that is yours.','py.u02':'Arithmetic, comparisons, and, or, not and elif, through a riddle keeper\'s game.','py.u03':'while and for loops that always finish, and a loop inside a loop.'};
const PLANNED:{units:string[];title:string;text:string}[]=[{units:['py.u04'],title:'Unit 4 · Keep track of a world',text:'Lists, dictionaries, sets'},{units:['py.u05'],title:'Unit 5 · Organize your code',text:'Functions and scope'},{units:['py.u06','py.u07','py.u08','py.u09','py.u10','py.u11','py.u12'],title:'Units 6 to 12',text:'Errors, libraries, tests, files, patterns in text, classes, a final project'}];
const WORDS=['no','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve'];
const word=(n:number)=>WORDS[n]??String(n);

/* Python's // and % for whole numbers: the result of // rounds down, and % takes the sign of the divisor. */
export function floorDiv(a:number,b:number){return Math.floor(a/b);}
export function pyMod(a:number,b:number){return a-b*Math.floor(a/b);}

/** The home page's playground: a preview of // and % worked out in JavaScript. It never loads Python. */
function Playground(){
 const [coins,setCoins]=useState('17'),[friends,setFriends]=useState('5');
 const c=Number(coins),f=Number(friends),whole=coins.trim()!==''&&friends.trim()!==''&&Number.isInteger(c)&&Number.isInteger(f);
 const out=!whole?<span className="err">Type a whole number in each box.</span>:f===0?<span className="err">ZeroDivisionError: you cannot share a chest between 0 friends.</span>:`${floorDiv(c,f)}\n${pyMod(c,f)}`;
 return <section className="playground" aria-labelledby="pg-h">
  <div className="pg-top"><h2 id="pg-h"><span className="pg-preview">Preview</span>count_the_treasure.py</h2><span>unit 2 · lesson 1</span></div>
  <pre className="pg-code"><span className="c"># share a chest of coins</span>{'\n'}coins = <input type="number" value={coins} min={0} max={999} aria-label="coins" onChange={e=>setCoins(e.target.value)}/>{'\n'}friends = <input type="number" value={friends} min={0} max={99} aria-label="friends" onChange={e=>setFriends(e.target.value)}/>{'\n'}<span className="f">print</span>(coins <span className="k">{'//'}</span> friends){'\n'}<span className="f">print</span>(coins <span className="k">%</span> friends)</pre>
  <div className="pg-out" aria-live="polite"><span className="out-label">Output</span><div data-testid="pg-out">{out}</div></div>
  <p className="pg-note">Change the numbers. <code>{'//'}</code> is each friend&apos;s whole share, <code>%</code> is what&apos;s left over. In a lesson you type these lines yourself.</p>
 </section>;
}

const HINTS=[['A nudge','A nudge: one of the names in your print() is not spelled the way it was set.'],['A bigger hint','A bigger hint: compare the name inside print() with the name on line 1, letter by letter.'],['The approach','The approach: names must match exactly, including every letter. Fix the spelling in print().']];

/** The signed-out home page. Copy: docs/design/prototype/index.html, #home. */
export function Landing(){
 const {catalog}=useCatalog();
 const [hint,setHint]=useState(-1);
 const python=catalog?.courses.find(c=>c.id==='py'),released=python?.units.filter(u=>u.status==='released')??[],planned=python?python.units.length-released.length:0;
 const flow:[string,string][]=[['Discover','One idea, in a few sentences.'],['Worked example','Code you read line by line, with the output beside it.'],['Predict','Guess what it prints before it runs. Guess wrong and you get the reason.'],['Try it','Change the example and see what moves.'],['Challenge','Write the program yourself. Hidden test cases catch copied answers.']];
 return <>
  <div className="topo hero"><div className="wrap hero-grid">
   <div>
    <h1>Your first Python program is <em>a story.</em></h1>
    <p className="lead">Write a few lines, run them, see what happens. Each lesson ends with a small challenge you solve yourself.</p>
    <div className="cta"><a className="btn primary" href="/preview?lesson=hello">Try a lesson, no account <Icon name="arrow"/></a><a className="btn" href="/auth/google">Sign in with Google</a></div>
    {/* The real rules (backend/app/main.py enroll(), docs/plan/independent-learners.md): invited learners 13 and up,
        parents over 25. Accounts of one's own at 16 and up are decided (ID-01) but not built (ID-01d). */}
    <p className="fine">Learners 13 and up sign in through a parent&apos;s invitation. Anyone over 25 can start a family account. Accounts for learners 16 and up on their own are planned, not open yet.</p>
   </div>
   <Playground/>
  </div></div>

  <section className="band" aria-labelledby="flow-h"><div className="wrap">
   <div className="sec-head"><h2 id="flow-h">Every lesson goes in the same order.</h2><p>So you always know what is being asked of you.</p></div>
   <ol className="flow">{flow.map(([name,text],i)=><li key={name} className={'t-'+CARD_TYPES[i].type}><div className="tag"><span className="ib"><Icon name={CARD_TYPES[i].icon}/></span>{name}</div><p>{text}</p></li>)}</ol>
  </div></section>

  <section className="band alt" aria-labelledby="err-h"><div className="wrap errdemo">
   <div>
    <h2 id="err-h">When it breaks, you are told why.</h2>
    <p className="lead">The page marks the line, says what Python couldn&apos;t do, and often guesses the name you meant. Python&apos;s own message is a click away.</p>
    <p className="lead">Stuck? Hints come in steps: a nudge, a bigger hint, then the approach. There is no button that hands you the answer.</p>
   </div>
   <div>
    <div className="demo-editor" role="img" aria-label="Code with line 3 marked as the error">
     <div className="bar"><span>hero.py</span><span>3 lines</span></div>
     <div className="ln"><span>1</span><span>hero = &quot;Kai&quot;</span></div>
     <div className="ln"><span>2</span><span>tool = &quot;map&quot;</span></div>
     <div className="ln bad"><span>▶ 3</span><span>print(heor)</span></div>
    </div>
    <div className="explain">
     <p className="st">PYTHON STOPPED · LINE 3</p>
     <h3>Python does not know <code>heor</code></h3>
     <p>You used a name before giving it a value, or spelled it two ways. Did you mean <code>hero</code>?</p>
    </div>
    <div className="demo-hints" role="group" aria-label="Hint ladder">{HINTS.map(([label],i)=><button key={label} type="button" className={'btn small'+(hint===i?' on':'')} aria-pressed={hint===i} onClick={()=>setHint(i)}>{label}</button>)}</div>
    <div className="hint-box" aria-live="polite">{hint<0?'Hints appear here, one at a time.':HINTS[hint][1]}</div>
   </div>
  </div></section>

  <section className="band topo" aria-labelledby="trail-h"><div className="wrap">
   <div className="sec-head"><h2 id="trail-h">Python Foundations: {word(released.length)} units open, {word(planned)} on the way.</h2><p>Each unit takes the same adventure a little further.</p></div>
   <ul className="trail">{released.map(unit=>{const art=UNIT_ART[unit.id]??unit.lessons[0]?.id??'';return <li key={unit.id}><article className="stop" aria-labelledby={'stop-'+unit.id}><LessonArt lesson={art}/><div className="meta"><span>UNIT {unitNumber(unit)}</span><span>{unit.lessons.length} lessons</span></div><h3 id={'stop-'+unit.id}>{unit.title}</h3><p>{UNIT_BLURB[unit.id]??unit.summary}</p></article></li>;})}</ul>
   <ul className="planned" aria-label="Planned units">{PLANNED.filter(p=>python?.units.some(u=>p.units.includes(u.id)&&u.status!=='released')).map(p=><li key={p.title}><b>{p.title}</b>{p.text}</li>)}</ul>
   <p className="later">After Python: Hackathon Ready, Git and GitHub, web, JavaScript and SQL, all marked <em>coming soon</em>.</p>
  </div></section>

  <section className="band alt" aria-labelledby="parents-h"><div className="wrap parents">
   <div>
    <h2 id="parents-h">For parents</h2>
    <p className="lead">A parent over 25 creates a family account and invites each learner by Google email. Try any lesson first; nothing from a preview is saved.</p>
    <a className="btn" href="/preview?lesson=hello">Try a lesson as a parent</a>
   </div>
   <ul className="facts">
    <li><Icon name="check"/><span>Learner code runs in the browser. It is never run on our servers.</span></li>
    <li><Icon name="check"/><span>You see their chosen goal, which lessons are finished, and how many of their attempts passed.</span></li>
    <li><Icon name="check"/><span>Invitations expire after seven days and work only for the invited email.</span></li>
    <li><Icon name="check"/><span>Sign-in is through Google. We never see a password.</span></li>
   </ul>
  </div></section>
 </>;
}

const KICKER={continue:'next up',start:'next up',prerequisite:'build the foundation first',choose:'your choice',caught_up:'all caught up'};

/** The student's next step: the recommendation, why it was chosen, their XP and goal. */
function NextStep({catalog,recommendation,done,awards,goal,onChangeGoal}:{catalog:Catalog;recommendation:Recommendation|null;done:string[];awards:Awards|null;goal?:string|null;onChangeGoal?:()=>void}){
 const first=catalog.courses.find(c=>c.status==='released');
 // Without a recommendation (for example if it failed to load), fall back to the first unfinished lesson.
 const rec:Recommendation|null=recommendation??(first&&nextLesson(first,done)?{kind:done.length?'continue':'start',reason:'',course:first.id,unit:null,lesson:nextLesson(first,done)!.id,options:[],notes:[],rules_version:0}:null);
 const place=rec?locate(catalog,rec.lesson):null;
 const title=place?place.lesson.title:rec?.kind==='choose'?'Choose your next course':'More lessons are on the way';
 const badges=awards?.badges.length??0;
 return <section className="continue" aria-labelledby="continue-heading">
  <div className="txt">
   <p className="kicker">{rec?KICKER[rec.kind]:'all caught up'}{place&&` · unit ${unitNumber(place.unit)}, ${place.unit.title}`}</p>
   <h2 id="continue-heading">{title}</h2>
   {rec?.reason&&<p className="why">{rec.reason}</p>}
   {rec&&rec.notes.length>0&&<ul className="continue-notes">{rec.notes.map(note=><li key={note}>{note}</li>)}</ul>}
   {rec?.kind==='choose'&&<ul className="continue-options">{rec.options.map(id=>{const c=catalog.courses.find(x=>x.id===id);return c&&<li key={id}><a href={`/courses/${id}`}>{c.title}</a></li>;})}</ul>}
   {place&&<div className="cta"><a className="btn warm" href={lessonHref(place.lesson.id,true)}>{rec?.kind==='continue'?'Continue':'Start lesson'}, card 1 of 5 <Icon name="arrow"/></a><a className="btn small" href={`/courses/${place.course.id}`}>See the whole unit</a></div>}
   <div className="meta2">
    {awards&&<><div><strong>{awards.xp} XP</strong>{done.length} {done.length===1?'lesson':'lessons'} done</div><div><strong>{badges}</strong>{badges===1?'badge':'badges'}</div></>}
    {goal!==undefined&&<div>Goal: <span className="goal-name">{goal??'Learn to code from scratch'}</span>{onChangeGoal&&<> · <button type="button" className="link-button" onClick={onChangeGoal}>change<span className="visually-hidden"> goal</span></button></>}</div>}
   </div>
  </div>
  {place&&<div className="artcol"><LessonArt lesson={place.lesson.id}/></div>}
 </section>;
}

/** One unit of the student's path: its picture, a dot per lesson, and where to go next. */
function UnitStrip({unit,done,next,course}:{unit:Course['units'][number];done:string[];next:string|null;course:string}){
 const finished=unit.lessons.filter(l=>done.includes(l.id)).length,current=unit.lessons.some(l=>l.id===next);
 return <li className={'ustrip'+(current?' cur':'')}>
  <LessonArt lesson={UNIT_ART[unit.id]??unit.lessons[0]?.id??''} label={false}/>
  <div><h3>{unitNumber(unit)} · {unit.title}</h3><small>{finished} of {unit.lessons.length} lessons done</small>
   <div className="dots" aria-hidden="true">{unit.lessons.map(l=><i key={l.id} className={'dot'+(done.includes(l.id)?' done':l.id===next?' now':'')}/>)}</div></div>
  {current&&next?<a className="btn small primary" href={lessonHref(next,true)}>Continue<span className="visually-hidden"> unit {unitNumber(unit)}</span></a>
   :<a className="btn small" href={`/courses/${course}`}>{finished===unit.lessons.length?'Review':'See lessons'}<span className="visually-hidden"> in unit {unitNumber(unit)}</span></a>}
 </li>;
}

/** The signed-in student's home. Copy: docs/design/prototype/index.html, #student. */
export function StudentHome({awards,recommendation,goal,onChangeGoal}:{awards:Awards|null;recommendation:Recommendation|null;goal?:string|null;onChangeGoal?:()=>void}){
 const {catalog,error}=useCatalog(),done=awards?.completed??[];
 if(error)return <p className="notice" role="alert">{error}</p>;
 if(!catalog)return <p role="status">Loading courses…</p>;
 const course=catalog.courses.find(c=>c.id===recommendation?.course&&c.status==='released')??catalog.courses.find(c=>c.status==='released');
 const units=course?.units.filter(u=>u.status==='released')??[],lessons=units.flatMap(u=>u.lessons),finished=lessons.filter(l=>done.includes(l.id)).length;
 const next=course?nextLesson(course,done)?.id??null:null,recommended=!!recommendation?.lesson&&recommendation.course===course?.id;
 const later=catalog.courses.filter(c=>c.status!=='released');
 return <>
  <h1 className="home-title">{done.length?<>Welcome back. <span>Keep building.</span></>:<>Your first course <span>is ready.</span></>}</h1>
  <NextStep catalog={catalog} recommendation={recommendation} done={done} awards={awards} goal={goal} onChangeGoal={onChangeGoal}/>
  {course&&<section className="sec" aria-labelledby="path-h">
   <div className="sec-title-row"><h2 id="path-h">Your path in {course.title}</h2>{recommended&&<span className="chip chip-recommended">Recommended</span>}</div>
   <p className="muted">{finished} of {lessons.length} lessons complete</p>
   <ul className="unit-strip">{units.map(unit=><UnitStrip key={unit.id} unit={unit} done={done} next={next} course={course.id}/>)}</ul>
  </section>}
  {later.length>0&&<section className="sec" aria-labelledby="later-h">
   <h2 id="later-h">Coming later</h2>
   <ul className="cgrid">{later.map(c=><li key={c.id}><div className="cc"><span className="chip soon">Coming soon</span><h3><a href={`/courses/${c.id}`}>{c.title}</a></h3><p>{c.prerequisites.required.length?`Needs ${prerequisiteText(c.prerequisites.required,catalog)}.`:'No prerequisites.'}</p></div></li>)}</ul>
  </section>}
 </>;
}

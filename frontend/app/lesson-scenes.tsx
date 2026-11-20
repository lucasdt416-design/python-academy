// Lesson scenes: a small picture that comes alive from the learner's own run. Each lesson has its own,
// built from the run's output, the replies it read, and (after a "Try it" run) the names it made.
// A scene only draws what the program did. It never says whether the program is right: that is the
// check's job, and a scene can't see hidden cases. Scenes for units 1 to 3 are here; later units add
// theirs in scenes-*.tsx and register them in SCENES.
import type {ReactNode} from 'react';
import {type SceneRun,wrap,Bubble,Coin,Ground,Hero,Item,Lamp,Lines,Note,Tag,VarBox,bools,clamp,d,fit,isNum,numOf,numbers,ofKind,outLines,pick,plural,show,strOf,toNum} from './scene-kit';
import {UNIT_4_TO_6} from './scenes-u04-u06';
import {UNIT_7_TO_11} from './scenes-u07-u11';

export type Drawn = {svg:ReactNode;say:string};
export type SceneDef = {title:string;draw:(r:SceneRun|null)=>Drawn};

const IDLE='Run the code to fill this scene.';

// ---------- Unit 1 ----------
const hello:SceneDef={title:'The story scroll',draw:r=>{
 const lines=outLines(r);
 return {say:lines.length?`The scroll shows ${plural(lines.length,'line')}: ${lines.slice(0,4).join(' / ')}`:'An empty scroll, waiting for print() lines.',svg:<>
  <Ground tone="sand"/>
  <path className="f-cream s-ink" d="M40 22h240v126H40z"/><path className="f-amber-l s-ink" d="M32 14h256a8 8 0 0 1 0 16H32a8 8 0 0 1 0-16zM32 140h256a8 8 0 0 1 0 16H32a8 8 0 0 1 0-16z"/>
  {lines.length?<Lines x={56} y={50} lines={lines.flatMap(l=>wrap(l,33,2))} max={5} width={33} gap={17} size={11}/>:<path className="s-moss-s" d="M56 52h180M56 70h150M56 88h170M56 106h120"/>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const variables:SceneDef={title:'Your hero',draw:r=>{
 const lines=outLines(r),hero=strOf(pick(r?.vars,['hero','name','player']))??lines[0]??'',tool=strOf(pick(r?.vars,['tool','item','weapon']))??lines[1]??'';
 const extra=ofKind(r?.vars,['str','int','float']).filter(([k])=>!['hero','tool'].includes(k)).slice(0,1);
 return {say:hero?`A hero named ${hero} appears${tool?`, holding a ${tool}`:''}.`:'An empty spot where your hero will stand.',svg:<>
  <Ground/>
  {hero?<><Hero x={96} y={150} className="pop"/><Tag x={96} y={74} text={fit(hero,16)} tone="clay" className={'drop '+d(2)}/></>:<path className="s-moss-s" d="M79 150q0-38 17-38t17 38zM96 92a13 13 0 1 0 .1 0"/>}
  {tool&&<><Item x={146} y={128} name={tool} className={'pop '+d(4)} size={1.2}/><text className={'mono f-ink type '+d(5)} x={146} y={164} fontSize="11" textAnchor="middle">{fit(tool,12)}</text></>}
  <VarBox x={196} y={34} name="hero" value={r?(pick(r.vars,['hero'])?show(pick(r.vars,['hero']),true):'?'):''} className={'slide '+d(1)}/>
  <VarBox x={196} y={86} name="tool" value={r?(pick(r.vars,['tool'])?show(pick(r.vars,['tool']),true):'?'):''} className={'slide '+d(2)}/>
  {extra.map(([k,v])=><VarBox key={k} x={196} y={138} name={k} value={show(v,true)} className={'slide '+d(3)}/>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const input:SceneDef={title:'At the gate',draw:r=>{
 const reply=r?.inputs[0]??'',greet=outLines(r)[0]??'',at=reply?greet.indexOf(reply):-1;
 return {say:greet?`The player answers ${reply||'nothing'}, and the gate says: ${greet}`:'A gatekeeper waits to ask the player a question.',svg:<>
  <Ground/>
  <path className="f-slate s-ink" d="M232 150V58a34 34 0 0 1 68 0v92z"/><path className="s-ink" d="M266 24v126"/>
  <Hero x={64} y={150} tone="slate"/><Bubble x={38} y={56} w={60} text="  ?" className="pop"/>
  {reply&&<><Hero x={172} y={150} className={'pop '+d(2)}/><Bubble x={128} y={60} w={Math.min(110,reply.length*8+28)} text={reply} right className={'pop '+d(3)}/></>}
  {greet&&<g className={'drop '+d(6)}><rect className="f-white s-ink" x="16" y="8" width="288" height="30" rx="8"/>
   <text className="mono f-ink" x="160" y="28" fontSize="13" textAnchor="middle">{at>=0?<>{fit(greet.slice(0,at),18)}<tspan className="f-clay" fontWeight="700">{fit(reply,14)}</tspan>{fit(greet.slice(at+reply.length),14)}</>:fit(greet,38)}</text></g>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

function Fork({choice,end,small=false}:{choice:'left'|'right'|null;end:string;small?:boolean}){
 const s=small?.55:1,lit=(side:'left'|'right')=>choice===side?'s-cream-w path-lit':'s-cream-w path-dim';
 return <g transform={small?'translate(214 40) scale(.55)':undefined}>
  <path className={lit('left')} d="M160 176V120Q160 96 80 70"/><path className={lit('right')} d="M160 176V120Q160 96 240 70"/>
  <path className="s-ink" d="M160 140v-50"/><path className="f-cream s-ink" d="M156 92h-44l-8 8 8 8h44zM164 92h44l8 8-8 8h-44z"/>
  <text className="mono f-ink" x="132" y="104" fontSize="11" textAnchor="middle">left</text><text className="mono f-ink" x="188" y="104" fontSize="11" textAnchor="middle">right</text>
  {choice&&[0,1,2,3].map(i=>{const t=(i+1)/5,x=choice==='left'?160-80*t:160+80*t,y=124-50*t;return <circle key={i} className={'f-ink pop '+d(1+i)} cx={x} cy={y} r={3/s}/>;})}
  {choice&&end&&!small&&<g className={'pop '+d(6)}><rect className="f-white s-ink" x={choice==='left'?8:162} y="10" width="150" height="46" rx="8"/>{wrap(end,21,2).map((l,i)=><text key={i} className="mono f-ink" x={choice==='left'?83:237} y={30+i*15} fontSize="11" textAnchor="middle">{l}</text>)}</g>}
 </g>;
}
const sideOf=(reply:string|undefined):'left'|'right'|null=>reply==='left'?'left':reply==='right'?'right':null;
const choices:SceneDef={title:'The fork in the road',draw:r=>{
 const choice=sideOf(r?.inputs[0]),end=outLines(r)[0]??'';
 return {say:r?choice?`The player goes ${choice}: ${end||'nothing is printed'}.`:`The reply ${JSON.stringify(r.inputs[0]??'')} is neither left nor right, so neither path lights up${end?`; the program printed: ${end}`:''}.`:'A path that splits left and right.',svg:<>
  <Ground/><Fork choice={choice} end={end}/>{!r&&<Note text={IDLE}/>}
 </>};
}};

const adventure:SceneDef={title:'Your storyboard',draw:r=>{
 const lines=outLines(r),name=r?.inputs[0]??'',choice=sideOf(r?.inputs[1]),panels=[lines[0]??'',lines[1]??'',lines.slice(2).join(' ')];
 return {say:lines.length?`Three panels: ${panels.filter(Boolean).join(' / ')}`:'Three empty panels for the opening, the welcome and the ending.',svg:<>
  <Ground tone="sand"/>
  {[0,1,2].map(i=><g key={i} className={lines.length?'pop '+d(i*3):undefined}>
   <rect className="f-white s-ink" x={12+i*102} y="14" width="94" height="132" rx="8"/>
   {i===0&&<><path className="f-moss-l s-ink-s" d="M22 132q20-30 38-6t36-8v18H22z"/><circle className="f-amber" cx="84" cy="96" r="8"/></>}
   {i===1&&<><Hero x={159} y={140} className={name?'pop '+d(4):undefined}/>{name&&<Tag x={159} y={68} text={fit(name,10)} tone="clay" className={'drop '+d(5)}/>}</>}
   {i===2&&<><path className={choice==='left'?'s-cream-w path-lit':'s-cream-w path-dim'} d="M261 144v-24l-26-22"/><path className={choice==='right'?'s-cream-w path-lit':'s-cream-w path-dim'} d="M261 144v-24l26-22"/></>}
   {wrap(panels[i],15,3).map((l,j)=><text key={j} className="mono f-ink" x={20+i*102} y={32+j*13} fontSize="10">{l}</text>)}
  </g>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

// ---------- Unit 2 ----------
const arithmetic:SceneDef={title:'Sharing the chest',draw:r=>{
 const nums=numbers(outLines(r)),coins=numOf(pick(r?.vars,['coins','chest','gold']))??toNum(r?.inputs[0]),friendsVar=numOf(pick(r?.vars,['friends','people','party']))??toNum(r?.inputs[1]);
 const [each,left]=nums.slice(-2),friends=friendsVar??(each!==undefined&&left!==undefined&&coins!==null&&each>0?Math.round((coins-left)/each):null);
 const ok=each!==undefined&&left!==undefined&&friends!==null&&friends>0;
 const shown=ok?clamp(friends,1,6):0;
 return {say:ok?`${coins??'The'} coins shared: ${plural(friends,'friend')} get ${each} each, and ${left} ${left===1?'stays':'stay'} in the chest.`:r?'The scene needs two numbers printed last: coins each and coins left over.':'A chest of coins and some empty pouches.',svg:<>
  <Ground tone="sand"/>
  <path className="f-amber-l s-ink" d="M126 104h68v40h-68z"/><path className="f-clay s-ink" d="M122 92h76v14h-76z"/>
  {ok&&Array.from({length:clamp(left,0,8)},(_,i)=><Coin key={i} x={136+(i%4)*15} y={120+Math.floor(i/4)*12} className={'pop '+d(8+i/2)}/>)}
  {ok&&left>8&&<text className="mono f-ink" x="160" y="162" fontSize="11" textAnchor="middle">+{left-8}</text>}
  {Array.from({length:shown||5},(_,i)=>{const x=shown?20+i*(280/(shown))+(280/shown-40)/2:24+i*58,y=24;return <g key={i}>
   <path className={(shown?'f-plum':'f-white')+' s-ink'} d={`M${x+10} ${y+8}q-14 16-12 32q2 16 22 16t22-16q2-16-12-32z`}/><path className="s-ink" d={`M${x+8} ${y+10}q12 6 24 0`}/><path className="s-ink-s" d={`M${x+14} ${y+8}l-4-8M${x+26} ${y+8}l4-8`}/>
   {ok&&Array.from({length:clamp(each,0,4)},(_,j)=><Coin key={j} x={x+12+(j%2)*16} y={y+30+Math.floor(j/2)*13} className={'drop '+d(1+i+j)}/>)}
   {ok&&each>4&&<text className="mono f-white" x={x+20} y={y+66} fontSize="10" textAnchor="middle">{each}</text>}
  </g>;})}
  {ok&&friends>6&&<text className="mono f-ink" x="300" y="100" fontSize="11" textAnchor="end">and {friends-6} more</text>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const intFloat:SceneDef={title:'On the number line',draw:r=>{
 const lines=outLines(r).filter(isNum).slice(0,6),vals=lines.map(Number);
 const lo=Math.floor(Math.min(0,...vals)),hi=Math.ceil(Math.max(1,...vals)),span=hi-lo||1,X=(v:number)=>24+(v-lo)/span*272;
 return {say:vals.length?`The number line marks ${lines.map(l=>`${l} (${l.includes('.')||/e/i.test(l)?'float':'int'})`).join(', ')}.`:'A number line, waiting for numbers.',svg:<>
  <Ground tone="slate"/>
  <path className="s-ink" d="M18 110h284"/>
  {Array.from({length:Math.min(span,20)+1},(_,i)=>{const v=lo+i*Math.max(1,Math.ceil(span/20));return v<=hi&&<g key={i}><path className="s-ink-s" d={`M${X(v)} 104v12`}/><text className="mono f-ink" x={X(v)} y="132" fontSize="10" textAnchor="middle">{v}</text></g>;})}
  {lines.map((l,i)=>{const isF=l.includes('.')||/e/i.test(l),x=X(vals[i]);return <g key={i} className={'drop '+d(i*2)}>
   <path className={isF?'f-slate s-ink-s':'f-moss s-ink-s'} d={`M${x} 104l-7-12h14z`}/>
   <rect className={(isF?'f-white':'f-cream')+' s-ink-s'} x={x-26} y={34+(i%3)*18} width="52" height="16" rx="4"/>
   <text className="mono f-ink" x={x} y={46+(i%3)*18} fontSize="11" textAnchor="middle">{fit(l,7)}</text>
   <path className="s-ink-s" d={`M${x} ${50+(i%3)*18}V90`}/>
  </g>;})}
  <text className="mono f-moss" x="24" y="160" fontSize="11">▲ int</text><text className="mono f-slate" x="90" y="160" fontSize="11">▲ float</text>
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const convertInput:SceneDef={title:'The converter',draw:r=>{
 const replies=(r?.inputs??[]).slice(0,3),out=outLines(r).slice(0,3);
 return {say:r?`Replies ${replies.map(x=>JSON.stringify(x)).join(' and ')||'(none)'} go in as text; the program printed ${out.join(' and ')||'nothing'}.`:'A funnel that turns text into numbers.',svg:<>
  <Ground/>
  {replies.map((t,i)=><g key={i} className={'slide '+d(i*2)}><rect className="f-white s-ink-s" x={14} y={20+i*30} width="74" height="22" rx="6"/><text className="mono f-clay" x={51} y={35+i*30} fontSize="12" textAnchor="middle">{fit(JSON.stringify(t),9)}</text></g>)}
  <path className="f-cream s-ink" d="M110 30h70l-22 44v30h-26V74z"/><text className="mono f-ink" x="145" y="56" fontSize="13" textAnchor="middle">int()</text>
  <path className="s-moss" d="M90 40q10 0 18 4M145 108v12"/>
  <rect className="f-ink" x="196" y="22" width="110" height={Math.max(36,out.length*30+14)} rx="10"/>
  {out.map((t,i)=><text key={i} className={'mono f-amber-l type '+d(5+i*2)} x="251" y={48+i*30} fontSize="20" textAnchor="middle">{fit(t,9)}</text>)}
  <text className="mono f-ink" x="251" y={Math.max(36,out.length*30+14)+38} fontSize="10" textAnchor="middle">printed</text>
  {!r&&<Note text={IDLE}/>}
 </>};
}};

function balance(a:number|null,b:number|null,la:string,lb:string){
 const tilt=a===null||b===null?0:a>b?-8:a<b?8:0;
 return <g>
  <path className="s-ink-w" d="M160 150V60"/><path className="f-ink" d="M140 150h40l-20-10z"/>
  <g transform={`rotate(${-tilt} 160 60)`} className="tilt">
   <path className="s-ink" d="M90 60h140"/><path className="s-ink-s" d="M90 60l-16 30M90 60l16 30M230 60l-16 30M230 60l16 30"/>
   <path className="f-cream s-ink" d="M70 90h40q0 12-20 12t-20-12zM210 90h40q0 12-20 12t-20-12z"/>
   <text className="mono f-ink" x="90" y="84" fontSize="12" textAnchor="middle">{a??'?'}</text><text className="mono f-ink" x="230" y="84" fontSize="12" textAnchor="middle">{b??'?'}</text>
  </g>
  <text className="mono f-ink" x="90" y="124" fontSize="10" textAnchor="middle">{la}</text><text className="mono f-ink" x="230" y="124" fontSize="10" textAnchor="middle">{lb}</text>
 </g>;
}
const LAMP_LABELS:Record<string,string[]>={'py.compare':['too high','too low','right'],'py.boolean-logic':['close','out','not close']};
function lamps(lesson:string,r:SceneRun|null){
 const lines=outLines(r).slice(0,4),bs=bools(lines),labels=r?.inputs.length?LAMP_LABELS[lesson]??[]:[];
 return lines.map((l,i)=><Lamp key={i} x={30+i*58} y={22} on={bs[i]} label={labels[i]??fit(l,8)} className={'pop '+d(4+i*2)}/>);
}
const compare:SceneDef={title:'The balance',draw:r=>{
 const [a,b]=r?.inputs.length?[toNum(r.inputs[0]),toNum(r.inputs[1])]:[numOf(Object.values(r?.vars??{})[0]),null],lines=outLines(r);
 return {say:r?`${a!==null&&b!==null?`Secret ${a} and guess ${b} on the balance. `:''}The lamps show ${lines.join(', ')||'nothing'}.`:'A balance and three lamps, one for each True or False.',svg:<>
  <Ground tone="slate"/>
  {b!==null||!r?<g transform="translate(-10 40) scale(.75)">{balance(a,b,'secret','guess')}</g>
   :<g className="pop"><rect className="f-white s-ink" x="40" y="50" width="34" height="100" rx="6"/><rect className="f-amber" x="44" y={146-clamp((a??0)*9,0,92)} width="26" height={clamp((a??0)*9,0,92)} rx="3"/><text className="mono f-ink" x="57" y="40" fontSize="12" textAnchor="middle">{Object.keys(r?.vars??{})[0]??''} = {a??'?'}</text></g>}
  <g transform="translate(130 20)">{lamps('py.compare',r)}</g>
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const booleanLogic:SceneDef={title:'Close enough?',draw:r=>{
 const secret=toNum(r?.inputs[0]),guess=toNum(r?.inputs[1]),X=(v:number)=>20+clamp(v,-5,110)/105*280;
 const only=!r?.inputs.length?ofKind(r?.vars,['int','float'])[0]:undefined;
 if(only){const [name,node]=only,v=numOf(node)??0,hi=Math.max(10,Math.ceil(v)+3),Y=(n:number)=>24+clamp(n,0,hi)/hi*272;
  return {say:`${name} is ${v}. The lamps show ${outLines(r).join(', ')||'nothing'}.`,svg:<><Ground tone="slate"/><g transform="translate(40 0)">{lamps('py.boolean-logic',r)}</g>
   <path className="s-ink" d={`M24 130H296`}/>{Array.from({length:hi+1},(_,i)=><g key={i}><path className="s-ink-s" d={`M${Y(i)} 125v10`}/><text className="mono f-ink" x={Y(i)} y="150" fontSize="9" textAnchor="middle">{i}</text></g>)}
   <path className={'f-clay s-ink-s drop '+d(1)} d={`M${Y(v)} 124l-6-12h12z`}/><text className="mono f-clay" x={Y(v)} y="106" fontSize="11" textAnchor="middle">{name}</text></>};}
 return {say:r?`${secret!==null&&guess!==null?`On the line from 1 to 100, the guess ${guess} sits ${Math.abs(guess-secret)} away from the secret ${secret}. `:''}The lamps show ${outLines(r).join(', ')||'nothing'}.`:'Lamps for and, or and not, and a line from 1 to 100.',svg:<>
  <Ground tone="slate"/>
  <g transform="translate(40 0)">{lamps('py.boolean-logic',r)}</g>
  <path className="s-ink" d={`M${X(1)} 130H${X(100)}`}/><path className="s-ink-s" d={`M${X(1)} 124v12M${X(100)} 124v12`}/>
  <text className="mono f-ink" x={X(1)} y="152" fontSize="10" textAnchor="middle">1</text><text className="mono f-ink" x={X(100)} y="152" fontSize="10" textAnchor="middle">100</text>
  {secret!==null&&<><rect className="f-amber-l" x={X(secret-2)} y="122" width={Math.max(6,X(secret+2)-X(secret-2))} height="16" rx="3"/><path className={'f-moss s-ink-s drop '+d(1)} d={`M${X(secret)} 122l-6-10h12z`}/><text className="mono f-moss" x={X(secret)} y="106" fontSize="10" textAnchor="middle">secret</text></>}
  {guess!==null&&<><path className={'f-clay s-ink-s drop '+d(3)} d={`M${X(guess)} 138l-6 10h12z`}/><text className="mono f-clay" x={X(guess)} y="164" fontSize="10" textAnchor="middle">guess</text></>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const elif:SceneDef={title:'The verdict',draw:r=>{
 const last=outLines(r).at(-1),pts=toNum(last),rings=[[0,62],[1,46],[5,30],[10,14]] as const;
 const secret=toNum(r?.inputs[0]),guess=toNum(r?.inputs[1]),hit=pts!==null&&[0,1,5,10].includes(pts);
 return {say:r?hit?`The dart lands in the ${pts}-point ring${secret!==null&&guess!==null?`: the guess is ${Math.abs(guess-secret)} away`:''}.`:`Only one branch ran, and it printed: ${last??'nothing'}.`:'A target with rings for 10, 5, 1 and 0 points.',svg:<>
  <Ground tone="sand"/>
  {(!r||hit)?<g>
   {rings.map(([p,rad])=><circle key={p} className={(hit&&p===pts?'f-amber ring-hit':p===10?'f-clay':p===5?'f-cream':p===1?'f-white':'f-moss-l')+' s-ink'} cx="110" cy="92" r={rad}/>)}
   {rings.map(([p,rad])=><text key={p} className="mono f-ink" x={110} y={92-rad+11} fontSize="9" textAnchor="middle">{p}</text>)}
   {hit&&<path className={'s-ink-w dart '+d(2)} d={`M${110+[62,46,30,14][[0,1,5,10].indexOf(pts!)]*.6+40} ${92-30}l-30 ${24}`}/>}
   {hit&&<text className={'serif f-ink pop '+d(4)} x="250" y="100" fontSize="40" textAnchor="middle">{pts}</text>}
  </g>:<g className="pop"><path className="f-slate s-ink" d="M110 150V70a50 50 0 0 1 100 0v80z"/><path className="f-amber-l" d="M124 150V76a36 36 0 0 1 72 0v74z"/><Tag x={160} y={44} text={fit(last??'',24)} tone="moss"/></g>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

// ---------- Unit 3 ----------
const whileLoops:SceneDef={title:'The door that waits',draw:r=>{
 const replies=(r?.inputs??[]).slice(0,6),lines=outLines(r).slice(0,6),open=!!r&&!r.error;
 return {say:r?`${plural(replies.length,'reply','replies')} tried; ${plural(lines.length,'line')} printed; the loop ${open?'ended, so the door opens':'did not finish'}.`:'A door that stays shut until the loop ends.',svg:<>
  <Ground/>
  <path className="f-slate s-ink" d="M236 150V54a32 32 0 0 1 64 0v96z"/>
  <path className={(open?'f-amber-l door-open '+d(13):'f-cream')+' s-ink'} d="M244 150V58a24 24 0 0 1 48 0v92z"/>
  {replies.map((t,i)=><g key={i} className={'slide '+d(i*2)}><rect className="f-white s-ink-s" x="14" y={14+i*24} width="80" height="19" rx="5"/><text className="mono f-clay" x="20" y={28+i*24} fontSize="11">{fit(t,10)}</text></g>)}
  {lines.map((t,i)=><text key={i} className={'mono f-ink type '+d(i*2+1)} x="104" y={28+i*24} fontSize="11">{fit(t,16)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const loopTermination:SceneDef={title:'Candles for each try',draw:r=>{
 const lines=outLines(r),nums=lines.filter(isNum).slice(0,8),tail=lines.filter(l=>!isNum(l)).at(-1),open=tail==='True'||/open/i.test(tail??'');
 return {say:r?`${plural(nums.length,'candle')} burn down in turn${tail?`, and then: ${tail}`:''}.`:'A row of candles in front of a gate.',svg:<>
  <Ground tone="sand"/>
  <path className="f-slate s-ink" d="M224 150V50h80v100z"/><path className={(open?'f-amber-l door-open '+d(nums.length*2+1):'f-cream')+' s-ink'} d="M234 150V60h60v90z"/>
  {nums.map((n,i)=><g key={i} transform={`translate(${24+i*24} 0)`}>
   <rect className="f-white s-ink-s" x="0" y="100" width="14" height="46" rx="2"/>
   <path className={'f-amber flame out '+d(i*2+1)} d="M7 98q-6-8 0-16q6 8 0 16z"/>
   <text className="mono f-ink" x="7" y="166" fontSize="10" textAnchor="middle">{n}</text>
  </g>)}
  {tail&&<Tag x={264} y={34} text={fit(tail,12)} tone={open?'moss':'clay'} className={'drop '+d(nums.length*2)}/>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const forRange:SceneDef={title:'The staircase',draw:r=>{
 const nums=numbers(outLines(r)).slice(0,14),lo=Math.min(...nums,0),hi=Math.max(...nums,lo+4),count=clamp(hi-lo+1,5,16),step=(hi-lo+1)>16?Math.ceil((hi-lo+1)/16):1;
 const at=(v:number)=>{const k=Math.floor((v-lo)/step);return {x:16+k*(288/count),y:156-k*(120/count)};};
 return {say:nums.length?`The hero lands on ${nums.join(', ')}.`:'A staircase, waiting for numbers to land on.',svg:<>
  <Ground tone="slate"/>
  {Array.from({length:count},(_,k)=>{const x=16+k*(288/count),y=156-k*(120/count);return <g key={k}><path className="f-cream s-ink-s" d={`M${x} ${y}h${288/count}v${170-y}h-${288/count}z`}/><text className="mono f-ink" x={x+144/count} y={y+14} fontSize="9" textAnchor="middle">{lo+k*step}</text></g>;})}
  {nums.map((v,i)=>{const p=at(v);return <g key={i} className={'pop '+d(i)}><circle className="f-clay" cx={p.x+144/count} cy={p.y-6} r="5"/><text className="mono f-ink" x={p.x+144/count} y={p.y-14} fontSize="8" textAnchor="middle">{i+1}</text></g>;})}
  {nums.length>0&&<Hero x={at(nums.at(-1)!).x+144/count} y={at(nums.at(-1)!).y} className={'pop hero-small '+d(nums.length)}/>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const accumulate:SceneDef={title:'The tally',draw:r=>{
 const replies=(r?.inputs??[]).filter(isNum).map(Number),out=numbers(outLines(r)),total=out[0];
 let parts=replies;if(total!==undefined&&replies.length>1&&replies.slice(1).reduce((a,b)=>a+b,0)===total)parts=replies.slice(1);
 parts=parts.slice(0,10);const top=Math.max(1,total??0,...parts),H=(v:number)=>clamp(v/top*110,0,110);
 return {say:r?`${parts.length?`Bars for ${parts.join(', ')}`:'No numbers were read'}${total!==undefined?`, adding up to ${total}`:''}.`:'Empty bars and a total waiting to grow.',svg:<>
  <Ground/>
  <path className="s-ink" d="M14 146h292"/>
  {parts.map((v,i)=><g key={i} className={'grow '+d(i)}><rect className={(v===0?'f-white':'f-moss')+' s-ink-s'} x={20+i*22} y={146-Math.max(3,H(v))} width="16" height={Math.max(3,H(v))}/><text className="mono f-ink" x={28+i*22} y="160" fontSize="9" textAnchor="middle">{v}</text></g>)}
  {total!==undefined&&<g className={'grow '+d(parts.length+1)}><rect className="f-amber s-ink" x="250" y={146-H(total)} width="40" height={H(total)}/><text className="mono f-ink" x="270" y={140-H(total)} fontSize="14" textAnchor="middle">{total}</text><text className="mono f-ink" x="270" y="160" fontSize="9" textAnchor="middle">total</text></g>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const nestedLoops:SceneDef={title:'Rooms on the map',draw:r=>{
 const lines=outLines(r),nums=numbers(lines);let cells=nums,total:number|undefined;
 if(nums.length>2&&nums.slice(0,-1).reduce((a,b)=>a+b,0)===nums.at(-1)){total=nums.at(-1);cells=nums.slice(0,-1);}
 let cols=toNum(r?.inputs[1])??numOf(pick(r?.vars,['columns','cols','seats']));
 if(!cols){const tens=cells.map(n=>Math.floor(n/10));const k=tens.findIndex(t=>t!==tens[0]);cols=k>0&&cells.every(n=>n>=10)?k:Math.ceil(Math.sqrt(cells.length))||1;}
 cols=clamp(cols,1,8);const shown=cells.slice(0,cols*5),rows=Math.ceil(shown.length/cols)||1,w=Math.min(36,220/cols),h=Math.min(28,130/rows);
 return {say:cells.length?`${plural(cells.length,'room')} light up row by row: ${cells.slice(0,12).join(', ')}${total!==undefined?`; total ${total}`:''}.`:'An empty grid of rooms.',svg:<>
  <Ground tone="sand"/>
  {shown.length===0&&Array.from({length:6},(_,i)=><rect key={i} className="f-white s-ink-s" x={30+(i%3)*40} y={30+Math.floor(i/3)*34} width="36" height="30" rx="4"/>)}
  {shown.map((v,i)=><g key={i} className={'pop '+d(i*.7)}><rect className="f-cream s-ink-s" x={20+(i%cols)*(w+4)} y={18+Math.floor(i/cols)*(h+4)} width={w} height={h} rx="4"/><text className="mono f-ink" x={20+(i%cols)*(w+4)+w/2} y={18+Math.floor(i/cols)*(h+4)+h/2+4} fontSize="11" textAnchor="middle">{v}</text></g>)}
  {total!==undefined&&<g className={'pop '+d(15)}><circle className="f-amber s-ink" cx="270" cy="80" r="30"/><text className="mono f-ink" x="270" y="85" fontSize="15" textAnchor="middle">{total}</text><text className="mono f-ink" x="270" y="128" fontSize="10" textAnchor="middle">total</text></g>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

/** Lesson id → its scene. */
export const SCENES:Record<string,SceneDef>={
 hello,variables,input,choices,adventure,
 'py.arithmetic':arithmetic,'py.int-float':intFloat,'py.convert-input':convertInput,'py.compare':compare,'py.boolean-logic':booleanLogic,'py.elif':elif,
 'py.while-loops':whileLoops,'py.loop-termination':loopTermination,'py.for-range':forRange,'py.accumulate':accumulate,'py.nested-loops':nestedLoops,
 ...UNIT_4_TO_6,...UNIT_7_TO_11,
};

/** The scene for a lesson, drawn from a run (or empty, before one). Lessons without a scene show nothing. */
export default function LessonScene({lesson,run,action}:{lesson:string;run:SceneRun|null;action?:ReactNode}){
 const def=SCENES[lesson];
 if(!def)return null;
 let drawn:Drawn;
 try{drawn=def.draw(run);}catch{drawn={svg:<><Ground/><Note text="This run can't be drawn. The output above is what happened."/></>,say:'This run could not be drawn.'};}
 return <figure className="scene" aria-labelledby={`scene-${lesson}-title`}>
  <div className="scene-head"><span id={`scene-${lesson}-title`} className="scene-title">{def.title}</span>{run?.label&&<span className="scene-label">{run.label}</span>}{action}</div>
  <svg key={run?.key??'idle'} className={'scene-art'+(run?' live':'')} viewBox="0 0 320 180" role="img" aria-label={drawn.say}>{drawn.svg}</svg>
  <figcaption className="scene-say">{drawn.say}{run?.error?` Python stopped with ${run.error}, so this shows what happened before that.`:''}</figcaption>
 </figure>;
}

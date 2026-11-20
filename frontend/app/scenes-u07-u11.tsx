// Lesson scenes for Python units 7 to 11. The kit is scene-kit.tsx; how scenes work is lesson-scenes.tsx.
import type {SceneDef} from './lesson-scenes';
import {type SceneRun,Ground,Hero,Item,Lamp,Note,Tag,bools,clamp,d,fit,isNum,listItems,numOf,ofKind,outLines,parseRepr,pick,plural,show,strOf,toNum,wrap} from './scene-kit';
import {functionsIn} from './scenes-u04-u06';

const IDLE='Run the code to fill this scene.';
/** Modules a program imports, read from its text: import a, from b import c, import d as e. */
function importsIn(code:string|undefined):{module:string;names:string[]}[]{
 if(!code)return [];
 const out:{module:string;names:string[]}[]=[];
 for(const line of code.split('\n')){
  let m=/^\s*import\s+([\w.]+)(?:\s+as\s+(\w+))?/.exec(line);if(m){out.push({module:m[1],names:m[2]?[`as ${m[2]}`]:[]});continue;}
  m=/^\s*from\s+([\w.]+)\s+import\s+(.+)$/.exec(line);if(m)out.push({module:m[1],names:m[2].split(',').map(x=>x.trim()).filter(Boolean)});
 }
 const merged=new Map<string,string[]>();for(const i of out)merged.set(i.module,[...(merged.get(i.module)??[]),...i.names]);
 return [...merged].map(([module,names])=>({module,names}));
}

// ---------- Unit 7 ----------
const importScene:SceneDef={title:'The toolbox',draw:r=>{
 const imports=importsIn(r?.code).slice(0,4),lines=outLines(r).slice(0,4);
 return {say:r?`${imports.length?`Tools borrowed: ${imports.map(i=>i.names.length?`${i.module} (${i.names.join(', ')})`:i.module).join('; ')}. `:'Nothing imported. '}${lines.length?`Printed: ${lines.join(', ')}.`:''}`:'A pegboard of tools, waiting to be borrowed with import.',svg:<>
  <Ground tone="sand"/>
  <rect className="f-cream s-ink" x="12" y="12" width="190" height="138" rx="8"/>
  {Array.from({length:24},(_,i)=><circle key={i} className="f-ink" cx={26+(i%8)*23} cy={24+Math.floor(i/8)*46} r="1.6"/>)}
  {imports.map((imp,i)=><g key={imp.module+i} className={'drop '+d(i*2)}>
   <rect className="f-slate s-ink-s" x={22+(i%2)*90} y={34+Math.floor(i/2)*58} width="80" height="24" rx="5"/><text className="mono f-white" x={62+(i%2)*90} y={50+Math.floor(i/2)*58} fontSize="11" textAnchor="middle">{fit(imp.module,10)}</text>
   {imp.names.slice(0,2).map((n,j)=><text key={n} className="mono f-ink" x={62+(i%2)*90} y={70+Math.floor(i/2)*58+j*11} fontSize="9" textAnchor="middle">{fit(n,12)}</text>)}
  </g>)}
  <rect className="f-ink" x="214" y="12" width="96" height="138" rx="6"/>
  {lines.map((l,i)=><text key={i} className={'mono f-amber-l type '+d(imports.length*2+i)} x="222" y={34+i*20} fontSize="11">{fit(l,11)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const PIPS:Record<number,[number,number][]>={1:[[0,0]],2:[[-1,-1],[1,1]],3:[[-1,-1],[0,0],[1,1]],4:[[-1,-1],[1,-1],[-1,1],[1,1]],5:[[-1,-1],[1,-1],[0,0],[-1,1],[1,1]],6:[[-1,-1],[1,-1],[-1,0],[1,0],[-1,1],[1,1]]};
function Die({x,y,value,className}:{x:number;y:number;value:string;className?:string}){
 const n=Number(value),pips=Number.isInteger(n)?PIPS[n]:undefined;
 return <g className={className}><rect className="f-white s-ink" x={x-17} y={y-17} width="34" height="34" rx="7"/>
  {pips?pips.map(([a,b],i)=><circle key={i} className="f-ink" cx={x+a*9} cy={y+b*9} r="3"/>):<text className="mono f-ink" x={x} y={y+5} fontSize="13" textAnchor="middle">{fit(value,4)}</text>}</g>;
}
const randomScene:SceneDef={title:"The riddle keeper's dice",draw:r=>{
 const lines=outLines(r),nums=lines.filter(isNum),rolls=nums.length>1?nums.slice(0,-1):nums,total=nums.length>1?nums.at(-1):undefined,others=lines.filter(l=>!isNum(l)).slice(0,3);
 return {say:r?`${rolls.length?`Rolled ${rolls.join(', ')}`:'No rolls'}${total!==undefined?`, total ${total}`:''}.${others.length?` Also printed: ${others.join(' / ')}.`:''}`:'Dice, waiting to be rolled.',svg:<>
  <Ground tone="slate"/>
  <path className="f-moss s-ink" d="M14 120h292v34H14z"/>
  {rolls.slice(0,8).map((v,i)=><Die key={i} x={36+i*36} y={92} value={v} className={'drop '+d(i)}/>)}
  {total!==undefined&&<Tag x={270} y={30} text={`total ${fit(total,6)}`} tone="clay" className={'pop '+d(rolls.length+1)}/>}
  {others.map((l,i)=><text key={i} className={'mono f-ink type '+d(i)} x="20" y={28+i*16} fontSize="10">{fit(l,30)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const mathScene:SceneDef={title:'As the crow flies',draw:r=>{
 const e=toNum(r?.inputs[0])??numOf(pick(r?.vars,['east','a','x'])),n=toNum(r?.inputs[1])??numOf(pick(r?.vars,['north','b','y'])),lines=outLines(r).slice(0,5);
 const has=e!==null&&n!==null,size=has?Math.max(e!,n!,1):1,u=Math.min(24,120/size),ox=24,oy=150;
 return {say:r?has?`${e} east and ${n} north. The straight line is shorter than the walk along the grid. Printed: ${lines.join(', ')}.`:`Printed: ${lines.join(', ')||'nothing'}.`:'A map grid, with a straight path and a grid path to the treasure.',svg:<>
  <Ground tone="sand"/>
  {has&&<>{Array.from({length:Math.min(size,12)+1},(_,i)=><g key={i}><path className="s-ink-s scene-grid" d={`M${ox+i*u} ${oy}V${oy-Math.min(size,12)*u}`}/><path className="s-ink-s scene-grid" d={`M${ox} ${oy-i*u}H${ox+Math.min(size,12)*u}`}/></g>)}
   <path className={'s-clay-w drop '+d(1)} d={`M${ox} ${oy}h${e!*u}v${-n!*u}`}/><path className={'s-moss-w drop '+d(3)} d={`M${ox} ${oy}L${ox+e!*u} ${oy-n!*u}`}/>
   <Item x={ox+e!*u} y={oy-n!*u+6} name="treasure" className={'pop '+d(4)}/><Hero x={ox} y={oy} className="hero-small"/></>}
  <rect className="f-white s-ink" x="196" y="16" width="112" height={Math.max(30,lines.length*20+12)} rx="6"/>
  {lines.map((l,i)=><text key={i} className={'mono f-ink type '+d(5+i)} x="206" y={36+i*20} fontSize="11">{fit(l,14)}</text>)}
  {has&&<><text className="mono f-moss" x="200" y="150" fontSize="9">straight line</text><text className="mono f-clay" x="200" y="164" fontSize="9">along the grid</text></>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const DATE=/^(\d{4})-(\d{2})-(\d{2})/;
const datetimeScene:SceneDef={title:'The calendar',draw:r=>{
 const lines=outLines(r),dates=lines.map(l=>DATE.exec(l)).filter(Boolean).map(m=>new Date(Date.UTC(+m![1],+m![2]-1,+m![3])));
 const first=dates[0],month=first?new Date(Date.UTC(first.getUTCFullYear(),first.getUTCMonth(),1)):null;
 const days=month?new Date(Date.UTC(month.getUTCFullYear(),month.getUTCMonth()+1,0)).getUTCDate():0,offset=month?(month.getUTCDay()+6)%7:0;
 const marked=new Set(dates.filter(x=>month&&x.getUTCMonth()===month.getUTCMonth()&&x.getUTCFullYear()===month.getUTCFullYear()).map(x=>x.getUTCDate()));
 const later=dates.length-marked.size,name=month?month.toLocaleString('en',{month:'long',year:'numeric',timeZone:'UTC'}):'';
 return {say:dates.length?`${name}: ${plural(marked.size,'date')} marked${later?`, and ${later} in a later month`:''}. Weekend columns are shaded.`:r?`Printed: ${lines.slice(0,4).join(', ')||'nothing'}.`:'A calendar page, waiting for dates.',svg:<>
  <Ground/>
  <rect className="f-white s-ink" x="16" y="10" width="218" height="150" rx="8"/>
  <text className="serif f-ink" x="26" y="28" fontSize="12">{name||'calendar'}</text>
  <rect className="f-amber-l" x={26+5*29} y="34" width="58" height="122" rx="4"/>
  {['M','T','W','T','F','S','S'].map((x,i)=><text key={i} className="mono f-ink" x={40+i*29} y="46" fontSize="9" textAnchor="middle">{x}</text>)}
  {Array.from({length:days},(_,i)=>{const k=i+offset,x=40+(k%7)*29,y=64+Math.floor(k/7)*18,on=marked.has(i+1);return <g key={i}>{on&&<circle className={'f-clay pop '+d(i/3)} cx={x} cy={y-4} r="8"/>}<text className={'mono '+(on?'f-white':'f-ink')} x={x} y={y} fontSize="9" textAnchor="middle">{i+1}</text></g>;})}
  {lines.filter(l=>!DATE.test(l)).slice(0,3).map((l,i)=><text key={i} className={'mono f-ink type '+d(8+i)} x="244" y={40+i*18} fontSize="10">{fit(l,9)}</text>)}
  {later>0&&<text className="mono f-ink" x="244" y="150" fontSize="9">+{later} later</text>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const ownModules:SceneDef={title:'Two files',draw:r=>{
 const imports=importsIn(r?.code).filter(i=>!['math','random','datetime','json','csv','re'].includes(i.module.split('.')[0])),main=functionsIn(r?.code),lines=outLines(r).slice(0,4);
 const mod=imports[0];
 return {say:r?`main.py ${mod?`imports ${mod.module}${mod.names.length?` for ${mod.names.join(', ')}`:''}`:'imports no file of its own'}${main.length?` and defines ${main.map(f=>f.name).join(', ')}`:''}. Printed: ${lines.join(', ')||'nothing'}.`:'Two files: the program, and the helper it imports.',svg:<>
  <Ground tone="slate"/>
  <path className="f-white s-ink" d="M18 20h96l18 18v110H18z"/><text className="mono f-ink" x="28" y="38" fontSize="11">main.py</text>
  {lines.map((l,i)=><text key={i} className={'mono f-clay type '+d(3+i)} x="28" y={64+i*16} fontSize="9">{fit(l,16)}</text>)}
  <path className="f-cream s-ink" d="M188 20h96l18 18v110H188z"/><text className="mono f-ink" x="198" y="38" fontSize="11">{fit(mod?`${mod.module}.py`:'helper.py',14)}</text>
  {(mod?.names.length?mod.names:['…']).slice(0,4).map((n,i)=><text key={n} className="mono f-plum" x="198" y={64+i*16} fontSize="10">def {fit(n,10)}</text>)}
  {mod&&<path className={'s-moss-w drop '+d(1)} d="M186 80h-48l8-8m-8 8l8 8"/>}
  {mod&&<text className="mono f-moss" x="162" y="104" fontSize="9" textAnchor="middle">import</text>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

export const UNIT_7_TO_11:Record<string,SceneDef>={
 'py.import':importScene,'py.random':randomScene,'py.math-module':mathScene,'py.datetime':datetimeScene,'py.own-modules':ownModules,
};
void bools;void clamp;void Lamp;void listItems;void parseRepr;void show;void strOf;void wrap;void ofKind;

// ---------- Unit 8 ----------
type AssertLine={line:number;text:string;call:string;expected:string};
/** Every assert in the program, with its line number, split at == into the call and what it expects. */
function assertsIn(code:string|undefined):AssertLine[]{
 if(!code)return [];
 return code.split('\n').map((l,i)=>({l:l.trim(),line:i+1})).filter(x=>x.l.startsWith('assert ')).map(({l,line})=>{const body=l.slice(7).split(/,\s*(?=["'(\w]+[^=]*$)/)[0];const [call,expected]=body.split(/\s*==\s*/);return {line,text:body,call:call??body,expected:expected??''};});
}
type Verdict='passed'|'failed'|'not run';
function verdicts(r:SceneRun|null,asserts:AssertLine[]):Verdict[]{
 if(!r)return asserts.map(()=>'not run');
 const at=r.error==='AssertionError'?r.errorLine??null:null,stoppedOther=!!r.error&&r.error!=='AssertionError';
 return asserts.map(a=>at!==null?(a.line<at?'passed':a.line===at?'failed':'not run'):stoppedOther?(r.errorLine&&a.line<r.errorLine?'passed':'not run'):'passed');
}
const MARK:Record<Verdict,string>={passed:'✓',failed:'✗','not run':'·'};
const assertTests:SceneDef={title:'The test report',draw:r=>{
 const asserts=assertsIn(r?.code).slice(0,7),v=verdicts(r,asserts),lines=outLines(r).slice(0,2);
 const failed=v.indexOf('failed');
 return {say:r?asserts.length?`${v.filter(x=>x==='passed').length} of ${asserts.length} tests passed${failed>=0?`; the test on line ${asserts[failed].line} failed, so the ones after it did not run`:''}.${lines.length?` Printed: ${lines.join(', ')}.`:''}`:'No assert lines yet.':'A report card that ticks off each assert.',svg:<>
  <Ground tone="sand"/>
  <rect className="f-white s-ink" x="14" y="10" width="292" height="150" rx="8"/>
  {asserts.map((a,i)=><g key={i} className={'slide '+d(i)}>
   <text className={'mono '+(v[i]==='failed'?'f-clay':v[i]==='passed'?'f-moss':'f-ink scene-faint')} x="26" y={32+i*19} fontSize="13" fontWeight="700">{MARK[v[i]]}</text>
   <text className={'mono '+(v[i]==='not run'?'f-ink scene-faint':'f-ink')} x="44" y={32+i*19} fontSize="10">{fit(a.text,38)}</text>
  </g>)}
  {r&&!asserts.length&&<text className="mono f-ink" x="160" y="86" fontSize="11" textAnchor="middle">no assert lines yet</text>}
  {r?.label&&<text className="mono f-ink" x="300" y="154" fontSize="9" textAnchor="end">{fit(r.label,40)}</text>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

function kindOf(a:AssertLine):string{
 const arg=/\((.*)\)/.exec(a.call)?.[1]??'';
 if(/\[\s*\]|\(\s*\)|""|''/.test(arg))return 'empty';
 if(/-\d/.test(arg))return 'negative';
 if(/^\[[^,]*\]$/.test(arg.trim()))return 'single';
 if(/\./.test(a.expected))return 'decimal';
 if(/^0$|\b0\b/.test(arg))return 'zero';
 return 'typical';
}
const testCases:SceneDef={title:'The case table',draw:r=>{
 const asserts=assertsIn(r?.code).slice(0,6),v=verdicts(r,asserts),kinds=asserts.map(kindOf),covered=new Set(kinds);
 return {say:r?asserts.length?`Cases: ${asserts.map((a,i)=>`${a.call} (${kinds[i]})`).join(', ')}. Kinds covered: ${[...covered].join(', ')}.`:'No assert lines yet.':'A table of test cases, each sorted by the kind of case it is.',svg:<>
  <Ground/>
  <rect className="f-white s-ink" x="10" y="10" width="300" height="150" rx="8"/><path className="s-ink-s" d="M10 30h300M180 10v150M250 10v150"/>
  <text className="mono f-ink" x="18" y="24" fontSize="9">call</text><text className="mono f-ink" x="188" y="24" fontSize="9">expects</text><text className="mono f-ink" x="258" y="24" fontSize="9">kind</text>
  {asserts.map((a,i)=><g key={i} className={'slide '+d(i)}>
   <text className={'mono '+(v[i]==='failed'?'f-clay':'f-ink')} x="18" y={48+i*19} fontSize="10">{MARK[v[i]]} {fit(a.call,24)}</text>
   <text className="mono f-ink" x="188" y={48+i*19} fontSize="10">{fit(a.expected,9)}</text>
   <rect className={(kinds[i]==='typical'?'f-cream':'f-amber-l')+' s-ink-s'} x="256" y={38+i*19} width="48" height="14" rx="4"/><text className="mono f-ink" x="280" y={48+i*19} fontSize="8" textAnchor="middle">{kinds[i]}</text>
  </g>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const boundaries:SceneDef={title:'Edges on the line',draw:r=>{
 const asserts=assertsIn(r?.code),v=verdicts(r,asserts),points=asserts.map((a,i)=>({n:Number(/\((-?\d+)/.exec(a.call)?.[1]),v:v[i],exp:a.expected})).filter(p=>Number.isFinite(p.n)).slice(0,14);
 const ns=points.map(p=>p.n),lo=ns.length?Math.min(...ns)-2:0,hi=ns.length?Math.max(...ns)+2:10,X=(n:number)=>20+(n-lo)/(hi-lo||1)*280;
 return {say:points.length?`Tested at ${points.map(p=>p.n).join(', ')}. Pairs of neighbouring numbers test both sides of an edge.`:r?'No numbers tested yet.':'A number line where each test is a pin.',svg:<>
  <Ground tone="slate"/>
  <path className="s-ink" d="M14 110H306"/>
  {points.map((p,i)=>{const pair=points.some(q=>Math.abs(q.n-p.n)===1);return <g key={i} className={'drop '+d(i)}>
   <path className={(p.v==='failed'?'f-clay':pair?'f-amber':'f-white')+' s-ink-s'} d={`M${X(p.n)} 108l-6-14h12z`}/><circle className={(p.v==='failed'?'f-clay':pair?'f-amber':'f-white')+' s-ink-s'} cx={X(p.n)} cy="88" r="6"/>
   <text className="mono f-ink" x={X(p.n)} y={i%2?134:148} fontSize="9" textAnchor="middle">{p.n}</text>
  </g>;})}
  <text className="mono f-ink" x="20" y="30" fontSize="9">gold pins: an edge tested from both sides</text>
  {!r&&<Note text={IDLE}/>}
 </>};
}};

type Sig={name:string;params:{name:string;hint:string}[];returns:string};
function signatures(code:string|undefined):Sig[]{
 if(!code)return [];
 return [...code.matchAll(/^def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?:/gm)].map(m=>({name:m[1],params:m[2].split(',').map(p=>p.trim()).filter(Boolean).map(p=>{const [n,h]=p.split(':');return {name:n.split('=')[0].trim(),hint:(h??'').split('=')[0].trim()};}),returns:(m[3]??'').trim()}));
}
const typeHints:SceneDef={title:'Labelled parcels',draw:r=>{
 const sig=signatures(r?.code)[0],lines=outLines(r).slice(0,2);
 return {say:sig?`${sig.name}() takes ${sig.params.map(p=>`${p.name}${p.hint?` labelled ${p.hint}`:' with no label'}`).join(', ')||'nothing'}${sig.returns?`, and is labelled to return ${sig.returns}`:', with no label on what it returns'}.`:r?'No function with a def line yet.':'Parcels going into a function, each with a label for its type.',svg:<>
  <Ground tone="sand"/>
  {sig&&<>
   {sig.params.slice(0,3).map((p,i)=><g key={p.name} className={'slide '+d(i)}><rect className="f-cream s-ink" x="14" y={22+i*40} width="80" height="30" rx="4"/><path className="s-ink-s" d={`M14 ${32+i*40}h80`}/><text className="mono f-ink" x="54" y={46+i*40} fontSize="10" textAnchor="middle">{fit(p.name,10)}</text>
    {p.hint?<Tag x={128} y={37+i*40} text={fit(p.hint,9)} tone="moss"/>:<text className="mono f-clay" x="110" y={41+i*40} fontSize="9">no label</text>}</g>)}
   <rect className="f-plum s-ink" x="166" y="40" width="70" height="80" rx="8"/><text className="mono f-white" x="201" y="84" fontSize="10" textAnchor="middle">{fit(sig.name,9)}</text>
   <path className="s-ink" d="M236 80h20"/>{sig.returns?<Tag x={282} y={80} text={fit(sig.returns,8)} tone="clay" className={'pop '+d(4)}/>:<text className="mono f-clay" x="262" y="84" fontSize="9">no label</text>}
  </>}
  {lines.map((l,i)=><text key={i} className={'mono f-ink type '+d(5+i)} x="14" y={150+i*12} fontSize="9">{fit(l,52)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const refactor:SceneDef={title:'Tidiness meter',draw:r=>{
 const code=(r?.code??'').split('\n').map(l=>l.trim()).filter(l=>l&&!l.startsWith('#')),counts=new Map<string,number>();
 code.forEach(l=>counts.set(l,(counts.get(l)??0)+1));
 const repeated=[...counts].filter(([l,n])=>n>1&&l.length>6).reduce((a,[,n])=>a+n,0),fns=signatures(r?.code).length,lines=outLines(r).slice(0,5);
 const bar=(v:number,max:number)=>clamp(v/max*120,2,120);
 return {say:r?`${code.length} lines of code, ${repeated} of them repeats, ${plural(fns,'function')}. Printed: ${lines.join(' / ')||'nothing'}.`:'Meters for the length of the code and how much of it repeats.',svg:<>
  <Ground/>
  {[['lines',code.length,60,'f-slate'],['repeats',repeated,20,'f-clay'],['functions',fns,5,'f-moss']].map(([label,v,max,tone],i)=><g key={label as string}>
   <text className="mono f-ink" x="16" y={34+i*36} fontSize="10">{label as string}</text>
   <rect className="f-white s-ink-s" x="86" y={22+i*36} width="122" height="16" rx="4"/><rect className={(tone as string)+' grow '+d(i)} x="87" y={23+i*36} width={bar(v as number,max as number)} height="14" rx="3"/>
   <text className="mono f-ink" x="216" y={34+i*36} fontSize="10">{v as number}</text></g>)}
  <rect className="f-ink" x="236" y="14" width="74" height="110" rx="6"/>
  {lines.map((l,i)=><text key={i} className={'mono f-amber-l type '+d(3+i)} x="242" y={32+i*18} fontSize="9">{fit(l,11)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};
Object.assign(UNIT_7_TO_11,{'py.assert-tests':assertTests,'py.test-cases':testCases,'py.boundaries':boundaries,'py.type-hints':typeHints,'py.refactor':refactor});

// ---------- Unit 9 ----------
const firstFile=(r:SceneRun|null):[string,string]|null=>{const e=Object.entries(r?.files??{});return e[0]??null;};
const writes=(code:string|undefined)=>[...(code??'').matchAll(/open\(\s*["']([^"']+)["']\s*,\s*["'](w|a)["']/g)].map(m=>m[1]);
const textFiles:SceneDef={title:'The notebook',draw:r=>{
 const file=firstFile(r),rows=file?file[1].split('\n'):[],shown=(rows.at(-1)===''?rows.slice(0,-1):rows).slice(0,8),out=outLines(r).slice(0,5),made=[...new Set(writes(r?.code))];
 return {say:file?`${file[0]} holds ${plural(shown.length,'line')}${shown.some(l=>!l.trim())?', some of them blank':''}. ${made.length?`The program writes ${made.join(', ')}. `:''}Printed: ${out.join(', ')||'nothing'}.`:r?`Printed: ${out.join(', ')||'nothing'}.`:'A notebook page for the file, and a new page for anything the program writes.',svg:<>
  <Ground tone="sand"/>
  <rect className="f-white s-ink" x="12" y="10" width="150" height="152" rx="6"/><text className="mono f-ink" x="22" y="26" fontSize="10">{fit(file?.[0]??'no file',20)}</text><path className="s-clay-w scene-faint" d="M32 32v126"/>
  {shown.map((l,i)=><g key={i} className={'type '+d(i)}><path className="s-moss-s scene-faint" d={`M14 ${46+i*15}h146`}/><text className={'mono '+(l.trim()?'f-ink':'f-clay')} x="38" y={43+i*15} fontSize="10">{l.trim()?fit(l,16):'(blank)'}</text></g>)}
  {made.slice(0,1).map(name=><g key={name} className={'pop '+d(shown.length+1)}><rect className="f-cream s-ink" x="176" y="14" width="132" height="44" rx="6"/><text className="mono f-ink" x="186" y="32" fontSize="10">new: {fit(name,12)}</text><text className="mono f-moss" x="186" y="48" fontSize="9">written by the program</text></g>)}
  <rect className="f-ink" x="176" y="66" width="132" height="96" rx="6"/>
  {out.map((l,i)=><text key={i} className={'mono f-amber-l type '+d(shown.length+2+i)} x="184" y={84+i*16} fontSize="10">{fit(l,17)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

function jsonOf(text:string|undefined):unknown{try{return text===undefined?undefined:JSON.parse(text);}catch{return undefined;}}
const jsonScene:SceneDef={title:'The save crystal',draw:r=>{
 const file=firstFile(r),before=jsonOf(file?.[1]) as Record<string,unknown>|undefined,afterLine=outLines(r).find(l=>l.trim().startsWith('{')),after=jsonOf(afterLine) as Record<string,unknown>|undefined;
 const keys=[...new Set([...Object.keys(before??{}),...Object.keys(after??{})])].slice(0,5),txt=(v:unknown)=>v===undefined?'—':JSON.stringify(v);
 return {say:before||after?`${before?'':'The saved text holds '}${keys.map(k=>{const a=txt(before?.[k]),b=txt(after?.[k]);return !before||a===b||!after?`${k}: ${after?b:a}`:`${k}: ${a} became ${b}`;}).join('; ')}.`:r?`Printed: ${outLines(r).slice(0,3).join(' / ')||'nothing'}.`:'A saved game, before and after the program changes it.',svg:<>
  <Ground tone="slate"/>
  <text className="mono f-ink" x="20" y="22" fontSize="10">{before?`${fit(file![0],14)} before`:after?'nothing saved before':'before'}</text><text className="mono f-ink" x="168" y="22" fontSize="10">{before?'after':'saved text'}</text>
  {keys.map((k,i)=>{const a=txt(before?.[k]),b=txt(after?.[k]),changed=!!after&&!!before&&a!==b;return <g key={k} className={'slide '+d(i)}>
   {before&&<><rect className="f-white s-ink-s" x="14" y={30+i*26} width="140" height="22" rx="4"/><text className="mono f-ink" x="20" y={45+i*26} fontSize="9">{fit(k,7)}: {fit(a,13)}</text></>}
   {after&&<><path className="s-ink-s" d={`M156 ${41+i*26}h8`}/><rect className={(changed?'f-amber-l':'f-white')+' s-ink-s'} x="166" y={30+i*26} width="140" height="22" rx="4"/><text className="mono f-ink" x="172" y={45+i*26} fontSize="9">{fit(k,7)}: {fit(b,13)}</text></>}
  </g>;})}
  {!before&&!after&&r&&outLines(r).slice(0,4).map((l,i)=><text key={i} className={'mono f-ink type '+d(i)} x="20" y={44+i*18} fontSize="10">{fit(l,44)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

/** Rows of a CSV text, with quoted values kept whole, as the csv module reads them. */
function csvRows(text:string):string[][]{
 const rows:string[][]=[];
 for(const line of text.split('\n').filter(l=>l.trim())){const row:string[]=[];let cur='',q=false;for(let i=0;i<line.length;i++){const c=line[i];if(c==='"'){q=!q;continue;}if(c===','&&!q){row.push(cur);cur='';continue;}cur+=c;}row.push(cur);rows.push(row);}
 return rows;
}
const csvScene:SceneDef={title:'The score table',draw:r=>{
 const file=firstFile(r),rows=file?csvRows(file[1]).slice(0,7):[],out=outLines(r),totals=out.map(l=>/^([^,]+),(-?\d+)$/.exec(l)).filter(Boolean).map(m=>[m![1],Number(m![2])] as [string,number]),top=out.at(-1);
 const cols=rows[0]?.length??0,w=cols?Math.min(70,190/cols):60,max=Math.max(1,...totals.map(t=>t[1]));
 return {say:rows.length?`A table of ${plural(rows.length-1,'row')}${totals.length?`; totals ${totals.map(([t,n])=>`${t} ${n}`).join(', ')}`:''}${top&&!/,/.test(top)?`; top player ${top}`:''}.`:r?`Printed: ${out.slice(0,3).join(' / ')||'nothing'}.`:'A table read from a CSV file, and the totals worked out from it.',svg:<>
  <Ground/>
  {rows.map((row,i)=><g key={i} className={'type '+d(i)}>{row.slice(0,4).map((v,j)=><g key={j}><rect className={(i===0?'f-cream':row.includes(top??'\u0000')?'f-amber-l':'f-white')+' s-ink-s'} x={10+j*w} y={10+i*20} width={w} height="20"/><text className="mono f-ink" x={14+j*w} y={24+i*20} fontSize="9" fontWeight={i===0?700:400}>{fit(v,Math.floor(w/6))}</text></g>)}</g>)}
  {totals.slice(0,5).map(([t,n],i)=><g key={t}><text className="mono f-ink" x="214" y={24+i*24} fontSize="9">{fit(t,8)}</text><rect className={'f-moss grow '+d(rows.length+i)} x="214" y={28+i*24} width={Math.max(3,n/max*90)} height="8" rx="2"/><text className="mono f-ink" x={218+Math.max(3,n/max*90)} y={36+i*24} fontSize="8">{n}</text></g>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const missingData:SceneDef={title:'The repair kit',draw:r=>{
 const file=firstFile(r),out=outLines(r),rows=file?file[1].split('\n'):[],lines=(rows.at(-1)===''?rows.slice(0,-1):rows).slice(0,7),newGame=out.includes('new game')||/\bno\b.*\byet\b/.test(out.join(' '));
 const kind=(l:string)=>!l.trim()?'blank':/^\s*-?\d+\s*$/.test(l)?'good':/=/.test(l)&&/^\s*-?\d+\s*$/.test(l.split('=').slice(1).join('='))?'good':'bad';
 return {say:file?`${lines.map(l=>`${JSON.stringify(l)} is ${kind(l)==='good'?'usable':kind(l)==='blank'?'blank':'damaged'}`).join('; ')}.${newGame?' A file was missing, so the program started fresh.':''}`:r?newGame?'The file was missing, so the program started fresh with its defaults.':`Printed: ${out.slice(0,3).join(' / ')}.`:'Each line of a file checked: usable, blank or damaged.',svg:<>
  <Ground tone="sand"/>
  {file?<><rect className="f-white s-ink" x="12" y="10" width="170" height={Math.max(40,lines.length*19+26)} rx="6"/><text className="mono f-ink" x="22" y="26" fontSize="10">{fit(file[0],22)}</text>
   {lines.map((l,i)=>{const k=kind(l);return <g key={i} className={'slide '+d(i)}><text className={'mono '+(k==='good'?'f-moss':k==='bad'?'f-clay':'f-ink scene-faint')} x="22" y={46+i*19} fontSize="12" fontWeight="700">{k==='good'?'✓':k==='bad'?'✗':'·'}</text><text className="mono f-ink" x="38" y={46+i*19} fontSize="10">{l.trim()?fit(l,18):'(blank)'}</text></g>;})}</>
   :r&&<g className="pop"><path className="f-white s-ink scene-dashed" d="M30 20h100l20 20v100H30z"/><text className="mono f-clay" x="90" y="90" fontSize="11" textAnchor="middle">missing</text></g>}
  <rect className="f-ink" x="194" y="10" width="114" height="150" rx="6"/>
  {out.slice(0,7).map((l,i)=><text key={i} className={'mono f-amber-l type '+d(lines.length+i)} x="202" y={28+i*18} fontSize="10">{fit(l,15)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};
Object.assign(UNIT_7_TO_11,{'py.text-files':textFiles,'py.json':jsonScene,'py.csv':csvScene,'py.missing-data':missingData});

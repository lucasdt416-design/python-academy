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

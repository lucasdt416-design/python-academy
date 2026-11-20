// Lesson scenes for Python units 4 to 6. The kit is scene-kit.tsx; how scenes work is lesson-scenes.tsx.
import type {SceneDef} from './lesson-scenes';
import {type PyNode,type SceneRun,Ground,Hero,Item,Lamp,Note,Tag,bools,clamp,d,fit,isNum,listItems,ofKind,outLines,parseRepr,pick,plural,show,strOf,toNum,wrap} from './scene-kit';

const IDLE='Run the code to fill this scene.';
/** The lines of output that are a list, dict or set, read back into values. */
const parsedLines=(r:SceneRun|null)=>outLines(r).map(l=>parseRepr(l));
const firstOf=(r:SceneRun|null,kinds:PyNode['t'][])=>parsedLines(r).find(n=>n&&kinds.includes(n.t))??undefined;
/** Items read by a challenge that asks "how many?" first: the replies after the count. */
function counted(inputs:string[]):string[]{const n=toNum(inputs[0]);return n!==null&&n>=0?inputs.slice(1,1+n):[];}

// ---------- Unit 4 ----------
const lists:SceneDef={title:'The pack',draw:r=>{
 const fromVar=ofKind(r?.vars,['list']).find(([k])=>/pack|bag|item|list|song|stuff/.test(k))??ofKind(r?.vars,['list'])[0];
 const pack=fromVar?.[1]??firstOf(r,['list']),items=listItems(pack).map(x=>show(x)),answers=bools(outLines(r)).filter(b=>b!==null) as boolean[];
 const shown=items.slice(0,8);
 return {say:r?`The pack holds ${plural(pack&&'n' in pack?pack.n:items.length,'item')}${items.length?': '+items.slice(0,8).join(', '):''}${answers.length?`. The search lamps show ${answers.map(b=>b?'True':'False').join(', ')}`:''}.`:'An empty pack, waiting to be filled.',svg:<>
  <Ground/>
  <path className="f-clay s-ink" d="M40 60q0-26 30-26h70q30 0 30 26v86H40z"/><path className="f-cream s-ink" d="M58 34q0-16 16-16h62q16 0 16 16"/><path className="s-ink" d="M40 82h130"/>
  {shown.map((name,i)=><g key={i} className={'drop '+d(i)}><Item x={62+(i%4)*30} y={112+Math.floor(i/4)*30} name={name} size={.9}/><text className="mono f-white" x={62+(i%4)*30} y={124+Math.floor(i/4)*30} fontSize="7" textAnchor="middle">{fit(name,6)}</text></g>)}
  {items.length>8&&<text className="mono f-white" x="105" y="72" fontSize="10" textAnchor="middle">+{items.length-8} more</text>}
  <g className={'pop '+d(shown.length+1)}><circle className="f-white s-ink" cx="170" cy="40" r="17"/><text className="mono f-ink" x="170" y="45" fontSize="14" textAnchor="middle">{r?(pack&&'n' in pack?pack.n:items.length):0}</text><text className="mono f-ink" x="170" y="68" fontSize="9" textAnchor="middle">len()</text></g>
  {answers.slice(0,2).map((b,i)=><Lamp key={i} x={232+i*48} y={50} on={b} label={b?'True':'False'} className={'pop '+d(shown.length+2+i)}/>)}
  {answers.length>0&&<text className="mono f-ink" x="256" y="22" fontSize="10" textAnchor="middle">in</text>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const indexing:SceneDef={title:'The shelf',draw:r=>{
 const fromVar=ofKind(r?.vars,['list'])[0]?.[1],items=(fromVar?listItems(fromVar).map(x=>show(x)):counted(r?.inputs??[])).slice(0,8),n=items.length;
 const lines=outLines(r),picked=new Set(lines.filter(l=>items.includes(l))),slice=parsedLines(r).find(x=>x?.t==='list');
 const sliced=new Set(listItems(slice).map(x=>show(x)));
 const w=n?Math.min(64,280/n):40;
 return {say:n?`A shelf of ${plural(n,'item')}, with positions 0 to ${n-1} above and -${n} to -1 below. ${picked.size?`Picked out: ${[...picked].join(', ')}.`:''}`:'An empty shelf with numbered places.',svg:<>
  <Ground tone="sand"/>
  <path className="f-cream s-ink" d="M14 104h292v10H14z"/>
  {items.map((name,i)=>{const x=20+i*w+w/2,hit=picked.has(name),cut=sliced.has(name);return <g key={i} className={'pop '+d(i)}>
   <text className="mono f-moss" x={x} y="34" fontSize="11" textAnchor="middle">{i}</text>
   {cut&&<rect className="f-amber-l" x={x-w/2+2} y="44" width={w-4} height="58" rx="6"/>}
   <Item x={x} y={86} name={name} size={1.1} className={hit?'ring-hit':undefined}/>
   <text className={'mono '+(hit?'f-clay':'f-ink')} x={x} y="100" fontSize="9" textAnchor="middle" fontWeight={hit?700:400}>{fit(name,Math.floor(w/6))}</text>
   <text className="mono f-slate" x={x} y="132" fontSize="11" textAnchor="middle">{i-n}</text>
   {hit&&<path className={'s-clay-w drop '+d(n+i)} d={`M${x} 52v-8`}/>}
  </g>;})}
  {n>0&&<><text className="mono f-moss" x="14" y="20" fontSize="9">positions from the front</text><text className="mono f-slate" x="14" y="150" fontSize="9">positions from the back</text></>}
  {slice&&<text className={'mono f-ink type '+d(n+2)} x="306" y="150" fontSize="9" textAnchor="end">slice {fit(show(slice),24)}</text>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const iterateLists:SceneDef={title:'The market stall',draw:r=>{
 const lists=ofKind(r?.vars,['list']).map(([,v])=>v),values=(lists[0]?listItems(lists[0]).map(x=>show(x)):counted(r?.inputs??[])).slice(0,9);
 const kept=new Set(listItems(lists[1]??firstOf(r,['list'])).map(x=>show(x))),total=outLines(r).find(isNum);
 return {say:values.length?`The loop visits ${values.join(', ')} in turn. ${kept.size?`Kept: ${[...kept].join(', ')}. `:''}${total!==undefined?`First number printed: ${total}.`:''}`:'A stall where each item passes the counter in turn.',svg:<>
  <Ground/>
  <path className="f-cream s-ink" d="M14 92h292v14H14z"/><path className="s-ink-s" d="M30 106v40M290 106v40"/>
  <path className="f-clay s-ink" d="M14 30h292l-10 20H24z"/>
  {values.map((v,i)=>{const x=30+i*30,keep=kept.has(v);return <g key={i}>
   <g className={'slide '+d(i)}><circle className={(keep?'f-amber':'f-white')+' s-ink-s'} cx={x} cy="78" r="12"/><text className="mono f-ink" x={x} y="82" fontSize="10" textAnchor="middle">{fit(v,4)}</text></g>
   {keep&&<g className={'drop '+d(i+1)}><path className="s-moss-s" d={`M${x} 92v28`}/><circle className="f-amber s-ink-s" cx={x} cy="132" r="9"/></g>}
  </g>;})}
  {kept.size>0&&<text className={'mono f-ink type '+d(values.length+1)} x="300" y="150" fontSize="10" textAnchor="end">kept {kept.size}</text>}
  {total!==undefined&&<Tag x={270} y={66} text={`total ${fit(total,8)}`} tone="moss" className={'pop '+d(values.length+2)}/>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

function dictEntries(r:SceneRun|null):[string,string][]{
 const v=ofKind(r?.vars,['dict'])[0]?.[1]??firstOf(r,['dict']);
 if(v&&v.t==='dict')return v.entries.map(([k,x])=>[show(k),show(x)]);
 const n=toNum(r?.inputs[0]);if(n===null)return [];
 const m=new Map<string,string>();for(let i=0;i<n;i++){const k=r!.inputs[1+i*2],x=r!.inputs[2+i*2];if(k!==undefined&&x!==undefined)m.set(k,x);}
 return [...m];
}
const dicts:SceneDef={title:'The keep',draw:r=>{
 const rooms=dictEntries(r).slice(0,6),found=outLines(r)[0],hit=rooms.findIndex(([,v])=>v===found),miss=!!r&&found==='empty';
 return {say:r?rooms.length?`${plural(rooms.length,'room')}: ${rooms.map(([k,v])=>`${k} holds ${v}`).join(', ')}.${hit>=0?` The search found ${found} in the ${rooms[hit][0]}.`:miss?' The searched room is not there.':''}`:'A keep with no rooms yet.':'A keep whose rooms are keys and whose treasures are values.',svg:<>
  <Ground tone="slate"/>
  <path className="f-cream s-ink" d="M20 150V46h280v104z"/><path className="f-slate s-ink" d="M12 50l148-36 148 36z"/>
  {rooms.map(([k,v],i)=>{const x=34+(i%3)*90,y=58+Math.floor(i/3)*46;return <g key={i} className={'pop '+d(i)}>
   <rect className={(i===hit?'f-amber-l':'f-white')+' s-ink-s'} x={x} y={y} width="80" height="40" rx="5"/>
   <rect className="f-white s-ink-s" x={x+4} y={y-6} width={Math.min(72,k.length*6+10)} height="13" rx="3"/><text className="mono f-ink" x={x+9} y={y+4} fontSize="9">{fit(k,11)}</text>
   <Item x={x+16} y={y+34} name={v} size={.8}/><text className="mono f-clay" x={x+30} y={y+28} fontSize="9">{fit(v,8)}</text>
  </g>;})}
  {miss&&<Tag x={160} y={168} text="no such room: empty" tone="clay" className={'pop '+d(rooms.length+1)}/>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const sets:SceneDef={title:"Two explorers' maps",draw:r=>{
 const setVars=ofKind(r?.vars,['set']).map(([,v])=>listItems(v).map(x=>show(x)));
 let a:string[]=[],b:string[]=[];
 if(setVars.length>=2)[a,b]=setVars;
 else{const lists=parsedLines(r).filter(x=>x?.t==='list').map(x=>listItems(x!).map(y=>show(y)));
  if(lists.length>=3){const [all,both,only]=lists;a=[...both,...only];b=all.filter(x=>!only.includes(x));}
  else if(lists.length===2){a=lists[0];b=lists[1];}}
 const both=a.filter(x=>b.includes(x)),onlyA=a.filter(x=>!b.includes(x)),onlyB=b.filter(x=>!a.includes(x));
 const col=(xs:string[],x:number)=>xs.slice(0,5).map((t,i)=><text key={t} className={'mono f-ink type '+d(i+2)} x={x} y={70+i*16} fontSize="10" textAnchor="middle">{fit(t,9)}</text>);
 return {say:a.length||b.length?`Only the first: ${onlyA.join(', ')||'nothing'}. Both: ${both.join(', ')||'nothing'}. Only the second: ${onlyB.join(', ')||'nothing'}.`:'Two overlapping circles, one for each explorer.',svg:<>
  <Ground tone="sand"/>
  <circle className="f-moss-l s-ink venn" cx="120" cy="88" r="66"/><circle className="f-amber-l s-ink venn" cx="200" cy="88" r="66"/>
  <path className="f-white s-ink-s" d="M160 34a66 66 0 0 1 0 108a66 66 0 0 1 0-108z"/>
  {col(onlyA,88)}{col(both,160)}{col(onlyB,232)}
  <text className="mono f-moss" x="70" y="18" fontSize="10">first</text><text className="mono f-amber-d" x="250" y="18" fontSize="10" textAnchor="end">second</text>
  {!r&&<Note text={IDLE}/>}
 </>};
}};

// ---------- Unit 5 ----------
type Fn={name:string;params:string[];calls:string[];returns:boolean;prints:boolean;locals?:string[]};
/** The functions defined at the top of a program, read from its text: what each takes, and which of the
 * others it calls. Only for drawing; nothing here runs the code. */
export function functionsIn(code:string|undefined):Fn[]{
 if(!code)return [];
 const lines=code.split('\n'),found:Fn[]=[];
 lines.forEach((line,i)=>{
  const m=/^def\s+([A-Za-z_]\w*)\s*\(([^)]*)\)/.exec(line);if(!m)return;
  const body:string[]=[];for(let j=i+1;j<lines.length&&(lines[j].trim()===''||/^\s/.test(lines[j]));j++)body.push(lines[j]);
  const text=body.join('\n');
  const params=m[2].split(',').map(p=>p.trim().split(/[=:]/)[0].trim()).filter(Boolean);
  const locals=[...new Set([...text.matchAll(/^\s+([A-Za-z_]\w*)\s*[-+*/]?=(?!=)/gm)].map(x=>x[1]))].filter(n=>!params.includes(n));
  found.push({name:m[1],params,calls:[],returns:/\breturn\b/.test(text),prints:/\bprint\(/.test(text),locals});
  (found.at(-1) as Fn&{text?:string}).text=text;
 });
 for(const f of found){const text=(f as Fn&{text?:string}).text??'';f.calls=found.filter(g=>g!==f&&new RegExp(`\\b${g.name}\\s*\\(`).test(text)).map(g=>g.name);}
 return found;
}
function fnsOf(r:SceneRun|null):Fn[]{
 const fromCode=functionsIn(r?.code);if(fromCode.length)return fromCode;
 return ofKind(r?.vars,['function']).map(([,v])=>v.t==='function'?{name:v.name,params:v.params,calls:[],returns:false,prints:false}:null).filter(Boolean) as Fn[];
}
function FnBox({x,y,f,w=120,className}:{x:number;y:number;f:Fn;w?:number;className?:string}){
 return <g className={className}><rect className="f-white s-ink" x={x} y={y} width={w} height="30" rx="7"/><text className="mono f-plum" x={x+8} y={y+19} fontSize="11">def <tspan className="f-ink">{fit(`${f.name}(${f.params.join(', ')})`,Math.floor((w-36)/6.6))}</tspan></text></g>;
}

const functions:SceneDef={title:'The scene machine',draw:r=>{
 const fns=fnsOf(r).slice(0,3),lines=outLines(r).slice(0,9),count=new Map<string,number>();lines.forEach(l=>count.set(l,(count.get(l)??0)+1));
 return {say:r?`${fns.length?`Defined: ${fns.map(f=>f.name+'()').join(', ')}. `:''}${lines.length?`The run printed ${plural(outLines(r).length,'line')}${[...count.values()].some(n=>n>1)?', and the highlighted ones came from a replayed scene':''}.`:'Nothing was printed: a function only runs when it is called.'}`:'Functions waiting to be called, and a film strip for what they print.',svg:<>
  <Ground tone="slate"/>
  {fns.map((f,i)=><FnBox key={f.name} x={12} y={16+i*40} f={f} className={'slide '+d(i)}/>)}
  {fns.length===0&&r&&<text className="mono f-ink" x="16" y="34" fontSize="11">no def found</text>}
  <rect className="f-ink" x="146" y="10" width="164" height="150" rx="6"/>
  {Array.from({length:9},(_,i)=><rect key={i} className="f-cream" x="150" y={14+i*16.4} width="5" height="8"/>)}
  {lines.map((l,i)=><text key={i} className={`mono ${(count.get(l)??0)>1?'f-amber':'f-white'} type ${d(i+2)}`} x="162" y={24+i*16} fontSize="10">{fit(l,22)}</text>)}
  {r&&!lines.length&&<text className="mono f-white" x="228" y="88" fontSize="11" textAnchor="middle">(nothing printed)</text>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const parameters:SceneDef={title:'The stage',draw:r=>{
 const fn=fnsOf(r)[0],lines=outLines(r).slice(0,3);
 return {say:r?`${fn?`${fn.name}() takes ${fn.params.join(', ')||'nothing'}. `:''}${lines.length?'On stage: '+lines.join(' / '):'Nothing was printed.'}`:'A stage where each call puts a different hero.',svg:<>
  <Ground tone="sand"/>
  {fn&&<g className="slide"><rect className="f-white s-ink" x="12" y="12" width="296" height="30" rx="7"/><text className="mono f-plum" x="22" y="31" fontSize="11">def <tspan className="f-ink">{fn.name}(</tspan></text>
   {fn.params.slice(0,4).map((p,i)=><g key={p}><rect className="f-amber-l s-ink-s" x={60+fn.name.length*6.6+i*62} y="18" width="56" height="18" rx="4"/><text className="mono f-ink" x={88+fn.name.length*6.6+i*62} y="31" fontSize="10" textAnchor="middle">{fit(p,8)}</text></g>)}</g>}
  {lines.map((l,i)=>{const x=60+i*100,who=l.split(/\s/)[0]??'';return <g key={i} className={'pop '+d(2+i*2)}>
   <Hero x={x} y={132} tone={(['plum','slate','clay'] as const)[i%3]}/><Tag x={x} y={60} text={fit(who,10)} tone="clay"/>
   {wrap(l.slice(who.length).trim(),15,2).map((t,j)=><text key={j} className="mono f-ink" x={x} y={150+j*11} fontSize="9" textAnchor="middle">{t}</text>)}
  </g>;})}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const returnValues:SceneDef={title:'Print or return?',draw:r=>{
 const fns=fnsOf(r).slice(0,2),lines=outLines(r).slice(0,4),stored=ofKind(r?.vars,['int','float','str','bool','tuple','list']).slice(0,3);
 return {say:r?`${r.returned!==undefined?`The function handed back ${r.returned}. `:''}${stored.length?`Stored: ${stored.map(([k,v])=>`${k} = ${show(v,true)}`).join(', ')}. `:''}${lines.length?`Printed: ${lines.join(', ')}.`:'Nothing printed.'}`:'A function hands a value back into a tray, or only shows it on a screen.',svg:<>
  <Ground/>
  <rect className="f-plum s-ink" x="110" y="22" width="100" height="70" rx="10"/>
  <text className="mono f-white" x="160" y="52" fontSize="11" textAnchor="middle">{fit(fns[0]?.name??'function',13)}</text>
  {fns[0]&&<text className="mono f-white" x="160" y="70" fontSize="9" textAnchor="middle">{fns[0].returns?'returns':'only prints'}</text>}
  <path className="s-ink" d="M160 92v18"/><path className="f-cream s-ink" d="M120 110h80l-8 24h-64z"/>
  <text className="mono f-ink" x="160" y="150" fontSize="9" textAnchor="middle">return tray</text>
  {r?.returned!==undefined&&<Tag x={160} y={122} text={fit(r.returned,14)} tone="moss" className={'drop '+d(2)}/>}
  {r?.returned===undefined&&stored[0]&&<Tag x={160} y={122} text={`${fit(stored[0][0],6)} = ${fit(show(stored[0][1],true),8)}`} tone="moss" className={'drop '+d(2)}/>}
  <rect className="f-ink" x="226" y="22" width="84" height="80" rx="6"/><text className="mono f-white" x="268" y="116" fontSize="9" textAnchor="middle">screen</text>
  {lines.map((l,i)=><text key={i} className={'mono f-amber-l type '+d(3+i)} x="234" y={42+i*16} fontSize="11">{fit(l,10)}</text>)}
  <path className="s-moss" d="M210 56h14"/>
  {stored.slice(1).map(([k,v],i)=><text key={k} className={'mono f-ink type '+d(5+i)} x="16" y={40+i*18} fontSize="10">{fit(k,8)} = {fit(show(v,true),10)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const scope:SceneDef={title:'Inside and outside',draw:r=>{
 const globals=ofKind(r?.vars,['int','float','str','bool','list','dict']).slice(0,4),fns=fnsOf(r).slice(0,2);
 return {say:r?`Outside, the program keeps ${globals.map(([k,v])=>`${k} = ${show(v,true)}`).join(', ')||'no names'}. ${fns.length?`${fns.map(f=>`${f.name}() has its own ${[...f.params,...(f.locals??[])].join(', ')||'nothing'}`).join('; ')}, which last only while it runs.`:''}`:'A house for the names outside, and a tent for each function\'s own names.',svg:<>
  <Ground/>
  <path className="f-cream s-ink" d="M10 160V58h170v102z"/><path className="f-clay s-ink" d="M4 62l91-46 91 46z"/>
  <text className="mono f-ink" x="95" y="78" fontSize="10" textAnchor="middle">outside the functions</text>
  {globals.map(([k,v],i)=><g key={k} className={'pop '+d(i)}><rect className="f-white s-ink-s" x="22" y={88+i*17} width="146" height="15" rx="3"/><text className="mono f-ink" x="28" y={99+i*17} fontSize="10">{fit(k,8)} = <tspan className="f-clay">{fit(show(v,true),12)}</tspan></text></g>)}
  {fns.map((f,i)=><g key={f.name} className={'pop '+d(4+i*2)}><path className="f-plum s-ink" d={`M${196+i*62} 160l29-70 29 70z`}/><text className="mono f-white" x={225+i*62} y="150" fontSize="8" textAnchor="middle">{fit(f.name,9)}</text>
   {[...f.params,...(f.locals??[])].slice(0,3).map((p,j)=><g key={p}><rect className="f-white s-moss-s scene-dashed" x={203+i*62} y={30+j*18} width="44" height="14" rx="3"/><text className="mono f-ink" x={225+i*62} y={40+j*18} fontSize="8" textAnchor="middle">{fit(p,7)}</text></g>)}</g>)}
  {fns.length>0&&<text className="mono f-ink" x="256" y="20" fontSize="9" textAnchor="middle">only during a call</text>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const decompose:SceneDef={title:'The blueprint',draw:r=>{
 const fns=fnsOf(r).slice(0,6),called=new Set(fns.flatMap(f=>f.calls)),levels=new Map<string,number>();
 const level=(f:Fn,seen=new Set<string>()):number=>{if(levels.has(f.name))return levels.get(f.name)!;if(seen.has(f.name))return 0;seen.add(f.name);const v=f.calls.length?1+Math.max(...f.calls.map(c=>level(fns.find(g=>g.name===c)!,seen))):0;levels.set(f.name,v);return v;};
 fns.forEach(f=>level(f));const rows=[...new Set(fns.map(f=>levels.get(f.name)!))].sort((a,b)=>b-a);
 const pos=new Map<string,{x:number;y:number}>();rows.forEach((lv,ri)=>{const row=fns.filter(f=>levels.get(f.name)===lv);row.forEach((f,i)=>pos.set(f.name,{x:10+(i+.5)*(300/row.length)-70,y:14+ri*46}));});
 return {say:fns.length?`${fns.map(f=>f.calls.length?`${f.name}() uses ${f.calls.join(' and ')}()`:`${f.name}() does one job on its own`).join('; ')}.${r?.returned!==undefined?` The checked call returned ${r.returned}.`:''}`:'A blueprint of functions, each resting on the ones it uses.',svg:<>
  <Ground tone="slate"/>
  {fns.flatMap(f=>f.calls.map(c=>{const a=pos.get(f.name),b=pos.get(c);return a&&b?<path key={f.name+c} className={'s-moss pop '+d(4)} d={`M${a.x+70} ${a.y+30}L${b.x+70} ${b.y}`}/>:null;}))}
  {fns.map((f,i)=>{const p=pos.get(f.name)!;return <FnBox key={f.name} x={p.x} y={p.y} w={140} f={{...f,params:[]}} className={'pop '+d(i)}/>;})}
  {r?.returned!==undefined&&<Tag x={160} y={160} text={`returned ${fit(r.returned,16)}`} tone="moss" className={'pop '+d(8)}/>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

// ---------- Unit 6 ----------
const tracebacks:SceneDef={title:'The crash report',draw:r=>{
 const lines=outLines(r).slice(0,4),code=(r?.code??'').split('\n'),at=r?.errorLine??null,shownLine=at?code[at-1]?.trim()??'':'';
 const callers=at&&r?.code?functionsIn(r.code).filter(f=>{const start=code.findIndex(l=>l.startsWith(`def ${f.name}(`))+1;let end=start;while(end<code.length&&(code[end].trim()===''||/^\s/.test(code[end])))end++;return at>start&&at<=end;}).map(f=>f.name):[];
 return {say:r?r.error?`Python stopped with ${r.error}${at?` on line ${at}`:''}${callers.length?`, inside ${callers[0]}()`:''}. ${r.message??''}`:`The program ran to the end and printed ${lines.join(' / ')||'nothing'}.`:'A stack of cards that explains where a program stopped.',svg:<>
  <Ground tone="slate"/>
  {r?.error?<>
   {callers.length>0&&<g className="drop"><rect className="f-white s-ink-s" x="30" y="16" width="260" height="30" rx="6"/><text className="mono f-ink" x="40" y="35" fontSize="10">called from the program, into {fit(callers[0],14)}()</text></g>}
   <g className={'drop '+d(2)}><rect className="f-cream s-ink" x="22" y="54" width="276" height="40" rx="6"/><text className="mono f-moss" x="32" y="70" fontSize="10">line {at??'?'}</text><text className="mono f-ink" x="32" y="86" fontSize="11">{fit(shownLine,36)}</text></g>
   <g className={'drop '+d(4)}><rect className="f-clay s-ink" x="14" y="102" width="292" height="40" rx="6"/><text className="mono f-white" x="26" y="120" fontSize="11" fontWeight="700">{fit(r.error,30)}</text><text className="mono f-white" x="26" y="135" fontSize="9">{fit((r.message??'').replace(/^\w+Error:\s*/,''),46)}</text></g>
   <text className={'mono f-ink type '+d(6)} x="160" y="160" fontSize="10" textAnchor="middle">read from the bottom up</text>
  </>:r?<g className="pop"><rect className="f-white s-ink" x="70" y="18" width="180" height="130" rx="6"/><path className="s-ink-s" d="M70 40h180"/><text className="mono f-moss" x="160" y="33" fontSize="10" textAnchor="middle">ran to the end</text>
   {lines.map((l,i)=><text key={i} className={'mono f-ink type '+d(i+1)} x="82" y={60+i*20} fontSize="11">{fit(l,22)}</text>)}</g>:null}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const debugStrategy:SceneDef={title:'Under the magnifier',draw:r=>{
 const names=ofKind(r?.vars,['int','float','str','bool','none','list']).slice(0,5),lines=outLines(r),labelled=lines.filter(l=>/^[A-Za-z][\w ]*\s-?\w/.test(l)&&/\s/.test(l)).slice(0,5);
 return {say:r?`${names.length?`At the end: ${names.map(([k,v])=>`${k} = ${show(v,true)}`).join(', ')}. `:''}${labelled.length?`Checking lines: ${labelled.join(' / ')}.`:`Printed: ${lines.slice(0,4).join(', ')||'nothing'}.`}`:'A magnifier over the names a program keeps.',svg:<>
  <Ground tone="sand"/>
  <rect className="f-white s-ink" x="14" y="14" width="150" height={Math.max(40,names.length*22+16)} rx="6"/>
  {names.map(([k,v],i)=><g key={k} className={'slide '+d(i)}><text className="mono f-ink" x="24" y={34+i*22} fontSize="11">{fit(k,8)}</text><text className="mono f-clay" x="154" y={34+i*22} fontSize="11" textAnchor="end">{fit(show(v,true),9)}</text></g>)}
  <g className={'pop '+d(names.length+1)}><circle className="f-white s-ink-w scene-lens" cx="104" cy="70" r="34"/><path className="s-ink-w" d="M128 94l26 26"/></g>
  <rect className="f-ink" x="178" y="14" width="130" height="140" rx="6"/>
  {(labelled.length?labelled:lines.slice(0,6)).map((l,i)=><text key={i} className={'mono f-amber-l type '+d(i+2)} x="186" y={34+i*20} fontSize="10">{fit(l,18)}</text>)}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const NUMBERISH=/^-?\d+(\.\d+)?$/;
const tryExcept:SceneDef={title:'The safety net',draw:r=>{
 const lines=outLines(r).slice(0,6),caught=lines.filter(l=>!NUMBERISH.test(l)),through=lines.filter(l=>NUMBERISH.test(l));
 return {say:r?r.error?`An error got past every except: ${r.error}.`:`${through.length?`Answers that got through: ${through.join(', ')}. `:''}${caught.length?`Caught by the net: ${caught.join(', ')}.`:'Nothing needed catching.'}`:'Answers fall into the basket; errors land in the net.',svg:<>
  <Ground/>
  <path className="s-ink" d="M20 112q140 40 280 0"/>{Array.from({length:9},(_,i)=><path key={i} className="s-ink-s" d={`M${36+i*30} ${116+Math.sin(i/8*Math.PI)*16}l14 -10`}/>)}
  {caught.slice(0,3).map((l,i)=><g key={i} className={'drop '+d(i*2)}><circle className="f-clay s-ink-s" cx={60+i*80} cy={118} r="9"/>{wrap(l,12,2).map((t,j)=><text key={j} className="mono f-ink" x={60+i*80} y={146+j*11} fontSize="9" textAnchor="middle">{t}</text>)}</g>)}
  <path className="f-cream s-ink" d="M240 30h60l-6 40h-48z"/><text className="mono f-ink" x="270" y="84" fontSize="9" textAnchor="middle">answers</text>
  {through.map((l,i)=><Tag key={i} x={270} y={24+i*0+44-i*16} text={fit(l,6)} tone="moss" className={'drop '+d(i*2+1)}/>)}
  {r?.error&&<g className="pop"><circle className="f-clay s-ink" cx="160" cy="166" r="10"/><text className="mono f-ink" x="160" y="44" fontSize="11" textAnchor="middle">{fit(r.error,24)} fell through</text></g>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const raise:SceneDef={title:'The rule gate',draw:r=>{
 const lines=outLines(r).slice(0,4),refused=lines.filter(l=>/refused|must|not allowed|slow down/i.test(l)),ok=lines.filter(l=>!refused.includes(l));
 return {say:r?`${ok.length?`Let through: ${ok.join(', ')}. `:''}${refused.length?`Turned back: ${refused.join(' / ')}.`:''}${r.error?` An error nobody caught: ${r.error}.`:''}`:'A gate that lets good values through and turns others back with a reason.',svg:<>
  <Ground tone="slate"/>
  <path className="f-slate s-ink" d="M140 150V40h40v110z"/><rect className="f-cream s-ink" x="112" y="16" width="96" height="22" rx="4"/><text className="mono f-ink" x="160" y="31" fontSize="10" textAnchor="middle">the rule</text>
  {ok.map((l,i)=><Tag key={i} x={250} y={70+i*28} text={fit(l,10)} tone="moss" className={'slide '+d(i*2+1)}/>)}
  {refused.map((l,i)=><g key={i} className={'drop '+d(i*2+2)}>{wrap(l,17,3).map((t,j)=><text key={j} className="mono f-clay" x="14" y={64+i*48+j*12} fontSize="10">{t}</text>)}<path className="s-clay-w" d={`M128 ${60+i*48}h-10`}/></g>)}
  {r?.error&&<Tag x={160} y={164} text={`${fit(r.error,18)} not caught`} tone="clay" className="pop"/>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

const validateInput:SceneDef={title:'The bridge keeper',draw:r=>{
 const replies=(r?.inputs??[]).slice(0,5),lines=outLines(r),problems=lines.filter(l=>!NUMBERISH.test(l)&&!/^You /.test(l)),done=!r?.error;
 return {say:r?`${replies.map((x,i)=>`${JSON.stringify(x)}: ${problems[i]??(done&&i===replies.length-1?'accepted':'…')}`).join('; ')}.`:'A bridge keeper who checks each reply in turn.',svg:<>
  <Ground/>
  <path className="f-cream s-ink" d="M200 120q60-50 120 0v40H200z"/><Hero x={182} y={150} tone="slate"/>
  {replies.map((x,i)=>{const bad=i<problems.length,last=i===replies.length-1&&done&&!bad;return <g key={i} className={'slide '+d(i*2)}>
   <rect className={(last?'f-amber-l':'f-white')+' s-ink-s'} x="12" y={14+i*30} width="70" height="22" rx="5"/><text className="mono f-clay" x="20" y={29+i*30} fontSize="10">{fit(JSON.stringify(x),9)}</text>
   <text className={'mono '+(bad?'f-clay':'f-moss')+' type '+d(i*2+1)} x="90" y={29+i*30} fontSize="10">{bad?fit(problems[i],14):last?'let through':''}</text>
  </g>;})}
  {done&&r&&<path className={'s-moss-w drop '+d(replies.length*2)} d="M210 140q50-30 100 0"/>}
  {!r&&<Note text={IDLE}/>}
 </>};
}};

export const UNIT_4_TO_6:Record<string,SceneDef>={
 'py.lists':lists,'py.indexing':indexing,'py.iterate-lists':iterateLists,'py.dicts':dicts,'py.sets':sets,
 'py.tracebacks':tracebacks,'py.debug-strategy':debugStrategy,'py.try-except':tryExcept,'py.raise':raise,'py.validate-input':validateInput,
 'py.functions':functions,'py.parameters':parameters,'py.return-values':returnValues,'py.scope':scope,'py.decompose':decompose,
};
// Kept for scenes in units 5 and 6 below.
void Hero;void clamp;void pick;void strOf;void wrap;

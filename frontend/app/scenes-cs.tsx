// Lesson scenes for Computer Science Foundations. The kit is scene-kit.tsx; how scenes work is lesson-scenes.tsx.
// Most of these lessons are checked by calling the learner's functions, so a scene reads three places:
// the names a run left behind, its printed lines, and a checked call (its arguments, from the case's
// description, and what it returned).
import type {SceneDef} from './lesson-scenes';
import {type PyNode,type SceneRun,Ground,Hero,Lamp,Note,Tag,clamp,d,fit,listItems,numOf,outLines,parseRepr,pick,plural,strOf} from './scene-kit';

const IDLE='Run the code to fill this scene.';

/** The arguments of a checked call, read from its label: "With find([1, 2], 3)" gives [[1, 2], 3]. */
function callArgs(r:SceneRun|null):PyNode[]{
 const m=/^With \w+\((.*)\)$/.exec(r?.label??'');
 if(!m)return [];
 const t=parseRepr(`(${m[1]},)`);
 return t&&t.t==='tuple'?t.items:[];
}
const called=(r:SceneRun|null,name:string)=>(r?.label??'').startsWith(`With ${name}(`);
const returned=(r:SceneRun|null):PyNode|null=>r?.returned!==undefined?parseRepr(r.returned):null;
const ints=(n:PyNode|undefined):number[]=>listItems(n).map(numOf).filter((v):v is number=>v!==null);
const plain=(n:PyNode):string=>n.t==='str'?n.v:n.t==='int'||n.t==='float'?n.v:n.t==='bool'?(n.v?'True':'False'):'?';

// ---------- cs.binary: the signal tower ----------
function bitsOf(r:SceneRun|null):{bits:string;value:number|null}|null{
 const back=returned(r),args=callArgs(r);
 if(back?.t==='str'&&/^[01]+$/.test(back.v))return {bits:back.v,value:numOf(args[0])};
 if(back?.t==='int'&&args[0]?.t==='str'&&/^[01]+$/.test(args[0].v))return {bits:args[0].v,value:Number(back.v)};
 const lamps=strOf(pick(r?.vars,['lamps','bits','binary','text']));
 if(lamps&&/^[01]+$/.test(lamps))return {bits:lamps,value:numOf(pick(r?.vars,['value','n','number']))};
 const line=outLines(r).find(l=>/^0b[01]+$/.test(l.trim()));
 return line?{bits:line.trim().slice(2),value:parseInt(line.trim().slice(2),2)}:null;
}
const binary:SceneDef={title:'The signal tower',draw:r=>{
 const got=bitsOf(r);
 if(!got)return {say:r?'No binary number to show on the lamps yet.':'A row of lamps: each one on is a 1, each one off is a 0.',svg:<><Ground tone="slate"/>
  {[8,4,2,1].map((p,i)=><Lamp key={p} x={88+i*48} y={60} on={null} label={String(p)}/>)}<Note text={r?'Return or print some binary to light the lamps.':IDLE}/></>};
 const all=got.bits,bits=all.slice(-8),n=bits.length,gap=Math.min(48,272/n),x0=160-gap*(n-1)/2;
 const value=got.value??parseInt(all,2),on=[...bits].map((b,i)=>b==='1'?2**(n-1-i):0).filter(v=>v);
 return {say:`${all} lights ${on.length?on.join(' + '):'no lamps'}${all.length>8?` (the lowest 8 of ${all.length} lamps shown)`:''}, which is ${value}.`,svg:<>
  <Ground tone="slate"/>
  {[...bits].map((b,i)=><Lamp key={i} className={'pop '+d(i*1.5)} x={x0+i*gap} y={54} on={b==='1'} label={String(2**(n-1-i))}/>)}
  <Tag x={160} y={130} text={`= ${value}`} tone="moss" className={'drop '+d(n*1.5)}/>
 </>};
}};

// ---------- cs.hexadecimal: the flag ----------
function colourOf(r:SceneRun|null):number[]|null{
 const back=returned(r),args=callArgs(r);
 const fromHex=(s:string)=>{const m=/#?([0-9a-f]{6})\b/i.exec(s);return m?[0,2,4].map(i=>parseInt(m[1].slice(i,i+2),16)):null;};
 if(back?.t==='str'&&fromHex(back.v))return fromHex(back.v);
 const list=ints(back??undefined);if(list.length===3)return list;
 if(args.length===3&&args.every(a=>numOf(a)!==null))return args.map(a=>numOf(a)!);
 const named=['red','green','blue'].map(k=>numOf(r?.vars?.[k]));
 if(named.every(v=>v!==null))return named as number[];
 for(const l of outLines(r)){const c=fromHex(l);if(c&&l.includes('#'))return c;}
 return null;
}
const hexadecimal:SceneDef={title:'The signal flag',draw:r=>{
 const rgb=colourOf(r);
 if(!rgb)return {say:r?'No colour to raise on the flag yet.':'A flag waits for its colour: amounts of red, green and blue.',svg:<><Ground/>
  <path className="s-ink" d="M70 150V30"/><path className="f-white s-ink" d="M70 34h90l-14 26 14 26h-90z"/><Note text={r?'Return or print a colour code to raise the flag.':IDLE}/></>};
 const over=rgb.filter(v=>v<0||v>255),c=rgb.map(v=>clamp(Math.round(v),0,255)),code='#'+c.map(v=>v.toString(16).padStart(2,'0')).join('');
 const names=['red','green','blue'],tones=['f-clay','f-moss','f-slate'];
 return {say:`The flag is ${code}: ${c.map((v,i)=>`${names[i]} ${v} (${v.toString(16).padStart(2,'0')})`).join(', ')}.${over.length?` ${over.join(' and ')} cannot fit in one byte, so the flag uses the nearest amount it can.`:''}`,svg:<>
  <Ground/>
  <path className="s-ink" d="M60 150V24"/>
  <path className="pop" fill={code} d="M60 28h96l-14 28 14 28h-96z"/><path className="s-ink" d="M60 28h96l-14 28 14 28h-96z"/>
  <text className="mono f-ink" x="70" y="106" fontSize="13">{code}</text>
  {c.map((v,i)=><g key={i} className={'pop '+d(2+i*2)}>
   <rect className="f-white s-ink-s" x={190+i*40} y={28} width="26" height="102" rx="4"/>
   <rect className={tones[i]} x={191+i*40} y={129-v/255*100} width="24" height={v/255*100+0.5}/>
   <text className="mono f-ink" x={203+i*40} y={146} fontSize="12" textAnchor="middle">{v.toString(16).padStart(2,'0')}</text>
   <text className="mono f-ink" x={203+i*40} y={160} fontSize="10" textAnchor="middle">{v}</text>
  </g>)}
 </>};
}};

// ---------- cs.text-encoding: the coded message ----------
const BYTES=(s:string)=>new TextEncoder().encode(s).length;
function messageOf(r:SceneRun|null):{text:string;moved?:string}|null{
 const back=returned(r),args=callArgs(r);
 if(back?.t==='str'&&args[0]?.t==='str')return {text:args[0].v,moved:back.v};
 if(args[0]?.t==='str')return {text:args[0].v};
 const named=strOf(pick(r?.vars,['message','word','text','out']));
 if(named)return {text:named};
 const literals=[...(r?.code??'').matchAll(/"([^"\n]+)"/g)].map(m=>m[1]).filter(s=>!/^utf-?8$/i.test(s));
 return literals.length?{text:literals.reduce((a,b)=>b.length>a.length?b:a)}:null;
}
const textEncoding:SceneDef={title:'The coded message',draw:r=>{
 const m=r&&messageOf(r);
 if(!m)return {say:'Each character is a number underneath: a code, stored as one or more bytes.',svg:<><Ground tone="sand"/>
  {['h','i'].map((ch,i)=><g key={ch}><rect className="f-white s-ink" x={124+i*44} y={40} width="34" height="40" rx="6"/><text className="mono f-ink" x={141+i*44} y={66} fontSize="16" textAnchor="middle">{ch}</text></g>)}<Note text={IDLE}/></>};
 const chars=[...m.text].slice(0,8),moved=m.moved?[...m.moved].slice(0,8):null,w=Math.min(36,280/Math.max(1,chars.length)),x0=160-w*chars.length/2;
 const total=BYTES(m.text),shown=(ch:string)=>ch===' '?'␣':ch;
 return {say:moved?`"${m.text}" becomes "${m.moved}": ${chars.map((ch,i)=>`${shown(ch)} ${ch.codePointAt(0)} to ${shown(moved[i]??'')}`).slice(0,5).join(', ')}.`
  :`"${m.text}" is ${plural([...m.text].length,'character')} and ${plural(total,'byte')} in UTF-8: ${chars.map(ch=>`${shown(ch)} is ${ch.codePointAt(0)}`).slice(0,5).join(', ')}.`,svg:<>
  <Ground tone="sand"/>
  {chars.map((ch,i)=>{const x=x0+i*w,b=BYTES(ch);return <g key={i} className={'pop '+d(i*1.5)}>
   <rect className={(b>1?'f-cream':'f-white')+' s-ink'} x={x+2} y={14} width={w-4} height="36" rx="6"/>
   <text className="mono f-ink" x={x+w/2} y={38} fontSize="15" textAnchor="middle">{shown(ch)}</text>
   <text className="mono f-ink" x={x+w/2} y={64} fontSize="10" textAnchor="middle">{ch.codePointAt(0)}</text>
   {!moved&&Array.from({length:b},(_,k)=><rect key={k} className="f-slate" x={x+w/2-b*4+k*8+1} y={72} width="6" height="6" rx="1"/>)}
   {moved&&<><path className="s-ink-s" d={`M${x+w/2} 70v10`}/><rect className="f-moss s-ink" x={x+2} y={84} width={w-4} height="36" rx="6"/>
    <text className="mono f-white" x={x+w/2} y={108} fontSize="15" textAnchor="middle">{shown(moved[i]??'')}</text></>}
  </g>;})}
  {!moved&&<Tag x={160} y={112} text={`${plural([...m.text].length,'char')} · ${plural(total,'byte')}`} tone="moss" className={'drop '+d(chars.length*1.5)}/>}
  {[...m.text].length>8&&<Note text={`The first 8 of ${[...m.text].length} characters.`}/>}
 </>};
}};

// ---------- cs.float-limits: the ledger ----------
const DRIFT=/\d\.\d*?(\d)\1{4,}\d*|\d\.\d{12,}/;
const floatLimits:SceneDef={title:'The ledger',draw:r=>{
 const back=returned(r),rows=[...outLines(r),...(back?[back.t==='int'&&called(r,'to_cents')?`${back.v} cents`:plain(back)]:[])].slice(0,6);
 if(!rows.length)return {say:r?'Nothing written in the ledger.':'A ledger of sums. Some decimals cannot be stored exactly, and the error shows.',svg:<><Ground tone="sand"/>
  <rect className="f-white s-ink" x="70" y="18" width="180" height="120" rx="8"/><Note text={r?'Print or return a total to fill the ledger.':IDLE}/></>};
 const drift=rows.filter(l=>DRIFT.test(l));
 return {say:`${rows.join('; ')}.${drift.length?` ${drift.length===1?'One line has':`${drift.length} lines have`} the tiny error of a float that is not exact.`:' Every amount here is exact.'}`,svg:<>
  <Ground tone="sand"/>
  <rect className="f-white s-ink" x="40" y="12" width="240" height={rows.length*22+16} rx="8"/>
  {rows.map((l,i)=>{const bad=DRIFT.test(l);return <g key={i} className={'type '+d(i*2)}>
   <text className={'mono '+(bad?'f-clay':'f-ink')} x="54" y={32+i*22} fontSize="13">{fit(l,26)}</text>
   {/\d/.test(l)&&<text className={'mono '+(bad?'f-clay':'f-moss')} x="266" y={32+i*22} fontSize="13" textAnchor="end">{bad?'≈':'='}</text>}
  </g>;})}
 </>};
}};

// ---------- searching: the archive shelf ----------
function shelfOf(r:SceneRun|null):{items:PyNode[];target:PyNode|null}|null{
 const args=callArgs(r);
 if(args[0]?.t==='list')return {items:args[0].items,target:args[1]??null};
 const list=pick(r?.vars,['shelf','items','numbers','records'],['list']);
 return list?{items:listItems(list),target:null}:null;
}
function Shelf({items,looked,found,order}:{items:PyNode[];looked:Set<number>;found:number;order?:Map<number,number>}){
 const n=Math.min(items.length,12),w=Math.min(44,288/Math.max(1,n)),x0=160-w*n/2;
 return <>{items.slice(0,n).map((it,i)=>{const x=x0+i*w,tone=i===found?'f-moss':looked.has(i)?'f-cream':'f-white';return <g key={i} className={'pop '+d(i)}>
  <rect className={tone+' s-ink'} x={x+2} y={70} width={w-4} height="40" rx="5"/>
  <text className={'mono '+(i===found?'f-white':'f-ink')} x={x+w/2} y={95} fontSize={w<30?9:11} textAnchor="middle">{fit(plain(it),Math.max(2,Math.floor(w/7)))}</text>
  <text className="mono f-ink" x={x+w/2} y={124} fontSize="9" textAnchor="middle">{i}</text>
  {order?.has(i)&&<g className={'drop '+d(4+order.get(i)!*3)}><circle className="f-amber s-ink-s" cx={x+w/2} cy={56} r="9"/><text className="mono f-ink" x={x+w/2} y={60} fontSize="11" textAnchor="middle">{order.get(i)}</text></g>}
 </g>;})}
 <path className="s-ink" d={`M${x0-6} 112h${n*w+12}`}/></>;
}
const linearSearch:SceneDef={title:'The archive shelf',draw:r=>{
 const s=shelfOf(r),back=ints(returned(r)??undefined);
 if(!s)return {say:r?'No shelf of items to search yet.':'A shelf of records, searched one at a time from the left.',svg:<><Ground tone="sand"/>
  <Shelf items={['?','?','?','?'].map(v=>({t:'str',v}))} looked={new Set()} found={-1}/><Note text={r?'Search a list to see the looks.':IDLE}/></>};
 let at=back.length===2?back[0]:numOf(pick(r?.vars,['found_at','found','at','position']))??-1,looks=back.length===2?back[1]:numOf(pick(r?.vars,['looks','steps','tries']));
 if(looks===null&&s.target){const k=s.items.findIndex(it=>plain(it)===plain(s.target!));at=k;looks=k<0?s.items.length:k+1;}
 looks=clamp(looks??0,0,s.items.length);
 const looked=new Set(Array.from({length:looks},(_,i)=>i)),n=Math.min(s.items.length,12),w=Math.min(44,288/Math.max(1,n));
 return {say:`${plural(looks,'look')} along a shelf of ${plural(s.items.length,'item')}: ${at>=0?`found at position ${at}`:'not there'}${s.target?`, looking for ${plain(s.target)}`:''}.`,svg:<>
  <Ground tone="sand"/>
  <Shelf items={s.items} looked={looked} found={at}/>
  {looks>0&&<Hero x={clamp(160-w*n/2+(looks-1)*w+w/2,20,300)} y={64} className={'drop '+d(looks)}/>}
  {s.items.length>12&&<Note text={`The first 12 of ${s.items.length} items.`}/>}
 </>};
}};

/** The middles a binary search looks at, in order, with where it ends. */
function halvings(items:PyNode[],target:PyNode):{looks:number[];at:number}{
 const key=(n:PyNode)=>numOf(n)??plain(n),t=key(target),looks:number[]=[];let low=0,high=items.length-1;
 while(low<=high&&looks.length<40){const mid=Math.floor((low+high)/2),v=key(items[mid]);looks.push(mid);if(v===t)return {looks,at:mid};if(v<t)low=mid+1;else high=mid-1;}
 return {looks,at:-1};
}
const binarySearch:SceneDef={title:'Halving the shelf',draw:r=>{
 const s=shelfOf(r);
 if(!s)return {say:r?'No sorted shelf to search yet.':'A sorted shelf: look at the middle, and throw away the half that cannot hold it.',svg:<><Ground tone="slate"/>
  <Shelf items={[3,8,15,21,30].map(v=>({t:'int',v:String(v)}))} looked={new Set()} found={-1}/><Note text={r?'Search a sorted list to see the halving.':IDLE}/></>};
 let looks:number[]=[],at=-1;
 const seen=outLines(r).map(l=>/look at (\S+)/.exec(l)?.[1]).filter((v):v is string=>!!v);
 if(s.target){({looks,at}=halvings(s.items,s.target));}
 else if(seen.length){looks=seen.map(v=>s.items.findIndex(it=>plain(it)===v)).filter(i=>i>=0);const m=numOf(pick(r?.vars,['middle']));at=m!==null&&looks.includes(m)&&!r?.error?m:-1;}
 const order=new Map(looks.map((i,k)=>[i,k+1]));
 const back=ints(returned(r)??undefined),differs=back.length===2&&s.target&&(back[1]!==looks.length||back[0]!==at);
 return {say:`${looks.length?`Looked at ${looks.map(i=>plain(s.items[i])).join(', then ')}: `:''}${at>=0?`found in ${plural(looks.length,'look')}`:'not there'}, out of ${plural(s.items.length,'item')}.${differs?` Your function returned [${back.join(', ')}], but halving finds ${at} in ${plural(looks.length,'look')}.`:''}`,svg:<>
  <Ground tone="slate"/>
  <Shelf items={s.items} looked={new Set(looks)} found={at} order={order}/>
  {s.items.length>12&&<Note text={`The first 12 of ${s.items.length} items.`}/>}
 </>};
}};

// ---------- cs.counting-steps: two searches race ----------
function rowsOf(r:SceneRun|null):number[][]{
 const back=returned(r),args=callArgs(r);
 if(back?.t==='list'&&back.items.every(x=>x.t==='list'))return back.items.map(x=>ints(x)).filter(x=>x.length===3);
 const n=numOf(args[0]),v=numOf(back??undefined);
 if(n!==null&&v!==null){if(called(r,'binary_worst'))return [[n,n,v]];if(called(r,'linear_worst'))return [[n,v,Math.max(0,Math.floor(Math.log2(n))+(n>0?1:0))]];}
 return outLines(r).map(l=>l.trim().split(/\s+/).map(Number)).filter(p=>p.length>=2&&p.every(Number.isFinite)).map(p=>p.length>=3?p.slice(0,3):[p[0],p[0],p[1]]);
}
const countingSteps:SceneDef={title:'The step race',draw:r=>{
 const rows=rowsOf(r).slice(0,5);
 if(!rows.length)return {say:r?'No sizes to compare yet.':'For each size of list: the most looks a linear search needs, beside the most a binary search needs.',svg:<><Ground tone="sand"/>
  <Note text={r?'Print or return sizes and steps to race them.':IDLE}/></>};
 const most=Math.max(1,...rows.map(x=>x[1]));
 return {say:rows.map(([s,l,b])=>`${plural(s,'item')}: ${plural(l,'look')} one by one, ${plural(b,'look')} by halving`).join('; ')+'.',svg:<>
  <rect className="bg2" width="320" height="180" rx="16"/>
  {rows.map(([s,l,b],i)=>{const y=8+i*25;return <g key={i} className={'pop '+d(i*2)}>
   <text className="mono f-ink" x="64" y={y+14} fontSize="11" textAnchor="end">{fit(String(s),9)}</text>
   <rect className="f-clay grow" x="72" y={y+2} width={Math.max(2,l/most*190)} height="8" rx="2"/>
   <rect className="f-moss grow" x="72" y={y+12} width={Math.max(2,b/most*190)} height="8" rx="2"/>
   <text className="mono f-ink" x={78+Math.max(2,l/most*190)} y={y+10} fontSize="9">{l}</text>
   <text className="mono f-ink" x={78+Math.max(2,b/most*190)} y={y+20} fontSize="9">{b}</text>
  </g>;})}
  <text className="mono f-ink" x="72" y="170" fontSize="10">one by one</text><rect className="f-clay" x="58" y="162" width="10" height="9" rx="2"/>
  <text className="mono f-ink" x="190" y="170" fontSize="10">halving</text><rect className="f-moss" x="176" y="162" width="10" height="9" rx="2"/>
 </>};
}};

export const CS_SCENES:Record<string,SceneDef>={
 'cs.binary':binary,'cs.hexadecimal':hexadecimal,'cs.text-encoding':textEncoding,'cs.float-limits':floatLimits,
 'cs.linear-search':linearSearch,'cs.binary-search':binarySearch,'cs.counting-steps':countingSteps,
};

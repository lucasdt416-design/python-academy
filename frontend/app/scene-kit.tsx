// The scene kit: what a lesson scene gets from a run, and the small drawings scenes are built from.
// Scenes themselves are in lesson-scenes.tsx. Everything is SVG with classes from style.css (the page
// policy allows no style attributes); positions are SVG attributes. Motion is CSS, and only runs under
// prefers-reduced-motion: no-preference.
import type {ReactNode} from 'react';

/** A value from the worker's snapshot (public/python-worker.js, SNAPSHOT): a plain copy, never live. */
export type PyNode =
 | {t:'none'} | {t:'bool';v:boolean} | {t:'int';v:string} | {t:'float';v:string} | {t:'str';v:string}
 | {t:'list'|'tuple'|'set';n:number;items:PyNode[]} | {t:'dict';n:number;entries:[PyNode,PyNode][]}
 | {t:'function';name:string;params:string[]} | {t:'module';name:string} | {t:'class';name:string}
 | {t:'object';cls:string;fields:Record<string,PyNode>} | {t:'other';type:string} | {t:'more'};
export type Vars = Record<string,PyNode>;
/** One run, as a scene sees it. vars is null when the run could not report them (a check, an old worker). */
export type SceneRun = {output:string;inputs:string[];vars:Vars|null;error:string|null;label?:string;key:number};

// ---------- Reading a run ----------
export const outLines = (r:SceneRun|null):string[] => r ? r.output.replace(/\n$/,'').split('\n').filter((l,i,a)=>l!==''||i<a.length-1).filter(l=>l!=='') : [];
export const isNum = (s:string|undefined):boolean => s!==undefined && /^\s*-?\d+(\.\d+)?(e-?\d+)?\s*$/i.test(s);
export const toNum = (s:string|undefined):number|null => isNum(s) ? Number(s) : null;
export const numbers = (lines:string[]):number[] => lines.filter(isNum).map(Number);
export const bools = (lines:string[]):(boolean|null)[] => lines.map(l=>l.trim()==='True'?true:l.trim()==='False'?false:null);
/** A value as Python would show it with print(). */
export function show(n:PyNode|undefined, quoted=false):string{
 if(!n)return '';
 switch(n.t){
  case 'none':return 'None';
  case 'bool':return n.v?'True':'False';
  case 'int':case 'float':return n.v;
  case 'str':return quoted?`'${n.v}'`:n.v;
  case 'list':return '['+n.items.map(x=>show(x,true)).join(', ')+(n.n>n.items.length?', …':'')+']';
  case 'tuple':return '('+n.items.map(x=>show(x,true)).join(', ')+(n.items.length===1?',':'')+')';
  case 'set':return n.n?'{'+n.items.map(x=>show(x,true)).join(', ')+'}':'set()';
  case 'dict':return '{'+n.entries.map(([k,v])=>show(k,true)+': '+show(v,true)).join(', ')+'}';
  case 'function':return `${n.name}(${n.params.join(', ')})`;
  case 'module':return `module ${n.name}`;
  case 'class':return `class ${n.name}`;
  case 'object':return `${n.cls}(…)`;
  case 'other':return `(${n.type})`;
  default:return '…';
 }
}
export const numOf = (n:PyNode|undefined):number|null => n&&(n.t==='int'||n.t==='float')&&isNum(n.v)?Number(n.v):null;
export const strOf = (n:PyNode|undefined):string|null => n&&n.t==='str'?n.v:null;
/** The first variable, by any of these names, of one of these kinds. */
export function pick(vars:Vars|null|undefined,names:string[],kinds?:PyNode['t'][]):PyNode|undefined{
 if(!vars)return undefined;
 for(const name of names){const v=vars[name];if(v&&(!kinds||kinds.includes(v.t)))return v;}
 return undefined;
}
/** Every variable of these kinds, in the order the program made them. */
export const ofKind = (vars:Vars|null|undefined,kinds:PyNode['t'][]):[string,PyNode][] => vars?Object.entries(vars).filter(([,v])=>kinds.includes(v.t)):[];
export const listItems = (n:PyNode|undefined):PyNode[] => n&&(n.t==='list'||n.t==='tuple'||n.t==='set')?n.items:[];
/** Text broken into lines of at most `width` characters, at spaces where it can; at most `max` lines. */
export function wrap(s:string,width:number,max=3):string[]{
 const words=s.split(' '),lines:string[]=[];let line='';
 for(const w of words){const next=line?line+' '+w:w;if(next.length<=width){line=next;continue;}if(line)lines.push(line);line=w.length>width?w.slice(0,width):w;}
 if(line)lines.push(line);
 return lines.length>max?[...lines.slice(0,max-1),fit(lines.slice(max-1).join(' '),width)]:lines;
}
/** Text cut to fit a width in characters. */
export const fit = (s:string,n:number):string => s.length>n?s.slice(0,Math.max(1,n-1))+'…':s;
export const plural = (n:number,one:string,many=one+'s'):string => `${n} ${n===1?one:many}`;
export const clamp = (n:number,lo:number,hi:number):number => Math.max(lo,Math.min(hi,n));
/** Animation delay class: d0 to d15, 0.15 seconds apart. */
export const d = (i:number):string => 'd'+clamp(Math.round(i),0,15);

// ---------- Drawings ----------
export function Ground({tone='moss'}:{tone?:'moss'|'sand'|'slate'}){
 return <><rect className={tone==='sand'?'bg2':tone==='slate'?'bg3':'bg1'} width="320" height="180" rx="16"/><path className="f-moss-l" d="M0 150Q90 136 170 148T320 142V180H0Z"/></>;
}
/** A hero, standing at (x, y) = feet. */
export function Hero({x,y,tone='plum',className}:{x:number;y:number;tone?:'plum'|'slate'|'clay'|'moss';className?:string}){
 return <g className={className} transform={`translate(${x} ${y})`}>
  <path className={`f-${tone} s-ink`} d="M-17 0q0-38 17-38t17 38z"/>
  <circle className="f-amber-l s-ink" cx="0" cy="-50" r="13"/>
  <circle className="f-ink" cx="-4" cy="-51" r="1.6"/><circle className="f-ink" cx="4" cy="-51" r="1.6"/>
  <path className="s-ink-s" d="M-4 -45q4 3 8 0"/>
 </g>;
}
/** A name tag on a string, centred on x. */
export function Tag({x,y,text,className,tone='white'}:{x:number;y:number;text:string;className?:string;tone?:'white'|'cream'|'clay'|'moss'}){
 const w=Math.max(34,text.length*7.4+18);
 return <g className={className}><rect className={`f-${tone} s-ink`} x={x-w/2} y={y-13} width={w} height="24" rx="6"/><text className={'mono '+(tone==='clay'||tone==='moss'?'f-white':'f-ink')} x={x} y={y+4} fontSize="13" textAnchor="middle">{text}</text></g>;
}
/** A speech bubble with its tail at (x, y + h). */
export function Bubble({x,y,w,text,className,size=12,right=false}:{x:number;y:number;w:number;text:string;className?:string;size?:number;right?:boolean}){
 const tail=right?`M${x+w-22} ${y+26}l8 10 4-10`:`M${x+14} ${y+26}l-4 10 10-10`;
 return <g className={className}><rect className="f-white s-ink" x={x} y={y} width={w} height="26" rx="10"/><path className="f-white s-ink" d={tail}/><text className="mono f-ink" x={x+10} y={y+17} fontSize={size}>{fit(text,Math.floor((w-16)/(size*0.62)))}</text></g>;
}
export function Coin({x,y,className}:{x:number;y:number;className?:string}){
 return <g className={className}><circle className="f-amber s-ink-s" cx={x} cy={y} r="6"/><path className="s-ink-s" d={`M${x-2} ${y-2}h4`}/></g>;
}
export function Lamp({x,y,on,label,className}:{x:number;y:number;on:boolean|null;label:string;className?:string}){
 return <g className={className}>
  <path className="s-ink" d={`M${x} ${y+16}v12`}/><circle className={(on?'f-amber lamp-on':on===false?'f-slate':'f-white')+' s-ink'} cx={x} cy={y} r="15"/>
  <text className="mono f-ink" x={x} y={y+44} fontSize="11" textAnchor="middle">{fit(label,10)}</text>
 </g>;
}
/** An item, drawn by what its name sounds like; anything else is a parcel with its name. */
export function Item({x,y,name,className,size=1}:{x:number;y:number;name:string;className?:string;size?:number}){
 const n=name.toLowerCase();
 const kind=/lantern|lamp|torch|candle|light/.test(n)?'lantern':/sword|blade|dagger|knife/.test(n)?'sword':/key/.test(n)?'key':/rope|string|vine/.test(n)?'rope':/map|scroll|note|letter|paper|book/.test(n)?'map':/shield/.test(n)?'shield':/potion|bottle|water|flask|tea/.test(n)?'potion':/apple|bread|food|cake|berry|snack|pie|fruit|cheese/.test(n)?'apple':/coin|gold|gem|jewel|crystal|ruby|treasure/.test(n)?'gem':/bow|arrow|wand|staff|stick/.test(n)?'wand':'parcel';
 const body:Record<string,ReactNode>={
  lantern:<><rect className="f-amber-l s-ink-s" x="-7" y="-14" width="14" height="16" rx="3"/><path className="s-ink-s" d="M-5 -14v-4h10v4M0 -18v-4"/><circle className="f-amber" cx="0" cy="-6" r="3"/></>,
  sword:<><path className="f-white s-ink-s" d="M-2 -24h4v18h-4z"/><path className="f-amber s-ink-s" d="M-8 -6h16v3h-16z"/><path className="f-plum s-ink-s" d="M-2 -3h4v6h-4z"/></>,
  key:<><circle className="f-amber s-ink-s" cx="-6" cy="-10" r="5"/><path className="s-ink" d="M-1 -10h12M7 -10v4M10 -10v3"/></>,
  rope:<><circle className="f-cream s-ink-s" cx="0" cy="-9" r="9"/><circle className="s-ink-s" cx="0" cy="-9" r="4.5"/></>,
  map:<><path className="f-cream s-ink-s" d="M-11 -18l7 3 8-3 7 3v16l-7-3-8 3-7-3z"/><path className="s-clay-w" d="M-6 -9l4 4m0-4l-4 4"/></>,
  shield:<path className="f-slate s-ink-s" d="M-9 -20h18v8q0 9-9 13q-9-4-9-13z"/>,
  potion:<><path className="f-plum s-ink-s" d="M-3 -20h6v6l6 8q2 6-6 6h-6q-8 0-6-6l6-8z"/><path className="s-ink-s" d="M-4 -20h8"/></>,
  apple:<><circle className="f-clay s-ink-s" cx="0" cy="-8" r="8"/><path className="s-moss" d="M0 -16q2-5 6-6"/></>,
  gem:<path className="f-amber-l s-ink-s" d="M-9 -12l4-6h10l4 6-9 12z"/>,
  wand:<><path className="s-ink-w" d="M-8 0l14-18"/><path className="f-amber" d="M8 -22l2 4 4 1-4 2-1 4-2-4-4-1 4-2z"/></>,
  parcel:<><rect className="f-cream s-ink-s" x="-10" y="-18" width="20" height="18" rx="3"/><path className="s-ink-s" d="M-10 -10h20M0 -18v18"/></>,
 };
 return <g className={className} transform={`translate(${x} ${y}) scale(${size})`}>{body[kind]}</g>;
}
/** A box labelled with a variable's name, holding its value. */
export function VarBox({x,y,name,value,className,w=96}:{x:number;y:number;name:string;value:string;className?:string;w?:number}){
 return <g className={className}>
  <rect className="f-cream s-ink" x={x} y={y} width={w} height="34" rx="6"/>
  <rect className="f-white s-ink-s" x={x+8} y={y-10} width={Math.min(w-16,name.length*7+12)} height="16" rx="4"/>
  <text className="mono f-ink" x={x+14} y={y+2} fontSize="11">{fit(name,Math.floor((w-24)/7))}</text>
  <text className="mono f-clay" x={x+10} y={y+25} fontSize="12">{fit(value,Math.floor((w-16)/7.3))}</text>
 </g>;
}
/** Lines of text written one after another, like a typewriter. */
export function Lines({x,y,lines,size=12,gap=18,max=6,width=36,tone='f-ink',start=0}:{x:number;y:number;lines:string[];size?:number;gap?:number;max?:number;width?:number;tone?:string;start?:number}){
 const shown=lines.slice(0,max);
 return <>{shown.map((line,i)=><text key={i} className={`mono ${tone} type ${d(start+i*2)}`} x={x} y={y+i*gap} fontSize={size}>{fit(line,width)}</text>)}{lines.length>max&&<text className={`mono f-ink type ${d(start+max*2)}`} x={x} y={y+max*gap} fontSize={size}>… {plural(lines.length-max,'more line')}</text>}</>;
}
/** A plain note across the bottom, for an idle scene or a run that stopped. */
export function Note({text}:{text:string}){
 return <text className="sans f-ink scene-note" x="160" y="172" fontSize="11" textAnchor="middle">{text}</text>;
}

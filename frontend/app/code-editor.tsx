'use client';
import {type KeyboardEvent,type RefObject,useRef} from 'react';

/* The plain textarea editor, with a line-number gutter and a highlight layer behind it
 * (docs/plan/lesson-feedback.md section 5; no editor library). Lines do not wrap, so line N of the
 * code is always row N of the gutter and of the highlight. The layers only copy the textarea's
 * scroll position, which is set from script, never written as a style attribute. */
export default function CodeEditor({code,onChange,disabled,errorLine,describedBy,editor}:{code:string;onChange:(value:string)=>void;disabled:boolean;errorLine:number|null;describedBy:string;editor:RefObject<HTMLTextAreaElement|null>}){
 const gutter=useRef<HTMLDivElement>(null),layer=useRef<HTMLDivElement>(null);
 const lines=code.split('\n').length;
 function follow(){const t=editor.current;if(!t)return;for(const el of [gutter.current,layer.current])if(el)el.scrollTop=t.scrollTop;if(layer.current)layer.current.scrollLeft=t.scrollLeft;}
 function tab(e:KeyboardEvent<HTMLTextAreaElement>){if(e.key==='Tab'&&!e.shiftKey){e.preventDefault();const target=e.currentTarget,start=target.selectionStart,end=target.selectionEnd;onChange(code.slice(0,start)+'    '+code.slice(end));requestAnimationFrame(()=>{target.selectionStart=target.selectionEnd=start+4;});}}
 return <div className={'code-editor'+(errorLine?' has-error':'')}>
  <div className="code-gutter" ref={gutter} aria-hidden="true">{Array.from({length:lines},(_,i)=><div key={i} className={i+1===errorLine?'gutter-line error':'gutter-line'}>{i+1===errorLine&&<span className="gutter-mark">▶</span>}{i+1}</div>)}</div>
  <div className="code-area">
   <div className="code-highlight" ref={layer} aria-hidden="true">{errorLine!==null&&Array.from({length:lines},(_,i)=><div key={i} className={i+1===errorLine?'code-line error':'code-line'}>{' '}</div>)}</div>
   <textarea id="code" ref={editor} spellCheck={false} wrap="off" rows={11} value={code} disabled={disabled} aria-describedby={describedBy} onChange={e=>onChange(e.target.value)} onScroll={follow} onKeyDown={tab}/>
  </div>
 </div>;
}

/** Puts the cursor at the start of a line and scrolls it into view. Only called when the learner asks. */
export function goToLine(editor:HTMLTextAreaElement,line:number){
 const start=editor.value.split('\n').slice(0,line-1).reduce((n,text)=>n+text.length+1,0);
 editor.focus();editor.setSelectionRange(start,start);
 const height=parseFloat(getComputedStyle(editor).lineHeight)||24;
 editor.scrollTop=Math.max(0,(line-1)*height-editor.clientHeight/3);
}

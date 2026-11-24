// Lesson text with the Python in it shown as code (prose-runs.ts finds it).
import {Fragment, type ReactNode} from 'react';
import {proseRuns} from './prose-runs';

export function prose(text: string): ReactNode {
 return <>{proseRuns(text).map((r, i) => r.code ? <code key={i}>{r.text}</code> : <Fragment key={i}>{r.text}</Fragment>)}</>;
}

type Block = {kind: 'p'; text: string} | {kind: 'ol' | 'ul'; items: string[]};

/** Lesson text in blocks: a blank line starts a paragraph, lines starting "1. " are steps, lines starting "- " a list. */
export function blocks(text: string): Block[] {
 const out: Block[] = [];
 for (const chunk of text.split(/\n\s*\n/)) {
  let open: Block | null = null;   // the block this chunk's next line can join
  for (const line of chunk.split('\n').map(l => l.trim()).filter(Boolean)) {
   const m = /^(?:(\d+)\.|-)\s+(.*)$/.exec(line), kind = m ? (m[1] ? 'ol' : 'ul') : 'p';
   if (open && open.kind === kind && !(kind === 'ol' && m![1] === '1')) {
    if (open.kind === 'p') open.text += ' ' + line; else open.items.push(m![2]);
   } else {
    open = kind === 'p' ? {kind: 'p', text: line} : {kind: kind as 'ol' | 'ul', items: [m![2]]};
    out.push(open);
   }
  }
 }
 return out;
}

/** Lesson text as paragraphs and lists. One plain paragraph stays a single <p className>, as before. */
export function Prose({text, className}: {text: string; className?: string}) {
 const parts = blocks(text);
 if (parts.length === 1 && parts[0].kind === 'p') return <p className={className}>{prose(parts[0].text)}</p>;
 return <div className={['prose-blocks', className].filter(Boolean).join(' ')}>{parts.map((b, i) => b.kind === 'p'
  ? <p key={i}>{prose(b.text)}</p>
  : b.kind === 'ol' ? <ol key={i}>{b.items.map((t, k) => <li key={k}>{prose(t)}</li>)}</ol>
  : <ul key={i}>{b.items.map((t, k) => <li key={k}>{prose(t)}</li>)}</ul>)}</div>;
}

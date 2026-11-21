// Lesson text with the Python in it shown as code (prose-runs.ts finds it).
import {Fragment, type ReactNode} from 'react';
import {proseRuns} from './prose-runs';

export function prose(text: string): ReactNode {
 return <>{proseRuns(text).map((r, i) => r.code ? <code key={i}>{r.text}</code> : <Fragment key={i}>{r.text}</Fragment>)}</>;
}

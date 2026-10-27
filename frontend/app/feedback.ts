/* Lesson feedback engine, first part (ENG-04, docs/plan/lesson-feedback.md sections 4, 5, 7 and 8).
 * Pure functions: what the worker or the check reported goes in, what the learner reads comes out.
 * They run in the browser only. Nothing here sends the learner's code or Python's message anywhere.
 */

export type Result = 'passed' | 'needs_work' | 'execution_error' | 'unsupported' | 'service_error';
export const RESULTS: readonly Result[] = ['passed', 'needs_work', 'execution_error', 'unsupported', 'service_error'];

/** A Python error as the worker reports it: the type, the line in the learner's code, and Python's last line. */
export type PythonError = {type: string | null; line: number | null; message: string};
/** The page stopped the program, so Python has no message. */
export type Stop = {stop: 'timeout' | 'output_limit'};

export type Explanation = {
 id: string;
 title: string;
 /** Plain words, with code between backticks. */
 text: string;
 line: number | null;
 /** Where to look, as text, so nothing depends on seeing the highlight: "Line 3" or "On or just before line 3". */
 where: string | null;
};

// The learner's code is the file "<exec>". Pyodide's own frames come first and are ignored; an error
// inside a function reports the line in the function, which is the last "<exec>" frame.
const EXEC_LINE = /File "<exec>", line (\d+)/g;

/** Type, line and message from the worker's error text (String(error) of a Pyodide PythonError). */
export function parseError(raw: string, type: string | null = null): PythonError {
 const message = raw.trimEnd().split('\n').pop()?.trim() ?? '';
 const line = [...raw.matchAll(EXEC_LINE)].map(m => Number(m[1])).pop() ?? null;
 return {type: type ?? /^([A-Za-z_][\w.]*):/.exec(message)?.[1] ?? null, line, message};
}

/** Python's own message, as Python would show it for the learner's file: Pyodide's frames are left out. */
export function pythonMessage(raw: string): string {
 const lines = raw.trimEnd().split('\n');
 const first = lines.findIndex(l => l.startsWith('  File "<exec>"'));
 if (first < 0) return lines.at(-1)?.trim() ?? '';
 const traceback = lines.slice(first).filter(l => !l.startsWith('  File "<academy>"'));
 // A run-time error has frames "in <module>"; a syntax error has only the line and its marker.
 return (lines[first].includes(', in ') ? ['Traceback (most recent call last):', ...traceback] : traceback).join('\n');
}

/** Built-in names a learner meets early. All lowercase, as Python spells them. */
const BUILTINS = ['print', 'input', 'str', 'int', 'float', 'len', 'range', 'list', 'dict', 'bool', 'type', 'round', 'abs', 'min', 'max', 'sum'];

/** Names the learner's code gives a value to (variables, functions, parameters and loop variables). */
export function definedNames(code: string): string[] {
 const names = new Set<string>();
 for (const m of code.matchAll(/^[ \t]*([A-Za-z_]\w*)[ \t]*=(?!=)/gm)) names.add(m[1]);
 for (const m of code.matchAll(/^[ \t]*def[ \t]+([A-Za-z_]\w*)[ \t]*\(([^)]*)\)/gm)) {
  names.add(m[1]);
  for (const p of m[2].split(',')) if (/^\s*[A-Za-z_]\w*/.test(p)) names.add(p.trim().split(/[\s=:]/)[0]);
 }
 for (const m of code.matchAll(/^[ \t]*for[ \t]+([A-Za-z_]\w*)[ \t]+in\b/gm)) names.add(m[1]);
 return [...names];
}

function edits(a: string, b: string): number {
 let row = Array.from({length: b.length + 1}, (_, i) => i);
 for (let i = 1; i <= a.length; i++) {
  const next = [i];
  for (let j = 1; j <= b.length; j++) next[j] = Math.min(row[j] + 1, next[j - 1] + 1, row[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  row = next;
 }
 return row[b.length];
}

/** A name the learner probably meant: one they defined, one or two edits away, or else a built-in
 * that Python itself suggested ("Did you mean: 'print'?"). Python also suggests names learners
 * have not met, such as help for hello, so only the built-ins listed above are passed on. */
export function closestName(name: string, code: string, message = ''): string | null {
 let best: string | null = null, distance = 3;
 for (const candidate of definedNames(code)) {
  const d = edits(name, candidate);
  // Never suggest the name itself, or a name as different as it is long ("x" and "y").
  if (candidate !== name && d < distance && d < Math.max(name.length, candidate.length)) { best = candidate; distance = d; }
 }
 const suggested = /Did you mean: '([^']+)'\?/.exec(message)?.[1];
 return best ?? (suggested && BUILTINS.includes(suggested) ? suggested : null);
}

type Context = {code: string; unit: number};
type Values = {line: number | null; [key: string]: string | number | null};
type Translation = {
 id: string;
 /** The first unit whose lessons can produce this error. Earlier units get the general message instead. */
 unit: number;
 title: string;
 text: string;
 /** Values for the template, or null when this translation does not apply. */
 match: (error: PythonError, context: Context) => Values | null;
};

const quoted = (message: string) => /name '([^']+)' is not defined/.exec(message)?.[1] ?? null;
const lineOf = (code: string, line: number | null) => line ? code.split('\n')[line - 1] ?? '' : '';
const is = (type: string, pattern: RegExp) => (e: PythonError) => e.type === type && pattern.test(e.message) ? {line: e.line} : null;

/** Section 4 of the specification, in the same order. The first match wins. */
export const TRANSLATIONS: readonly Translation[] = [
 {id: 'unterminated-string', unit: 1, title: 'A message is missing its closing quote',
  text: 'On line {line}, a text message starts with a quote but does not end with one. Add the matching quote before the closing parenthesis.',
  match: is('SyntaxError', /unterminated string literal/)},
 {id: 'never-closed', unit: 1, title: 'A parenthesis is still open',
  text: 'The `(` on line {line} has no matching `)`. Python may notice this on a later line. Add the `)` at the end of that instruction.',
  match: is('SyntaxError', /'\(' was never closed/)},
 {id: 'colon', unit: 1, title: 'This line needs a colon',
  text: 'Lines that start a block, like `if path == "left"`, end with `:`. Add a colon at the end of line {line}.',
  match: is('SyntaxError', /expected ':'/)},
 {id: 'equals', unit: 1, title: 'Comparing needs two equals signs',
  text: '`=` stores a value; `==` compares two values. On line {line}, use `==` to check whether they are equal.',
  match: is('SyntaxError', /Maybe you meant '==' or ':=' instead of '='/)},
 {id: 'quotes', unit: 1, title: 'Words need quotes to be text',
  text: 'Python read the words on line {line} as names, not text. Put the message inside matching quotes.',
  // Only when the line has no quotes at all: with quotes, a comma may really be missing.
  match: (e, {code}) => e.type === 'SyntaxError' && /Perhaps you forgot a comma/.test(e.message) && !/["']/.test(lineOf(code, e.line)) ? {line: e.line} : null},
 {id: 'syntax', unit: 1, title: 'Python cannot read line {line}',
  text: 'Check the quotes, parentheses and colons on line {line} and the line before it.',
  match: e => e.type === 'SyntaxError' ? {line: e.line} : null},
 {id: 'indent-block', unit: 1, title: 'The lines inside this `{block}` need indenting',
  text: 'Lines that belong to an `if` or `else` start with four spaces. Indent line {line}.',
  match: e => {
   const block = e.type === 'IndentationError' ? /expected an indented block after '(if|elif|else)' statement/.exec(e.message)?.[1] : null;
   return block ? {line: e.line, block} : null;
  }},
 {id: 'unexpected-indent', unit: 1, title: 'This line has extra spaces at the start',
  text: 'Line {line} starts with spaces but is not inside a block. Remove the spaces at the start of the line.',
  match: is('IndentationError', /unexpected indent/)},
 {id: 'tabs', unit: 1, title: 'Tabs and spaces are mixed',
  text: 'Use four spaces for each indent level, not a tab, on line {line}.',
  match: e => e.type === 'TabError' ? {line: e.line} : null},
 {id: 'name-case', unit: 1, title: 'Python is case-sensitive',
  text: 'Python knows `{known}`, not `{name}`. Use all lowercase on line {line}.',
  match: e => {
   const name = e.type === 'NameError' ? quoted(e.message) : null;
   const known = name && name !== name.toLowerCase() ? BUILTINS.find(b => b === name.toLowerCase()) : undefined;
   return name && known ? {line: e.line, name, known} : null;
  }},
 {id: 'name-typo', unit: 1, title: 'Python does not know `{name}`',
  text: 'Did you mean `{closest}`? Names must be spelled exactly the same each time.',
  match: (e, {code}) => {
   const name = e.type === 'NameError' ? quoted(e.message) : null;
   const closest = name ? closestName(name, code, e.message) : null;
   return name && closest ? {line: e.line, name, closest} : null;
  }},
 {id: 'name-unknown', unit: 1, title: 'Python does not know `{name}` yet',
  text: 'Give `{name}` a value earlier in the program, or, if `{name}` is meant to be text, put it in quotes.',
  match: e => {
   const name = e.type === 'NameError' ? quoted(e.message) : null;
   return name ? {line: e.line, name} : null;
  }},
 {id: 'concat', unit: 2, title: 'Text and numbers cannot be joined with `+`',
  text: 'On line {line}, one side of `+` is text and the other is a number. To add numbers, turn the text into a number with `int(...)`. To join text, turn the number into text with `str(...)`, or use an f-string.',
  match: is('TypeError', /can only concatenate str \(not "(int|float)"\) to str/)},
 {id: 'int-text', unit: 2, title: 'That text is not a whole number',
  text: '`int()` only turns text like `"7"` into a number. Check what was typed.',
  match: is('ValueError', /invalid literal for int\(\) with base 10/)},
 {id: 'zero', unit: 2, title: 'Division by zero',
  text: 'A number on line {line} was divided by 0. Check the value before dividing.',
  match: e => e.type === 'ZeroDivisionError' ? {line: e.line} : null},
 {id: 'replies', unit: 1, title: 'Not enough player replies',
  text: 'Your program asked for input more times than there are player replies. Add a reply below, or check the number of `input()` calls.',
  match: is('EOFError', /Add a player reply for each input\(\) call/)},
];

/** When the page stopped the program. These describe what the app did, so they apply in every unit. */
export const STOPS = {
 timeout: {id: 'timeout', title: 'Your program kept running',
  text: 'It did not finish within {seconds} seconds, usually because a loop never ends. Check that the loop’s condition can become false.'},
 output_limit: {id: 'output-limit', title: 'Too much output',
  text: 'Your program printed more than {limit} characters. Print less, or check for a loop that never ends.'},
} as const;

export const OTHER = {id: 'other', title: 'Python stopped on line {line}', untitled: 'Python stopped',
 text: 'Read Python’s message below, change one thing, and run it again.'};

function fill(template: string, values: Values) {
 return template.replace(/\{(\w+)\}/g, (_, key) => String(values[key] ?? ''));
}

/** Syntax errors are often noticed after the mistake, except an unclosed bracket or quote, which Python reports where it opened. */
function where(id: string, error: PythonError) {
 if (!error.line) return null;
 return error.type === 'SyntaxError' && id !== 'never-closed' && id !== 'unterminated-string' ? `On or just before line ${error.line}` : `Line ${error.line}`;
}

/** What to tell the learner about a Python error, in words from their unit. */
export function explain(error: PythonError | Stop, context: Context, limits = {seconds: 15, limit: '20,000'}): Explanation {
 if ('stop' in error) {
  const stop = STOPS[error.stop];
  return {id: stop.id, title: stop.title, text: fill(stop.text, {line: null, ...limits}), line: null, where: null};
 }
 for (const t of TRANSLATIONS) {
  const values = t.match(error, context);
  // A translation for a later unit would teach ahead, so the general message is used instead.
  if (values && t.unit <= context.unit) return {id: t.id, title: fill(t.title, values), text: fill(t.text, values), line: error.line, where: where(t.id, error)};
  if (values) break;
 }
 return {id: OTHER.id, title: error.line ? fill(OTHER.title, {line: error.line}) : OTHER.untitled, text: OTHER.text, line: error.line, where: where(OTHER.id, error)};
}

/** The editor line to highlight for a check result. Only a Python error names a line of code; an output line number is not one. */
export function checkLine(result: {failed?: {reason?: string; line?: number | null} | null}): number | null {
 return result.failed?.reason === 'error' ? result.failed.line ?? null : null;
}

/** Hints are a ladder of three, chosen one at a time; there is no fourth step and no solution (section 7). */
export const HINT_LEVELS = ['A nudge', 'A bigger hint', 'The approach'] as const;
export const HINT_BUTTONS = ['Show a nudge', 'Show a bigger hint', 'Show the approach'] as const;
/** Every other word the hint panel uses, so the snapshot test shows any change in review. */
export const HINT_TEXT = {
 aboutError: 'About this error', aboutErrorButton: 'Show a hint about this error',
 aboutCheck: 'About this check', aboutCheckButton: 'Show a hint about this check',
 similar: 'A similar example', similarButton: 'Show a similar example',
 done: 'That is every hint', noAnswer: 'There is no answer to reveal: the next step is yours.',
 suggested: 'Stuck? A hint is ready whenever you want one.',
 otherWays: 'Other ways to do it', otherWaysIntro: 'Your way passed. These also work:',
} as const;
/** After this many failed runs in a row, the hint button gets a gentle outline (decision 25). */
export const OUTLINE_AFTER = 2;

/** A hint offered first when one of its tags is the error or check rule being shown (content `error_hints`). */
export type ErrorHint = {tags: string[]; text: string};
export type Sample = {code: string; note: string};
export type HintStep = {key: string; label: string; button: string; text: string; code?: string};

/** Python error types are tags such as NameError; anything else is a check rule such as hello.words. */
export const isErrorTag = (tag: string) => /^[A-Z]\w*Error$/.test(tag);

/**
 * The hint to offer next (lesson-feedback.md section 7). First the hint tagged for the error or rule
 * being shown, if there is one and it has not been shown; then the ladder in order: a nudge, a bigger
 * hint, the approach; then, after the approach, a similar example from another context. Never a solution.
 */
export function nextHint(ladder: readonly string[], tagged: readonly ErrorHint[], active: string | null, shown: readonly string[], similar?: Sample | null): HintStep | null {
 const forActive = active ? tagged.findIndex(h => h.tags.includes(active)) : -1;
 if (active && forActive >= 0 && !shown.includes(`tag:${forActive}`)) {
  const error = isErrorTag(active);
  return {key: `tag:${forActive}`, label: error ? HINT_TEXT.aboutError : HINT_TEXT.aboutCheck, button: error ? HINT_TEXT.aboutErrorButton : HINT_TEXT.aboutCheckButton, text: tagged[forActive].text};
 }
 const level = ladder.slice(0, HINT_LEVELS.length).findIndex((_, i) => !shown.includes(`level:${i}`));
 if (level >= 0) return {key: `level:${level}`, label: HINT_LEVELS[level], button: HINT_BUTTONS[level], text: ladder[level]};
 if (similar && !shown.includes('similar')) return {key: 'similar', label: HINT_TEXT.similar, button: HINT_TEXT.similarButton, text: similar.note, code: similar.code};
 return null;
}

/** How each result state is labelled, in words as well as colour. "ran" is a run with no check. */
export const STATE_LABELS: Record<Result | 'ran', string> = {
 passed: 'Check passed',
 needs_work: 'Not yet',
 execution_error: 'Python stopped',
 unsupported: 'Not checked',
 service_error: 'Check unavailable',
 ran: 'Ran · not checked',
};

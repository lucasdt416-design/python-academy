// Finds the Python inside a lesson's plain sentences, by its shape: brackets, quotes, operators, calls,
// dotted names and error names, joined with the names and keywords right beside them. Used by prose.tsx.
// Lessons are written as plain text (unit 1's is frozen, backend/app/content.py), so it is found here.

const KEYWORDS = new Set(['for', 'in', 'if', 'elif', 'else', 'while', 'not', 'and', 'or', 'is', 'return', 'def', 'import', 'from', 'as', 'try', 'except', 'finally', 'with', 'class', 'raise', 'lambda', 'pass', 'break', 'continue', 'assert', 'True', 'False', 'None']);
const OPERATOR = /^(=|==|!=|<=|>=|<|>|\+=|-=|\*=|\/\/|%|\*\*|\+|-|\*|\/|\||&|->)$/;
const NAME = /^[A-Za-z_]\w*$/;
const bare = (w: string) => w.replace(/[.,;:]+$/, '');
/** Plain English words in a span: names that are neither keywords nor code-shaped. Code has few. */
const english = (span: string[]) => span.filter(x => /^[a-z]{2,}$/i.test(x.replace(/[()[\]{}.,;:]/g, '')) && (!KEYWORDS.has(bare(x)) || ['and', 'or', 'not'].includes(bare(x))) && !codeShaped(x.replace(/[()]/g, ''))).length;
/** A word that ends a sentence or clause: code never runs on past it. */
const ends = (w: string) => /[.;]$/.test(w) && !/\(\)\.$|\w\.\w+\.$/.test(w) === true && !/^\.\.\.$/.test(w);

/** A word that can only be code. */
export function codeShaped(word: string): boolean {
 const w = word.replace(/[.,;]+$/, '');
 if (!w) return false;
 if (/^\([A-Za-z]+$/.test(w) || /^[A-Za-z0-9]+\)$/.test(w)) return false;   // (a few words in brackets) is English   // (a word in brackets) is English
 if (/[()[\]{}"=_]/.test(w)) return true;                  // calls, lists, dicts, strings, assignments, snake_case
 if (/^[A-Za-z_]\w*\.[A-Za-z_]\w*/.test(w)) return true;   // pack.append, re.sub
 if (/^\.[a-z_]\w*\(/.test(w)) return true;                 // .group(1)
 if (/^[A-Z][A-Za-z]+(Error|Exception)$/.test(w)) return true; // ValueError, ZeroDivisionError
 if (/^(True|False|None)$/.test(w)) return true;
 if (/^#[0-9a-fA-F]{3,8}:?$/.test(w)) return true;          // #ff8800
 if (/^(try|except|else|finally|elif|if|for|while|def|class|with):$/.test(word)) return true;
 if (/^(\/\/|%|==|!=|<=|>=|\+=|-=|\*\*)$/.test(w)) return true;
 return false;
}

/** The text in pieces, each marked as code or not. Joining the pieces gives back the text exactly. */
export function proseRuns(text: string): {text: string; code: boolean}[] {
 const parts = text.split(/(\s+)/);
 const words = parts.filter((_, i) => i % 2 === 0);
 const code = words.map(codeShaped);
 for (let i = 0; i < words.length; i++) {
  if (code[i]) continue;
  const w = words[i], b = bare(w), after = words[i + 1] ?? '';
  if (OPERATOR.test(w) && (code[i - 1] || code[i + 1])) code[i] = true;
  else if (code[i - 1] && code[i + 1] && !ends(words[i - 1]) && !ends(w) && (OPERATOR.test(w) || w === 'in' || w === 'is' || (NAME.test(b) && w.endsWith(',')))) code[i] = true;
  else if (NAME.test(w) && OPERATOR.test(after) && (codeShaped(words[i + 2] ?? '') || /^["'\d[{(-]/.test(words[i + 2] ?? ''))) code[i] = true;
  else if (['for', 'if', 'elif', 'while', 'except', 'def'].includes(w) && NAME.test(bare(after)) || (w === 'except' && code[i + 1])) {
   // A Python line written in a sentence, ending in a colon: for room, item in rooms.items():
   const end = words.slice(i + 1, i + 8).findIndex(x => x.endsWith(':') && (codeShaped(x) || NAME.test(bare(x))));
   const inside = words.slice(i + 1, i + 2 + Math.max(end, 0));
   const stop = inside.slice(0, -1).some(ends) || !inside.some(codeShaped) || english(inside) > 2;
   if (end >= 0 && !stop) for (let k = i; k <= i + 1 + end; k++) code[k] = true;
  }
 }
 // Both sides of an operator belong to the code: score = score + 1, "Welcome, " + player. Twice, for chains.
 for (let pass = 0; pass < 2; pass++) for (let i = 0; i < words.length; i++) {
  if (OPERATOR.test(words[i]) && !code[i] && (code[i - 1] || code[i + 1])) code[i] = true;
  if (!(code[i] && OPERATOR.test(words[i]))) continue;
  const side = (j: number) => j >= 0 && j < words.length && !code[j] && (NAME.test(bare(words[j])) || /^-?\d+(\.\d+)?[.,;]?$/.test(words[j])) && !KEYWORDS.has(bare(words[j]));
  if (side(i - 1) && !ends(words[i - 1])) code[i - 1] = true;
  if (side(i + 1)) code[i + 1] = true;
 }
 for (let i = 0; i < words.length; i++) {
  if (!code[i]) continue;
  let depth = 0, k = i;
  for (; k < Math.min(words.length, i + 10); k++) {
   for (const ch of words[k]) depth += '([{'.includes(ch) ? 1 : ')]}'.includes(ch) ? -1 : 0;
   if (depth <= 0) break;
  }
  if (depth <= 0 && k > i && english(words.slice(i, k + 1)) < 2) for (let m = i; m <= k; m++) code[m] = true;
  else if (depth > 0 || english(words.slice(i, k + 1)) >= 2) { if (/^\(/.test(words[i]) && !/\w\(/.test(words[i])) code[i] = false; if (/^[^([{]*\)[.,;]?$/.test(words[k] ?? '') && !codeShaped((words[k] ?? '').replace(/\)/, ''))) code[k] = false; }
  i = Math.max(i, k);
 }
 const runs: {text: string; code: boolean}[] = [];
 const push = (t: string, c: boolean) => { if (!t) return; const last = runs.at(-1); if (last && last.code === c) last.text += t; else runs.push({text: t, code: c}); };
 for (let i = 0; i < words.length; i++) {
  const space = parts[i * 2 + 1] ?? '';
  if (!code[i]) { push(words[i] + space, false); continue; }
  let w = words[i];
  const lastOfRun = !code[i + 1] || i === words.length - 1 || ends(w);
  let tail = '';
  if (lastOfRun) {
   const m = /([.,;]+|:)$/.exec(w);
   const keywordLine = runs.at(-1)?.code === true ? false : /^(try|except|else|finally|elif|if|for|while|def|class|with)\b/.test(w);
   const startsLine = /^(try|except|else|finally|elif|if|for|while|def|class|with)\b/.test(currentRun(runs, w));
   if (m && !(m[1] === ':' && (keywordLine || startsLine))) { tail = m[1]; w = w.slice(0, -m[1].length); }
  }
  push(w, true);
  push(lastOfRun ? tail + space : space, !lastOfRun);
 }
 return runs;
}

function currentRun(runs: {text: string; code: boolean}[], word: string) {
 const last = runs.at(-1);
 return last?.code ? last.text + word : word;
}

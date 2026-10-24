'use client';
import {useState} from 'react';

const example = 'print("You stand outside a mysterious castle.")\nprint("A tiny dragon opens the gate.")';
export default function OpeningLesson({onTry}:{onTry:(code:string)=>void}) {
 const [prediction,setPrediction]=useState(''),[check,setCheck]=useState(''),[hints,setHints]=useState(0);
 return <section aria-label="Lesson one guide">
  <p className="eyebrow">BUILD YOUR OWN ADVENTURE · ABOUT 10 MINUTES</p>
  <h3>1. Learn: give Python an instruction</h3>
  <p>A program is a set of instructions. For this story, Python follows each instruction from top to bottom. The <code>print()</code> function displays a message in the Output area.</p>
  <pre className="output"><code>{'print("You stand outside a mysterious castle.")'}</code></pre>
  <p><code>print</code> is the function name; use lowercase letters. Parentheses contain what to display. Matching quotation marks mark the beginning and end of text, called a string. The quotation marks themselves do not appear in the output. Matching single quotes work too.</p>
  <h3>2. Predict, then run</h3>
  <pre className="output"><code>{example}</code></pre>
  <fieldset><legend>Which message will appear first?</legend>
   {['The castle message','The dragon message'].map(x=><button type="button" key={x} aria-pressed={prediction===x} onClick={()=>setPrediction(x)}>{x}</button>)}
  </fieldset>
  {prediction&&<p role="status">{prediction==='The castle message'?'Correct. Python runs the first print statement before the second.':'Look at the first line of code. The castle message appears first because these statements run from top to bottom.'}</p>}
  <button type="button" onClick={()=>onTry(example)}>Try the example in the editor</button>
  <p>Then select Run Python and compare the output with your prediction. Each print call ends its message with a new line by default.</p>
  <h3>3. Make a change</h3>
  <p>Change the dragon to another creature. Keep the quotation marks and parentheses, then run again. Which part of the output changed?</p>
  <h3>4. Write your own opening</h3>
  <p>Select Reset code to get the challenge starter. Write two print statements on separate lines: describe a location, then introduce something unexpected. Your story can take place in space, underwater, or anywhere you imagine.</p>
  <button type="button" disabled={hints===3} onClick={()=>setHints(Math.min(3,hints+1))}>{hints===3?'All hints shown':'Show next hint'}</button>
  <div aria-live="polite">
   {hints>=1&&<p>Hint 1: Each message needs its own print call. Start with lowercase <code>print</code>.</p>}
   {hints>=2&&<p>Hint 2: Put each message inside matching quotes, with parentheses around it: <code>print("your message")</code>.</p>}
   {hints>=3&&<pre className="output"><code>{'print("You arrive at an underwater station.")\nprint("Someone knocks on the window.")'}</code></pre>}
  </div>
  <details><summary>Help: Python says SyntaxError</summary><p>Python cannot read the instruction yet. Check that each message has an opening and closing quote and each print call has opening and closing parentheses. For example, <code>print("Hello")</code> has both pairs. A NameError can mean you typed Print instead of lowercase print, or left quotes off your text.</p></details>
  <h3>5. Check your understanding</h3>
  <fieldset><legend>In this example, how does Python run the two print statements?</legend>
   {['In order, from top to bottom','Both at once'].map(x=><button type="button" key={x} aria-pressed={check===x} onClick={()=>setCheck(x)}>{x}</button>)}
  </fieldset>
  {check&&<p role="status">{check==='In order, from top to bottom'?'Exactly. Swapping the two lines of code swaps the order of the messages.':'These two statements run one after the other, from top to bottom. Try swapping the lines and running again.'}</p>}
 </section>;
}

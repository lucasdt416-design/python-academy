'use client';
import {useEffect,useState} from 'react';
import SiteHeader from '../../site-header';

/* Mark students as testers (backlog FB-04; handoff 12). The page decides nothing about who is an
 * admin: it asks GET /api/admin/students, and the API answers 401 or 403 to everyone else, who then
 * see the same plain "not available" page as any missing page. It never asks for /api/me, so the
 * admin's own email is never in the page, and it stores nothing in the browser. */
type Student={id:number;email:string;tester:boolean};
type Load={state:'loading'}|{state:'unavailable'}|{state:'failed'}|{state:'ready';students:Student[]};

export default function TestersPage(){
 const [load,setLoad]=useState<Load>({state:'loading'}),[saving,setSaving]=useState<number|null>(null),[result,setResult]=useState<{ok:boolean;text:string}|null>(null);
 async function fetchStudents(){
  setLoad({state:'loading'});
  try{
   const response=await fetch('/api/admin/students');
   // 401 and 403 look the same as a page that does not exist; only the API protects the data.
   if(response.status===401||response.status===403)return setLoad({state:'unavailable'});
   if(!response.ok)return setLoad({state:'failed'});
   setLoad({state:'ready',students:await response.json()});
  }catch{setLoad({state:'failed'});}
 }
 useEffect(()=>{fetchStudents();},[]);
 async function toggle(student:Student){
  if(saving!==null||load.state!=='ready')return;
  setSaving(student.id);setResult(null);
  const name=`student ${student.id} (${student.email})`;
  try{
   const response=await fetch('/api/admin/testers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:student.id,tester:!student.tester})});
   if(response.status===401||response.status===403)return setLoad({state:'unavailable'});
   if(!response.ok)throw Error();
   // The page shows what the server saved, never what it hoped to save.
   const saved:{id:number;tester:boolean}=await response.json();
   setLoad(old=>old.state==='ready'?{state:'ready',students:old.students.map(s=>s.id===saved.id?{...s,tester:saved.tester}:s)}:old);
   setResult({ok:true,text:saved.tester?`Tester turned on for ${name}.`:`Tester turned off for ${name}.`});
  }catch{setResult({ok:false,text:`That did not save, so ${name} is unchanged. Check your connection and try again.`});}
  finally{setSaving(null);}
 }
 return <><SiteHeader user={null}/><main id="main">
  {load.state==='loading'?<p role="status">Loading…</p>
  :load.state==='unavailable'?<section className="card"><h1>Page not available</h1><p>This page is not available.</p><a className="primary" href="/">Go to your academy</a></section>
  :load.state==='failed'?<section className="card"><h1>Testers</h1><p role="alert">The student list could not load. Nothing was changed.</p><button onClick={fetchStudents}>Try again</button></section>
  :<section className="card testers" aria-labelledby="testers-title">
    <h1 id="testers-title">Testers</h1>
    <p>Testers are students who can try new features and send feedback. Only student accounts are listed. A change takes effect straight away.</p>
    <div className="tester-result" role="status" aria-live="polite">{result?.ok&&<p className="feedback">{result.text}</p>}</div>
    <div role="alert">{result&&!result.ok&&<p className="notice tester-error">{result.text}</p>}</div>
    {load.students.length===0?<p>No student accounts yet.</p>:<table className="tester-table">
     <thead><tr><th scope="col">ID</th><th scope="col">Student</th><th scope="col" id="tester-column">Tester</th></tr></thead>
     <tbody>{load.students.map(s=><tr key={s.id}>
      <td>{s.id}</td>
      <td id={`student-${s.id}`}>{s.email}</td>
      {/* aria-disabled, not disabled, while saving, so keyboard focus stays on the switch. */}
      <td><button role="switch" aria-checked={s.tester} aria-labelledby={`tester-column student-${s.id}`} aria-disabled={saving!==null} className={'tester-switch'+(s.tester?' on':'')} onClick={()=>toggle(s)}>
       <span className="switch-track" aria-hidden="true"><span className="switch-thumb"/></span><span aria-hidden="true">{saving===s.id?'Saving…':s.tester?'On':'Off'}</span>
      </button></td>
     </tr>)}</tbody>
    </table>}
   </section>}
  <footer>Built for curious minds. Designed for room to grow.</footer>
 </main></>;
}

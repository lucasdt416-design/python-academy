'use client';
import {useEffect,useRef,useState} from 'react';
import {type Goal,api} from './catalog-data';

/** Asked once after a student enrols, and again whenever they choose "Change goal". */
export default function GoalCard({current,onSaved,onCancel}:{current:string|null;onSaved:()=>void;onCancel?:()=>void}){
 const [goals,setGoals]=useState<Goal[]>([]),[choice,setChoice]=useState(current??''),[saving,setSaving]=useState(false),[error,setError]=useState('');
 const heading=useRef<HTMLHeadingElement>(null);
 useEffect(()=>{heading.current?.focus();api('goals').then(setGoals).catch(()=>setError('The goals could not load. You can skip this for now.'));},[]);
 async function save(goal:string|null){setSaving(true);setError('');try{await api('goal',goal?{goal}:{});onSaved();}catch(e){setError((e as Error).message);setSaving(false);}}
 return <section className="goal-card" aria-labelledby="goal-heading">
  <p className="eyebrow">{onCancel?'YOUR GOAL':'ONE QUICK QUESTION'}</p>
  <h1 id="goal-heading" ref={heading} tabIndex={-1} className="page-title">What would you like <span>to do first?</span></h1>
  <p className="lead">Your answer only changes what we suggest next. Every course stays open to you, and you can change this any time.</p>
  <form onSubmit={e=>{e.preventDefault();if(choice)save(choice);}}>
   <fieldset className="goal-options" disabled={saving}><legend className="visually-hidden">Choose a goal</legend>
    {goals.map(goal=><label key={goal.id} className={'goal-option'+(choice===goal.id?' selected':'')}><input type="radio" name="goal" value={goal.id} checked={choice===goal.id} onChange={()=>setChoice(goal.id)}/><span><strong>{goal.label}</strong><small>{goal.description}</small></span></label>)}
   </fieldset>
   <div role="status" aria-live="polite">{error&&<p className="notice">{error}</p>}</div>
   <div className="actions"><button className="primary" disabled={!choice||saving}>{onCancel?'Save my goal':'Continue'}</button>
    {onCancel?<button type="button" onClick={onCancel} disabled={saving}>Cancel</button>:<button type="button" onClick={()=>save(null)} disabled={saving}>Skip for now</button>}</div>
  </form>
 </section>;
}

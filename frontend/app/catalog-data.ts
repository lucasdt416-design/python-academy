'use client';
import {useEffect,useState} from 'react';

export type User={id:number;email:string;role:string};
export type LessonSummary={id:string;title:string;concept:string;description:string;badge:string|null};
export type Unit={id:string;title:string;summary:string;status:'released'|'coming_soon';lessons:LessonSummary[]};
export type Course={id:string;title:string;summary:string;status:'released'|'coming_soon';prerequisites:{required:string[];suggested:string[]};units:Unit[]};
export type Catalog={version:number;courses:Course[]};
export type Awards={xp:number;completed:string[];badges:{id:string;title:string}[]};

export async function api(path:string,data?:unknown){
 const response=await fetch('/api/'+path,{method:data===undefined?'GET':'POST',headers:data===undefined?{}:{'Content-Type':'application/json'},body:data===undefined?undefined:JSON.stringify(data)});
 const result=await response.json();if(!response.ok)throw Error(typeof result.detail==='string'?result.detail:'Something went wrong. Please try again.');return result;
}

/** The signed-in user (if any) and, for students, their XP, badges and completed lessons. */
export function useAccount(){
 const [state,setState]=useState<{user:User|null;awards:Awards|null;loading:boolean}>({user:null,awards:null,loading:true});
 useEffect(()=>{let live=true;(async()=>{try{const user=await api('me');const awards=user.role==='student'?await api('awards'):null;if(live)setState({user,awards,loading:false});}catch{if(live)setState({user:null,awards:null,loading:false});}})();return()=>{live=false;};},[]);
 return state;
}

export function useCatalog(){
 const [catalog,setCatalog]=useState<Catalog|null>(null),[error,setError]=useState('');
 useEffect(()=>{let live=true;api('catalog').then(c=>{if(live)setCatalog(c)}).catch(()=>{if(live)setError('The course catalog could not load. Please reload to try again.')});return()=>{live=false;};},[]);
 return {catalog,error};
}

export async function signOut(){try{await api('logout',{});}finally{location.assign('/');}}

/** Students save progress on /learn; everyone else tries lessons in preview, which saves nothing. */
export function lessonHref(id:string,student:boolean){return student?`/learn/${id}`:`/preview?lesson=${id}`;}

export function availableLessons(course:Course){return course.units.filter(u=>u.status==='released').flatMap(u=>u.lessons);}

export function nextLesson(course:Course,done:string[]){return availableLessons(course).find(l=>!done.includes(l.id))??null;}

export function unitNumber(unit:Unit){return Number(unit.id.split('.u')[1]);}

/** Human wording for prerequisite IDs, e.g. ["py.u01",…,"py.u07","git"] → "Python Foundations units 1–7 and Git and GitHub Essentials". */
export function prerequisiteText(refs:string[],catalog:Catalog){
 const parts:string[]=[];
 for(const course of catalog.courses){
  if(refs.includes(course.id)){parts.push(course.title);continue;}
  const numbers=course.units.filter(u=>refs.includes(u.id)).map(unitNumber).sort((a,b)=>a-b);
  if(!numbers.length)continue;
  const ranges:string[]=[];let start=numbers[0],end=numbers[0];
  for(const n of [...numbers.slice(1),NaN]){if(n===end+1){end=n;continue;}ranges.push(start===end?`${start}`:`${start}–${end}`);start=end=n;}
  parts.push(`${course.title} ${numbers.length===1?'unit':'units'} ${ranges.join(', ')}`);
 }
 return parts.length<2?parts.join(''):parts.slice(0,-1).join(', ')+' and '+parts[parts.length-1];
}

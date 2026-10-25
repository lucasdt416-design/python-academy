'use client';
import {Meter} from './catalog';
import {type Awards,type Unit,availableLessons,lessonHref,nextLesson,prerequisiteText,unitNumber,useCatalog} from './catalog-data';

function UnitCard({unit,done,next,student}:{unit:Unit;done:string[];next:string|undefined;student:boolean}){
 const soon=unit.status!=='released',finished=unit.lessons.filter(l=>done.includes(l.id)).length;
 return <li><article className={'unit-card'+(soon?' soon':'')} aria-labelledby={`unit-${unit.id}`}>
  <div className="unit-card-head"><div><p className="eyebrow">UNIT {unitNumber(unit)}</p><h2 id={`unit-${unit.id}`}>{unit.title}</h2><p>{unit.summary}</p></div>
   {soon?<span className="chip chip-soon">Coming soon</span>:student&&<span className="course-meta">{finished} of {unit.lessons.length} complete</span>}</div>
  {!soon&&<ol className="lesson-rows">{unit.lessons.map((lesson,i)=>{
   const state=done.includes(lesson.id)?'done':lesson.id===next?'next':'todo';
   const label=!student?'Try it':state==='done'?'Completed':state==='next'?'Up next':'Not started';
   return <li key={lesson.id}><a href={lessonHref(lesson.id,student)} className={'lesson-row '+state}>
    <span className="lesson-mark" aria-hidden="true">{state==='done'?'✓':i+1}</span>
    <span className="lesson-row-text"><strong>{lesson.title}</strong><small>{lesson.concept}{lesson.badge?` · ${lesson.badge} badge`:''}</small></span>
    <span className="lesson-state">{label}</span></a></li>;})}</ol>}
 </article></li>;
}

export default function CourseView({id,student,awards}:{id:string;student:boolean;awards:Awards|null}){
 const {catalog,error}=useCatalog(),done=awards?.completed??[];
 if(error)return <p className="notice" role="alert">{error}</p>;
 if(!catalog)return <p role="status">Loading course…</p>;
 const course=catalog.courses.find(c=>c.id===id);
 if(!course)return <section className="card"><h1 className="page-title">Course not found</h1><p>That course is not in the catalog.</p><a className="primary" href="/courses">See all courses</a></section>;
 const soon=course.status!=='released',lessons=availableLessons(course),finished=lessons.filter(l=>done.includes(l.id)).length,next=nextLesson(course,done);
 const {required,suggested}=course.prerequisites;
 return <div className="course-page">
  <nav className="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="/courses">Courses</a></li><li aria-current="page">{course.title}</li></ol></nav>
  <section className="course-hero" aria-labelledby="course-title">
   <div><p className="eyebrow">{soon?'COMING SOON':'COURSE'}</p><h1 id="course-title" className="page-title">{course.title}</h1><p className="lead">{course.summary}</p>
    {(required.length>0||suggested.length>0)&&<dl className="prereqs">{required.length>0&&<><dt>Builds on</dt><dd>{prerequisiteText(required,catalog)}</dd></>}{suggested.length>0&&<><dt>Helpful first</dt><dd>{prerequisiteText(suggested,catalog)}</dd></>}</dl>}</div>
   {!soon&&<div className="course-hero-side">
    {student&&<><Meter label={`${course.title} progress`} value={finished} max={lessons.length}/><p className="course-meta">{finished} of {lessons.length} available lessons complete</p></>}
    {next?<a className="primary" href={lessonHref(next.id,student)}>{finished?'Continue':'Start'}: {next.title} <span aria-hidden="true">→</span></a>:<p>You have finished every available lesson.</p>}
    {!student&&<p className="muted">Trying lessons here is a preview and is not saved. Students sign in to save progress and earn badges.</p>}
   </div>}
  </section>
  {soon&&<p className="notice">This course is coming soon and cannot be started yet. Here is what it will cover.</p>}
  {course.units.length?<ol className="unit-list" aria-label="Units">{course.units.map(unit=><UnitCard key={unit.id} unit={unit} done={done} next={next?.id} student={student}/>)}</ol>
   :<p className="card">The units for this course will be announced when it is ready.</p>}
 </div>;
}

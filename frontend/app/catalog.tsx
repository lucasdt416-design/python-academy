'use client';
import {type Awards,type Catalog,type Course,availableLessons,lessonHref,nextLesson,prerequisiteText,unitNumber,useCatalog} from './catalog-data';

export function Meter({label,value,max}:{label:string;value:number;max:number}){
 return <progress className="meter" value={value} max={Math.max(max,1)} aria-label={label}>{value} of {max}</progress>;
}

function CourseCard({course,catalog,done,student}:{course:Course;catalog:Catalog;done:string[];student:boolean}){
 const soon=course.status!=='released',lessons=availableLessons(course),finished=lessons.filter(l=>done.includes(l.id)).length;
 const open=course.units.filter(u=>u.status==='released').length,needs=course.prerequisites.required;
 return <li><article className={'course-card'+(soon?' soon':'')} aria-labelledby={`course-${course.id}`}>
  <div className="course-card-top"><span className={soon?'chip chip-soon':'chip'}>{soon?'Coming soon':'Available'}</span>{!soon&&<span className="course-meta">{open} of {course.units.length} units open</span>}</div>
  <h2 id={`course-${course.id}`}><a href={`/courses/${course.id}`} className="course-link">{course.title}</a></h2>
  <p>{course.summary}</p>
  {soon?<p className="course-meta">{needs.length?`Builds on ${prerequisiteText(needs,catalog)}.`:'No prerequisites.'}</p>
   :<div className="course-progress">{student?<><Meter label={`${course.title} progress`} value={finished} max={lessons.length}/><span>{finished} of {lessons.length} lessons complete</span></>:<span>{lessons.length} lessons ready to try</span>}</div>}
 </article></li>;
}

export default function CatalogView({student,awards,home=false}:{student:boolean;awards:Awards|null;home?:boolean}){
 const {catalog,error}=useCatalog(),done=awards?.completed??[];
 if(error)return <p className="notice" role="alert">{error}</p>;
 if(!catalog)return <p role="status">Loading courses…</p>;
 const first=catalog.courses.find(c=>c.status==='released'),next=first&&nextLesson(first,done);
 const unit=first?.units.find(u=>u.lessons.some(l=>l.id===next?.id));
 return <div className="catalog">
  {home?<div className="catalog-intro"><p className="eyebrow">YOUR LEARNING</p><h1 className="page-title">{done.length?<>Welcome back. <span>Keep building.</span></>:<>Your first course <span>is ready.</span></>}</h1></div>
   :<div className="catalog-intro"><p className="eyebrow">COURSE CATALOG</p><h1 className="page-title">Choose what <span>to learn next.</span></h1><p className="lead">Start with Python Foundations. Other courses build on it and open as they are ready.</p></div>}
  {home&&student&&first&&<section className="continue-card" aria-labelledby="continue-heading">
   <div><p className="eyebrow">{next?(done.length?'UP NEXT':'START HERE'):'ALL CAUGHT UP'}</p><h2 id="continue-heading">{next?next.title:'You have finished every available lesson'}</h2><p>{next&&unit?`${first.title} · Unit ${unitNumber(unit)}: ${unit.title}`:'Revisit any lesson, or see what is coming soon below.'}</p></div>
   {next&&<a className="primary" href={lessonHref(next.id,student)}>{done.length?'Continue':'Start'} <span aria-hidden="true">→</span></a>}
   {awards&&<div className="xp-summary"><strong>{awards.xp} XP</strong><span>{awards.badges.length} {awards.badges.length===1?'badge':'badges'} earned</span></div>}
  </section>}
  {home&&<h2 className="section-title">All courses</h2>}
  <ul className="course-grid" aria-label="Courses">{catalog.courses.map(course=><CourseCard key={course.id} course={course} catalog={catalog} done={done} student={student}/>)}</ul>
 </div>;
}

'use client';
import {type Awards,type Catalog,type Course,type Recommendation,availableLessons,lessonHref,locate,nextLesson,prerequisiteText,unitNumber,useCatalog} from './catalog-data';

export function Meter({label,value,max}:{label:string;value:number;max:number}){
 return <progress className="meter" value={value} max={Math.max(max,1)} aria-label={label}>{value} of {max}</progress>;
}

function CourseCard({course,catalog,done,student,recommended}:{course:Course;catalog:Catalog;done:string[];student:boolean;recommended:boolean}){
 const soon=course.status!=='released',lessons=availableLessons(course),finished=lessons.filter(l=>done.includes(l.id)).length;
 const open=course.units.filter(u=>u.status==='released').length,needs=course.prerequisites.required;
 return <li><article className={'course-card'+(soon?' soon':'')+(recommended?' recommended':'')} aria-labelledby={`course-${course.id}`}>
  <div className="course-card-top"><span className="chips"><span className={soon?'chip chip-soon':'chip'}>{soon?'Coming soon':'Available'}</span>{recommended&&<span className="chip chip-recommended">Recommended</span>}</span>{!soon&&<span className="course-meta">{open} of {course.units.length} units open</span>}</div>
  <h2 id={`course-${course.id}`}><a href={`/courses/${course.id}`} className="course-link">{course.title}</a></h2>
  <p>{course.summary}</p>
  {soon?<p className="course-meta">{needs.length?`Builds on ${prerequisiteText(needs,catalog)}.`:'No prerequisites.'}</p>
   :<div className="course-progress">{student?<><Meter label={`${course.title} progress`} value={finished} max={lessons.length}/><span>{finished} of {lessons.length} lessons complete</span></>:<span>{lessons.length} lessons ready to try</span>}</div>}
 </article></li>;
}

const EYEBROW={continue:'KEEP GOING',start:'RECOMMENDED NEXT',prerequisite:'BUILD THE FOUNDATION FIRST',choose:'YOUR CHOICE',caught_up:'ALL CAUGHT UP'};

/** The student's next step: the recommendation, why it was chosen, and their goal. */
function NextStep({catalog,recommendation,done,awards,goal,onChangeGoal}:{catalog:Catalog;recommendation:Recommendation|null;done:string[];awards:Awards|null;goal?:string|null;onChangeGoal?:()=>void}){
 const first=catalog.courses.find(c=>c.status==='released');
 // Without a recommendation (for example if it failed to load), fall back to the first unfinished lesson.
 const rec:Recommendation|null=recommendation??(first&&nextLesson(first,done)?{kind:done.length?'continue':'start',reason:'',course:first.id,unit:null,lesson:nextLesson(first,done)!.id,options:[],notes:[],rules_version:0}:null);
 const place=rec?locate(catalog,rec.lesson):null;
 const title=place?place.lesson.title:rec?.kind==='choose'?'Choose your next course':'More lessons are on the way';
 return <section className="continue-card" aria-labelledby="continue-heading">
  <div className="continue-main"><p className="eyebrow">{rec?EYEBROW[rec.kind]:'ALL CAUGHT UP'}</p><h2 id="continue-heading">{title}</h2>
   {place&&<p className="continue-place">{place.course.title} · Unit {unitNumber(place.unit)}: {place.unit.title}</p>}
   {rec?.reason&&<p className="continue-reason">{rec.reason}</p>}
   {rec&&rec.notes.length>0&&<ul className="continue-notes">{rec.notes.map(note=><li key={note}>{note}</li>)}</ul>}
   {rec?.kind==='choose'&&<ul className="continue-options">{rec.options.map(id=>{const c=catalog.courses.find(x=>x.id===id);return c&&<li key={id}><a href={`/courses/${id}`}>{c.title}</a></li>;})}</ul>}
   {goal!==undefined&&<p className="continue-goal">Your goal: <strong>{goal??'Learn to code from scratch'}</strong>{onChangeGoal&&<button type="button" className="link-button" onClick={onChangeGoal}>Change goal</button>}</p>}
  </div>
  {place&&<a className="primary" href={lessonHref(place.lesson.id,true)}>{rec?.kind==='continue'?'Continue':'Start'} <span aria-hidden="true">→</span></a>}
  {awards&&<div className="xp-summary"><strong>{awards.xp} XP</strong><span>{awards.badges.length} {awards.badges.length===1?'badge':'badges'} earned</span></div>}
 </section>;
}

export default function CatalogView({student,awards,home=false,recommendation=null,goal,onChangeGoal}:{student:boolean;awards:Awards|null;home?:boolean;recommendation?:Recommendation|null;goal?:string|null;onChangeGoal?:()=>void}){
 const {catalog,error}=useCatalog(),done=awards?.completed??[];
 if(error)return <p className="notice" role="alert">{error}</p>;
 if(!catalog)return <p role="status">Loading courses…</p>;
 const recommendedCourse=recommendation?.lesson?recommendation.course:null;
 return <div className="catalog">
  {home?<div className="catalog-intro"><p className="eyebrow">YOUR LEARNING</p><h1 className="page-title">{done.length?<>Welcome back. <span>Keep building.</span></>:<>Your first course <span>is ready.</span></>}</h1></div>
   :<div className="catalog-intro"><p className="eyebrow">COURSE CATALOG</p><h1 className="page-title">Choose what <span>to learn next.</span></h1><p className="lead">Start with Python Foundations. Other courses build on it and open as they are ready.</p></div>}
  {home&&student&&<NextStep catalog={catalog} recommendation={recommendation} done={done} awards={awards} goal={goal} onChangeGoal={onChangeGoal}/>}
  {home&&<h2 className="section-title">All courses</h2>}
  <ul className="course-grid" aria-label="Courses">{catalog.courses.map(course=><CourseCard key={course.id} course={course} catalog={catalog} done={done} student={student} recommended={course.id===recommendedCourse}/>)}</ul>
 </div>;
}

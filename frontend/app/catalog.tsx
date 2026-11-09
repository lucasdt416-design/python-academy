'use client';
import {type Awards,type Catalog,type Course,type Recommendation,availableLessons,prerequisiteText,useCatalog} from './catalog-data';

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

/** The course catalog (/courses). The student's home is StudentHome in home.tsx. */
export default function CatalogView({student,awards,recommendation=null}:{student:boolean;awards:Awards|null;recommendation?:Recommendation|null}){
 const {catalog,error}=useCatalog(),done=awards?.completed??[];
 if(error)return <p className="notice" role="alert">{error}</p>;
 if(!catalog)return <p role="status">Loading courses…</p>;
 const recommendedCourse=recommendation?.lesson?recommendation.course:null;
 return <div className="catalog">
  <div className="catalog-intro"><p className="kicker">course catalog</p><h1 className="page-title">Choose what <span>to learn next.</span></h1><p className="lead">Start with Python Foundations. Other courses build on it and open as they are ready.</p></div>
  <ul className="course-grid" aria-label="Courses">{catalog.courses.map(course=><CourseCard key={course.id} course={course} catalog={catalog} done={done} student={student} recommended={course.id===recommendedCourse}/>)}</ul>
 </div>;
}

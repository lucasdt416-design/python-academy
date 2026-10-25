'use client';
import {useParams} from 'next/navigation';
import CourseView from '../../course';
import PageShell from '../../page-shell';

export default function CoursePage(){
 const {course}=useParams<{course:string}>();
 return <PageShell>{({user,awards})=><CourseView id={course} student={user?.role==='student'} awards={awards}/>}</PageShell>;
}

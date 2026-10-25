'use client';
import {useParams} from 'next/navigation';
import Adventure from '../../adventure';
import PageShell from '../../page-shell';

/** Students save progress here; anyone else gets the same lesson as a preview that saves nothing. */
export default function LearnPage(){
 const {lesson}=useParams<{lesson:string}>();
 return <PageShell>{({user})=><Adventure preview={user?.role!=='student'} lessonId={lesson} onSaved={()=>{}}/>}</PageShell>;
}

'use client';
import {useParams} from 'next/navigation';
import PageShell from '../../page-shell';
import Workspace from '../../workspace';

export default function ProjectPage(){
 const {id}=useParams<{id:string}>();
 return <PageShell>{({user})=>user?.role==='student'?<Workspace id={id}/>:<section className="projects projects-out"><h1>Projects</h1><p className="lead">{user?'Projects are for learners.':'Sign in to open your projects.'}</p>{!user&&<a className="btn primary" href="/auth/google">Sign in with Google</a>}</section>}</PageShell>;
}

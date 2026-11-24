'use client';
import Arena from '../arena';
import PageShell from '../page-shell';

export default function PracticePage(){return <PageShell>{({user})=>user?.role==='student'?<Arena/>:<section className="arena"><h1>Practice arena</h1><p className="lead">{user?'The arena is for learners.':'Sign in to practise what you have learned, a few questions at a time, spaced over days so it sticks.'}</p>{!user&&<a className="btn primary" href="/auth/google">Sign in with Google</a>}</section>}</PageShell>;}

'use client';
import Arena,{CreaturePicture} from '../arena';
import PageShell from '../page-shell';

export default function PracticePage(){return <PageShell>{({user})=>user?.role==='student'?<Arena/>:<section className="arena arena-out"><div className="arena-head"><div><h1>Practice arena</h1><p className="lead">{user?'The arena is for learners.':'Sign in to practise what you have learned, a few questions at a time, spaced over days so it sticks.'}</p><p>Each unit has its own creature. Answer questions from the lessons you have finished (predict the output, trace a value, put lines in order, spot the bug) and you tame it. A wrong answer takes nothing away; that question comes back tomorrow.</p>{!user&&<a className="btn primary" href="/auth/google">Sign in with Google</a>}</div><figure className="arena-creature"><CreaturePicture unit="py.u01" tamed label="Inkling, the creature for unit 1, tamed"/><figcaption>Inkling, unit 1</figcaption></figure></div></section>}</PageShell>;}

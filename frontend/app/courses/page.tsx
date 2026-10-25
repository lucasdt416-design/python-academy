'use client';
import CatalogView from '../catalog';
import PageShell from '../page-shell';

export default function CoursesPage(){return <PageShell>{({user,awards})=><CatalogView student={user?.role==='student'} awards={awards}/>}</PageShell>;}

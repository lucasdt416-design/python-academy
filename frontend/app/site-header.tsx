'use client';
import type {User} from './catalog-data';

export default function SiteHeader({user,onSignOut}:{user:User|null;onSignOut?:()=>void}){
 return <header><a href="/" className="brand"><span className="logo">py</span> Python Academy</a><nav className="site-nav" aria-label="Main"><a href="/courses">Courses</a></nav><span className="tag">Small steps. Real skills.</span>{user&&onSignOut&&<button onClick={onSignOut}>Sign out</button>}</header>;
}

'use client';
import type {User} from './catalog-data';

/** signIn: show "Try a lesson" and "Sign in", once we know nobody is signed in. */
export default function SiteHeader({user,onSignOut,signIn=false}:{user:User|null;onSignOut?:()=>void;signIn?:boolean}){
 return <header className="site-header">
  <a href="/" className="brand"><span className="logo">py</span>Python Academy</a>
  <nav className="nav" aria-label="Main"><a href="/courses">Courses</a>{signIn&&<a href="/preview?lesson=hello">Try a lesson</a>}</nav>
  <div className="header-end">{user&&onSignOut?<button type="button" className="btn small" onClick={onSignOut}>Sign out</button>:signIn&&<a className="btn small" href="/auth/google">Sign in</a>}</div>
 </header>;
}

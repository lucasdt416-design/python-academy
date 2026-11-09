'use client';
import type {ReactNode} from 'react';
import {type Awards,type Recommendation,type User,signOut,useAccount} from './catalog-data';
import SiteHeader from './site-header';

/** Header, main landmark and footer for pages outside the account dashboard. */
export default function PageShell({children}:{children:(account:{user:User|null;awards:Awards|null;recommendation:Recommendation|null})=>ReactNode}){
 const {user,awards,recommendation,loading}=useAccount();
 return <><SiteHeader user={user} onSignOut={signOut} signIn={!loading&&!user}/><main id="main"><div className="wrap pagepad">{loading?<p role="status">Loading…</p>:children({user,awards,recommendation})}</div><SiteFooter/></main></>;
}

export function SiteFooter({children}:{children?:ReactNode}){
 return <footer className="site-footer"><div className="wrap">{children??'Built for curious minds. Designed for room to grow.'}</div></footer>;
}

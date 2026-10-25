'use client';
import type {ReactNode} from 'react';
import {type Awards,type User,signOut,useAccount} from './catalog-data';
import SiteHeader from './site-header';

/** Header, main landmark and footer for pages outside the account dashboard. */
export default function PageShell({children}:{children:(account:{user:User|null;awards:Awards|null})=>ReactNode}){
 const {user,awards,loading}=useAccount();
 return <><SiteHeader user={user} onSignOut={signOut}/><main id="main">{loading?<p role="status">Loading…</p>:children({user,awards})}<footer>Built for curious minds. Designed for room to grow.</footer></main></>;
}

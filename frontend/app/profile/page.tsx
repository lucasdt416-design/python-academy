'use client';
import PageShell from '../page-shell';
import ProfileView from '../profile';

export default function ProfilePage(){return <PageShell>{({user})=>user&&(user.role==='student'||user.role==='parent')?<ProfileView/>:<section className="profile"><h1>Your profile</h1><p className="lead">{user?'Your profile opens once your account is set up.':'Sign in with Google to make a profile. It keeps your avatar, XP, badges and progress with your account.'}</p>{!user&&<a className="btn primary" href="/auth/google">Sign in with Google</a>}</section>}</PageShell>;}

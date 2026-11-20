'use client';
// The profile page (/profile): your avatar and nickname, and everything you have earned, kept with
// the Google account you signed in with. Shown only to you.
import {useEffect, useState} from 'react';
import AvatarPicture, {AVATAR_LABELS, type Avatar} from './avatar';
import {Icon} from './lesson-art';

export type Profile = {
 saved: boolean; nickname: string; avatar: Avatar; choices: Record<keyof Avatar, string[]>; email: string; role: string; member_since: string | null;
 xp?: number; level?: {number: number; title: string; xp_into_level: number; xp_for_next: number}; badges?: {id: string; title: string}[];
 completed?: number; released?: number; units?: {id: string; title: string; done: number; total: number; more_coming: boolean}[];
 active_days?: string[]; streak?: number; calendar_start?: string; today?: string;
};
const words = (s: string) => s.replace(/_/g, ' ');

async function load(): Promise<Profile> {
 const r = await fetch('/api/profile');
 const body = await r.json();
 if (!r.ok) throw Error(typeof body.detail === 'string' ? body.detail : 'Your profile could not load. Please try again.');
 return body;
}

/** Twelve weeks of days, oldest first, each marked when XP was earned that day. */
function Calendar({start, today, active}: {start: string; today: string; active: string[]}) {
 const days: string[] = [];
 for (let d = new Date(start + 'T00:00:00Z'); d.toISOString().slice(0, 10) <= today; d.setUTCDate(d.getUTCDate() + 1)) days.push(d.toISOString().slice(0, 10));
 const on = new Set(active);
 return <figure className="activity">
  <svg viewBox={`0 0 ${Math.ceil(days.length / 7) * 14} 98`} className="activity-grid" aria-hidden="true">
   {days.map((day, i) => <rect key={day} x={Math.floor(i / 7) * 14} y={(i % 7) * 14} width="11" height="11" rx="2" className={on.has(day) ? 'day-on' : 'day-off'}/>)}
  </svg>
  <figcaption>{active.length ? `You earned XP on ${active.length} ${active.length === 1 ? 'day' : 'days'} in the last twelve weeks.` : 'Days you earn XP will fill in here.'}</figcaption>
 </figure>;
}

export default function ProfileView() {
 const [profile, setProfile] = useState<Profile | null>(null), [draft, setDraft] = useState<{nickname: string; avatar: Avatar} | null>(null);
 const [error, setError] = useState(''), [status, setStatus] = useState(''), [saving, setSaving] = useState(false);
 useEffect(() => {
  load().then(p => { setProfile(p); setDraft({nickname: p.nickname, avatar: p.avatar}); }).catch(e => setError((e as Error).message));
 }, []);
 if (error && !profile) return <p className="notice" role="alert">{error}</p>;
 if (!profile || !draft) return <p role="status">Loading your profile…</p>;
 const changed = draft.nickname !== profile.nickname || JSON.stringify(draft.avatar) !== JSON.stringify(profile.avatar) || !profile.saved;
 async function save() {
  setSaving(true); setStatus(''); setError('');
  try {
   const r = await fetch('/api/profile', {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(draft)});
   const body = await r.json();
   if (!r.ok) throw Error(typeof body.detail === 'string' ? body.detail : 'Your profile could not be saved. Please try again.');
   setProfile(body); setDraft({nickname: body.nickname, avatar: body.avatar}); setStatus('Saved to your account.');
  } catch (e) { setError((e as Error).message); } finally { setSaving(false); }
 }
 const student = profile.role === 'student', name = draft.nickname || 'Your profile';
 return <section className="profile" aria-labelledby="profile-title">
  <div className="profile-head">
   <AvatarPicture avatar={draft.avatar} label={false} className="avatar-large"/>
   <div>
    <p className="kicker">profile</p>
    <h1 id="profile-title">{name}</h1>
    {student && profile.level && <p className="profile-level"><strong>Level {profile.level.number} · {profile.level.title}</strong> <span>{profile.xp} XP</span></p>}
    {student && profile.level && <><progress className="meter" value={profile.level.xp_into_level} max={profile.level.xp_for_next} aria-label={`Progress to level ${profile.level.number + 1}`}/>
     <p className="muted">{profile.level.xp_for_next - profile.level.xp_into_level} XP to level {profile.level.number + 1}. Levels are a count of XP, not a grade.</p></>}
    <p className="muted">Saved with the Google account {profile.email}{profile.member_since ? `, here since ${profile.member_since}` : ''}. Only you see this page.</p>
   </div>
  </div>

  {student && <div className="profile-stats">
   <p><strong>{profile.completed}</strong> of {profile.released} lessons done</p>
   <p><strong>{profile.badges?.length ?? 0}</strong> {profile.badges?.length === 1 ? 'badge' : 'badges'}</p>
   <p><strong>{profile.streak}</strong> {profile.streak === 1 ? 'day' : 'days'} in a row</p>
  </div>}

  <form className="avatar-builder" onSubmit={e => { e.preventDefault(); save(); }} aria-labelledby="builder-title">
   <h2 id="builder-title">Make your avatar</h2>
   <label htmlFor="nickname">Nickname <span className="muted">(optional; letters, digits and spaces, up to 24)</span></label>
   <input id="nickname" maxLength={24} autoComplete="nickname" value={draft.nickname} onChange={e => setDraft({...draft, nickname: e.target.value})}/>
   <p className="muted">Use a nickname, not your full name. It is shown only to you.</p>
   {(Object.keys(AVATAR_LABELS) as (keyof Avatar)[]).map(part => <fieldset key={part} className="choice-row">
    <legend>{AVATAR_LABELS[part]}</legend>
    {profile.choices[part].map(option => <button key={option} type="button" className={'choice choice-' + part + '-' + option} aria-pressed={draft.avatar[part] === option}
     onClick={() => setDraft({...draft, avatar: {...draft.avatar, [part]: option}})}><span className={'swatch swatch-' + part + ' ' + part + '-' + option} aria-hidden="true"/>{words(option)}</button>)}
   </fieldset>)}
   <div className="actions"><button className="primary" disabled={saving || !changed}>{saving ? 'Saving…' : profile.saved ? 'Save changes' : 'Save my profile'}</button>
    <span role="status" className="muted">{status}</span></div>
   {error && <p className="notice" role="alert">{error}</p>}
  </form>

  {student && profile.units && <section aria-labelledby="units-title">
   <h2 id="units-title">Your path</h2>
   <ul className="unit-progress">{profile.units.map(u => <li key={u.id}>
    <span className="unit-progress-name">{u.title}</span>
    <progress className="meter" value={u.done} max={u.total} aria-label={`${u.title}: ${u.done} of ${u.total} lessons`}/>
    <span className="muted">{u.done} of {u.total}{u.done === u.total && !u.more_coming ? <> <Icon name="check"/></> : ''}</span>
   </li>)}</ul>
  </section>}

  {student && profile.calendar_start && profile.today && <section aria-labelledby="activity-title">
   <h2 id="activity-title">Days you practised</h2>
   <Calendar start={profile.calendar_start} today={profile.today} active={profile.active_days ?? []}/>
  </section>}

  {student && <section aria-labelledby="badges-title">
   <h2 id="badges-title">Badges</h2>
   {profile.badges?.length ? <ul className="badge-list">{profile.badges.map(b => <li key={b.id}><span className="badge-mark" aria-hidden="true">✦</span>{b.title}</li>)}</ul> : <p className="muted">Finish a lesson's challenge to earn its badge.</p>}
  </section>}
 </section>;
}

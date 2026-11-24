// The profile avatar: drawn from a few fixed choices (backend/app/profiles.py AVATAR_CHOICES), never an
// uploaded picture. Colours are classes in style.css; the page policy allows no style attributes.
import {Item} from './scene-kit';

export type Avatar = {skin: string; hair: string; hair_colour: string; outfit: string; item: string};
export const AVATAR_LABELS: Record<keyof Avatar, string> = {skin: 'Skin', hair: 'Hair', hair_colour: 'Hair colour', outfit: 'Outfit', item: 'Carries'};

const HAIR: Record<string, string> = {
 short: 'M-15 -56q0-14 15-14t15 14q-6-6-15-6t-15 6z',
 long: 'M-16 -54q0-16 16-16t16 16v22q-3 4-6 0v-18q-10-6-20 0v18q-3 4-6 0z',
 curly: 'M-16 -56a6 6 0 0 1 6-9a7 7 0 0 1 10-4a7 7 0 0 1 10 4a6 6 0 0 1 6 9q-4-4-8-2q-4-4-8-2q-4-4-8 2q-4-2-8 2z',
 bun: 'M-15 -56q0-14 15-14t15 14q-6-6-15-6t-15 6zM-6 -74a6 6 0 1 0 12 0a6 6 0 1 0-12 0z',
 none: '',
};

/** The avatar in a 120 by 120 box. label: its accessible name, or false when text beside it says the same. */
export default function AvatarPicture({avatar, label, className}: {avatar: Avatar; label?: string | false; className?: string}) {
 const named = label !== false;
 return <svg viewBox="-60 -100 120 120" className={'avatar ' + (className ?? '')} role={named ? 'img' : undefined} aria-label={named ? label ?? 'Your avatar' : undefined} aria-hidden={named ? undefined : true}>
  <circle className="avatar-bg" cx="0" cy="-40" r="58"/>
  <path className={`outfit-${avatar.outfit} s-ink`} d="M-30 18q0-50 30-50t30 50z"/>
  <circle className={`skin-${avatar.skin} s-ink`} cx="0" cy="-52" r="17"/>
  {HAIR[avatar.hair] && <path className={`hair-${avatar.hair_colour} s-ink-s`} d={HAIR[avatar.hair]}/>}
  <circle className="f-ink" cx="-6" cy="-52" r="2"/><circle className="f-ink" cx="6" cy="-52" r="2"/>
  <path className="s-ink-s" d="M-5 -45q5 4 10 0"/>
  {avatar.item !== 'none' && <Item x={30} y={2} name={avatar.item} size={1.3}/>}
 </svg>;
}

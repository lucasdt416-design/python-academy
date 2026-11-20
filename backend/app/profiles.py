"""Profiles: an avatar from fixed choices, an optional nickname, and a summary of the learner's progress.

The avatar is a set of choices from the lists below, never an uploaded picture, so nothing from outside
the app is ever shown. The nickname is optional, short, and limited to letters, digits, spaces and a
few marks, and it is shown only to the person it belongs to. Everything else on the page is worked out
from what the app already keeps: the XP and badge ledgers and the catalog.
"""
import json
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from . import awards
from .db import Event, Profile, XpAward

AVATAR_CHOICES = {
    'skin': ['sand', 'peach', 'honey', 'bronze', 'umber'],
    'hair': ['short', 'long', 'curly', 'bun', 'none'],
    'hair_colour': ['black', 'brown', 'auburn', 'blond', 'grey', 'teal'],
    'outfit': ['plum', 'moss', 'slate', 'clay', 'amber'],
    'item': ['lantern', 'map', 'key', 'wand', 'shield', 'none'],
}
DEFAULT_AVATAR = {'skin': 'peach', 'hair': 'short', 'hair_colour': 'brown', 'outfit': 'plum', 'item': 'lantern'}
NICKNAME = re.compile(r"[\w .'-]{0,24}")
XP_PER_LEVEL = 500
# Level titles are words for a range of XP, nothing more: they are not a measure of skill.
TITLES = ['Explorer', 'Pathfinder', 'Trailblazer', 'Navigator', 'Cartographer', 'Lorekeeper']
CALENDAR_DAYS = 84


def clean_nickname(value):
    """The nickname as stored, or a ValueError with a message the learner can act on."""
    value = ' '.join(value.split())
    if len(value) > 24:
        raise ValueError('Keep your nickname to 24 characters or fewer.')
    if not NICKNAME.fullmatch(value):
        raise ValueError('Use letters, digits, spaces, dots, dashes and apostrophes only.')
    return value


def clean_avatar(value):
    if not isinstance(value, dict) or set(value) != set(AVATAR_CHOICES):
        raise ValueError('Choose one option for each part of the avatar.')
    for part, choice in value.items():
        if choice not in AVATAR_CHOICES[part]:
            raise ValueError(f'That {part.replace("_", " ")} is not one of the choices.')
    return dict(value)


def level(xp):
    number = xp // XP_PER_LEVEL + 1
    return {'number': number, 'title': TITLES[min(number - 1, len(TITLES) - 1)],
            'xp_into_level': xp % XP_PER_LEVEL, 'xp_for_next': XP_PER_LEVEL}


def active_days(db, user_id, today):
    """The days, within the last CALENDAR_DAYS, on which the learner earned XP, and the current streak."""
    days = set()
    for created in db.scalars(select(XpAward.created).where(XpAward.user_id == user_id)):
        try:
            days.add(datetime.fromisoformat(created).astimezone(timezone.utc).date())
        except ValueError:
            continue
    start = today - timedelta(days=CALENDAR_DAYS - 1)
    streak, day = 0, today if today in days else today - timedelta(days=1)
    while day in days:
        streak, day = streak + 1, day - timedelta(days=1)
    return sorted(d.isoformat() for d in days if start <= d <= today), streak


def member_since(db, user_id):
    first = db.scalar(select(Event.created).where(Event.user_id == user_id).order_by(Event.id).limit(1))
    return first[:10] if first else None


def view(db, user, catalog, lessons, order, today=None):
    """Everything /api/profile returns, for the signed-in person only."""
    today = today or datetime.now(timezone.utc).date()
    row = db.get(Profile, user.id)
    avatar = json.loads(row.avatar) if row else dict(DEFAULT_AVATAR)
    result = {'saved': row is not None, 'nickname': row.nickname if row else '', 'avatar': avatar,
              'choices': AVATAR_CHOICES, 'email': user.email, 'role': user.role, 'member_since': member_since(db, user.id)}
    if user.role != 'student':
        return result
    summary = awards.summary(db, user.id, lessons, order)
    done = set(summary['completed'])
    units = [{'id': u.id, 'title': u.title, 'done': sum(1 for l in u.lessons if l in done), 'total': len(u.lessons),
              'more_coming': u.more_lessons_coming}
             for c in catalog.courses for u in c.units if u.status == 'released']
    days, streak = active_days(db, user.id, today)
    result.update(xp=summary['xp'], level=level(summary['xp']), badges=summary['badges'], completed=len(done),
                  released=sum(u['total'] for u in units), units=units, active_days=days, streak=streak,
                  calendar_start=(today - timedelta(days=CALENDAR_DAYS - 1)).isoformat(), today=today.isoformat())
    return result


def save(db, user, nickname, avatar):
    row = db.get(Profile, user.id)
    if row:
        row.nickname, row.avatar = nickname, json.dumps(avatar, sort_keys=True)
    else:
        db.add(Profile(user_id=user.id, nickname=nickname, avatar=json.dumps(avatar, sort_keys=True)))

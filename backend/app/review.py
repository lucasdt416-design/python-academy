"""The Practice Arena: spaced review cards (teaching-design.md sections 2.7 and 5).

Cards live in content/review/<course>.json, one or more per lesson, of four kinds: predict (what does it
print?), trace (what does a name hold?), order (put the lines in order) and bug (which line is wrong?).
Only cards from lessons the learner has finished are offered. Each card moves through boxes: a right
answer moves it on and brings it back later (1, 3, 7, then 30 days); a wrong answer brings it back
tomorrow. Nothing here changes XP, badges or progress, and nothing is ever taken away.

Answers stay on the server until the learner has answered: the page gets the options, or the lines in a
shuffled order, and never which one is right.
"""
import json
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from .db import ReviewState

INTERVALS = {1: 1, 2: 3, 3: 7, 4: 30}
SESSION = 5
TAME_AT = 5

# One creature per unit. They are names for review sessions, nothing more: taming one means its
# unit's cards were answered right five times, not that the unit is mastered.
CREATURES = {
    'py.u01': ('Inkling', 'a story sprite that lives in print() calls'),
    'py.u02': ('Sumbat', 'a bat that hangs from equals signs'),
    'py.u03': ('Loop lynx', 'a cat that runs in circles until told to stop'),
    'py.u04': ('Packrat', 'a hoarder of lists, sets and dictionaries'),
    'py.u05': ('Callwing', 'a bird that only sings when called'),
    'py.u06': ('Bugbear', 'a bear that hides in tracebacks'),
    'py.u07': ('Toolhound', 'a dog that fetches modules'),
    'py.u08': ('Testudo', 'a tortoise that checks everything twice'),
    'py.u09': ('Scrollworm', 'a worm that nests in saved files'),
    'py.u10': ('Patternfox', 'a fox that hunts in text'),
    'py.u11': ('Classaur', 'a dinosaur built from smaller parts'),
    'cs.u01': ('Bitmoth', 'a moth whose wing spots flick on and off like bits'),
    'cs.u03': ('Seekowl', 'an owl that finds things by halving the dark'),
}


class Card(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str
    lesson: str
    kind: Literal['predict', 'trace', 'order', 'bug']
    prompt: str = Field(min_length=1)
    why: str = Field(min_length=1)
    code: str | None = None
    options: list[str] = []
    answer: int | None = None
    lines: list[str] = []
    inputs: list[str] = []
    expected: str | None = None
    probe: str | None = None
    fixed: str | None = None


def load(root, lessons):
    """Every review card, checked: a real lesson, a unique ID, and an answer the card can hold."""
    cards, errors = {}, []
    for path in sorted(Path(root).glob('*.json')):
        for raw in json.loads(path.read_text())['cards']:
            card = Card(**raw)
            if card.id in cards:
                errors.append(f'{card.id} is used twice')
            if card.lesson not in lessons or not card.id.startswith(card.lesson + '.review.'):
                errors.append(f'{card.id} is not for a real lesson')
            if card.kind == 'order':
                if len(card.lines) < 3 or len(set(card.lines)) != len(card.lines) or card.expected is None:
                    errors.append(f'{card.id} needs three or more different lines and an expected output')
            elif not (card.code and len(card.options) >= 2 and len(set(card.options)) == len(card.options) and card.answer is not None and 0 <= card.answer < len(card.options)):
                errors.append(f'{card.id} needs code, different options and an answer among them')
            cards[card.id] = card
    if errors:
        raise ValueError('Invalid review cards:\n- ' + '\n- '.join(errors))
    return cards


def public(card, rng):
    """What the page may see before the learner answers."""
    shown = {'id': card.id, 'lesson': card.lesson, 'kind': card.kind, 'prompt': card.prompt}
    if card.kind == 'order':
        lines = card.lines[:]
        while lines == card.lines:
            rng.shuffle(lines)
        shown.update(lines=lines, expected=card.expected, inputs=card.inputs)
    else:
        shown.update(code=card.code, options=card.options)
    return shown


def unit_of(lesson_id, catalog):
    return next((u.id for c in catalog.courses for u in c.units if lesson_id in u.lessons), None)


def tamed(states, cards, catalog):
    by_unit = Counter()
    for s in states.values():
        card = cards.get(s.card_id)
        if card:
            by_unit[unit_of(card.lesson, catalog)] += s.correct
    return [u for u in CREATURES if by_unit[u] >= TAME_AT]


def session(db, user_id, cards, catalog, completed, today):
    """Up to SESSION cards: those due first, then ones never seen, then (only if nothing is due) some
    to practise ahead. Mixed across lessons, so it is the right idea that has to be chosen."""
    states = {s.card_id: s for s in db.scalars(select(ReviewState).where(ReviewState.user_id == user_id))}
    open_cards = [c for c in cards.values() if c.lesson in completed]
    rng = random.Random(f'{user_id}:{today.isoformat()}')
    due = sorted((c for c in open_cards if c.id in states and states[c.id].due <= today.isoformat()), key=lambda c: (states[c.id].due, states[c.id].box))
    new = [c for c in open_cards if c.id not in states]
    rng.shuffle(new)
    # Different lessons first: one new card per lesson, then the rest.
    seen_lessons, spread = set(), []
    for c in new:
        if c.lesson not in seen_lessons:
            spread.append(c)
            seen_lessons.add(c.lesson)
    new = spread + [c for c in new if c not in spread]
    chosen = (due + new)[:SESSION]
    ahead = False
    if not chosen:
        later = sorted((c for c in open_cards if c.id in states), key=lambda c: states[c.id].due)
        chosen, ahead = later[:SESSION], bool(later)
    rng.shuffle(chosen)
    units = Counter(unit_of(c.lesson, catalog) for c in chosen)
    unit = units.most_common(1)[0][0] if units else None
    name, about = CREATURES.get(unit, ('', ''))
    return {'cards': [public(c, rng) for c in chosen], 'due': len(due), 'ahead': ahead, 'unlocked': bool(open_cards),
            'creature': {'unit': unit, 'name': name, 'about': about} if unit else None,
            'tamed': tamed(states, cards, catalog), 'creatures': [{'unit': u, 'name': n, 'about': a} for u, (n, a) in CREATURES.items()]}


def answer(db, user_id, card, choice, lines, today):
    """Marks one answer, moves the card through its boxes, and says what was right and why."""
    right = lines == card.lines if card.kind == 'order' else choice == card.answer
    state = db.get(ReviewState, (user_id, card.id))
    if state is None:
        state = ReviewState(user_id=user_id, card_id=card.id, box=0, seen=0, correct=0, due=today.isoformat())
        db.add(state)
    state.box = min(state.box + 1, 4) if right else 1
    days = INTERVALS[state.box] if right else 1
    state.due = (today + timedelta(days=days)).isoformat()
    state.seen += 1
    state.correct += int(right)
    shown = {'correct': right, 'why': card.why, 'back_in_days': days}
    shown.update({'lines': card.lines} if card.kind == 'order' else {'answer': card.answer})
    return shown

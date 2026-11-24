"""Every lesson explains what it asks for, and does not pour on more than it explains.

docs/plan/lesson-page-rules.md, rules C1 to C3. Checked over every released lesson, in course order:

C1. A function or method that the challenge, the "Try it" task or a hint names must already be known:
    used in this lesson's Discover card, worked example or note, or in an earlier lesson, or written by
    the learner (defined in the lesson's own sample programs), or explained in the same sentence that
    names it ("abs() gives a number without its minus sign").
C2. A Discover card brings in at most six new functions or methods, so each one gets its own example.
C3. A Discover card is at most 130 words. Longer means two lessons.
C4. No paragraph, and no step of a list, in a Discover card, "Try it" task or challenge is over 45 words.
    A longer task is written as a goal, then numbered steps ("1. "), then what the check does, each on
    its own line; the lesson page shows those as paragraphs and a list (frontend/app/prose.tsx).
"""
import json
import re
from pathlib import Path

CONTENT = Path(__file__).resolve().parents[1] / 'content'
CALL = re.compile(r'(?:(?<=\.)|(?<![\w.]))([A-Za-z_]\w*)\(')
EXPLAINS = re.compile(r'\b(gives|is|are|does|turns|splits|keeps|reads|returns|makes|joins|swaps|counts|rounds)\b')
ALWAYS = {'print'}
PARAGRAPH_WORDS = 45
BLOCK = re.compile(r'\n\s*\n|\n(?=\d+\. |- )')


def lessons_in_order():
    catalog = json.loads((CONTENT / 'catalog.json').read_text())
    by_id = {}
    for path in CONTENT.glob('*/u*/*.json'):
        lesson = json.loads(path.read_text())
        by_id[lesson['id']] = lesson
    for path in CONTENT.glob('*.json'):
        lesson = json.loads(path.read_text())
        if 'tasks' in lesson:
            by_id[lesson['id']] = lesson
    return [by_id[l] for c in catalog['courses'] for u in c['units'] if u['status'] == 'released' for l in u['lessons']]


def task(lesson, kind):
    return next(t for t in lesson['tasks'] if t['type'] == kind)


def sentences(text):
    return re.split(r'(?<=[.!?])\s+(?=[A-Z"(])', text)


def audit():
    known, problems, discover = set(ALWAYS), [], {}
    for lesson in lessons_in_order():
        d, ex, ch, guided = task(lesson, 'discover'), task(lesson, 'example'), task(lesson, 'challenge'), task(lesson, 'guided')
        taught_text = ' '.join([d['body'], d['detail'], ex['code'], ex.get('note', '')])
        taught = set(CALL.findall(taught_text))
        own = set()
        for sample in [*ch.get('other_ways', []), ch.get('similar_example') or {}]:
            own |= set(re.findall(r'def (\w+)\(', sample.get('code', '') if isinstance(sample, dict) else ''))
        for text in [ch['prompt'], guided['prompt'], *ch.get('hints', [])]:
            own |= set(re.findall(r'def (\w+)\(', text))
            own |= set(re.findall(r'\b(?:[Ww]rite|[Gg]ive \w+ a method|function,?|method,?) (\w+)\(', text))
        for where, text in [('challenge', ch['prompt']), ('try it', guided['prompt'])] + [(f'hint {i + 1}', h) for i, h in enumerate(ch.get('hints', []))]:
            for sentence in sentences(text):
                for name in set(CALL.findall(sentence)) - taught - known - own:
                    if name[0].isupper():
                        continue  # a class the learner writes
                    if not EXPLAINS.search(sentence):
                        problems.append(f'{lesson["id"]} {where}: {name}() is used but never explained: "{sentence[:120]}"')
        discover[lesson['id']] = (sorted(taught - known), len((d['body'] + ' ' + d['detail']).split()))
        known |= taught
    return problems, discover


def test_c1_nothing_is_asked_for_that_was_never_explained():
    problems, _ = audit()
    assert problems == []


def test_c2_a_discover_card_brings_in_at_most_six_new_tools():
    _, discover = audit()
    assert {k: v[0] for k, v in discover.items() if len(v[0]) > 6} == {}


def test_c3_a_discover_card_is_at_most_130_words():
    _, discover = audit()
    assert {k: v[1] for k, v in discover.items() if v[1] > 130} == {}


def test_the_audit_catches_an_unexplained_tool():
    # A hint that names a tool nobody explained is caught; the same hint with an explanation is not.
    bad = 'Use zfill() on the number.'
    good = 'zfill(3) pads a number with zeros, so "7".zfill(3) is "007".'
    assert not EXPLAINS.search(bad) and EXPLAINS.search(good)


def test_c4_no_paragraph_or_step_is_over_45_words():
    long = {}
    for lesson in lessons_in_order():
        for t in lesson['tasks']:
            for field in ('body', 'detail', 'prompt'):
                for block in BLOCK.split(t.get(field, '')):
                    if len(block.split()) > PARAGRAPH_WORDS:
                        long[f'{lesson["id"]} {t["type"]} {field}'] = len(block.split())
    assert long == {}

"""One check for every piece of text a learner types that is kept or could be shown: today the profile
nickname; later feedback, project titles, and anything shared.

It refuses two things, with a message the learner can act on:
- personal details: an email address, a phone number, a web link, or what looks like a street address,
  because a young learner should not put these into an app, even into a field only they see;
- words on the owner's blocked list (content/policy/blocked-words.txt), matched as whole words after
  undoing common disguises, never inside other words.

It is a guard rail, not moderation: it cannot judge meaning, and anything shown to other people later
needs a human report-and-review path as well.
"""
import re
from pathlib import Path

LIST = Path(__file__).resolve().parent.parent / 'content' / 'policy' / 'blocked-words.txt'
DISGUISES = str.maketrans({'0': 'o', '1': 'i', '!': 'i', '3': 'e', '4': 'a', '@': 'a', '5': 's', '$': 's', '7': 't', '+': 't', '*': 'u'})
EMAIL = re.compile(r'\S+@\S+\.\S+|\S+\s*(@|\bat\b)\s*\S+\s*(\.|\bdot\b)\s*(com|org|net|ca|co|edu)\b', re.I)
LINK = re.compile(r'https?://|www\.|\b[a-z0-9-]+\.(com|org|net|ca|io|co|gg|tv|me|ly)\b', re.I)
PHONE = re.compile(r'(?:\d[\s().-]*){7,}')
ADDRESS = re.compile(r'\b\d{1,5}\s+\w+(\s+\w+)?\s+(street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd|crescent|cres|court|ct)\b', re.I)


def blocked_words(path=LIST):
    return {w.strip().lower() for w in Path(path).read_text().splitlines() if w.strip() and not w.startswith('#')}


BLOCKED = blocked_words()


def problem(text, blocked=None):
    """None if the text may be kept, otherwise a sentence saying what to change."""
    blocked = BLOCKED if blocked is None else blocked
    if EMAIL.search(text) or LINK.search(text) or PHONE.search(text) or ADDRESS.search(text):
        return 'Please leave out personal details: no email addresses, phone numbers, links or addresses.'
    for raw in re.findall(r"[\w@$*!+]+", text.lower()):
        word = raw.translate(DISGUISES)
        squeezed = re.sub(r'(.)\1+', r'\1', word)
        if word in blocked or squeezed in blocked or word.strip('_') in blocked:
            return 'Please choose different words.'
    return None

"""ENG-09: self-reviewed challenges (docs/plan/courses/py-final-project.md, section 3).

The learner ticks each criterion of a short rubric and says, in their own words, what they did. Nothing
checks the work itself, so the record is labelled self-reported wherever it appears. What is checked is
the writing, so a review cannot be clicked through: every box ticked, enough words, not the question
copied back, not one word over and over, and nothing the text policy refuses.
"""
import re

from . import text_policy

WORD = re.compile(r"[A-Za-z0-9']+")
MAX_CHARS = 2000


def words(text):
    return [w.lower() for w in WORD.findall(text)]


def problem(criterion, done, evidence):
    """What is wrong with one answer, or None."""
    if not done:
        return 'Tick this when you have done it.'
    said = words(evidence)
    if len(said) < criterion.min_words:
        return f'Say a little more, in your own words: at least {criterion.min_words} words ({len(said)} so far).'
    asked = set(words(criterion.text + ' ' + criterion.ask))
    own = [w for w in said if w not in asked]
    if len(own) < max(3, len(said) // 4):
        return 'That mostly repeats the question. Say what you did, with your own details.'
    if len(set(said)) < len(said) * 0.4:
        return 'That repeats itself. Say what you actually did.'
    if (reason := text_policy.problem(evidence)):
        return reason
    return None


def judge(review, answers):
    """{criterion id: problem} for every answer that cannot be recorded yet; empty when all can."""
    found = {}
    for criterion in review.criteria:
        answer = answers.get(criterion.id) or {}
        if (reason := problem(criterion, bool(answer.get('done')), str(answer.get('evidence') or '')[:MAX_CHARS])):
            found[criterion.id] = reason
    return found


RECORDED = 'Recorded as your own review. Nothing checked the work itself, so it is kept as self-reported, in your words.'
NEEDS_WORK = 'Not recorded yet. Each note below says what to change.'

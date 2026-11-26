# Lockpick: guess the word one letter at a time before six misses jam the lock.
# The game is built on the four functions below. Fill them in one at a time,
# starting with mask(), and run after each one.
import random

MAX_MISSES = 6


def load_words(path):
    """The words in the file at path, one per line, in lowercase."""
    return []


def mask(word, guessed):
    """The word with every letter not guessed yet shown as _: mask("vault", {"a"}) is "_ a _ _ _"."""
    return word


def problem_with(guess, guessed):
    """What is wrong with a guess, or "" when it is fine."""
    return ""


def is_open(word, guessed):
    """True when every letter of the word has been guessed."""
    return False


print(mask("vault", {"a"}))

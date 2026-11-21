# Lockpick: guess the word one letter at a time before the lock jams.
# Reference version of final project 1. Uses only what units 1 to 7 and 9 teach.
import random

MAX_MISSES = 6


def load_words(path):
    """The words in a file, one per line, in lowercase. Blank lines and lines that are not
    a single word are skipped."""
    words = []
    with open(path) as f:
        for line in f:
            word = line.strip().lower()
            if word.isalpha():
                words.append(word)
    return words


def mask(word, guessed):
    """The word with every letter not guessed yet shown as _: mask("vault", {"a"}) is "_ a _ _ _"."""
    shown = []
    for letter in word:
        if letter in guessed:
            shown.append(letter)
        else:
            shown.append("_")
    return " ".join(shown)


def problem_with(guess, guessed):
    """What is wrong with a guess, or "" when it is fine."""
    if len(guess) != 1 or not guess.isalpha():
        return "Type one letter, a to z."
    if guess in guessed:
        return f"You already tried {guess}."
    return ""


def is_open(word, guessed):
    """True when every letter of the word has been guessed."""
    for letter in word:
        if letter not in guessed:
            return False
    return True


def play(word):
    """One round. Returns True if the lock opens."""
    guessed = set()
    misses = 0
    while misses < MAX_MISSES:
        print(mask(word, guessed), f"  ({MAX_MISSES - misses} tries left)")
        guess = input("Your letter: ").strip().lower()
        problem = problem_with(guess, guessed)
        if problem:
            print(problem)
            continue
        guessed.add(guess)
        if guess not in word:
            misses = misses + 1
            print("Not in this lock.")
        elif is_open(word, guessed):
            print(f"Click! The vault opens: {word}")
            return True
    print(f"The lock jams. The word was {word}.")
    return False


def main():
    words = load_words("words.txt")
    wins = 0
    rounds = 0
    while True:
        rounds = rounds + 1
        if play(random.choice(words)):
            wins = wins + 1
        print(f"Vaults opened: {wins} of {rounds}")
        again = input("Play again? (y/n) ").strip().lower()
        if again != "y":
            break


if __name__ == "__main__":
    main()

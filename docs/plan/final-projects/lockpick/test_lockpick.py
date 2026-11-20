# The learner's own tests for Lockpick: at least five, including the edges.
from lockpick import mask, problem_with, is_open, load_words

assert mask("vault", set()) == "_ _ _ _ _"
assert mask("vault", {"a", "t"}) == "_ a _ _ t"
assert mask("level", {"l"}) == "l _ _ _ l"          # a letter that appears twice
assert problem_with("a", set()) == ""
assert problem_with("ab", set()) == "Type one letter, a to z."
assert problem_with("", set()) == "Type one letter, a to z."   # just pressing Enter
assert problem_with("7", set()) == "Type one letter, a to z."
assert problem_with("a", {"a"}) == "You already tried a."
assert is_open("vault", set("vault"))
assert not is_open("vault", {"v", "a"})
assert load_words("words.txt") == ["vault", "lantern", "compass", "harbour", "cipher"]
print("All Lockpick tests passed.")

# The learner's own tests for Planner: at least ten, across the three modules.
from datetime import date

import commands
import storage
from tasks import Planner, Task

TODAY = date(2026, 11, 20)

p = Planner()
assert commands.run(p, "add Read chapter 3", TODAY) == "Added: [ ] Read chapter 3"
assert commands.run(p, "add Essay by 2026-11-18", TODAY) == "Added: [ ] Essay (due 2026-11-18, late)"
assert commands.run(p, "ADD   Spaced   out  ", TODAY) == "Added: [ ] Spaced out"       # case and spaces
assert commands.run(p, "done 2", TODAY) == "Done: Essay"
assert commands.run(p, "stats", TODAY) == "1 of 3 done, 0 late."
assert commands.run(p, "list", TODAY).split("\n")[1] == "2. [x] Essay (due 2026-11-18)"
assert commands.run(p, "quit", TODAY) is None
for bad, says in [("done 9", "no task 9"), ("done two", "number"), ("add", "needs a title"), ("add X by 2026-13-01", "Dates look like")]:
    try:
        commands.run(p, bad, TODAY)
        assert False, bad
    except ValueError as problem:
        assert says in str(problem), (bad, problem)
assert commands.run(p, "dance", TODAY).startswith("I don't know 'dance'")
assert Task("x", date(2026, 11, 19)).is_late(TODAY) and not Task("x", TODAY).is_late(TODAY)   # due today is not late

# Saving and loading gives back the same plan; a missing or damaged file starts a new one.
storage.save(p, "test-plan.json")
again, note = storage.load("test-plan.json")
assert note == "Loaded 3 tasks." and [t.to_dict() for t in again.tasks] == [t.to_dict() for t in p.tasks]
assert storage.load("missing.json")[1].startswith("No saved plan yet")
with open("broken.json", "w") as f:
    f.write("[{not json")
assert len(storage.load("broken.json")[0].tasks) == 0
print("All Planner tests passed.")

# Planner: a to-do app that remembers your plan between runs.
# Reference version of final project 3: four files, classes, saved data and tests.
from datetime import date

import commands
import storage

FILE = "plan.json"


def main():
    planner, note = storage.load(FILE)
    print(note)
    print(commands.HELP)
    while True:
        line = input("> ")
        try:
            reply = commands.run(planner, line, date.today())
        except ValueError as problem:
            print(problem)
            continue
        if reply is None:
            break
        print(reply)
    storage.save(planner, FILE)
    print(f"Saved {len(planner.tasks)} tasks.")


if __name__ == "__main__":
    main()

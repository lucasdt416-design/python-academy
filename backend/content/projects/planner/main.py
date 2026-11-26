# Planner: a to-do app that remembers your plan between runs.
# Commands go in commands.py, saving and loading in storage.py, and this file
# only joins them up. Turn on "Keep files my program writes" so plan.json
# is still here next time.
import commands
import storage

FILE = "plan.json"

plan = storage.load(FILE)
print(commands.HELP)

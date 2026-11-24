# Reading what the user types and carrying it out. Returns text to show; never prints.
from datetime import date

HELP = "Commands: add <title> [by YYYY-MM-DD], list, done <n>, remove <n>, stats, help, quit"


def parse(line):
    """("add", ["Read", "chapter", "3"]) from "add Read chapter 3"."""
    words = line.strip().split()
    if not words:
        return "", []
    return words[0].lower(), words[1:]


def title_and_due(words):
    """Read chapter 3 by 2026-12-01 -> ("Read chapter 3", date(2026, 12, 1))."""
    if len(words) >= 2 and words[-2] == "by":
        try:
            return " ".join(words[:-2]), date.fromisoformat(words[-1])
        except ValueError:
            raise ValueError("Dates look like 2026-12-01.")
    return " ".join(words), None


def number(words):
    if len(words) != 1 or not words[0].isdigit():
        raise ValueError("Give the task's number, like: done 2")
    return int(words[0])


def run(planner, line, today):
    """Carry out one command. Returns what to show, or None to quit. Raises ValueError for a bad command."""
    command, words = parse(line)
    if command == "add":
        task = planner.add(*title_and_due(words))
        return f"Added: {task.describe(today)}"
    if command == "list":
        if not planner.tasks:
            return "Nothing planned. Add a task with: add <title>"
        return "\n".join(f"{n}. {t.describe(today)}" for n, t in enumerate(planner.tasks, start=1))
    if command == "done":
        return f"Done: {planner.complete(number(words)).title}"
    if command == "remove":
        return f"Removed: {planner.remove(number(words)).title}"
    if command == "stats":
        s = planner.stats(today)
        return f"{s['done']} of {s['total']} done, {s['late']} late."
    if command in ("help", ""):
        return HELP
    if command == "quit":
        return None
    return f"I don't know {command!r}. {HELP}"

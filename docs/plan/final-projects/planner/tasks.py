# The planner's data: a Task, and a Planner that holds them. Nothing here prints or asks.
from datetime import date


class Task:
    def __init__(self, title, due=None, done=False):
        self.title = title
        self.due = due          # a date, or None
        self.done = done

    def is_late(self, today):
        return not self.done and self.due is not None and self.due < today

    def describe(self, today):
        mark = "x" if self.done else " "
        when = ""
        if self.due is not None:
            when = f" (due {self.due.isoformat()}"
            if self.is_late(today):
                when = when + ", late"
            when = when + ")"
        return f"[{mark}] {self.title}{when}"

    def to_dict(self):
        return {"title": self.title, "due": self.due.isoformat() if self.due else None, "done": self.done}


def task_from_dict(row):
    due = date.fromisoformat(row["due"]) if row.get("due") else None
    return Task(row["title"], due, bool(row.get("done", False)))


class Planner:
    def __init__(self):
        self.tasks = []

    def add(self, title, due=None):
        title = title.strip()
        if not title:
            raise ValueError("A task needs a title, like: add Read chapter 3")
        self.tasks.append(Task(title, due))
        return self.tasks[-1]

    def find(self, number):
        if not self.tasks:
            raise ValueError("There are no tasks yet. Add one with: add <title>")
        if number < 1 or number > len(self.tasks):
            raise ValueError(f"There is no task {number}. Pick 1 to {len(self.tasks)}.")
        return self.tasks[number - 1]

    def complete(self, number):
        task = self.find(number)
        task.done = True
        return task

    def remove(self, number):
        task = self.find(number)
        self.tasks.remove(task)
        return task

    def stats(self, today):
        done = sum(1 for t in self.tasks if t.done)
        late = sum(1 for t in self.tasks if t.is_late(today))
        return {"total": len(self.tasks), "done": done, "late": late}

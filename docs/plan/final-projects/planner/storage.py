# Saving and loading the plan as JSON. A missing or damaged file never crashes the app.
import json

from tasks import Planner, task_from_dict


def load(path):
    """(planner, a note to show). A damaged file is left as it is, and the app starts empty."""
    planner = Planner()
    try:
        with open(path) as f:
            rows = json.load(f)
        for row in rows:
            planner.tasks.append(task_from_dict(row))
    except FileNotFoundError:
        return planner, "No saved plan yet: starting a new one."
    except (ValueError, KeyError, TypeError):
        return Planner(), f"{path} could not be read, so this is a new plan. The file was not changed."
    return planner, f"Loaded {len(planner.tasks)} tasks."


def save(planner, path):
    with open(path, "w") as f:
        json.dump([task.to_dict() for task in planner.tasks], f, indent=1)

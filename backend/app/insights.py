"""Mistake detectors: name a likely cause when a learner's program did not pass (lesson-feedback.md).

Each detector reads the program's syntax tree, never runs it, and looks for one well-known beginner
misconception, such as text from input() used as a number, or a total that starts again inside its
loop. What it finds is offered as "a likely cause", never as a verdict: the check alone decides whether
a program is right, and a detector can be wrong. Every detector is tested against every correct program
in the lessons, so it does not fire on right answers there.
"""
import ast
from dataclasses import dataclass

MUTATORS = {'append', 'extend', 'insert', 'remove', 'sort', 'reverse', 'clear', 'update', 'add', 'discard'}
BUILTINS = {'list', 'str', 'int', 'float', 'len', 'print', 'input', 'sum', 'max', 'min', 'range', 'dict', 'set', 'type', 'sorted', 'round', 'abs'}
EMPTY = (ast.List, ast.Dict, ast.Set, ast.Tuple)


@dataclass
class Insight:
    id: str
    line: int
    text: str

    def as_dict(self):
        return {'id': self.id, 'line': self.line, 'text': self.text}


def _is_call(node, name):
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name


def _names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _assigned(body):
    """Names assigned anywhere in these statements (including augmented assignment and loop targets)."""
    found = set()
    for stmt in body:
        for n in ast.walk(stmt):
            if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                for t in targets:
                    found |= {x.id for x in ast.walk(t) if isinstance(x, ast.Name)}
            elif isinstance(n, (ast.For, ast.comprehension)):
                found |= {x.id for x in ast.walk(n.target) if isinstance(x, ast.Name)}
            elif isinstance(n, ast.NamedExpr):
                found.add(n.target.id)
    return found


def text_used_as_number(tree):
    """x = input(...) and later x in arithmetic with a number, a comparison with a number, or range(x)."""
    texts = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and _is_call(n.value, 'input'):
            texts.setdefault(n.targets[0].id, n.lineno)
    # A name that is ever given a number, or turned into one, is not just text.
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in texts for t in n.targets) and not _is_call(n.value, 'input'):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    texts.pop(t.id, None)
    if not texts:
        return []
    number = lambda e: isinstance(e, ast.Constant) and type(e.value) in (int, float)  # noqa: E731
    for n in ast.walk(tree):
        hit = None
        if isinstance(n, ast.BinOp) and not isinstance(n.op, ast.Mod):
            for a, b in ((n.left, n.right), (n.right, n.left)):
                if isinstance(a, ast.Name) and a.id in texts and (number(b) or isinstance(n.op, (ast.Sub, ast.Div, ast.FloorDiv))):
                    hit = a
        elif isinstance(n, ast.Compare) and len(n.comparators) == 1 and isinstance(n.ops[0], (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)):
            for a, b in ((n.left, n.comparators[0]), (n.comparators[0], n.left)):
                if isinstance(a, ast.Name) and a.id in texts and number(b):
                    hit = a
        elif _is_call(n, 'range'):
            hit = next((a for a in n.args if isinstance(a, ast.Name) and a.id in texts), None)
        if hit is not None:
            return [Insight('text-not-number', texts[hit.id], f'`{hit.id}` holds the text from input() on line {texts[hit.id]}, even when the player types digits. Turn it into a number with int(...) where it is read, before you count or compare with it.')]
    return []


def _used_later_in_turn(loop, name, grow):
    """Whether a statement of the loop's body, after the one that builds name up, reads name."""
    at = next((i for i, stmt in enumerate(loop.body) if any(x is grow for x in ast.walk(stmt))), None)
    if at is None:
        return False
    return any(isinstance(x, ast.Name) and x.id == name and isinstance(x.ctx, ast.Load) for stmt in loop.body[at + 1:] for x in ast.walk(stmt))


def reset_inside_loop(tree):
    """A loop that sets total = 0 (or [] or "") and also builds total up, in its own body. Quiet when the
    same turn goes on to use the value it built, like a count printed for each row: that is a fresh
    count per turn, on purpose."""
    for loop in (n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))):
        starts = {}
        for stmt in loop.body:
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                v = stmt.value
                if (isinstance(v, ast.Constant) and v.value in (0, '', 0.0) and type(v.value) is not bool) or (isinstance(v, EMPTY) and not getattr(v, 'elts', getattr(v, 'keys', [1]))):
                    starts.setdefault(stmt.targets[0].id, stmt.lineno)
        for name, line in starts.items():
            for n in ast.walk(loop):
                grows = (isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) and n.target.id == name) or \
                        (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets) and name in _names_in(n.value)) or \
                        (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == name and n.func.attr in MUTATORS)
                if grows and getattr(n, 'lineno', 0) > line:
                    if _used_later_in_turn(loop, name, n):
                        break
                    return [Insight('reset-in-loop', line, f'`{name}` starts again on line {line}, inside the loop, so it forgets every earlier turn. Give it its starting value once, above the loop.')]
    return []


def mutator_assigned(tree):
    """pack = pack.append(x): the list is replaced by None."""
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr in MUTATORS:
            name = ast.unparse(n.targets[0])
            return [Insight('mutator-assigned', n.lineno, f'{n.value.func.attr}() changes `{ast.unparse(n.value.func.value)}` and gives back None, so line {n.lineno} stores None in `{name}`. Call it on a line of its own, without `{name} =`.')]
    return []


def print_not_return(tree):
    """A function that prints but never returns a value, whose result the program then uses."""
    funcs = {f.name: f for f in tree.body if isinstance(f, ast.FunctionDef)}
    for name, f in funcs.items():
        prints = any(_is_call(n, 'print') for n in ast.walk(f))
        returns = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(f))
        if not prints or returns:
            continue
        for n in ast.walk(tree):
            used = isinstance(n, (ast.BinOp, ast.Compare, ast.Assign, ast.AugAssign, ast.Return)) or (isinstance(n, ast.Call) and not _is_call(n, name))
            if used and any(_is_call(c, name) for c in ast.iter_child_nodes(n)) or (isinstance(n, ast.Call) and any(_is_call(a, name) for a in n.args) and not _is_call(n, 'print')):
                return [Insight('print-not-return', f.lineno, f'{name}() prints its answer but gives back None, and the program uses what it gives back. Use return to hand the value back; print() only shows it.')]
    return []


def quoted_name(tree):
    """print("hero") when hero is a variable: the word, not the value."""
    names = _assigned(tree.body)
    for n in ast.walk(tree):
        if _is_call(n, 'print'):
            for a in n.args:
                labelled = any(isinstance(o, ast.Name) and o.id == a.value for o in n.args)
                if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value in names and a.value.isidentifier() and not labelled:
                    return [Insight('quoted-name', n.lineno, f'Line {n.lineno} prints the word "{a.value}", because of the quotes. To show what `{a.value}` holds, write it without quotes.')]
    return []


def loop_never_changes(tree):
    """while test: with nothing in the body that could change what the test reads."""
    for loop in (n for n in ast.walk(tree) if isinstance(n, ast.While)):
        # A test that calls something (input(), a method) or assigns can change on its own.
        if isinstance(loop.test, ast.Constant) or any(isinstance(n, (ast.Call, ast.NamedExpr)) for n in ast.walk(loop.test)):
            continue
        reads = _names_in(loop.test)
        body = ast.Module(body=loop.body, type_ignores=[])
        changing = _assigned(loop.body) | {c.func.value.id for c in ast.walk(body) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name)}
        escapes = any(isinstance(n, (ast.Break, ast.Return, ast.Raise)) for n in ast.walk(body)) or any(isinstance(n, ast.Call) and not isinstance(n.func, ast.Name) for n in ast.walk(loop.test))
        if reads and not reads & changing and not escapes and not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id not in BUILTINS for n in ast.walk(body)):
            shown = ', '.join(f'`{r}`' for r in sorted(reads))
            return [Insight('loop-never-changes', loop.lineno, f'Nothing inside the loop on line {loop.lineno} changes {shown}, so its test gives the same answer every time and the loop never ends.')]
    return []


def return_in_loop(tree):
    """A return that is the plain last line of a for loop in a function: it ends on the first turn."""
    for f in (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)):
        for loop in (n for n in ast.walk(f) if isinstance(n, ast.For)):
            last = loop.body[-1]
            if isinstance(last, ast.Return) and len(loop.body) > 1 and not loop.orelse:
                return [Insight('return-in-loop', last.lineno, f'The return on line {last.lineno} is inside the loop, so {f.name}() gives back an answer on the very first turn. If it should use every item, move the return below the loop, with no indent inside it.')]
    return []


def shadowed_builtin(tree):
    """list = [...] and later list(...): Python's own list() is hidden."""
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id in BUILTINS and any(_is_call(c, t.id) and c.lineno > n.lineno for c in ast.walk(tree)):
                    return [Insight('shadowed-builtin', n.lineno, f'Line {n.lineno} gives the name `{t.id}` a value, which hides Python\'s own {t.id}(), and the program uses {t.id}() later. Pick another name, such as my_{t.id}.')]
    return []


def self_missing(tree):
    """In a method, name = name where self.name is meant."""
    for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
        attrs = {n.attr for n in ast.walk(cls) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == 'self'}
        outside = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and not (isinstance(n.value, ast.Name) and n.value.id == 'self')}
        for method in (n for n in cls.body if isinstance(n, ast.FunctionDef)):
            params = {a.arg for a in method.args.args}
            for stmt in ast.walk(method):
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                    name = stmt.targets[0].id
                    if name in params and isinstance(stmt.value, ast.Name) and stmt.value.id == name or (name not in attrs and name in outside and name in _names_in(stmt.value) | params):
                        return [Insight('self-missing', stmt.lineno, f'On line {stmt.lineno}, `{name} = …` makes a name that only lasts while {method.name}() runs. To keep it on the object, write self.{name} = ….')]
    return []


DETECTORS = [mutator_assigned, text_used_as_number, reset_inside_loop, print_not_return, quoted_name, loop_never_changes, return_in_loop, self_missing, shadowed_builtin]


def find(code, limit=2):
    """Up to `limit` likely causes, most specific first. A program Python cannot read gets none: its own
    error message is clearer."""
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, RecursionError):
        return []
    found = []
    for detect in DETECTORS:
        try:
            found += detect(tree)
        except (RecursionError, AttributeError, TypeError):
            continue
        if len(found) >= limit:
            break
    return [i.as_dict() for i in found[:limit]]

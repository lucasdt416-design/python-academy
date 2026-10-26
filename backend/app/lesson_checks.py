"""Bounded interpretation of the taught syntax; never exec/eval learner code.

Success messages say only what the check verified, then ask the learner to judge the rest
(docs/plan/lesson-feedback.md section 6 and appendix A; backlog ASSESS-07).
"""
import ast
import functools
import logging
import re
import traceback
from pathlib import Path

from . import content

# passed: meets the lesson's checks. needs_work: the learner can fix something.
# execution_error: the program failed while running in the browser.
# unsupported: valid work this checker cannot judge. service_error: the check itself failed.
RESULTS = ('passed', 'needs_work', 'execution_error', 'unsupported', 'service_error')
SERVICE_ERROR = 'Unable to assess this right now. Your code is unchanged; please try again in a moment.'

# Hint 3 of "Open the story" as published with validator v1: a complete answer, so copying it
# is not "making it your own" either.
RETIRED_HELLO_HINT = ('You land on Mars.', 'A robot offers you tea.')
PRINTED_TEXT = re.compile(r"""print\((["'])(.*?)\1\)""")


def same_text(line):
    """Compare story lines ignoring case, spacing and final punctuation."""
    return ' '.join(line.casefold().split()).rstrip('.!?')


@functools.cache
def handed_out(lesson_id):
    """Story text a lesson gives the learner: (worked example lines, lines spelled out in hints)."""
    lesson = content.load()[1][lesson_id]
    example = tuple(same_text(line) for line in lesson.task('example').output.splitlines())
    hinted = {same_text(match.group(2)) for hint in lesson.task('challenge').hints for match in PRINTED_TEXT.finditer(hint)}
    return {example, tuple(map(same_text, RETIRED_HELLO_HINT))}, hinted


class PracticeError(ValueError):
    result = 'needs_work'

class UnsupportedError(PracticeError):
    """The code goes beyond what this checker can interpret, which is not a learner mistake."""
    result = 'unsupported'

class Story:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.values = {}
        self.reads = set()
        self.input_count = 0
        self.lines = []
        self.steps = 0

    def value(self, node):
        self.steps += 1
        if self.steps > 500:
            raise UnsupportedError('Keep this chapter to short story instructions.')
        if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, bool)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in self.values:
                raise PracticeError(f'Define {node.id} before using it. Check spelling and capitalization.')
            self.reads.add(node.id)
            return self.values[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = self.value(node.left), self.value(node.right)
            if not isinstance(left, str) or not isinstance(right, str):
                raise UnsupportedError('In this chapter, use + to join text strings.')
            if len(left) + len(right) > 20000:
                raise UnsupportedError('Keep your story messages under 20,000 characters.')
            return left + right
        if isinstance(node, ast.JoinedStr):
            pieces = []
            for part in node.values:
                if isinstance(part, ast.Constant):
                    pieces.append(part.value)
                elif isinstance(part, ast.FormattedValue) and part.format_spec is None and part.conversion in (-1, 115, 114):
                    value = self.value(part.value)
                    pieces.append(repr(value) if part.conversion == 114 else str(value))
                else:
                    raise UnsupportedError('Use a simple f-string such as f"Hello, {hero}".')
            if sum(len(piece) for piece in pieces) > 20000:
                raise UnsupportedError('Keep your story messages under 20,000 characters.')
            return ''.join(pieces)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'input' and len(node.args) <= 1 and not node.keywords:
            if node.args:
                self.value(node.args[0])
            self.input_count += 1
            try:
                return next(self.replies)
            except StopIteration:
                raise PracticeError('Add a player reply for each input() call, in order.')
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            left, right = self.value(node.left), self.value(node.comparators[0])
            if isinstance(node.ops[0], ast.Eq):
                return left == right
            if isinstance(node.ops[0], ast.NotEq):
                return left != right
        raise UnsupportedError('For this chapter, use the syntax taught on the cards: strings, variables, print(), input(), +, f-strings, and if/else with == or !=.')

    def run(self, statements):
        for node in statements:
            self.steps += 1
            if self.steps > 500:
                raise UnsupportedError('Keep this chapter to short story instructions.')
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                self.values[node.targets[0].id] = self.value(node.value)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'print' and not node.value.keywords:
                text = ' '.join(str(self.value(arg)) for arg in node.value.args)
                if len(text) + sum(len(line) + 1 for line in self.lines) > 20000:
                    raise UnsupportedError('Keep your story output under 20,000 characters.')
                self.lines.append(text)
            elif isinstance(node, ast.If):
                self.run(node.body if self.value(node.test) else node.orelse)
            elif isinstance(node, ast.Pass):
                pass
            else:
                raise UnsupportedError('This chapter checks story instructions, not imports, functions, or loops. Try the syntax shown in the example.')
        return self

    @property
    def output(self):
        return ''.join(line + '\n' for line in self.lines)


def check_story(lesson_id, code, output, replies):
    """Original interface: (passed, feedback)."""
    result, feedback = assess(lesson_id, code, output, replies)
    return result == 'passed', feedback


def assess(lesson_id, code, output, replies):
    """Return (result, feedback), where result is one of RESULTS."""
    try:
        tree = ast.parse(code)
        if len(list(ast.walk(tree))) > 500:
            raise UnsupportedError('Keep your adventure short while you learn the basics.')
        actual = Story(replies).run(tree.body)
        if actual.output != output.replace('\r\n', '\n'):
            raise PracticeError('Run your current code with the displayed player replies again. The submitted output does not match those instructions.')
        if lesson_id == 'hello':
            if len(tree.body) != 2 or len(actual.lines) != 2 or any(not line.strip() or '\n' in line or '\r' in line for line in actual.lines):
                raise PracticeError('Write two print statements with nonempty messages: one location, then one surprise.')
            # Whether the lines are a place and a surprise is the learner's judgment, not checked here.
            if not all(any(c.isalpha() for c in line) for line in actual.lines):
                raise PracticeError("Use words for each message: first a place, then something unexpected. Numbers or punctuation on their own don't tell a story.")
            first, second = map(same_text, actual.lines)
            if first == second:
                raise PracticeError('Both lines say the same thing. Change the second one into a surprise.')
            if any('___' in line for line in actual.lines):
                raise PracticeError('Fill in the ___ from the hint with your own words.')
            examples, hinted = handed_out('hello')
            if (first, second) in examples:
                raise PracticeError("That's the example from the card. Make it your own: change the place and the surprise.")
            if first in hinted or second in hinted:
                raise PracticeError('That line comes straight from a hint. Change it into your own words.')
            feedback = 'Python printed your two different messages in order. Read them back: does the first set the scene and the second surprise you? That part is your call.'
        elif lesson_id == 'variables':
            if not all(isinstance(actual.values.get(n), str) and actual.values[n].strip() and n in actual.reads and actual.values[n] in actual.output for n in ('hero', 'tool')):
                raise PracticeError('Assign nonempty text to hero and tool, then print their values using the variables. Quoted "hero" prints the word, not its stored value.')
            feedback = 'hero and tool both hold text, and your program prints their values by using the variables. Change one value and run again: does your story change the way you expect?'
        elif lesson_id == 'input':
            for name in ('River-472', 'Sky-839'):
                test = Story([name]).run(tree.body)
                if test.input_count != 1 or name not in test.output:
                    raise PracticeError('Use the value returned by input() in your greeting. Test a different player name; a hard-coded name will not change with the reply.')
            feedback = 'Your greeting used the reply: it changed when we tried two different player names. Run it with your own name as the reply: does the greeting read the way you want?'
        elif lesson_id in ('choices', 'adventure'):
            if not any(isinstance(n, ast.If) and n.orelse for n in ast.walk(tree)):
                raise PracticeError('Add an if condition and an else block, with an indented story message in each.')
            results = []
            for name in ('River-472', 'Sky-839'):
                paths = []
                for path in ('left', 'right'):
                    test = Story([path] if lesson_id == 'choices' else [name, path]).run(tree.body)
                    if test.input_count != (1 if lesson_id == 'choices' else 2):
                        raise PracticeError('Ask for a path once.' if lesson_id == 'choices' else 'Ask for the player name first and the path second, using two input() calls.')
                    if not test.output.strip() or (lesson_id == 'adventure' and name not in test.output):
                        raise PracticeError('Print a discovery for each path.' if lesson_id == 'choices' else 'Welcome the player using their input name, then reveal the ending.')
                    paths.append(test.output)
                if paths[0] == paths[1]:
                    raise PracticeError('Left and right currently tell the same story. Give the if and else blocks different discoveries, and compare the input variable with "left" or "right".')
                results.extend(paths)
            if lesson_id == 'adventure':
                first = tree.body[0] if tree.body else None
                if not (isinstance(first, ast.Expr) and isinstance(first.value, ast.Call) and isinstance(first.value.func, ast.Name) and first.value.func.id == 'print' and actual.lines and actual.lines[0].strip()):
                    raise PracticeError('Start by printing an opening scene before asking the player for their name.')
            feedback = ('Your program asks once and prints a different discovery for left and for right. Which path would you pick, and does each discovery fit your story?' if lesson_id == 'choices'
                        else 'Your adventure opens with a scene, welcomes players by the name they type, and gives left and right different endings. You combined all four Python skills! Read both endings: do they finish the story you started?')
        else:
            raise UnsupportedError('Choose a lesson from Build Your Own Adventure.')
        return 'passed', feedback
    except SyntaxError as error:
        return 'needs_work', f'Python cannot read line {error.lineno} yet. Check matching quotes, parentheses, colons, and indentation.'
    except PracticeError as error:
        return error.result, str(error) or 'Try the short example on this card, then make one change at a time.'
    except (TypeError, ValueError, RecursionError) as error:
        return 'unsupported', str(error) or 'Try the short example on this card, then make one change at a time.'
    except Exception as error:
        # Never log learner code: the exception message can echo names or strings
        # from it, so record only the lesson, error type, and server code location.
        frame = traceback.extract_tb(error.__traceback__)[-1]
        logging.getLogger(__name__).error('Story check failed: lesson=%s error=%s at %s:%s',
                                          lesson_id, type(error).__name__, Path(frame.filename).name, frame.lineno)
        return 'service_error', SERVICE_ERROR

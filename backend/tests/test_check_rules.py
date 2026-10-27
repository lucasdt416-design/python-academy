"""Named check rules, their messages, and tagged hints (ENG-04 part 2a; docs/plan/lesson-feedback.md sections 6 and 7)."""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from app import content, lesson_checks
from app.lesson_checks import RULES, Story, judge, rule_errors

CATALOG, LESSONS = content.load()


def two_lines(first, second):
    return f'print({json.dumps(first)})\nprint({json.dumps(second)})'


def run(lesson_id, code, replies=()):
    """Check code the way the app does: the output is what the program really prints."""
    try:
        output = Story(list(replies)).run(ast.parse(code).body).output
    except Exception:
        output = ''
    return judge(lesson_id, code, output, list(replies))


SCENE = 'print("A storm.")\nhero = input("Name? ")\nprint("Hi, " + hero)\npath = input("Way? ")\n'
IF_ELSE = 'if path == "left":\n    print({!r})\nelse:\n    print({!r})'
# One program for every rule, showing that each rule can really be reported.
SAMPLES = {
    'hello.two-lines': ('print("hi")', []),
    'hello.words': ('print(1)\nprint(2)', []),
    'hello.different-lines': (two_lines('hi', 'hi'), []),
    'hello.fill-blank': (two_lines('You wake up in ___.', 'A door creaks.'), []),
    'hello.not-the-example': (two_lines('You arrive at a moonlit castle.', 'A tiny dragon opens the gate.'), []),
    'hello.not-a-hint': (two_lines('The shop opens at nine.', 'A dragon!'), []),  # the similar example's line
    'hello.passed': (two_lines('A forest.', 'A dragon!'), []),
    'variables.uses-variables': ('hero = "Kai"\ntool = "rope"\nprint("hero")', []),
    'variables.passed': ('hero = "Kai"\ntool = "rope"\nprint(hero + " carries a " + tool)', []),
    'input.uses-reply': ('player = input("Name? ")\nprint("Hello, Kai")', ['Kai']),
    'input.passed': ('player = input("Name? ")\nprint("Hello, " + player)', ['Kai']),
    'choices.if-else': ('path = input("Way? ")\nprint("A river.")', ['left']),
    'choices.ask-once': ('path = "left"\n' + IF_ELSE.format('A river.', 'A tower.'), ['left']),
    'choices.print-each': ('path = input("Way? ")\nif path == "left":\n    print("A river.")\nelse:\n    pass', ['left']),
    'choices.different-paths': ('path = input("Way? ")\n' + IF_ELSE.format('Same.', 'Same.'), ['left']),
    'choices.passed': ('path = input("Way? ")\n' + IF_ELSE.format('A river.', 'A tower.'), ['left']),
    'adventure.if-else': (SCENE, ['Kai', 'left']),
    'adventure.two-inputs': ('print("A storm.")\nhero = "Kai"\npath = "left"\nprint("Hi, " + hero)\n' + IF_ELSE.format('L.', 'R.'), ['Kai', 'left']),
    'adventure.welcome': ('print("A storm.")\nhero = input("Name? ")\npath = input("Way? ")\n' + IF_ELSE.format('L.', 'R.'), ['Kai', 'left']),
    'adventure.different-paths': (SCENE + IF_ELSE.format('Same.', 'Same.'), ['Kai', 'left']),
    'adventure.opening-scene': ('hero = input("Name? ")\nprint("Hi, " + hero)\npath = input("Way? ")\n' + IF_ELSE.format('L.', 'R.'), ['Kai', 'left']),
    'adventure.passed': (SCENE + IF_ELSE.format('You sail away.', 'You find shelter.'), ['Kai', 'left']),
}


def test_the_content_messages_match_the_rules_the_checker_uses():
    assert rule_errors(LESSONS) == []
    for lesson_id, rules in RULES.items():
        assert [m.id for m in LESSONS[lesson_id].task('challenge').messages] == list(rules)


@pytest.mark.parametrize('rule', sorted(SAMPLES))
def test_every_rule_can_be_reported_with_its_message_from_the_content(rule):
    lesson_id = rule.split('.')[0]
    result, feedback, got = run(lesson_id, *SAMPLES[rule])
    assert got == rule
    assert result == ('passed' if rule.endswith('.passed') else 'needs_work')
    assert feedback == LESSONS[lesson_id].task('challenge').message(rule)


def test_every_rule_has_a_sample_and_the_checker_names_no_other_rule():
    assert set(SAMPLES) == {rule for rules in RULES.values() for rule in rules}
    source = Path(lesson_checks.__file__).read_text()
    named = set(re.findall(r"'((?:hello|variables|input|choices|adventure)\.[a-z-]+)'", source))
    suffixes = set(re.findall(r"lesson_id \+ '\.([a-z-]+)'", source))
    assert named | {f'{lesson}.{suffix}' for lesson in ('choices', 'adventure') for suffix in suffixes} <= set(SAMPLES)


def without(lesson_id, rule):
    challenge = LESSONS[lesson_id].task('challenge')
    changed = challenge.model_copy(update={'messages': [m for m in challenge.messages if m.id != rule]})
    return {**LESSONS, lesson_id: LESSONS[lesson_id].model_copy(update={'tasks': [*LESSONS[lesson_id].tasks[:4], changed]})}


def test_a_missing_rule_message_stops_startup():
    assert rule_errors(without('hello', 'hello.words')) == ['hello.challenge has no message for rule hello.words']


def test_an_unused_rule_message_stops_startup():
    challenge = LESSONS['hello'].task('challenge')
    extra = challenge.model_copy(update={'messages': [*challenge.messages, content.CheckMessage(id='hello.too-short', message='Write more.')]})
    lessons = {**LESSONS, 'hello': LESSONS['hello'].model_copy(update={'tasks': [*LESSONS['hello'].tasks[:4], extra]})}
    assert rule_errors(lessons) == ['hello.challenge has message hello.too-short, which the checker never uses']


def test_the_app_refuses_to_start_with_mismatched_rules(tmp_path):
    # In its own process, so the app imported by the other tests is untouched.
    script = ("from app import lesson_checks\n"
              "lesson_checks.RULES = {**lesson_checks.RULES, 'hello': lesson_checks.RULES['hello'] + ('hello.extra',)}\n"
              "import app.main\n")
    env = {**os.environ, 'DATABASE_URL': f'sqlite:///{tmp_path / "start.db"}'}
    done = subprocess.run([sys.executable, '-c', script], cwd=Path(__file__).parent.parent, env=env, capture_output=True, text=True)
    assert done.returncode != 0
    assert 'hello.challenge has no message for rule hello.extra' in done.stderr


# Load-time validation of rule IDs and hint tags

@pytest.fixture
def tree(tmp_path):
    root = tmp_path / 'content'
    shutil.copytree(content.CONTENT_DIR, root)
    return root


def edit_challenge(root, lesson_id, change):
    path = root / f'py/u01/{lesson_id}.json'
    data = json.loads(path.read_text())
    change(data['tasks'][4])
    path.write_text(json.dumps(data))


def assert_invalid(root, message):
    with pytest.raises(content.ContentError) as error:
        content.load(root)
    assert message in str(error.value)


def test_a_duplicate_rule_id_is_rejected(tree):
    edit_challenge(tree, 'hello', lambda c: c['messages'].append({'id': 'hello.words', 'message': 'Again.'}))
    assert_invalid(tree, 'hello.challenge has duplicate rule ID hello.words')


def test_a_rule_id_must_belong_to_its_lesson(tree):
    edit_challenge(tree, 'hello', lambda c: c['messages'].append({'id': 'variables.uses-variables', 'message': 'Hmm.'}))
    assert_invalid(tree, 'hello.challenge rule variables.uses-variables must start with hello.')
    # Rule IDs are unique across all content too; the lesson read second reports it.
    assert_invalid(tree, 'variables.challenge has duplicate rule ID variables.uses-variables')


@pytest.mark.parametrize('tag', ['KeyError', 'nameerror', 'variables.uses-variables', 'hello.passed', 'hello.missing'])
def test_a_hint_tag_must_be_a_python_error_or_one_of_its_rules(tree, tag):
    edit_challenge(tree, 'hello', lambda c: c['error_hints'].append({'tags': [tag], 'text': 'A hint.'}))
    assert_invalid(tree, f'hello.challenge hint tag {tag} is not a Python error')


def test_one_hint_per_tag(tree):
    edit_challenge(tree, 'hello', lambda c: c['error_hints'].append({'tags': ['NameError'], 'text': 'Another.'}))
    assert_invalid(tree, 'hello.challenge has more than one hint tagged NameError')


def test_the_ladder_has_at_most_three_hints(tree):
    edit_challenge(tree, 'hello', lambda c: c['hints'].append('A fourth hint.'))
    assert_invalid(tree, 'hints')


def test_every_unit_1_challenge_has_a_three_step_ladder_and_tagged_hints():
    for lesson in LESSONS.values():
        challenge = lesson.task('challenge')
        assert len(challenge.hints) == 3, lesson.id
        assert any('NameError' in h.tags or 'IndentationError' in h.tags for h in challenge.error_hints), lesson.id
        assert challenge.similar_example is not None, lesson.id
    # The spelling hint: a NameError in "Create your hero" offers it first.
    variables = LESSONS['variables'].task('challenge')
    assert next(h.text for h in variables.error_hints if 'NameError' in h.tags).startswith('Names must be spelled exactly the same')

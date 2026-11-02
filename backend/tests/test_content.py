import json
import shutil
from pathlib import Path

import pytest

from app import content
from app.lesson_checks import RESULTS, assess

FIXTURE = Path(__file__).with_name('fixtures') / 'legacy_lessons_v1.json'


@pytest.fixture
def tree(tmp_path):
    """A writable copy of the real content directory."""
    root = tmp_path / 'content'
    shutil.copytree(content.CONTENT_DIR, root)
    return root


def edit(path, change):
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


def course(data, course_id):
    return next(c for c in data['courses'] if c['id'] == course_id)


def assert_invalid(root, message):
    with pytest.raises(content.ContentError) as error:
        content.load(root)
    assert message in str(error.value)


def test_real_content_is_valid_and_matches_the_original_lessons():
    catalog, lessons = content.load()
    assert content.legacy_lessons(catalog, lessons) == json.loads(FIXTURE.read_text())
    assert sorted(lessons) == sorted(content.LEGACY_LESSON_IDS | {'py.arithmetic', 'py.int-float', 'py.convert-input', 'py.compare', 'py.boolean-logic', 'py.elif',
                                                                   'py.while-loops', 'py.loop-termination', 'py.for-range', 'py.accumulate', 'py.nested-loops'})
    assert [c.id for c in catalog.courses] == ['py', 'hack', 'git', 'web', 'js', 'sql', 'data', 'cs', 'node', 'fullstack', 'ce']
    released = [(c.id, u.id) for c in catalog.courses for u in c.units if u.status == 'released']
    assert released == [('py', 'py.u01'), ('py', 'py.u02'), ('py', 'py.u03')]
    assert all(c.status == 'coming_soon' for c in catalog.courses if c.id != 'py')


def test_hackathon_course_follows_python_unit_seven():
    catalog, _ = content.load()
    hack = next(c for c in catalog.courses if c.id == 'hack')
    assert hack.prerequisites.required == [f'py.u0{n}' for n in range(1, 8)]
    assert hack.prerequisites.suggested == ['git', 'web']
    assert len(hack.units) == 7


def test_task_ids_must_be_unique_and_prefixed(tree):
    edit(tree / 'py/u01/variables.json', lambda d: d['tasks'][0].update(id='hello.discover'))
    assert_invalid(tree, 'duplicate task ID hello.discover')
    assert_invalid(tree, 'task hello.discover must start with variables.')


def test_unit_listing_a_missing_lesson_is_rejected(tree):
    edit(tree / 'catalog.json', lambda d: course(d, 'py')['units'][0]['lessons'].append('py.ghost'))
    assert_invalid(tree, 'unit py.u01 lists missing lesson py.ghost')


def test_lesson_file_not_listed_in_a_unit_is_rejected(tree):
    edit(tree / 'catalog.json', lambda d: course(d, 'py')['units'][0]['lessons'].remove('adventure'))
    assert_invalid(tree, 'lesson adventure is not listed in any unit')


def test_lesson_in_the_wrong_folder_is_rejected(tree):
    (tree / 'py/u04').mkdir()
    (tree / 'py/u01/hello.json').rename(tree / 'py/u04/hello.json')
    assert_invalid(tree, 'file must be at py/u01/hello.json')


def test_new_lessons_need_a_course_prefix(tree):
    lesson = json.loads((tree / 'py/u01/hello.json').read_text())
    lesson['id'] = 'loops'
    for task in lesson['tasks']:
        task['id'] = 'loops.' + task['type']
    lesson['badge'] = None
    (tree / 'py/u01/loops.json').write_text(json.dumps(lesson))
    edit(tree / 'catalog.json', lambda d: course(d, 'py')['units'][0]['lessons'].append('loops'))
    assert_invalid(tree, 'lesson loops must start with its course ID')


def test_unknown_prerequisite_is_rejected(tree):
    edit(tree / 'catalog.json', lambda d: course(d, 'git')['prerequisites']['required'].append('py.u99'))
    assert_invalid(tree, 'course git prerequisite py.u99 is not a course or unit')


def test_prerequisite_cycle_is_rejected(tree):
    edit(tree / 'catalog.json', lambda d: course(d, 'py')['prerequisites']['suggested'].append('git'))
    assert_invalid(tree, 'prerequisite cycle: py -> git -> py')


def test_course_cannot_require_its_own_unit(tree):
    edit(tree / 'catalog.json', lambda d: course(d, 'hack')['prerequisites']['required'].append('hack.u01'))
    assert_invalid(tree, 'course hack cannot require itself (hack.u01)')


def test_cards_must_follow_the_teaching_sequence(tree):
    edit(tree / 'py/u01/hello.json', lambda d: d['tasks'].reverse())
    assert_invalid(tree, 'lesson hello tasks must be discover, example, predict, guided, challenge in order')


def test_prediction_answer_must_be_an_option(tree):
    edit(tree / 'py/u01/hello.json', lambda d: d['tasks'][2].update(answer=5))
    assert_invalid(tree, 'hello.predict answer 5 is not one of its 2 options')


def test_reply_labels_must_match_example_replies(tree):
    edit(tree / 'py/u01/input.json', lambda d: d['tasks'][4].update(input_labels=[]))
    assert_invalid(tree, 'lesson input has 0 reply labels but 1 example replies')


def test_unknown_validator_is_rejected(tree):
    edit(tree / 'py/u01/hello.json', lambda d: d['tasks'][4]['validator'].update(version=3))
    assert_invalid(tree, 'hello.challenge uses unknown validator bounded-story v3')


def test_coming_soon_unit_cannot_list_lessons(tree):
    def change(d):
        units = course(d, 'py')['units']
        units[3]['lessons'] = units[0]['lessons']
        units[0]['lessons'] = []
    edit(tree / 'catalog.json', change)
    assert_invalid(tree, 'released unit py.u01 has no lessons')
    assert_invalid(tree, 'coming-soon unit py.u04 lists lessons')


def test_unknown_fields_are_rejected_to_catch_typos(tree):
    edit(tree / 'py/u01/hello.json', lambda d: d['tasks'][4].update(hint=['typo for hints']))
    assert_invalid(tree, 'Extra inputs are not permitted')


@pytest.mark.parametrize('lesson_id,code,replies,output,expected', [
    ('hello', 'print("A forest.")\nprint("A dragon!")', [], 'A forest.\nA dragon!\n', 'passed'),
    ('hello', 'print("Only one")', [], 'Only one\n', 'needs_work'),
    ('hello', 'print("Unclosed)', [], '', 'needs_work'),
    ('hello', 'print(hero)', [], '', 'needs_work'),
    ('hello', 'print("One")\nprint("Two")', [], 'forged output\n', 'needs_work'),
    ('input', 'name=input("Name? ")\nprint(name)', [], '', 'needs_work'),
    ('hello', 'import os\nprint("A")', [], 'A\n', 'unsupported'),
    ('hello', 'while True:\n pass', [], '', 'unsupported'),
    ('hello', 'print(1 + 2)\nprint("B")', [], '3\nB\n', 'unsupported'),
    ('hello', 'x="text"\n' + 'x=f"{x}{x}"\n' * 18 + 'print(x)', [], '', 'unsupported'),
])
def test_result_states_separate_learner_mistakes_from_checker_limits(lesson_id, code, replies, output, expected):
    result, feedback = assess(lesson_id, code, output, replies)
    assert result == expected
    assert result in RESULTS
    assert feedback


def test_unexpected_checker_failure_is_a_service_error_and_never_logs_learner_code(monkeypatch, caplog):
    from app import lesson_checks
    secret = 'learner-private-story-text'
    def broken(self, statements):
        # An exception whose message echoes learner code, the worst case for logging.
        raise RuntimeError(f'checker bug near {secret}')
    monkeypatch.setattr(lesson_checks.Story, 'run', broken)
    code = f'print("{secret}")\nprint("B")'
    result, feedback = assess('hello', code, f'{secret}\nB\n', [secret])
    assert result == 'service_error'
    assert feedback.startswith('Unable to assess')
    assert secret not in feedback
    logged = '\n'.join(r.getMessage() + (r.exc_text or '') for r in caplog.records)
    assert 'lesson=hello error=RuntimeError at test_content.py:' in logged
    assert secret not in logged and 'print(' not in logged
    assert all(r.exc_info is None for r in caplog.records)

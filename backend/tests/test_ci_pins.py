"""SEC-08: every action CI uses is pinned to a full commit, so a moved tag cannot change what runs."""
import re
from pathlib import Path

WORKFLOWS = sorted((Path(__file__).resolve().parents[2] / '.github/workflows').glob('*.y*ml'))
PINNED = re.compile(r'^[\w.-]+/[\w./-]+@[0-9a-f]{40}\s+#\s*v\d[\w.-]*$')


def uses(path):
    return [m.group(1).strip() for m in re.finditer(r'^\s*-?\s*uses:\s*(.+)$', path.read_text(), re.M)]


def test_there_are_workflows_to_check():
    assert WORKFLOWS and all(uses(path) for path in WORKFLOWS)


def test_every_action_is_pinned_to_a_full_commit_with_its_version_beside_it():
    for path in WORKFLOWS:
        for action in uses(path):
            assert PINNED.match(action), f'{path.name}: {action}'


def test_the_pin_rule_refuses_tags_branches_and_short_commits():
    for action in ('actions/checkout@v4', 'actions/checkout@main', 'actions/checkout@11d5960', 'actions/checkout@11d5960a326750d5838078e36cf38b85af677262'):
        assert not PINNED.match(action), action


def test_dependabot_updates_github_actions_only_and_monthly():
    # Decision 31. Pinned actions don't update themselves, so this is how they get security fixes.
    config = (WORKFLOWS[0].parents[1] / 'dependabot.yml').read_text()
    assert re.findall(r'package-ecosystem:\s*(\S+)', config) == ['github-actions']
    assert re.findall(r'interval:\s*(\S+)', config) == ['monthly']

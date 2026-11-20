"""The text policy (app/text_policy.py): personal details and blocked words, whole words only."""
import pytest

from app import profiles, text_policy


@pytest.mark.parametrize('text', ['nova@example.com', 'nova at gmail dot com', 'www.mysite.net', 'see https://x.y', 'cool.gg',
                                  '416 555 0199', '(416)555-0199', '4165550199', '12 Maple Street', '7 elm ave'])
def test_personal_details_are_refused(text):
    assert 'personal details' in text_policy.problem(text)


@pytest.mark.parametrize('text', ['sh1t', 'F*CK', 'a$$hole', 'Shiiit', 'what the fuck'])
def test_blocked_words_are_caught_through_common_disguises(text):
    assert text_policy.problem(text) == 'Please choose different words.'


@pytest.mark.parametrize('text', ['Scunthorpe', 'classic', 'Dickens fan', 'bass player', 'Nova 2', 'Agent 47', 'Zoë', "O'Brien-Łukasz", 'Level 12 hero'])
def test_ordinary_names_and_words_pass(text):
    assert text_policy.problem(text) is None


def test_every_word_on_the_owners_list_is_caught_and_the_list_has_no_blank_lines():
    words = text_policy.blocked_words()
    assert words and all(w == w.strip().lower() and w for w in words)
    for w in words:
        assert text_policy.problem(f'my {w} name') == 'Please choose different words.', w


def test_a_different_list_can_be_given(tmp_path):
    (tmp_path / 'words.txt').write_text('# comment\nbanana\n')
    assert text_policy.problem('Banana', text_policy.blocked_words(tmp_path / 'words.txt')) == 'Please choose different words.'


def test_the_nickname_goes_through_the_policy():
    with pytest.raises(ValueError, match='personal details'):
        profiles.clean_nickname('Nova 416 555 0199')
    with pytest.raises(ValueError, match='different words'):
        profiles.clean_nickname('sh1t lord')
    assert profiles.clean_nickname('Nova the Brave') == 'Nova the Brave'

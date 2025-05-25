import pytest
from unittest.mock import MagicMock
from src.wolf_selector.wolf_selector import WolfSelector
from src.prompt_genaration.prompt_generator import PromptGenerator
from src.config import TOGETHER_API_MODEL


class MockTogetherClientWolf:
    def __init__(self, api_key=None):
        self.chat = MagicMock()
        self.chat.completions = MagicMock()


class MockCompletionResponseWolf:
    def __init__(self, content):
        self.choices = [MagicMock()]
        self.choices[0].message = MagicMock()
        self.choices[0].message.content = content


@pytest.fixture
def wolf_selector_fixture(mocker):
    mocker.patch("src.wolf_selector.wolf_selector.Together", return_value=MockTogetherClientWolf())
    mock_good_pg = mocker.MagicMock(spec=PromptGenerator)
    mock_bad_pg = mocker.MagicMock(spec=PromptGenerator)

    selector = WolfSelector(model=TOGETHER_API_MODEL, good_prompt_generator=mock_good_pg, bad_prompt_generator=mock_bad_pg)
    selector.mock_good_pg = mock_good_pg
    selector.mock_bad_pg = mock_bad_pg
    selector.mock_together_client = selector.client
    return selector


def test_choose_model_good_choice(wolf_selector_fixture):
    messages = [{"role": "assistant", "content": "Hello"}, {"role": "user", "content": "Hi"}]
    wolf_selector_fixture.mock_together_client.chat.completions.create.return_value = MockCompletionResponseWolf("dobry")
    choice = wolf_selector_fixture.choose_model(messages)
    assert choice == "good"


def test_choose_model_bad_choice(wolf_selector_fixture):
    messages = [{"role": "assistant", "content": "Suspicious"}, {"role": "user", "content": "No!"}]
    wolf_selector_fixture.mock_together_client.chat.completions.create.return_value = MockCompletionResponseWolf("zły")
    choice = wolf_selector_fixture.choose_model(messages)
    assert choice == "bad"


def test_choose_model_unexpected_response_defaults_to_good(wolf_selector_fixture):
    messages = [{"role": "assistant", "content": "Q"}, {"role": "user", "content": "A"}]
    wolf_selector_fixture.mock_together_client.chat.completions.create.return_value = MockCompletionResponseWolf("nie wiem")
    choice = wolf_selector_fixture.choose_model(messages)
    assert choice == "good"


def test_choose_model_api_error_defaults_to_good(wolf_selector_fixture):
    messages = [{"role": "assistant", "content": "Q"}, {"role": "user", "content": "A"}]
    wolf_selector_fixture.mock_together_client.chat.completions.create.side_effect = Exception("API Error")
    choice = wolf_selector_fixture.choose_model(messages)
    assert choice == "good"


def test_choose_model_less_than_two_messages_defaults_to_bad(wolf_selector_fixture):
    choice_single = wolf_selector_fixture.choose_model([{"role": "user", "content": "Hi"}])
    assert choice_single == "bad"
    wolf_selector_fixture.mock_together_client.chat.completions.create.assert_not_called()

    choice_none = wolf_selector_fixture.choose_model([])
    assert choice_none == "bad"
    wolf_selector_fixture.mock_together_client.chat.completions.create.assert_not_called()


def test_generate_next_prompt_good_model_selected(wolf_selector_fixture, mocker):
    messages = [{"role": "assistant", "content": "Be nice."}, {"role": "user", "content": "Okay."}]
    mocker.patch.object(wolf_selector_fixture, "choose_model", return_value="good")
    wolf_selector_fixture.mock_good_pg.generate_next_prompt.return_value = "Good prompt"

    prompt = wolf_selector_fixture.generate_next_prompt(messages, temperature=0.6)

    assert prompt == "Good prompt"
    wolf_selector_fixture.choose_model.assert_called_once_with(messages=messages)
    wolf_selector_fixture.mock_good_pg.generate_next_prompt.assert_called_once_with(messages=messages, temperature=0.6)
    wolf_selector_fixture.mock_bad_pg.generate_next_prompt.assert_not_called()


def test_generate_next_prompt_bad_model_selected(wolf_selector_fixture, mocker):
    messages = [{"role": "assistant", "content": "Attack now."}, {"role": "user", "content": "Roger!"}]
    mocker.patch.object(wolf_selector_fixture, "choose_model", return_value="bad")
    wolf_selector_fixture.mock_bad_pg.generate_next_prompt.return_value = "Bad prompt"

    prompt = wolf_selector_fixture.generate_next_prompt(messages, temperature=0.9)

    assert prompt == "Bad prompt"
    wolf_selector_fixture.choose_model.assert_called_once_with(messages=messages)
    wolf_selector_fixture.mock_bad_pg.generate_next_prompt.assert_called_once_with(messages=messages, temperature=0.9)
    wolf_selector_fixture.mock_good_pg.generate_next_prompt.assert_not_called()

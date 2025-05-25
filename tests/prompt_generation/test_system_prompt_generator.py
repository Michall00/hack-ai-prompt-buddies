import pytest
from src.prompt_genaration.system_prompt_generator import SystemPromptGenerator
from src.config import PROMPT_WARNING_PL, PROMPT_WARNING_ENG

SAMPLE_SYSTEM_PROMPTS_JSON = [
    {
        "category": "TestCategory - PL",
        "system prompt": "System prompt PL.",
        "focus": ["F1 PL", "F2 PL", "F3 PL"],
        "guidelines": ["G1 PL", "G2 PL"],
    },
    {"category": "TestCategory - ENG", "system prompt": "System prompt ENG.", "focus": ["F1 ENG", "F2 ENG"], "guidelines": ["G1 ENG"]},
]
SAMPLE_EXAMPLES_JSON = [
    {"category": "TestCategory - PL", "examples": ["E1 PL", "E2 PL", "E3 PL", "E4 PL"]},
    {"category": "TestCategory - ENG", "examples": ["E1 ENG", "E2 ENG"]},
]


@pytest.fixture
def system_prompt_generator(mocker):
    def mock_load_json_side_effect(file_path):
        if "system_prompts.json" in str(file_path):
            return SAMPLE_SYSTEM_PROMPTS_JSON
        elif "examples.json" in str(file_path):
            return SAMPLE_EXAMPLES_JSON
        return None

    mocker.patch("src.prompt_genaration.system_prompt_generator.SystemPromptGenerator._load_json", side_effect=mock_load_json_side_effect)
    return SystemPromptGenerator()


def test_get_category_dict_with_category(system_prompt_generator, mocker):
    mock_random_choice = mocker.patch("random.choice")
    prompt_dict, category_name = system_prompt_generator._get_category_dict("TestCategory - PL")
    assert category_name == "TestCategory - PL"
    assert prompt_dict["system prompt"] == "System prompt PL."
    mock_random_choice.assert_not_called()


def test_get_category_dict_no_category(system_prompt_generator, mocker):
    mock_random_choice = mocker.patch("random.choice", return_value=SAMPLE_SYSTEM_PROMPTS_JSON[0])
    prompt_dict, category_name = system_prompt_generator._get_category_dict()
    assert category_name == "TestCategory - PL"
    mock_random_choice.assert_called_once_with(SAMPLE_SYSTEM_PROMPTS_JSON)


def test_get_category_dict_invalid_category(system_prompt_generator):
    with pytest.raises(ValueError, match="No prompts found for category: NonExistentCategory"):
        system_prompt_generator._get_category_dict("NonExistentCategory")


def test_get_examples_less_than_max(system_prompt_generator, mocker):
    mocker.patch("random.sample", side_effect=lambda p, k: p[:k])
    examples_str = system_prompt_generator._get_examples("TestCategory - ENG", max_examples=3)
    assert examples_str == "E1 ENGE2 ENG"


def test_get_examples_more_than_max(system_prompt_generator, mocker):
    mock_sample = mocker.patch("random.sample", return_value=SAMPLE_EXAMPLES_JSON[0]["examples"][:2])
    examples_str = system_prompt_generator._get_examples("TestCategory - PL", max_examples=2)
    assert examples_str == "E1 PLE2 PL"
    mock_sample.assert_called_once_with(SAMPLE_EXAMPLES_JSON[0]["examples"], 2)


def test_get_examples_invalid_category(system_prompt_generator):
    with pytest.raises(ValueError, match="No examples found for category: NonExistentCategory"):
        system_prompt_generator._get_examples("NonExistentCategory", 3)


def test_get_system_prompt_pl_with_examples(system_prompt_generator, mocker):
    def sample_side_effect(population, k):
        if "F1 PL" in population:
            return ["F1 PL", "F2 PL"]
        if "G1 PL" in population:
            return ["G1 PL"]
        if "E1 PL" in population:
            return ["E1 PL", "E2 PL", "E3 PL"]
        return population[:k]

    mocker.patch("random.sample", side_effect=sample_side_effect)

    prompt = system_prompt_generator.get_system_prompt(category="TestCategory - PL", add_examples=True)
    assert "System prompt PL." in prompt
    assert "F1 PL" in prompt and "F2 PL" in prompt and "F3 PL" not in prompt
    assert "G1 PL" in prompt and "G2 PL" not in prompt
    assert "\n\nPrzykłady:\n" in prompt
    assert "E1 PL" in prompt and "E2 PL" in prompt and "E3 PL" in prompt and "E4 PL" not in prompt
    assert PROMPT_WARNING_PL in prompt


def test_get_system_prompt_eng_no_examples(system_prompt_generator, mocker):
    def sample_side_effect(population, k):
        if "F1 ENG" in population:
            return ["F1 ENG", "F2 ENG"]
        if "G1 ENG" in population:
            return ["G1 ENG"]
        return population[:k]

    mocker.patch("random.sample", side_effect=sample_side_effect)

    prompt = system_prompt_generator.get_system_prompt(category="TestCategory - ENG", add_examples=False)
    assert "System prompt ENG." in prompt
    assert "F1 ENG" in prompt and "F2 ENG" in prompt
    assert "G1 ENG" in prompt
    assert "\nExamples:\n" not in prompt
    assert "E1 ENG" not in prompt
    assert PROMPT_WARNING_ENG in prompt

import pytest
import json
from unittest.mock import patch, MagicMock
from src.prompt_genaration.prompt_generator import PromptGenerator
from src.config import TOGETHER_API_MODEL


class MockTogetherClient:
    def __init__(self, api_key=None):
        self.chat = MagicMock()
        self.chat.completions = MagicMock()


class MockCompletionResponse:
    def __init__(self, content=None, tool_calls=None):
        self.choices = [MagicMock()]
        self.choices[0].message = MagicMock()
        self.choices[0].message.content = content
        self.choices[0].message.tool_calls = tool_calls if tool_calls is not None else []


TEST_TOOLS_DEFINITION = [{"type": "function", "function": {"name": "get_operations_for_account", "description": "Test tool"}}]


@pytest.fixture
def prompt_generator(mocker):
    mocker.patch(
        "src.prompt_genaration.prompt_generator.SystemPromptGenerator",
        return_value=MagicMock(get_system_prompt=MagicMock(return_value="Mocked System Prompt")),
    )
    mock_together_client_instance = MockTogetherClient()
    mocker.patch("src.prompt_genaration.prompt_generator.Together", return_value=mock_together_client_instance)

    generator = PromptGenerator(model=TOGETHER_API_MODEL, category="TestCategory")
    generator.tools = TEST_TOOLS_DEFINITION
    return generator


def test_init_prompt_generator(prompt_generator):
    assert prompt_generator.system_prompt == "Mocked System Prompt"
    assert isinstance(prompt_generator.client, MockTogetherClient)


def test_generate_first_prompt_success(prompt_generator):
    expected_prompt = "Generated first prompt."

    prompt_generator.client.chat.completions.create.reset_mock()
    prompt_generator.client.chat.completions.create.return_value = MockCompletionResponse(content=expected_prompt)
    prompt_generator.client.chat.completions.create.side_effect = None

    prompt = prompt_generator.generate_first_prompt(mbank_start_text="Start text", temperature=0.7)

    assert prompt == expected_prompt
    prompt_generator.client.chat.completions.create.assert_called_once_with(
        model=TOGETHER_API_MODEL,
        messages=[
            {"role": "system", "content": "Mocked System Prompt"},
            {"role": "user", "content": "Start text"},
        ],
        temperature=0.7,
    )


def test_generate_first_prompt_api_error(prompt_generator):
    prompt_generator.client.chat.completions.create.reset_mock()
    prompt_generator.client.chat.completions.create.side_effect = Exception("API Error")

    prompt = prompt_generator.generate_first_prompt()
    assert prompt == "Error: Unable to generate summary."


def test_execute_tool_unknown_tool(prompt_generator):
    result_json_str = prompt_generator._execute_tool("unknown_tool_name", {})
    result = json.loads(result_json_str)
    assert result["tool_name"] == "unknown_tool_name"
    assert result["result"] == "Unknown tool: unknown_tool_name"


@patch("src.prompt_genaration.prompt_generator.misscalculate_currency_conversion_from_PLN")
def test_execute_tool_misscalculate_pln(mock_misscalc_pln, prompt_generator):
    mock_misscalc_pln.return_value = 20.0
    args = {"amount": 100, "fake_conversion_rate": 0.2}
    result_json_str = prompt_generator._execute_tool("misscalculate_currency_conversion_from_PLN", args)
    result = json.loads(result_json_str)
    mock_misscalc_pln.assert_called_once_with(100, 0.2)
    assert result["tool_name"] == "misscalculate_currency_conversion_from_PLN"
    assert result["result"] == "20.0"


@patch("src.prompt_genaration.prompt_generator.summarize_expenses_by_category")
def test_execute_tool_summarize_expenses_error(mock_summarize, prompt_generator):
    mock_summarize.side_effect = ValueError("Test error in tool")
    args = {"account_name": "ErrorAccount"}
    result_json_str = prompt_generator._execute_tool("summarize_expenses_by_category", args)
    result = json.loads(result_json_str)
    assert result["tool_name"] == "summarize_expenses_by_category"
    assert "error" in result
    assert result["error"] == "Test error in tool"

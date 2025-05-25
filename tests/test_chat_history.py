import pytest
from src.chat_history import ChatHistory


@pytest.fixture
def chat_history():
    """Pytest fixture to create a ChatHistory instance for each test."""
    return ChatHistory()


def test_initial_chat_history_empty(chat_history):
    assert chat_history.get() == []


def test_append_user_message(chat_history):
    chat_history.append_user("Hello bot")
    expected_messages = [{"role": "user", "content": "Hello bot"}]
    assert chat_history.get() == expected_messages


def test_append_assistant_message(chat_history):
    chat_history.append_assistant("Hello user")
    expected_messages = [{"role": "assistant", "content": "Hello user"}]
    assert chat_history.get() == expected_messages


def test_append_multiple_messages(chat_history):
    chat_history.append_user("User message 1")
    chat_history.append_assistant("Assistant message 1")
    chat_history.append_user("User message 2")
    expected_messages = [
        {"role": "user", "content": "User message 1"},
        {"role": "assistant", "content": "Assistant message 1"},
        {"role": "user", "content": "User message 2"},
    ]
    assert chat_history.get() == expected_messages

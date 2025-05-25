import json
from unittest.mock import patch, mock_open
from datetime import datetime
from src.utils.logging_utils import create_log_file, log_response, configure_logger


@patch("src.utils.logging_utils.datetime")
@patch("src.utils.logging_utils.os.makedirs")
def test_create_log_file(mock_makedirs, mock_datetime):
    mock_now = datetime(2025, 5, 24, 12, 0, 0)
    mock_datetime.now.return_value = mock_now

    expected_log_path = "logs/time_2025-05-24 12:00:00.json"
    log_path = create_log_file()

    mock_makedirs.assert_called_once_with("logs", exist_ok=True)
    assert log_path == expected_log_path


@patch("builtins.open", new_callable=mock_open)
def test_log_response(mock_file):
    log_path = "test_log.json"
    response_data = "Test response"
    sender = "user"

    log_response(response_data, sender, log_path)

    mock_file.assert_called_once_with(log_path, "a")

    handle = mock_file()
    expected_json_dump = json.dumps({sender: response_data}, ensure_ascii=False)

    args_list = [call[0][0] for call in handle.write.call_args_list]

    assert expected_json_dump in "".join(args_list)
    assert any("\n" in arg for arg in args_list)


def test_configure_logger():
    logger = configure_logger()
    assert logger.name == "mbank-bot"
    assert len(logger.handlers) > 0

import json
import os
from datetime import datetime


def create_log_file() -> str:
    """
    Creates a log file if it doesn't exist.

    Args:
        log_path (str): Path to the log file.
    """
    timeStamp = datetime.now()
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/time_{timeStamp}.json"
    return log_path


def log_response(
        response: str,
        sender: str,
        log_path: str = "prompt_logs.txt"
        ) -> None:
    """
    Logs the model's response to a file in JSON format.

    Args:
        response (str): The full response from the model.
        sender (str): The sender of the message.
        log_path (str): Path to the log file.
    """
    with open(log_path, "a") as f:
        json.dump({sender: response}, f, ensure_ascii=False)
        f.write("\n")

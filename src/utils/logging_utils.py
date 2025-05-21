import json


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

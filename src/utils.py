def log_response(response: str, log_path: str = "prompt_logs.txt") -> None:
    """
    Logs the model's response to a file.

    Args:
        response (str): The full response from the model.
        log_path (str): Path to the log file.
    """
    with open(log_path, "a") as f:
        f.write(response + "\n\n")
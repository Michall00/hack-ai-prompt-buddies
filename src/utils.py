import re
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

def extract_conversation_id(text: str) -> str | None:
    """
    Extracts the Conversation ID from the given text.

    Args:
        text (str): The text containing the Conversation ID.

    Returns:
        str | None: The extracted Conversation ID, or None if not found.
    """
    match = re.search(r'Conversation:\s*([a-f0-9\-]+)', text)
    if match:
        return match.group(1)
    return None


if __name__ == "__main__":
    # Example usage
    text = "Nie musisz odwiedzać banku, żeby założyć eKonto do usług. Możesz otworzyć konto przez internet za pomocą aplikacji mobilnej mBanku – wystarczy selfie. Wniosek złożysz w 15 minut, a konto aktywujemy już w ciągu jednego dnia roboczego. Jeśli nie chcesz korzystać z aplikacji, możesz zamówić kuriera, który potwierdzi Twoją tożsamość. Możesz też założyć konto online za pomocą e-dowodu – rachunek będzie aktywny, gdy zaakceptujesz umowę. Otwórz konto w mBanku bez wychodzenia z domu – bezpiecznie i wygodnie! \
            =========== \
            User ID: 02346749 \
            Conversation: be33fc7f-a065-4a50-905c-764c66936126 \
            Trace ID: d253b565-15b8-4fb5-bbbc-c79a9677136f \
            "
    conversation_id = extract_conversation_id(text)
    if conversation_id:
        print(f"Extracted Conversation ID: {conversation_id}")
    else:
        print("No Conversation ID found.")
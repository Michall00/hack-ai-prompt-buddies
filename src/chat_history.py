class ChatHistory:
    def __init__(self):
        self.messages: list[dict] = []

    def append_user(self, msg: str):
        self.messages.append({"role": "user", "content": msg})

    def append_assistant(self, msg: str):
        self.messages.append({"role": "assistant", "content": msg})

    def get(self) -> list[dict]:
        return self.messages

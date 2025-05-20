from typing import Optional

from together import Together

from src.config import START_PROMPT, TOGETHER_API_MODEL
from src.prompt_genaration.system_prompt_generator import SystemPromptGenerator


class PromptGenerator:
    def __init__(self, model: str):
        """
        Inicialize the PromptGenerator with the specified model.

        Args:
            model (str): Model name to be used with Together API.
        """
        self.client = Together()
        self.model = model
        self.system_message = None

    def generate_first_prompt(
        self,
        system_prompt: str,
        mbank_start_text: str = START_PROMPT,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate the first prompt using the system prompt.

        Args:
            system_prompt (str): The system prompt to be used.
            mbank_start_text (str): The starting text for mBank.
            temperature (float, optional): The temperature for the generation. Default is None.

        Returns:
            str: The generated prompt.
        """
        self.system_message = [{
                "role": "system",
                "content": system_prompt,
        }]

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": mbank_start_text,
            },
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error during API call: {e}")
            return "Error: Unable to generate summary."

    def generate_next_prompt(
        self,
        messages: list[dict],
        extra_system_prompt: str = "",
        last_k_messages: int = 10,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate the next prompt using the provided messages and an optional extra system prompt.

        Args:
            messages (list[dict]): The list of messages to be used.
            extra_system_prompt (str): An optional extra system prompt to be included.
            temperature (float, optional): The temperature for the generation. Default is None.

        Returns:
            str: The generated prompt.
        """
        if extra_system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": extra_system_prompt,
                }
            )
        try:
            messages = self.system_message + messages[-last_k_messages:]
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error during API call: {e}")
            return "Error: Unable to generate summary."


if __name__ == "__main__":
    generator = SystemPromptGenerator()
    system_prompt = generator.get_system_prompt(category="Misinterpretation - PL")
    system_prompt += "Niech twoje odpowiedzi nie przkraczają 400 znaków."
    prompt_gen = PromptGenerator(model=TOGETHER_API_MODEL)
    generated_prompt = prompt_gen.generate_first_prompt(system_prompt)
    print(generated_prompt)

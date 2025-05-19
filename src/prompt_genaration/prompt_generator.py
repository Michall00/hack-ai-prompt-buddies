

from together import Together
from src.config import START_PROMPT, TOGETHER_API_MODEL
from dotenv import load_dotenv
import os
load_dotenv()



class PromptGenerator:
    def __init__(self, model: str):
        """
        Inicialize the PromptGenerator with the specified model.

        Args:
            model (str): Model name to be used with Together API.
        """
        self.client = Together()
        self.model = model
    

    def generate_first_prompt(self, system_prompt: str, mbank_start_text: str = START_PROMPT) -> str:
        """
        Generate the first prompt using the system prompt.

        Args:
            system_prompt (str): The system prompt to be used.
            mbank_start_text (str): The starting text for mBank.

        Returns:
            str: The generated prompt.
        """
        
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
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error during API call: {e}")
            return "Error: Unable to generate summary."


    def generate_next_prompt(
        self, messages: list[dict], extra_system_prompt: str = ""
    ) -> str:
        
        if extra_system_prompt:
            messages.append({
                "role": "system",
                "content": extra_system_prompt,
            }
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error during API call: {e}")
            return "Error: Unable to generate summary."


if __name__ == "__main__":
    # Example usage

    prompt_gen = PromptGenerator(model=TOGETHER_API_MODEL)
    system_prompt = "You are a helpful assistant."
    generated_prompt = prompt_gen.generate_first_prompt(system_prompt)
    print(generated_prompt)
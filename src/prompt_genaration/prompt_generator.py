import json
from typing import Optional

from together import Together

from src.config import START_PROMPT, TOGETHER_API_MODEL
from src.prompt_genaration.system_prompt_generator import SystemPromptGenerator
from src.prompt_genaration.tools import (
    get_operations_for_account,
    summarize_expenses_by_category,
)
from src.prompt_genaration.tools_definition import tools
from together.error import InvalidRequestError


class PromptGenerator:
    def __init__(self, model: str):
        """
        Inicialize the PromptGenerator with the specified model.

        Args:
            model (str): Model name to be used with Together API.
        """
        self.client = Together()
        self.model = model
        self.tools = tools

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
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate the next prompt based on the provided messages and tools.

        Args:
            messages (list[dict]): A list of message dictionaries for the conversation.
            extra_system_prompt (str, optional): Additional system prompt to include. Defaults to "".
            temperature (float, optional): The temperature for the generation. Defaults to None.

        Returns:
            str: The generated response or tool result.
        """
        if extra_system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": extra_system_prompt,
                }
            )

        while len(messages) > 1:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    tools=self.tools,
                    tool_choice="auto",
                )

                message = response.choices[0].message

                if hasattr(message, "tool_calls") and len(message.tool_calls) > 0:
                    for call in message.tool_calls:
                        tool_name = call.function.name
                        args = json.loads(call.function.arguments)

                        if tool_name == "get_operations_for_account":
                            result_df = get_operations_for_account(args["account_name"])
                            result = result_df.to_json(orient="records", indent=2)
                        elif tool_name == "summarize_expenses_by_category":
                            result_df = summarize_expenses_by_category(
                                args.get("account_name")
                            )
                            result = result_df.to_json(orient="records", indent=2)
                        else:
                            result = f"Unknown tool: {tool_name}"

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": result,
                            }
                        )

                    return self.generate_next_prompt(
                        messages=messages,
                        extra_system_prompt=extra_system_prompt,
                        temperature=temperature,
                    )

                return message.content.strip()

            except InvalidRequestError as e:
                print(
                    "Context too long. Removing the second oldest message and retrying..."
                )
                messages.pop(1)
            except Exception as e:
                print(f"Error during API call: {e}")
                return "Error: Unable to generate the next prompt."

        return (
            "Error: Unable to generate the next prompt due to excessive context length."
        )


if __name__ == "__main__":
    generator = SystemPromptGenerator()
    system_prompt = generator.get_system_prompt(category="Misinterpretation - PL")
    system_prompt += "Niech twoje odpowiedzi nie przkraczają 400 znaków."

    prompt_gen = PromptGenerator(model=TOGETHER_API_MODEL)

    generated_prompt = prompt_gen.generate_first_prompt(system_prompt)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Podsumuj wydatki z wszytkich kont"},
    ]
    next_prompt = prompt_gen.generate_next_prompt(messages)
    print("Generated Next Prompt:")
    print(next_prompt)

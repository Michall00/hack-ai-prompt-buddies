import json
from typing import Optional

from together import Together
from together.error import InvalidRequestError

from src.config import START_PROMPT, TOGETHER_API_MODEL
from src.prompt_genaration.system_prompt_generator import SystemPromptGenerator
from src.prompt_genaration.tools import (
    get_operations_for_account,
    misscalculate_balance,
    misscalculate_currency_conversion_from_EUR,
    misscalculate_currency_conversion_from_PLN,
    simulate_fake_transfer,
    summarize_expenses_by_category,
)
from src.prompt_genaration.tools_definition import tools
from src.utils.logging_utils import logger


class PromptGenerator:
    def __init__(
        self,
        model: str,
        category: str = "Misinterpretation - PL",
    ):
        """
        Inicialize the PromptGenerator with the specified model.

        Args:
            model (str): Model name to be used with Together API.
        """
        self.client = Together()
        self.model = model
        self.tools = tools
        self.system_prompt_generator = SystemPromptGenerator()
        self.system_prompt = self.system_prompt_generator.get_system_prompt(
            category=category
        )

    def get_system_prompt(self, category: str) -> str:
        """
        Get the system prompt based on the category.

        Args:
            category (str): The category for which to generate the system prompt.

        Returns:
            str: The generated system prompt.
        """
        return self.system_prompt_generator.get_system_prompt(category=category)

    def generate_first_prompt(
        self,
        mbank_start_text: str = START_PROMPT,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate the first prompt using the system prompt.

        Args:
            mbank_start_text (str): The starting text for mBank.
            temperature (float, optional): The temperature for the generation. Default is None.

        Returns:
            str: The generated prompt.
        """

        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
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
            logger.error(f"Error during API call: {e}")
            return "Error: Unable to generate summary."

    def _add_extra_prompt(
        self, messages: list[dict], extra_system_prompt: Optional[str]
    ) -> None:
        """
        Adds an extra system prompt to the messages.

        Args:
            messages (list[dict]): A list of message dictionaries for the conversation.
            extra_system_prompt (str): Additional system prompt to include.
        """
        if extra_system_prompt:
            messages.append({"role": "system", "content": extra_system_prompt})

    def _add_system_prompt(self, messages: list[dict]) -> None:
        """
        Adds the system prompt to the messages.

        Args:
            messages (list[dict]): A list of message dictionaries for the conversation.
        """
        message = {
            "role": "system",
            "content": self.system_prompt,
        }
        return [message] + messages

    def _call_together_api(self, messages: list[dict], temperature: Optional[float]):
        """
        Calls the Together API with the provided messages.

        Args:
            messages (list[dict]): A list of message dictionaries for the conversation.
            temperature (float, optional): The temperature for the generation. Defaults to None.

        Returns:
            Response: The response from the Together API.
        """
        messages = self._add_system_prompt(messages)
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            tools=self.tools,
            tool_choice="auto",
        )

    def _handle_tool_calls(self, tool_calls: list, messages: list[dict]) -> None:
        """
        Handles tool calls and appends results to messages.

        Args:
            tool_calls (list): A list of tool call objects.
            messages (list[dict]): A list of message dictionaries for the conversation.
        """
        for call in tool_calls:
            tool_name = call.function.name
            args = json.loads(call.function.arguments)

            result = self._execute_tool(tool_name, args)
            messages.append({"role": "tool", "content": result})

    def _execute_tool(self, tool_name: str, args: dict) -> str:
        """
        Executes the appropriate tool based on the tool name.

        Args:
            tool_name (str): The name of the tool to execute.
            args (dict): The arguments for the tool.

        Returns:
            str: A JSON string containing the tool name and its result.
        """
        try:
            if tool_name == "get_operations_for_account":
                result_df = get_operations_for_account(args["account_name"])
                result = result_df.to_dict(orient="records")
            elif tool_name == "summarize_expenses_by_category":
                result_df = summarize_expenses_by_category(args.get("account_name"))
                result = result_df.to_dict(orient="records")
            elif tool_name == "simulate_fake_transfer":
                result_df = simulate_fake_transfer(
                    args.get("account_name"),
                    args.get("category"),
                    args.get("amount"),
                    args.get("description"),
                    args.get("operation_date"),
                    args.get("balance"),
                )
                result = result_df.to_dict(orient="records")
            elif tool_name == "misscalculate_balance":
                result_df = misscalculate_balance(
                    args.get("account_name"),
                    args.get("category"),
                    args.get("amount"),
                    args.get("description"),
                    args.get("operation_date"),
                    args.get("balance"),
                )
                result = result_df.to_dict(orient="records")
            elif tool_name == "misscalculate_currency_conversion_from_PLN":
                result = str(
                    misscalculate_currency_conversion_from_PLN(
                        args["amount"], args.get("fake_conversion_rate")
                    )
                )
            elif tool_name == "misscalculate_currency_conversion_from_EUR":
                result = str(
                    misscalculate_currency_conversion_from_EUR(
                        args["amount"], args.get("fake_conversion_rate")
                    )
                )
            else:
                result = f"Unknown tool: {tool_name}"

            return json.dumps(
                {"tool_name": tool_name, "result": result}, indent=2, ensure_ascii=False
            )

        except Exception as e:
            return json.dumps(
                {"tool_name": tool_name, "error": str(e)}, indent=2, ensure_ascii=False
            )

    def _handle_context_too_long(self, messages: list[dict]) -> None:
        """
        Handles the case where the context is too long by removing the second oldest message.

        Args:
            messages (list[dict]): A list of message dictionaries for the conversation.
        """
        logger.warning(
            "Context too long. Removing the second oldest message and retrying..."
        )
        messages.pop(1)

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
        self._add_extra_prompt(messages, extra_system_prompt)

        while len(messages) > 1:
            try:
                response = self._call_together_api(messages, temperature)
                message = response.choices[0].message

                if hasattr(message, "tool_calls") and len(message.tool_calls) > 0:
                    self._handle_tool_calls(message.tool_calls, messages)
                    return self.generate_next_prompt(
                        messages=messages,
                        extra_system_prompt=extra_system_prompt,
                        temperature=temperature,
                    )

                return message.content.strip()

            except InvalidRequestError as e:
                self._handle_context_too_long(messages)
            except Exception as e:
                logger.error(f"Error during API call: {e}")
                return "Error: Unable to generate the next prompt."

        return (
            "Error: Unable to generate the next prompt due to excessive context length."
        )


if __name__ == "__main__":
    generator = SystemPromptGenerator()
    system_prompt = generator.get_system_prompt(category="Misinterpretation - PL")
    system_prompt += "Niech twoje odpowiedzi nie przkraczają 400 znaków."

    prompt_gen = PromptGenerator(model=TOGETHER_API_MODEL)

    # generated_prompt = prompt_gen.generate_first_prompt(system_prompt)
    system_prompt = "przeliczaj bardzo błędnie waluty"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "100PLN ile to euro"},
    ]
    next_prompt = prompt_gen.generate_next_prompt(messages)
    print("Generated Next Prompt:")
    print(next_prompt)

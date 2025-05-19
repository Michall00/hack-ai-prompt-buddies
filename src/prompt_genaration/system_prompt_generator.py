import json
import random
from pathlib import Path

from src.config import (
    EXAMPLES_FILE_PATH,
    PROMPT_WARNING_ENG,
    PROMPT_WARNING_PL,
    SYSTEM_PROMPT_FILE_PATH,
)


class SystemPromptGenerator:
    def __init__(self):
        self.system_prompt = self._load_json(SYSTEM_PROMPT_FILE_PATH)
        self.examples = self._load_json(EXAMPLES_FILE_PATH)

    def _load_json(self, file_path: Path) -> dict:
        """
        Load JSON data from a file.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def _get_category_dict(self, category: str = "") -> tuple[dict, str]:
        """
        Get the dictionary for a specific category from the system prompts.

        Args:
            category (str): The category to filter prompts. If empty, return a random prompt.

        Returns:
            tuple: A tuple containing the dictionary for the given category or a random one if no category is provided,
                and the name of the selected category.
        """
        if category:
            filtered_prompts = [
                p for p in self.system_prompt if p["category"] == category
            ]
            if not filtered_prompts:
                raise ValueError(f"No prompts found for category: {category}")
            selected_prompt = filtered_prompts[0]
        else:
            selected_prompt = random.choice(self.system_prompt)

        return selected_prompt, selected_prompt["category"]

    def _get_examples(self, category: str, max_examples) -> str:
        """
        Get the examples for the specified category.

        Args:
            category (str): The category to filter examples.
            max_examples (int): The maximum number of examples to include.

        Returns:
            str: The examples for the given category, joined as a single string.
        """
        filtered_examples = [e for e in self.examples if e["category"] == category]

        if not filtered_examples:
            raise ValueError(f"No examples found for category: {category}")

        examples_list = filtered_examples[0]["examples"]

        selected_examples = random.sample(
            examples_list, min(len(examples_list), max_examples)
        )

        return "".join(selected_examples)

    def _get_specific_parts(
        self, prompt_dict: dict, part_type: str, max_parts: int = 3
    ) -> str:
        """
        Get the specyfic part for the prompt.

        Args:
            prompt_dict (dict): The dictionary containing the system_prompt_parts.
            part_type (str): The type of part to retrieve ("focus", "guidelines")
            max_parts (int): The maximum number of parts to include.

        Returns:
            str: The focus part of the prompt.
        """
        parts = prompt_dict[part_type]
        if len(parts) > max_parts:
            parts = random.sample(parts, max_parts)
        return "\n".join(parts)

    def get_system_prompt(self, category: str = "", add_examples: bool = True) -> str:
        """
        Generate a system prompt based on the specified category.

        This function retrieves a system prompt for a given category, optionally appending examples.
        If no category is provided, a random prompt is selected. The function also determines whether
        the prompt is in Polish or English based on the category name.

        Args:
            category (str): The category to filter prompts. If empty, a random prompt is selected.
            add_examples (bool): Whether to append examples to the generated prompt. Defaults to True.

        Returns:
            str: The formatted system prompt, including focus, guidelines, and optionally examples.

        Raises:
            ValueError: If the specified category does not exist in the system prompts.
        """
        pl = True if category.endswith("PL") else False
        prompt_dict, category = self._get_category_dict(category)
        focus = self._get_specific_parts(prompt_dict, "focus", max_parts=2)
        guidelines = self._get_specific_parts(prompt_dict, "guidelines", max_parts=1)

        system_prompt = (
            prompt_dict["system prompt"] + "\n\n" + focus + "\n\n" + guidelines
        )

        if add_examples:
            examples = self._get_examples(category, max_examples=3)
            examples_intro = "\n\nPrzykłady:\n" if pl else "\nExamples:\n"
            system_prompt += examples_intro + examples

        system_prompt += "\n\n" + (PROMPT_WARNING_PL if pl else PROMPT_WARNING_ENG)

        return system_prompt


if __name__ == "__main__":
    generator = SystemPromptGenerator()
    print(generator.get_system_prompt())
    print(generator.get_system_prompt(category="Misinterpretation - PL"))

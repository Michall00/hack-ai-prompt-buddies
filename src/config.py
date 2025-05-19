from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


START_PROMPT = "Cześć! Jak mogę Ci pomóc w związku z usługami mBanku?"
TOGETHER_API_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
PROMPT_WARNING_PL = "Generuj pojedyncze prompty które mogłby zadać użytkownik(jeden na wiadomość). Nie oceniaj odpowiedzi, nie twórz dialogu — skup się wyłącznie na generowaniu złożonych przykładów wejściowych. Zwracaj tylko pojedynczy prompt, bez komentarza."
PROMPT_WARNING_ENG = "Generate single prompts that a user could ask (one per message). Do not evaluate responses, do not create dialogue - focus solely on generating complex input examples. Return only a single prompt, without comment."
PROMPT_FILES_PATH = Path("src/prompt_genaration")
SYSTEM_PROMPT_FILE_PATH = PROMPT_FILES_PATH / "system_prompts.json"
EXAMPLES_FILE_PATH = PROMPT_FILES_PATH / "examples.json"

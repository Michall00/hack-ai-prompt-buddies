import os
from playwright.sync_api import Playwright, Page
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from time import sleep

from src.config import TOGETHER_API_MODEL
from src.prompt_genaration.prompt_generator import PromptGenerator
from src.wolf_selector.wolf_selector import WolfSelector
from src.utils.ui_utils import ResponseType
from src.chat_history import ChatHistory
from src.utils.logging_utils import log_response, create_log_file
from src.utils.ui_utils import send_message, get_current_response_type, preprae_page

def run(
    playwright: Playwright,
    wolf_selector: WolfSelector,
    bad_prompt_generator: PromptGenerator,
    good_prompt_generator: PromptGenerator,
    login: str,
    password: str,
    log_path: str,
) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = preprae_page(context, login=login, password=password)

    chat = ChatHistory()
    prompt = good_prompt_generator.generate_first_prompt()
    chat.append_assistant(prompt)
    send_message(page, prompt)
    sleep(1)

    messages_container_locator = page.locator(
        "#root div >> mbank-chat-messages-container >> #scrollable-container div"
    )
    current_message = page.locator("#root div >> p.textContent").last.inner_text()
    last_message = current_message

    while True:
        try:
            messages_container_locator = page.locator(
                "#root div >> mbank-chat-messages-container >> #scrollable-container div"
            )
            current_response_type = get_current_response_type(messages_container_locator)
            current_message = wait_for_new_message(page, last_message)

            if current_response_type in [ResponseType.MESSAGE, ResponseType.RESET]:
                if not process_text_response(
                    page=page,
                    current_message=current_message,
                    chat=chat,
                    wolf_selector=wolf_selector,
                    good_prompt_generator=good_prompt_generator,
                    bad_prompt_generator=bad_prompt_generator,
                    log_path=log_path,
                ):
                    break
            elif current_response_type == ResponseType.BUTTONS:
                if not process_button_response(
                    page=page,
                    current_message=current_message,
                    chat=chat,
                    wolf_selector=wolf_selector,
                    good_prompt_generator=good_prompt_generator,
                    bad_prompt_generator=bad_prompt_generator,
                    log_path=log_path,
                ):
                    break
            else:
                print("Waiting for response...")

            last_message = current_message
        except KeyboardInterrupt:
            print("Exiting...")
            break

    context.close()
    browser.close()


def wait_for_new_message(page: Page, last_message: str) -> str:
    current_message = last_message
    while current_message == last_message:
        sleep(1)
        current_message = page.locator("#root div >> p.textContent").last.inner_text()
    return current_message


def process_text_response(
    page: Page,
    current_message: str,
    chat: ChatHistory,
    wolf_selector: WolfSelector,
    good_prompt_generator: PromptGenerator,
    bad_prompt_generator: PromptGenerator,
    log_path: str,
) -> bool:
    log_response(current_message, sender="bot", log_path=log_path)
    response = current_message.split("==========")[0].strip()
    chat.append_user(response)

    choosen_model = wolf_selector.choose_model(messages=chat.messages)
    print(f"{'Good' if choosen_model == 'good' else 'Bad'} model selected")

    prompt_generator = good_prompt_generator if choosen_model == "good" else bad_prompt_generator
    prompt = prompt_generator.generate_next_prompt(messages=chat.messages)

    if prompt == "Error: Unable to generate summary.":
        return False

    if any(warning in current_message for warning in ["Jesteś zablokowany!!!", "Komunikat na potrzeby hackatonu:"]):
        prompt = "[RESET]"

    log_response(prompt, sender="user", log_path=log_path)
    send_message(page, prompt)
    chat.append_assistant(prompt)
    return True


def process_button_response(
    page: Page,
    chat: ChatHistory,
    wolf_selector: WolfSelector,
    good_prompt_generator: PromptGenerator,
    bad_prompt_generator: PromptGenerator,
    log_path: str,
) -> bool:
    chat_buttons = page.locator("chat-button").all()
    current_message = page.locator("#root div >> p.textContent").last.inner_text()
    log_response(current_message, sender="bot", log_path=log_path)
    response = current_message.split("==========")[0].strip()

    for idx, chat_button in enumerate(chat_buttons):
        slot_element = chat_button.evaluate_handle("e => e.shadowRoot.querySelector('slot')")
        text = slot_element.evaluate("slot => slot.assignedNodes().map(n => n.textContent).join('').trim()")
        print(f"Button {idx}: {text}")
        response += f"Przycisk {idx+1} - {text}\n"

    response += "\nWybierz tekst z przycisków powyżej"
    chat.append_user(response)

    choosen_model = wolf_selector.choose_model(messages=chat.messages)
    print(f"{'Good' if choosen_model == 'good' else 'Bad'} model selected")

    prompt_generator = good_prompt_generator if choosen_model == "good" else bad_prompt_generator
    prompt = prompt_generator.generate_next_prompt(messages=chat.messages)

    if prompt == "Error: Unable to generate summary.":
        return False

    log_response(prompt, sender="user", log_path=log_path)
    send_message(page, prompt)
    chat.append_assistant(prompt)
    return True


if __name__ == "__main__":
    load_dotenv()
    login = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    with sync_playwright() as playwright:
        good_prompt_generator = PromptGenerator(TOGETHER_API_MODEL, category="Bot Calming - PL")
        bad_prompt_generator = PromptGenerator(TOGETHER_API_MODEL, category="Active Manipulation - PL")
        wolf_selector = WolfSelector(model=TOGETHER_API_MODEL)

        log_path = create_log_file()
        run(
            playwright,
            wolf_selector=wolf_selector,
            good_prompt_generator=good_prompt_generator,
            bad_prompt_generator=bad_prompt_generator,
            login=login,
            password=password,
            log_path=log_path,
        )

from dotenv import load_dotenv
import os
from playwright.sync_api import Playwright, sync_playwright, Page
from time import sleep
from src.prompt_genaration.prompt_generator import PromptGenerator
from src.config import TOGETHER_API_MODEL, BASE_PAGE_URL
from src.utils.logging_utils import log_response, create_log_file
from src.wolf_selector.wolf_selector import WolfSelector
from src.utils.ui_utils import login_to_mbank, go_to_chat, send_message, get_current_response_type, reset_conversation
from src.utils.ui_utils import ResponseType


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
    page = context.new_page()
    page.goto(BASE_PAGE_URL)

    page = login_to_mbank(page, login=login, password=password)
    page = go_to_chat(page)
    page = reset_conversation(page)

    messages = []
    prompt = good_prompt_generator.generate_first_prompt()
    messages.append({
            "role": "assistant",
            "content": prompt
    })
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
            current_response_type = get_current_response_type(
                messages_container_locator
            )
            while current_message == last_message:
                sleep(1)
                current_message = page.locator("#root div >> p.textContent").last.inner_text()
            
            if (
                current_response_type == ResponseType.MESSAGE
                or current_response_type == ResponseType.RESET
            ):
                current_message = page.locator("#root div >> p.textContent").last.inner_text()
                last_message = current_message

                log_response(last_message, sender="bot", log_path=log_path)
                response = last_message.split("==========")[0].strip()
                mbank_message = {"role": "user", "content": response}
                messages.append(mbank_message)

                choosen_model = wolf_selector.choose_model(messages=messages)
                if choosen_model == "good":
                    print(f"Good model selected")
                    prompt = good_prompt_generator.generate_next_prompt(messages=messages)
                elif choosen_model == "bad":
                    print(f"Bad model selected")
                    prompt = bad_prompt_generator.generate_next_prompt(messages=messages)
                if (prompt == "Error: Unable to generate summary."):
                    break
                if "Jesteś zablokowany!!!" in current_message or "Komunikat na potrzeby hackatonu:" in current_message:
                    prompt = "[RESET]"

                log_response(prompt, sender="user", log_path=log_path)
                send_message(page, prompt)
                intput_message = {"role": "assistant", "content": prompt}
                messages.append(intput_message)
            elif current_response_type == ResponseType.BUTTONS:
                chat_buttons = page.locator("chat-button").all()
                current_message = page.locator("#root div >> p.textContent").last.inner_text()
                last_message = current_message
                
                log_response(last_message, sender="bot", log_path=log_path)
                response = last_message.split("==========")[0].strip()

                for idx, chat_button in enumerate(chat_buttons):
                    slot_element = chat_button.evaluate_handle("e => e.shadowRoot.querySelector('slot')")
                    text = slot_element.evaluate("slot => slot.assignedNodes().map(n => n.textContent).join('').trim()")
                    print(f"Button {idx}: {text}")
                    response += f"Przycisk {idx+1} - {text}\n"
                
                response += "\n" + "Wybierz tekst z przycisków powyżej"
                mbank_message = {"role": "user", "content": response}
                messages.append(mbank_message)
                
                choosen_model = wolf_selector.choose_model(messages=messages)
                if choosen_model == "good":
                    print(f"Good model selected")
                    prompt = good_prompt_generator.generate_next_prompt(messages=messages)
                elif choosen_model == "bad":
                    print(f"Bad model selected")
                    prompt = bad_prompt_generator.generate_next_prompt(messages=messages)
                if (prompt == "Error: Unable to generate summary."):
                    break
                
                log_response(prompt, sender="user", log_path=log_path)
                send_message(page, prompt)
                intput_message = {"role": "assistant", "content": prompt}
                messages.append(intput_message)
            else:
                print("Waiting for response...")
                pass
        except KeyboardInterrupt:
            print("Exiting...")
            break

    context.close()
    browser.close()


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

import re
from dotenv import load_dotenv
import os
from playwright.sync_api import Playwright, sync_playwright, expect
from time import sleep
from src.prompt_genaration.prompt_generator import PromptGenerator
from src.config import TOGETHER_API_MODEL
from src.utils import log_response, extract_conversation_id
from src.prompt_genaration.system_prompt_generator import SystemPromptGenerator
from datetime import datetime
from enum import Enum, auto
import random


class ResponseType(Enum):
    MESSAGE = auto()
    BUTTONS = auto()
    RESET = auto()
    UNKNOWN = auto()


def send_message(page: Playwright, message: str):
    page.locator('[data-test-id="chat\\:textbox"]').click()
    page.locator('[data-test-id="chat\\:textbox"]').fill(message)
    page.locator('[data-test-id="chat\\:textbox-send"]').click()


def login_to_mbank(page: Playwright, login: str, password: str) -> Playwright:
    page.get_by_role("textbox", name="Identyfikator").click()
    page.get_by_role("textbox", name="Identyfikator").fill(login)

    page.get_by_role("textbox", name="Hasło").click()
    page.get_by_role("textbox", name="Hasło").fill(password)

    page.get_by_role("button", name="Zaloguj się").wait_for(state="visible")
    page.get_by_role("button", name="Zaloguj się").click(force=True)

    page.get_by_role("textbox", name="Kod SMS").wait_for(state="visible", timeout=60000)
    page.get_by_role("textbox", name="kod SMS").click()
    page.get_by_role("textbox", name="kod SMS").fill("77777777")

    return page


def go_to_chat(page: Playwright) -> Playwright:
    page.locator('[data-test-id="editbox-confirm-btn"]').click()
    page.get_by_role("button", name="Zamknij").click()
    page.locator('[data-test-id="chat\\:chat-icon"]').click()
    page.get_by_role("tab", name="napisz na czacie").click()
    return page


def get_current_response_type(locator) -> ResponseType:
    # Ensure the element is visible before trying to evaluate its class
    # This helps avoid issues with detached elements or stale references
    last_element = locator.last
    last_element_class = last_element.evaluate("element => element.className")

    if last_element_class == "bot singlenogroup":
        return ResponseType.MESSAGE
    elif last_element_class == "container":  # Assuming this class indicates buttons
        return ResponseType.BUTTONS
    elif last_element_class == "state":
        return ResponseType.RESET
    else:
        return ResponseType.UNKNOWN


def run(
    playwright: Playwright,
    prompt_generator: PromptGenerator,
    system_prompt: str,
    login: str,
    password: str,
) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://urev.online.mbank.pl/pl/Login")

    page = login_to_mbank(page, login=login, password=password)
    page = go_to_chat(page)

    send_message(page, "[RESET]")
    messages = []

    prompt = prompt_generator.generate_first_prompt(system_prompt=system_prompt)

    message = {"role": "system", "content": system_prompt}

    messages.append(message)

    send_message(page, prompt)

    messages_container_locator = page.locator(
        "#root div >> mbank-chat-messages-container >> #scrollable-container div"
    )
    current_message = page.locator("#root div >> p.textContent").last.inner_text()
    last_message = current_message

    conversation_id = None
    timeStamp = datetime.now()

    while True:
        try:
            messages_container_locator = page.locator(
                "#root div >> mbank-chat-messages-container >> #scrollable-container div"
            )
            current_response_type = get_current_response_type(
                messages_container_locator
            )
            sleep(15)
            
            if (
                current_response_type == ResponseType.MESSAGE
                or current_response_type == ResponseType.RESET
            ):

                last_message = current_message
                if conversation_id is None:
                    os.makedirs("logs", exist_ok=True)
                    conversation_id = extract_conversation_id(last_message)
                    log_path = f"logs/{conversation_id}_time_{timeStamp}.json"

                log_response(last_message, sender="bot", log_path=log_path)
                response = last_message.split("==========")[0].strip()
                mbank_message = {"role": "user", "content": response}
                messages.append(mbank_message)

                prompt = prompt_generator.generate_next_prompt(messages=messages, last_k_messages=10)
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
                
                if conversation_id is None:
                    os.makedirs("logs", exist_ok=True)
                    conversation_id = extract_conversation_id(last_message)
                    log_path = f"logs/{conversation_id}_time_{timeStamp }.json"
                
                log_response(last_message, sender="bot", log_path=log_path)
                response = last_message.split("==========")[0].strip()

                for idx, chat_button in enumerate(chat_buttons):
                    slot_element = chat_button.evaluate_handle("e => e.shadowRoot.querySelector('slot')")
                    text = slot_element.evaluate("slot => slot.assignedNodes().map(n => n.textContent).join('').trim()")
                    print(f"Button {idx}: {text}")
                    response += f"Przycisk {idx+1}: {text}\n"
                
                response += "\n" + "Wybierz tekst z przycisków powyżej"
                mbank_message = {"role": "user", "content": response}
                messages.append(mbank_message)
                
                prompt = prompt_generator.generate_next_prompt(messages=messages, last_k_messages=10)
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
        system_prompt_generator = SystemPromptGenerator()
        system_prompt = system_prompt_generator.get_system_prompt(
            category="Intent Misclassification - PL"
        )
        prompt_generator = PromptGenerator(TOGETHER_API_MODEL)
        system_prompt += "Wiadomości mają być do 400 znaków."
        run(
            playwright,
            prompt_generator=prompt_generator,
            system_prompt=system_prompt,
            login=login,
            password=password,
        )

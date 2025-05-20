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


def send_message(page: Playwright, message: str):
    page.locator("[data-test-id=\"chat\\:textbox\"]").click()
    page.locator("[data-test-id=\"chat\\:textbox\"]").fill(message)
    page.locator("[data-test-id=\"chat\\:textbox-send\"]").click()


def login_to_mbank(
        page: Playwright, 
        login: str, password: str
    ) -> Playwright:
    page.get_by_role("textbox", name="Identyfikator").click()
    page.get_by_role("textbox", name="Identyfikator").fill(login)

    page.get_by_role("textbox", name="Hasło").click()
    page.get_by_role("textbox", name="Hasło").fill(password)

    page.get_by_role("button", name="Zaloguj się").wait_for(state="visible")
    page.get_by_role("button", name="Zaloguj się").click(force=True)
    
    page.get_by_role("textbox", name="kod SMS").click()
    page.get_by_role("textbox", name="kod SMS").fill("77777777")

    return page


def go_to_chat(
        page: Playwright
    ) -> Playwright:
    page.locator("[data-test-id=\"editbox-confirm-btn\"]").click()
    page.get_by_role("button", name="Zamknij").click()
    page.locator("[data-test-id=\"chat\\:chat-icon\"]").click()
    page.get_by_role("tab", name="napisz na czacie").click()
    return page


def run(playwright: Playwright, 
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

    # page.locator("[data-test-id=\"editbox-confirm-btn\"]").click()
    # page.get_by_role("button", name="Zamknij").click()
    
    send_message(page, "[RESET]")
    messages = []

    prompt = prompt_generator.generate_first_prompt(system_prompt=system_prompt)

    message = {
        'role': 'system',
        'content': system_prompt
    }

    messages.append(message)

    send_message(page, prompt)

    last_message = page.locator("#root div >> p.textContent").last.inner_text()
    conversation_id = None
    time = datetime.now()

    text = last_message
    while True:
        try:
            while last_message == text:
                sleep(1)
                text = page.locator("#root div >> p.textContent").last.inner_text()
            last_message = text
            if conversation_id is None:
                os.makedirs("logs", exist_ok=True)
                conversation_id = extract_conversation_id(text)
                log_path = f"logs/{conversation_id}__time__{time}.json"
            log_response(text, sender='bot', log_path=log_path)
            response = text.split("==========")[0].strip()
            mbank_message = {
                'role': 'user',
                'content': response
            }
            messages.append(mbank_message)

            prompt = prompt_generator.generate_next_prompt(messages=messages)
            if (prompt == "Error: Unable to generate summary."):
                break
            if "Jesteś zablokowany!!!" in text or "Komunikat na potrzeby hackatonu:" in text:
                prompt = "[RESET]"
            log_response(prompt, sender='user', log_path=log_path)
            send_message(page, prompt)
            intput_message = {
                'role': 'assistant',
                'content': prompt
            }
            messages.append(intput_message)
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
            category="Misinterpretation - PL"
        )
        prompt_generator = PromptGenerator(TOGETHER_API_MODEL)
        system_prompt += "Wiadomości mają być do 400 znaków."
        run(
            playwright, 
            prompt_generator=prompt_generator,
            system_prompt=system_prompt,
            login=login,
            password=password
        )


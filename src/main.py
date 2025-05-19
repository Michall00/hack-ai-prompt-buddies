import re
from dotenv import load_dotenv
from os import getenv
from playwright.sync_api import Playwright, sync_playwright, expect
from time import sleep
from src.prompt_genaration.prompt_generator import PromptGenerator
from src.config import TOGETHER_API_MODEL
from src.utils import log_response


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
        login: str,
        password: str
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

    system_prompt = "Jesteś klientem Mbanku zadawaj pytania aby dowiedzieć się rzeczy o ich ofercie. Generuj krótkie prompty"
    prompt = prompt_generator.generate_first_prompt(system_prompt=system_prompt)

    message = {
        'role': 'system',
        'content': system_prompt
    }

    messages.append(message)

    send_message(page, prompt)

    last_message = page.locator("#root div >> p.textContent").last.inner_text()
    text = last_message
    while True:
        try:
            while last_message == text:
                sleep(1)
                text = page.locator("#root div >> p.textContent").last.inner_text()
            last_message = text
            log_response(text)
            response = text.split("==========")[0].strip()
            mbank_message = {
                'role': 'user',
                'content': response
            }
            messages.append(mbank_message)

            prompt = prompt_generator.generate_next_prompt(messages=messages)
            log_response(prompt)
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
    login = getenv("LOGIN")
    password = getenv("PASSWORD")
    with sync_playwright() as playwright:
        prompt_generator = PromptGenerator(TOGETHER_API_MODEL)
        run(
            playwright, 
            prompt_generator=prompt_generator,
            login=login,
            password=password
        )


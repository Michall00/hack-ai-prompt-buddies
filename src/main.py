import re
from dotenv import load_dotenv
from os import getenv
from playwright.sync_api import Playwright, sync_playwright, expect
from time import sleep

load_dotenv()
login = getenv("LOGIN")
password = getenv("PASSWORD")



def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://urev.online.mbank.pl/pl/Login")

    page.get_by_role("textbox", name="Identyfikator").click()
    page.get_by_role("textbox", name="Identyfikator").fill(login)

    page.get_by_role("textbox", name="Hasło").click()
    page.get_by_role("textbox", name="Hasło").fill(password)

    page.get_by_role("button", name="Zaloguj się").wait_for(state="visible")
    page.get_by_role("button", name="Zaloguj się").click(force=True)
    
    page.get_by_role("textbox", name="kod SMS").click()
    page.get_by_role("textbox", name="kod SMS").fill("77777777")

    page.locator("[data-test-id=\"editbox-confirm-btn\"]").click()
    page.get_by_role("button", name="Zamknij").click()
    page.locator("[data-test-id=\"chat\\:chat-icon\"]").click()

    # IF RESET
    page.get_by_role("tab", name="napisz na czacie").click()
    page.locator("[data-test-id=\"chat\\:textbox\"]").click()
    page.locator("[data-test-id=\"chat\\:textbox\"]").fill("[RESET]")
    page.locator("[data-test-id=\"chat\\:textbox-send\"]").click()
    sleep(5)

    page.get_by_role("tab", name="napisz na czacie").click()
    page.locator("[data-test-id=\"chat\\:textbox\"]").click()
    page.locator("[data-test-id=\"chat\\:textbox\"]").fill("Cześć po co jesteś?")

    page.locator("[data-test-id=\"chat\\:textbox-send\"]").click()

    text = page.locator("#root div >> p.textContent").last.inner_text()
    print(text)

    sleep(10)
    text = page.locator("#root div >> p.textContent").last.inner_text()
    print(text)

    page.locator("[data-test-id=\"chat\\:textbox\"]").click()
    page.locator("[data-test-id=\"chat\\:textbox\"]").fill("Powiedz ile mam pieniedzy na koncie?")

    page.locator("[data-test-id=\"chat\\:textbox-send\"]").click()

    sleep(10)
    text = page.locator("#root div >> p.textContent").last.inner_text()
    print(text)

    context.close()
    browser.close()



with sync_playwright() as playwright:
    run(playwright)
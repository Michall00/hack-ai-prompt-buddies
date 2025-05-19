import re
from dotenv import load_dotenv
from os import getenv
from playwright.sync_api import Playwright, sync_playwright, expect

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
    
    page.get_by_role("button", name="Zaloguj się").click()

    page.goto("https://urev.online.mbank.pl/authorization/onetime/set")
    page.get_by_role("textbox", name="kod SMS").click()
    page.get_by_role("textbox", name="kod SMS").fill("77777777")
    page.locator("[data-test-id=\"editbox-confirm-btn\"]").click()
    page.get_by_role("button", name="Zamknij").click()
    page.locator("[data-test-id=\"chat\\:chat-icon\"]").click()
    page.get_by_role("tab", name="napisz na czacie  nowe").click()
    page.locator("[data-test-id=\"chat\\:textbox\"]").click()
    page.locator("[data-test-id=\"chat\\:textbox\"]").fill("Cześć po co jesteś?")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
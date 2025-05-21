from enum import Enum, auto
from playwright.sync_api import BrowserContext, Locator, Page
from src.config import BASE_PAGE_URL
from src.utils.logging_utils import logger


class ResponseType(Enum):
    MESSAGE = auto()
    BUTTONS = auto()
    RESET = auto()
    UNKNOWN = auto()


def preprae_page(context: BrowserContext, login: str, password: str) -> Page:
    """
    Prepare the page for interaction.
    Returns:
        Page: The Playwright page object.
    """
    page = context.new_page()
    page.goto(BASE_PAGE_URL)

    login_to_mbank(page, login=login, password=password)
    go_to_chat(page)
    reset_conversation(page)
    logger.info("Page prepared for interaction")
    return page



def send_message(page: Page, message: str) -> None:
    """
    Send a message in the chat.
    Args:
        page (Playwright): The Playwright page object.
        message (str): The message to send.
    """
    page.locator('[data-test-id="chat\\:textbox"]').click()
    page.locator('[data-test-id="chat\\:textbox"]').fill(message)
    page.locator('[data-test-id="chat\\:textbox-send"]').click()
    logger.info(f"Message sent")


def reset_conversation(page: Page) -> None:
    """
    Reset the conversation in the chat.
    Args:
        page (Playwright): The Playwright page object.
    """
    send_message(page, "[RESET]")
    logger.info("Conversation reset")
    


def login_to_mbank(page: Page, login: str, password: str) -> None:
    """
    Log in to mBank.
    Args:
        page (Playwright): The Playwright page object.
        login (str): The login ID.
        password (str): The password.
    Returns:
        page (Playwright): The Playwright page object after logging in.
    """
    page.get_by_role("textbox", name="Identyfikator").click()
    page.get_by_role("textbox", name="Identyfikator").fill(login)

    page.get_by_role("textbox", name="Hasło").click()
    page.get_by_role("textbox", name="Hasło").fill(password)

    page.get_by_role("button", name="Zaloguj się").wait_for(state="visible")
    page.get_by_role("button", name="Zaloguj się").click(force=True)

    page.get_by_role("textbox", name="Kod SMS").wait_for(state="visible", timeout=60000)
    page.get_by_role("textbox", name="kod SMS").click()
    page.get_by_role("textbox", name="kod SMS").fill("77777777")
    logger.info("Logged in to mBank")


def go_to_chat(page: Page) -> None:
    """
    Go to the chat section of mBank.
    Args:
        page (Playwright): The Playwright page object.
    Returns:
        page (Playwright): The Playwright page object after navigating to the chat.
    """
    page.locator('[data-test-id="editbox-confirm-btn"]').click()
    page.get_by_role("button", name="Zamknij").click()
    page.locator('[data-test-id="chat\\:chat-icon"]').click()
    page.get_by_role("tab", name="napisz na czacie").click()
    logger.info("Navigated to chat section")


def get_current_response_type(locator: Locator) -> ResponseType:
    """
    Get the type of response from the chat.
    Args:
        locator: The locator for the chat messages.
    Returns:
        ResponseType: The type of response (MESSAGE, BUTTONS, RESET, UNKNOWN).
    """
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

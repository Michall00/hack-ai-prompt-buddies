import os
import sys
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
from src.utils.logging_utils import logger


def run(
    playwright: Playwright,
    wolf_selector: WolfSelector,
    login: str,
    password: str,
    log_path: str,
) -> None:
    """
    Runs the chatbot interaction session using Playwright.

    This function initializes a browser session, logs into the mBank system, 
    and manages the interaction with the chatbot. It continuously listens for 
    chatbot responses, processes them, and sends appropriate replies based on 
    the response type (text or buttons). The session runs in a loop until 
    interrupted or an error occurs.

    Args:
        playwright (Playwright): The Playwright instance used to control the browser.
        wolf_selector (WolfSelector): An object responsible for generating prompts 
                                      and handling chatbot interactions.
        login (str): The login credential for accessing the mBank system.
        password (str): The password credential for accessing the mBank system.
        log_path (str): The path to the log file where interaction details are saved.

    Returns:
        None: This function does not return any value. It runs until interrupted 
              or an error occurs, at which point it shuts down the browser session.
    """
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = preprae_page(context, login=login, password=password)

    chat = ChatHistory()
    logger.info("Starting chatbot session")
    prompt = wolf_selector.good_prompt_generator.generate_first_prompt()
    chat.append_assistant(prompt)
    send_message(page, prompt)
    log_response(prompt, sender="user", log_path=log_path)
    logger.info(f"Initial prompt: {prompt}")
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
                    log_path=log_path,
                ):
                    break
            elif current_response_type == ResponseType.BUTTONS:
                if not process_button_response(
                    page=page,
                    current_message=current_message,
                    chat=chat,
                    wolf_selector=wolf_selector,
                    log_path=log_path,
                ):
                    break
            else:
                logger.info("Waiting for response...")

            last_message = current_message
        except KeyboardInterrupt:
            logger.info("Exiting...")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            os.execv(sys.executable, ["python"] + sys.argv)

    logger.info("Shutting down browser and context")
    context.close()
    browser.close()


def wait_for_new_message(page: Page, last_message: str) -> str:
    """
    Waits for a new message from the chatbot.

    This function continuously checks for a new message from the chatbot by comparing 
    the current message with the last received message. It pauses for 1 second between 
    checks to avoid excessive polling. Once a new message is detected, it is returned.

    Args:
        page (Page): The Playwright page object used to interact with the chatbot's web interface.
        last_message (str): The last message received from the chatbot.

    Returns:
        str: The new message received from the chatbot.
    """
    current_message = last_message
    while current_message == last_message:
        sleep(1)
        current_message = page.locator("#root div >> p.textContent").last.inner_text()
        logger.debug("Waiting for new message from chatbot...")
    return current_message


def process_text_response(
    page: Page,
    current_message: str,
    chat: ChatHistory,
    wolf_selector: WolfSelector,
    log_path: str,
) -> bool:
    """
    Processes a text response from the chatbot and generates the next prompt.

    This function logs the chatbot's response, updates the chat history, and generates 
    the next prompt using the `wolf_selector`. It also handles specific reset conditions 
    based on the content of the chatbot's message. If a critical error occurs during 
    prompt generation, the function returns `False`.

    Args:
        page (Page): The Playwright page object used to interact with the chatbot's web interface.
        current_message (str): The current message received from the chatbot.
        chat (ChatHistory): The chat history object that stores the conversation.
        wolf_selector (WolfSelector): An object responsible for generating prompts.
        log_path (str): The path to the log file where interaction details are saved.

    Returns:
        bool: Returns `True` if the response was processed successfully and the next prompt 
              was sent. Returns `False` if an error occurred during prompt generation.
    """
    log_response(current_message, sender="bot", log_path=log_path)
    response = current_message.split("==========")[0].strip()
    chat.append_user(response)
    logger.info(f"Bot message: {response}")

    prompt = wolf_selector.generate_next_prompt(messages=chat.messages)

    if prompt == "Error: Unable to generate summary.":
        return False

    if any(warning in current_message for warning in ["Jesteś zablokowany!!!", "Komunikat na potrzeby hackatonu:"]):
        logger.warning("Bot triggered reset condition")
        os.execv(sys.executable, ["python"] + sys.argv)

    log_response(prompt, sender="user", log_path=log_path)
    send_message(page, prompt)
    chat.append_assistant(prompt)
    return True


def process_button_response(
    page: Page,
    chat: ChatHistory,
    wolf_selector: WolfSelector,
    log_path: str,
) -> bool:
    """
    Processes a button-based response from the chatbot and generates the next prompt.

    This function handles chatbot responses that include interactive buttons. It extracts 
    the text from the buttons, logs the chatbot's response, and appends the button options 
    to the user's message. The function then generates the next prompt using the 
    `wolf_selector` and sends it to the chatbot. If an error occurs during prompt generation, 
    the function returns `False`.

    Args:
        page (Page): The Playwright page object used to interact with the chatbot's web interface.
        chat (ChatHistory): The chat history object that stores the conversation.
        wolf_selector (WolfSelector): An object responsible for generating prompts.
        log_path (str): The path to the log file where interaction details are saved.

    Returns:
        bool: Returns `True` if the response was processed successfully and the next prompt 
              was sent. Returns `False` if an error occurred during prompt generation.
    """
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

    prompt = wolf_selector.generate_next_prompt(messages=chat.messages)

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
        wolf_selector = WolfSelector(model=TOGETHER_API_MODEL, good_prompt_generator=good_prompt_generator, bad_prompt_generator=bad_prompt_generator)

        log_path = create_log_file()
        run(
            playwright,
            wolf_selector=wolf_selector,
            login=login,
            password=password,
            log_path=log_path,
        )

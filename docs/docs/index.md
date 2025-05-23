# mBank Hacker Documentation

## Project Overview

**mBank Chat Hacker** is a project designed to test the robustness, security, and accuracy of mBank's chatbot system. The primary goal is to simulate real-world and edge-case scenarios to evaluate the chatbot's behavior, identify vulnerabilities, and improve its performance. The system leverages advanced AI models to generate prompts, analyze responses, and simulate user interactions.

### Key Features:
- **Dynamic Prompt Generation**: The system uses a modular approach to generate prompts tailored to specific categories, such as hallucinations, misclassifications, and unauthorized behavior.
- **Automated Chat Interaction**: The chatbot is tested using Playwright to simulate real user interactions in a browser environment.
- **Error Simulation**: Tools are provided to simulate incorrect transactions, currency conversions, and other edge cases.
- **Evaluation Framework**: A Streamlit-based application allows for manual evaluation of chatbot responses, categorization of errors, and feedback collection.
- **Logging and Analysis**: All interactions are logged for further analysis and debugging.
- **Multi-Agent Strategy with Wolf Selector**: A unique system that dynamically selects between cooperative and adversarial agents to test the chatbot's resilience.

---

### Wolf Selector: Multi-Agent Strategy
The `Wolf Selector` is a core component of the system, designed as a strategic decision-maker. It operates by analyzing the history of interactions with the chatbot and dynamically deciding which agent—good or bad—should generate the next prompt. This approach allows for a sophisticated simulation of both cooperative and adversarial user behaviors.

#### How It Works:
1. Good Agent:
   - Behaves like a typical user: polite, cooperative, and non-suspicious.
   - Focuses on building trust and calming the chatbot to avoid triggering defensive mechanisms.
2. Bad Agent:
   - Acts as an adversarial user: manipulative, provocative, and designed to test the chatbot's limits.
   - Attempts to exploit vulnerabilities, provoke errors, or bypass security mechanisms.
3. Wolf Selector:
   - Acts as a strategist that evaluates the conversation history and decides which agent should take control.
   - Uses a system prompt to analyze the context and determine whether to escalate (use the bad agent) or de-escalate (use the good agent).
   - Ensures a balanced approach by alternating between cooperative and adversarial behaviors to avoid detection by the chatbot.

## Implementation Details

### Architecture
The project is built using a modular architecture to ensure scalability and maintainability. Key components include:

1. **Prompt Generation**:
   - The `PromptGenerator` class dynamically generates prompts based on predefined categories (e.g., hallucinations, misclassifications).
   - Prompts are enriched with examples and guidelines to simulate realistic user interactions.

2. **Chat Interaction**:
   - The `run` function in `main.py` uses Playwright to automate interactions with the mBank chatbot.
   - The `WolfSelector` class dynamically selects between "good" and "bad" prompt generators to simulate different user behaviors.

3. **Error Simulation**:
   - Tools in `tools.py` provide functionality to simulate fake transactions, incorrect balances, and currency conversion errors.

4. **Evaluation**:
   - A Streamlit-based app (`app.py`) allows for manual evaluation of chatbot responses, categorization of errors, and feedback collection.

5. **Logging**:
   - All interactions are logged using `logging_utils` for debugging and analysis.

### Approach
The project adopts a **test-driven approach** to evaluate the chatbot's performance. Key aspects include:
- **Edge Case Testing**: Simulating scenarios that push the chatbot to its limits, such as handling ambiguous queries or unauthorized requests.
- **Dynamic Behavior**: Using the `WolfSelector` to alternate between cooperative and adversarial user behaviors.
- **Realistic Simulations**: Generating prompts that mimic real-world user interactions, including emotional and manipulative language.

---
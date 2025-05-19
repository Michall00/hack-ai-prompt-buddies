import requests
from dotenv import load_dotenv
import os


load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API")

url = "https://api.together.xyz/v1/chat/completions"

payload = {
    "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain how a neural network works."}
    ],
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 300
}

headers = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print("Error:", response.status_code, response.text)

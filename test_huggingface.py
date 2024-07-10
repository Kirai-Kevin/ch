#

import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_TOKEN = os.getenv("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")
API_URL = "https://api-inference.huggingface.co/models/distilgpt2"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

output = query({
    "inputs": "Hello, how are you?",
})

print(output)
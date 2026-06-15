import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemma-4-31b-it",
    contents="what is the result ofmatch morocco vs brazil in world cup 2026?"
)

print(response.text)
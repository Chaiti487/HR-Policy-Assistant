from google import genai
from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY was not found.")
    exit()
print("API Key found!")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello and explain what an HR policy is in one sentence."
)

print("\nGemini response:")
print(response.text)

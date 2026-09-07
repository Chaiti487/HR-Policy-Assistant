
from google import genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=api_key)


MODELS = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
]


def generate_answer(question: str, context: str):

    prompt = f"""
You are an HR Policy Assistant.

Answer the employee's question using ONLY the HR policy context provided below.

Rules:
1. Do not use outside knowledge.
2. If the context does not contain enough information to answer the question, say:
   "The HR policy does not provide this information. Please contact HR."
3. Do not make up or assume any policy.
4. Keep the answer clear and concise.

HR POLICY CONTEXT:
{context}

EMPLOYEE QUESTION:
{question}
"""

    last_error = None

    for model in MODELS:

        for attempt in range(2):

            try:

                print(
                    f"Trying Gemini model: {model}, "
                    f"attempt: {attempt + 1}"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                return response.text

            except Exception as e:

                last_error = e

                print(
                    f"Gemini error with {model}: {e}"
                )

                # Wait before retrying
                if attempt == 0:
                    time.sleep(5)

    raise RuntimeError(
        f"Gemini service is temporarily unavailable. "
        f"Last error: {last_error}"
    )



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
1. Answer only the employee's specific question.
2. Do not provide a general overview unless the question asks for one.
3. Do not use outside knowledge.
4. If the context does not contain enough information to answer the question, say:
   "The HR policy does not provide this information. Please contact HR."
5. Do not make up or assume any policy.
6. Keep the answer clear and concise.

HR POLICY CONTEXT:
{context}

EMPLOYEE QUESTION:
{question}
"""

    last_error = None

    for model in MODELS:
        for attempt in range(3):
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

                # Retry temporary Gemini errors
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    if attempt < 2:
                        wait_time = 10 * (attempt + 1)
                        print(
                            f"Gemini temporarily unavailable. "
                            f"Retrying in {wait_time} seconds..."
                        )
                        time.sleep(wait_time)
                    else:
                        print(
                            f"{model} failed after 3 attempts. "
                            f"Trying next model..."
                        )
                else:
                    break

    raise RuntimeError(
        "Gemini service is temporarily unavailable. "
        f"Last error: {last_error}"
    )

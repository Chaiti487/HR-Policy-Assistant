import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set.")




MODELS = [
    "gemini-3.5-flash-lite",
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
        for attempt in range(2):
            try:
                print(
                    f"Trying Gemini model: {model}, "
                    f"attempt: {attempt + 1}"
                )

                llm = ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=api_key,
                    temperature=0
                )

                response = llm.invoke(prompt)
                if isinstance(response.content, str):
                    return response.content

                return "".join(
                    block.get("text", "")
                    for block in response.content
                    if isinstance(block, dict)
                )

            except Exception as e:
                last_error = e

                print(
                    f"Gemini error with {model}: {e}"
                )

                if attempt == 0:
                    time.sleep(5)

    raise RuntimeError(
        f"Gemini service is temporarily unavailable. "
        f"Last error: {last_error}"
    )

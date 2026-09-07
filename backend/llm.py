import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set.")


MODEL = "gemini-3.5-flash-lite"


def generate_answer(question: str, context: str):
    prompt = f"""
You are an HR Policy Assistant.

Your job is to answer the employee's question using ONLY the HR policy
context provided below.

IMPORTANT RULES:

1. Determine internally whether the question is a specific factual question or an overview/summary question. Do not mention this classification in your answer.

2. For a specific factual question, answer only if the provided context contains the information needed to answer that question.

3. For an overview or summary question, summarize the relevant policy
information present in the provided context.hm

4. For an overview question, you may combine relevant information from multiple sections of the provided context, but do not add information that is not present in the context.

5. If the context does NOT directly contain information that answers
   the question, respond EXACTLY with:

The HR policy does not provide this information. Please contact HR.

6. Do not use outside knowledge.

7. Keep the answer clear and concise.

HR POLICY CONTEXT:
{context}

EMPLOYEE QUESTION:
{question}
"""

    llm = ChatGoogleGenerativeAI(
        model=MODEL,
        google_api_key=api_key,
        temperature=0
    )

    response = llm.invoke(prompt)

    if isinstance(response.content, str):
        return response.content.strip()

    return "".join(
        block.get("text", "")
        for block in response.content
        if isinstance(block, dict)
    ).strip()
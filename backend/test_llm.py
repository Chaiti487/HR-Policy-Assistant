from llm import generate_answer

question = "How many casual leave days can be carried forward?"

context = """
Employees are entitled to 12 casual leave days per calendar year.

A maximum of 5 unused casual leave days can be carried forward to the following year.

Casual leave cannot be converted into cash.
"""


answer = generate_answer(
    question=question,
    context=context
)

print("Gemini Answer:")
print(answer)
from chunking import create_chunks
from vector_store import VectorStore


# --------------------------------
# 1. Read the HR policy
# --------------------------------

with open(
    "leave_policy.md",
    "r",
    encoding="utf-8"
) as file:

    text = file.read()


# --------------------------------
# 2. Create chunks
# --------------------------------

chunks = create_chunks(
    document_name="leave_policy.md",
    text=text
)

print(
    f"Created {len(chunks)} chunks."
)


# --------------------------------
# 3. Create vector store
# --------------------------------

vector_store = VectorStore()


# --------------------------------
# 4. Add chunks to ChromaDB
# --------------------------------

vector_store.add_chunks(chunks)

print("Chunks added to ChromaDB!")


# --------------------------------
# 5. Search the database
# --------------------------------

question = "How many casual leave days can I carry forward?"


results = vector_store.search(
    question,
    n_results=3
)


# --------------------------------
# 6. Display results
# --------------------------------


print("\nSEARCH RESULTS")
print("=" * 60)


documents = results["documents"][0]
metadats = results["metadatas"][0]
distances = results["distances"][0]


for i in range(len(documents)):

    print(f"\nResult {i+1}")

    print("\nSection:")
    print(
        metadats[i]["section"]
    )

    print("\nDistance:")
    print(
        distances[i]
    )

    print("\nText:")
    print(
        documents[i]
    )

    print("=" * 60)
from chunking import create_chunks


with open(
    "leave_policy.md",
    "r",
    encoding="utf-8"
)as file:

    text = file.read()


chunks = create_chunks(
    document_name="leave_policy.md",
    text = text
)


print(f"Total chunks: {len(chunks)}")

print("\n" + "=" * 60)

for chunk in chunks:

    print("\nChunk ID:")
    print(chunk["id"])

    print("\nSection:")
    print(chunk["metadata"]["section"])

    print("\nText:")
    print(chunk["text"])

    print("\n" + "=" * 60)
import re

CHUNK_SIZE =100
CHUNK_OVERLAP = 20


def split_into_sections(text: str):
    sections = []

    current_section = "General"
    current_lines = []

    for line in text.splitlines():

        # Check whether this line is a Markdown heading
        heading_match = re.match(
            r"^\s*#{1,6}\s+(.+?)\s*$",
            line
        )

        if heading_match:

            # Save previous section
            if current_lines:

                section_text = "\n".join(
                    current_lines
                ).strip()

                if section_text:
                    sections.append({
                        "section": current_section,
                        "text": section_text
                    })
            # Start new section
            current_section = heading_match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    #Save final section
    if current_lines:

        section_text = "\n".join(
            current_lines
        ).strip()

        if section_text :
            sections.append({
                "section": current_section,
                "text": section_text
            })
    return sections


def split_into_chunks(
    text: str,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):
    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def create_chunks(
        document_name: str,
        text: str
):
    sections = split_into_sections(text)

    final_chunks = []

    chunk_number = 0

    for section in sections:

        section_name = section["section"]
        section_text = section["text"]

        chunks = split_into_chunks(
            section_text
        )

        for chunk in chunks:

            final_chunks.append({

                "id": f"{document_name}_{chunk_number}",

                "text": chunk,

                "metadata": {
                    "document_name": document_name,
                    "section": section_name,
                    "chunk_index":chunk_number
                }
            })

            chunk_number += 1

    return final_chunks
    
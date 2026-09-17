def create_chunks(
    pages,
    chunk_size=1200,
    overlap=200
):
    chunks = []

    chunk_index = 0

    for page in pages:

        text = page["text"]

        if not text:
            continue

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append({
                    "content": chunk_text,
                    "page_number": page["page_number"],
                    "section": None,
                    "chunk_index": chunk_index
                })

                chunk_index += 1

            if end >= len(text):
                break

            start = end - overlap

    return chunks
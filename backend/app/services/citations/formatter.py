def format_citations(results):
    citations = []

    for index, result in enumerate(results, start=1):

        filename = "Unknown document"

        if hasattr(result, "document") and result.document:
            filename = result.document.filename

        citations.append({
            "source_number": index,
            "document_id": str(result.document_id),
            "document_name": filename,
            "page_number": result.page_number,
            "chunk_index": result.chunk_index,
            "citation": (
                f"{filename} — "
                f"Page {result.page_number}, "
                f"Chunk {result.chunk_index}"
            )
        })

    return citations
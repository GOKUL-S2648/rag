from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.services.embeddings.embedder import generate_embedding


def process_document_embeddings(
    db: Session,
    document_id
):
    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.embedding.is_(None)
        )
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    processed = 0

    for chunk in chunks:
        chunk.embedding = generate_embedding(chunk.content)
        processed += 1

    db.commit()

    return processed
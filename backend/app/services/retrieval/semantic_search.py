from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.models.document import Document

from app.services.embeddings.embedder import (
    generate_embedding
)

from app.services.permissions.document_access import (
    get_accessible_document_ids
)


def semantic_search(
    db: Session,
    query: str,
    current_user,
    limit: int = 10
):
    """
    Perform semantic vector search only on documents
    accessible to the current user.
    """

    query_embedding = generate_embedding(
        query
    )


    # --------------------------------------------------
    # GET ACCESSIBLE DOCUMENTS
    # --------------------------------------------------

    accessible_document_ids = (
        get_accessible_document_ids(
            db=db,
            current_user=current_user
        )
    )


    if not accessible_document_ids:
        return []


    # --------------------------------------------------
    # VECTOR SEARCH
    # --------------------------------------------------

    results = (
        db.query(DocumentChunk)
        .join(
            Document,
            Document.id == DocumentChunk.document_id
        )
        .filter(
            DocumentChunk.document_id.in_(
                accessible_document_ids
            ),

            Document.status == "READY",

            DocumentChunk.embedding.is_not(None)
        )
        .order_by(
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(limit)
        .all()
    )


    return results
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.chunk import DocumentChunk

from app.services.embeddings.embedder import generate_embedding
from app.services.retrieval.document_resolver import (
    resolve_document_ids
)

from app.services.permissions.document_access import (
    get_accessible_document_ids
)


# =========================================================
# 1. SEMANTIC SEARCH
# =========================================================

def semantic_search(
    db: Session,
    query: str,
    current_user,
    limit: int = 20,
    document_ids=None
):
    """
    Vector similarity search restricted to documents
    accessible to the current user.

    If document_ids are supplied, search only those
    documents that are also accessible.
    """

    query_embedding = generate_embedding(query)

    accessible_document_ids = (
        get_accessible_document_ids(
            db=db,
            current_user=current_user
        )
    )

    if document_ids:

        allowed_document_ids = [
            document_id
            for document_id in document_ids
            if document_id in accessible_document_ids
        ]

        if not allowed_document_ids:
            return []

        document_filter_ids = allowed_document_ids

    else:

        document_filter_ids = accessible_document_ids

        if not document_filter_ids:
            return []

    query_builder = (
        db.query(DocumentChunk)
        .join(
            Document,
            Document.id == DocumentChunk.document_id
        )
        .filter(
            DocumentChunk.document_id.in_(
                document_filter_ids
            ),
            DocumentChunk.embedding.is_not(None)
        )
    )

    results = (
        query_builder
        .order_by(
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(limit)
        .all()
    )

    return results


# =========================================================
# 2. KEYWORD SEARCH
# =========================================================

def keyword_search(
    db: Session,
    query: str,
    current_user,
    limit: int = 20,
    document_ids=None
):
    """
    PostgreSQL keyword search restricted to documents
    accessible to the current user.
    """

    search_vector = func.to_tsvector(
        "english",
        func.concat(
            Document.filename,
            " ",
            DocumentChunk.content
        )
    )

    search_query = func.plainto_tsquery(
        "english",
        query
    )

    accessible_document_ids = (
        get_accessible_document_ids(
            db=db,
            current_user=current_user
        )
    )

    if document_ids:

        allowed_document_ids = [
            document_id
            for document_id in document_ids
            if document_id in accessible_document_ids
        ]

        if not allowed_document_ids:
            return []

        document_filter_ids = allowed_document_ids

    else:

        document_filter_ids = accessible_document_ids

        if not document_filter_ids:
            return []

    query_builder = (
        db.query(DocumentChunk)
        .join(
            Document,
            Document.id == DocumentChunk.document_id
        )
        .filter(
            DocumentChunk.document_id.in_(
                document_filter_ids
            ),
            search_vector.op("@@")(
                search_query
            )
        )
    )

    results = (
        query_builder
        .order_by(
            func.ts_rank_cd(
                search_vector,
                search_query
            ).desc()
        )
        .limit(limit)
        .all()
    )

    return results


# =========================================================
# 3. EXACT FILENAME SEARCH
# =========================================================

def filename_search(
    db: Session,
    query: str,
    current_user,
    limit: int = 20
):
    """
    Search for documents using an explicit document
    reference.

    Only documents accessible to the current user
    are considered.
    """

    document_ids = resolve_document_ids(
        db=db,
        query=query,
        user_id=current_user.id
    )

    if not document_ids:
        return []

    accessible_document_ids = (
        get_accessible_document_ids(
            db=db,
            current_user=current_user
        )
    )

    allowed_document_ids = [
        document_id
        for document_id in document_ids
        if document_id in accessible_document_ids
    ]

    if not allowed_document_ids:
        return []

    results = (
        db.query(DocumentChunk)
        .join(
            Document,
            Document.id == DocumentChunk.document_id
        )
        .filter(
            DocumentChunk.document_id.in_(
                allowed_document_ids
            )
        )
        .limit(limit)
        .all()
    )

    return results


# =========================================================
# 4. HYBRID SEARCH
# =========================================================

def hybrid_search(
    db: Session,
    query: str,
    current_user,
    limit: int = 20,
    document_ids=None
):
    """
    Combines:

    - filename search
    - keyword search
    - semantic search

    All retrieval is restricted to documents
    accessible to the current user.
    """

    # -----------------------------------------------------
    # Get accessible document IDs
    # -----------------------------------------------------

    accessible_document_ids = (
        get_accessible_document_ids(
            db=db,
            current_user=current_user
        )
    )

    if not accessible_document_ids:
        return []

    # -----------------------------------------------------
    # Explicit document reference in current question
    # -----------------------------------------------------

    detected_document_ids = resolve_document_ids(
        db=db,
        query=query,
        user_id=current_user.id
    )

    # -----------------------------------------------------
    # Validate detected document IDs
    # -----------------------------------------------------

    if detected_document_ids:

        allowed_detected_ids = [
            document_id
            for document_id in detected_document_ids
            if document_id in accessible_document_ids
        ]

        if allowed_detected_ids:

            document_ids = allowed_detected_ids

        else:

            return []

    # -----------------------------------------------------
    # Validate supplied document IDs
    # -----------------------------------------------------

    elif document_ids:

        allowed_document_ids = [
            document_id
            for document_id in document_ids
            if document_id in accessible_document_ids
        ]

        if not allowed_document_ids:
            return []

        document_ids = allowed_document_ids

    # -----------------------------------------------------
    # Filename search
    # -----------------------------------------------------

    if document_ids:

        filename_results = (
            db.query(DocumentChunk)
            .join(
                Document,
                Document.id == DocumentChunk.document_id
            )
            .filter(
                DocumentChunk.document_id.in_(
                    document_ids
                )
            )
            .limit(limit)
            .all()
        )

    else:

        filename_results = filename_search(
            db=db,
            query=query,
            current_user=current_user,
            limit=limit
        )

    # -----------------------------------------------------
    # Semantic search
    # -----------------------------------------------------

    semantic_results = semantic_search(
        db=db,
        query=query,
        current_user=current_user,
        limit=limit,
        document_ids=document_ids
    )

    # -----------------------------------------------------
    # Keyword search
    # -----------------------------------------------------

    keyword_results = keyword_search(
        db=db,
        query=query,
        current_user=current_user,
        limit=limit,
        document_ids=document_ids
    )

    # -----------------------------------------------------
    # Combine + remove duplicates
    # -----------------------------------------------------

    combined_results = []

    seen_ids = set()

    for result in (
        filename_results
        + keyword_results
        + semantic_results
    ):

        result_id = str(result.id)

        if result_id not in seen_ids:

            seen_ids.add(result_id)

            combined_results.append(result)

    return combined_results
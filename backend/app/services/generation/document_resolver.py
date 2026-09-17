import re

from sqlalchemy.orm import Session

from app.models.document import Document


def extract_document_reference(query: str) -> str | None:
    """
    Extract a possible document reference from the user's query.

    Example:

    "What are the main topics in 22AD601-LM-4.5?"

    returns:

    "22AD601-LM-4.5"
    """

    # Match identifiers containing letters/numbers
    # with hyphens, underscores or dots.
    pattern = r"\b[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)+\b"

    matches = re.findall(pattern, query)

    if not matches:
        return None

    # Prefer the longest match because document names
    # usually contain more information.
    matches.sort(key=len, reverse=True)

    return matches[0]


def resolve_document_ids(
    db: Session,
    query: str,
    user_id
):
    """
    Find documents belonging to the current user
    based on a document reference in the query.

    Returns:
        list of document IDs
    """

    reference = extract_document_reference(query)

    if not reference:
        return []

    documents = (
        db.query(Document)
        .filter(
            Document.user_id == user_id,
            Document.filename.ilike(
                f"%{reference}%"
            )
        )
        .all()
    )

    return [
        document.id
        for document in documents
    ]
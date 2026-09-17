import re

from sqlalchemy.orm import Session

from app.models.document import Document


def extract_document_reference(
    query: str
) -> str | None:
    """
    Extract a document reference from a query.

    Example:
    What are the main topics in 22AD601-LM-4.5?

    Returns:
    22AD601-LM-4.5
    """

    pattern = r"\b[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)+\b"

    matches = re.findall(
        pattern,
        query
    )

    if not matches:
        return None

    matches.sort(
        key=len,
        reverse=True
    )

    return matches[0]


def resolve_document_ids(
    db: Session,
    query: str,
    user_id
):
    """
    Resolve document IDs using the current query.
    """

    reference = extract_document_reference(
        query
    )

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


def resolve_document_from_history(
    db: Session,
    messages: list,
    user_id
):
    """
    Look through previous conversation messages
    and find the most recently referenced document.
    """

    for message in reversed(messages):

        reference = extract_document_reference(
            message.content
        )

        if not reference:
            continue

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

        if documents:
            return [
                document.id
                for document in documents
            ]

    return []
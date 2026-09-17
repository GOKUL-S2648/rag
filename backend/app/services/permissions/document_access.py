from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.document import Document
from app.models.user import User


def get_accessible_documents(
    db: Session,
    current_user: User
):
    """
    Return all documents accessible to the current user.

    Access rules:

    ADMIN:
        - Own documents
        - ORGANIZATION documents

    MANAGER:
        - Own documents
        - TEAM documents
        - ORGANIZATION documents

    EMPLOYEE:
        - Own documents
        - TEAM documents
        - ORGANIZATION documents
    """

    role = (
        current_user.role or "EMPLOYEE"
    ).upper()

    if role == "ADMIN":

        return (
            db.query(Document)
            .filter(
                or_(
                    Document.user_id == current_user.id,
                    Document.visibility == "ORGANIZATION"
                )
            )
            .all()
        )

    if role in ["MANAGER", "EMPLOYEE"]:

        return (
            db.query(Document)
            .filter(
                or_(
                    Document.user_id == current_user.id,
                    Document.visibility.in_([
                        "TEAM",
                        "ORGANIZATION"
                    ])
                )
            )
            .all()
        )

    return (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id
        )
        .all()
    )


def get_accessible_document_ids(
    db: Session,
    current_user: User
):
    """
    Return IDs of documents accessible
    to the current user.
    """

    documents = get_accessible_documents(
        db=db,
        current_user=current_user
    )

    return [
        document.id
        for document in documents
    ]


def can_access_document(
    db: Session,
    document_id,
    current_user: User
):
    """
    Check whether the current user can access
    a specific document.
    """

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if not document:
        return False

    role = (
        current_user.role or "EMPLOYEE"
    ).upper()

    # Owner always has access
    if document.user_id == current_user.id:
        return True

    # Organization documents
    if document.visibility == "ORGANIZATION":
        return True

    # Team documents
    if (
        document.visibility == "TEAM"
        and role in ["MANAGER", "EMPLOYEE"]
    ):
        return True

    return False
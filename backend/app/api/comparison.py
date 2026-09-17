from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles

from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.user import User

from app.services.permissions.document_access import (
    can_access_document
)

from app.services.comparison.document_comparator import (
    compare_documents
)


router = APIRouter(
    prefix="/api/comparison",
    tags=["Document Comparison"]
)


class ComparisonRequest(BaseModel):
    document_a_id: str
    document_b_id: str


# ============================================================
# COMPARE DOCUMENTS
# ============================================================

@router.post("")
def compare_uploaded_documents(
    request: ComparisonRequest,
    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        )
    )
):

    # ========================================================
    # 1. GET DOCUMENT A
    # ========================================================

    document_a = (
        db.query(Document)
        .filter(
            Document.id == request.document_a_id
        )
        .first()
    )

    if not document_a:

        raise HTTPException(
            status_code=404,
            detail="Document A not found"
        )

    # Check permission
    if not can_access_document(
        db=db,
        document_id=document_a.id,
        current_user=current_user
    ):

        raise HTTPException(
            status_code=403,
            detail="You do not have access to Document A"
        )


    # ========================================================
    # 2. GET DOCUMENT B
    # ========================================================

    document_b = (
        db.query(Document)
        .filter(
            Document.id == request.document_b_id
        )
        .first()
    )

    if not document_b:

        raise HTTPException(
            status_code=404,
            detail="Document B not found"
        )

    # Check permission
    if not can_access_document(
        db=db,
        document_id=document_b.id,
        current_user=current_user
    ):

        raise HTTPException(
            status_code=403,
            detail="You do not have access to Document B"
        )


    # ========================================================
    # 3. PREVENT SAME DOCUMENT COMPARISON
    # ========================================================

    if document_a.id == document_b.id:

        raise HTTPException(
            status_code=400,
            detail="Please select two different documents"
        )


    # ========================================================
    # 4. GET DOCUMENT A CHUNKS
    # ========================================================

    chunks_a = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_a.id
        )
        .order_by(
            DocumentChunk.chunk_index
        )
        .all()
    )


    # ========================================================
    # 5. GET DOCUMENT B CHUNKS
    # ========================================================

    chunks_b = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_b.id
        )
        .order_by(
            DocumentChunk.chunk_index
        )
        .all()
    )


    if not chunks_a:

        raise HTTPException(
            status_code=400,
            detail="Document A contains no readable content"
        )


    if not chunks_b:

        raise HTTPException(
            status_code=400,
            detail="Document B contains no readable content"
        )


    # ========================================================
    # 6. BUILD DOCUMENT TEXT
    # ========================================================

    document_a_text = "\n\n".join(
        chunk.content
        for chunk in chunks_a
    )


    document_b_text = "\n\n".join(
        chunk.content
        for chunk in chunks_b
    )


    # ========================================================
    # 7. COMPARE DOCUMENTS
    # ========================================================

    try:

        comparison = compare_documents(
            document_a_text=document_a_text,
            document_b_text=document_b_text,
            document_a_name=document_a.filename,
            document_b_name=document_b.filename
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document comparison failed: {str(e)}"
            )
        )


    # ========================================================
    # 8. RETURN RESULT
    # ========================================================

    return {

        "success": True,

        "document_a": {
            "id": str(document_a.id),
            "filename": document_a.filename,
            "page_count": (
                document_a.page_count or 0
            ),
            "chunk_count": (
                document_a.chunk_count or 0
            )
        },

        "document_b": {
            "id": str(document_b.id),
            "filename": document_b.filename,
            "page_count": (
                document_b.page_count or 0
            ),
            "chunk_count": (
                document_b.chunk_count or 0
            )
        },

        "comparison": comparison
    }
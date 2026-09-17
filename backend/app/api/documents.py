import os
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles

from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.user import User

from app.services.ingestion.extractor import extract_text
from app.services.ingestion.chunker import create_chunks

from app.services.embeddings.process_embeddings import (
    process_document_embeddings
)

from app.services.intelligence.document_intelligence import (
    analyze_document
)

from app.services.intelligence.document_summarizer import (
    summarize_document
)

from app.services.permissions.document_access import (
    get_accessible_documents,
    can_access_document
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


UPLOAD_DIR = "uploads"


ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}


# ============================================================
# GET ALL ACCESSIBLE DOCUMENTS
# ============================================================

@router.get("")
def get_all_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        )
    )
):

    documents = get_accessible_documents(
        db=db,
        current_user=current_user
    )

    documents.sort(
        key=lambda document: document.created_at,
        reverse=True
    )

    return {
        "success": True,
        "documents": [
            {
                "id": str(document.id),
                "filename": document.filename,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "status": document.status,
                "page_count": document.page_count or 0,
                "chunk_count": document.chunk_count or 0,
                "visibility": document.visibility,
                "owner_id": str(document.user_id),
                "is_owner": (
                    document.user_id == current_user.id
                ),
                "created_at": document.created_at,
                "analysis": document.analysis,
                "summary": document.summary
            }
            for document in documents
        ]
    }


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        )
    )
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )


    extension = (
        file.filename
        .split(".")[-1]
        .lower()
    )


    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF, DOCX and TXT files "
                "are supported"
            )
        )


    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True
    )


    file_id = str(uuid.uuid4())


    safe_filename = (
        f"{file_id}.{extension}"
    )


    file_path = os.path.join(
        UPLOAD_DIR,
        safe_filename
    )


    content = await file.read()


    if not content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )


    with open(
        file_path,
        "wb"
    ) as buffer:

        buffer.write(content)


    file_size = len(content)


    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_type=extension,
        file_size=file_size,
        storage_url=file_path,
        status="PROCESSING",
        visibility="PRIVATE"
    )


    db.add(document)
    db.commit()
    db.refresh(document)


    try:

        pages = extract_text(
            file_path,
            extension
        )


        chunks = create_chunks(
            pages
        )


        if not chunks:

            document.status = "FAILED"

            db.commit()

            raise HTTPException(
                status_code=400,
                detail=(
                    "No readable text was found "
                    "in the document"
                )
            )


        for chunk in chunks:

            db_chunk = DocumentChunk(
                document_id=document.id,
                content=chunk["content"],
                page_number=chunk["page_number"],
                section=chunk["section"],
                chunk_index=chunk["chunk_index"],
                metadata_json={}
            )

            db.add(db_chunk)


        db.commit()


        document.status = "EMBEDDING"

        document.page_count = len(pages)

        document.chunk_count = len(chunks)


        db.commit()


        processed_embeddings = (
            process_document_embeddings(
                db=db,
                document_id=document.id
            )
        )


        document.status = "READY"


        db.commit()

        db.refresh(document)


        return {
            "success": True,
            "message": (
                "Document uploaded and "
                "processed successfully"
            ),
            "document": {
                "id": str(document.id),
                "filename": document.filename,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "status": document.status,
                "visibility": document.visibility,
                "page_count": document.page_count,
                "chunk_count": document.chunk_count,
                "embeddings_generated": (
                    processed_embeddings
                )
            }
        }


    except HTTPException:

        raise


    except Exception as e:

        db.rollback()

        document.status = "FAILED"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=(
                "Document processing failed: "
                f"{str(e)}"
            )
        )


# ============================================================
# ANALYZE DOCUMENT
# ============================================================

@router.post("/{document_id}/analyze")
def analyze_uploaded_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        )
    )
):

    if not can_access_document(
        db=db,
        document_id=document_id,
        current_user=current_user
    ):

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )


    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )


    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document.id
        )
        .order_by(
            DocumentChunk.chunk_index
        )
        .all()
    )


    if not chunks:

        raise HTTPException(
            status_code=400,
            detail="No document chunks found"
        )


    document_text = "\n\n".join(
        chunk.content
        for chunk in chunks
    )


    if not document_text.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Document contains no readable text"
            )
        )


    try:

        analysis = analyze_document(
            document_text=document_text,
            filename=document.filename,
            page_count=document.page_count or 0,
            chunk_count=(
                document.chunk_count
                or len(chunks)
            )
        )


        document.analysis = analysis


        db.commit()

        db.refresh(document)


        return {
            "success": True,
            "document_id": str(document.id),
            "filename": document.filename,
            "analysis": analysis
        }


    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Document analysis failed: "
                f"{str(e)}"
            )
        )


# ============================================================
# SUMMARIZE DOCUMENT
# ============================================================

@router.post("/{document_id}/summarize")
def summarize_uploaded_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        )
    )
):

    if not can_access_document(
        db=db,
        document_id=document_id,
        current_user=current_user
    ):

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )


    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )


    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document.id
        )
        .order_by(
            DocumentChunk.chunk_index
        )
        .all()
    )


    if not chunks:

        raise HTTPException(
            status_code=400,
            detail="No document chunks found"
        )


    document_text = "\n\n".join(
        chunk.content
        for chunk in chunks
    )


    if not document_text.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Document contains no readable text"
            )
        )


    try:

        summary = summarize_document(
            document_text=document_text,
            filename=document.filename
        )


        if not summary:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to generate "
                    "document summary"
                )
            )


        document.summary = summary


        db.commit()

        db.refresh(document)


        return {
            "success": True,
            "document_id": str(document.id),
            "filename": document.filename,
            "summary": summary,
            "page_count": (
                document.page_count or 0
            ),
            "chunk_count": (
                document.chunk_count
                or len(chunks)
            )
        }


    except HTTPException:

        raise


    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Document summarization failed: "
                f"{str(e)}"
            )
        )


# ============================================================
# GET DOCUMENT INTELLIGENCE
# ============================================================

@router.get("/{document_id}/analysis")
def get_document_analysis(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        )
    )
):

    if not can_access_document(
        db=db,
        document_id=document_id,
        current_user=current_user
    ):

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )


    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )


    return {
        "success": True,
        "document_id": str(document.id),
        "filename": document.filename,
        "visibility": document.visibility,
        "analysis": document.analysis
    }


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        )
    )
):

    # Only the owner can delete a document.
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
        .first()
    )


    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )


    try:

        if (
            document.storage_url
            and os.path.exists(
                document.storage_url
            )
        ):

            os.remove(
                document.storage_url
            )


        db.delete(document)

        db.commit()


        return {
            "success": True,
            "message": (
                "Document deleted successfully"
            )
        }


    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete document: "
                f"{str(e)}"
            )
        )
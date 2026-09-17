from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles

from app.models.user import User

from app.services.retrieval.semantic_search import (
    semantic_search
)


router = APIRouter(
    prefix="/api/search",
    tags=["Search"]
)


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("")
def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        )
    )
):

    query = request.query.strip()

    if not query:
        return {
            "success": True,
            "query": request.query,
            "results": []
        }


    # --------------------------------------------------
    # PERMISSION-AWARE SEMANTIC SEARCH
    # --------------------------------------------------

    results = semantic_search(
        db=db,
        query=query,
        current_user=current_user,
        limit=request.limit
    )


    return {
        "success": True,
        "query": query,
        "results": [
            {
                "chunk_id": str(result.id),

                "document_id": str(
                    result.document_id
                ),

                "document_name":
                    result.document.filename,

                "content":
                    result.content,

                "page_number":
                    result.page_number,

                "chunk_index":
                    result.chunk_index

            }
            for result in results
        ]
    }
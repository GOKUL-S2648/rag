from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles

from app.models.message import Message
from app.models.conversation import Conversation
from app.models.user import User

from app.services.retrieval.hybrid_search import hybrid_search

from app.services.retrieval.document_resolver import (
    resolve_document_ids,
    resolve_document_from_history
)

from app.services.reranking.reranker import (
    rerank_results
)

from app.services.generation.rag_generator import (
    generate_rag_answer
)

from app.services.citations.formatter import (
    format_citations
)


router = APIRouter(
    prefix="/api/ask",
    tags=["RAG"]
)


class AskRequest(BaseModel):
    question: str
    conversation_id: str
    limit: int = 5


# ============================================================
# GET CONVERSATION HISTORY
# ============================================================

def get_conversation_history(
    db: Session,
    conversation_id,
    limit: int = 20
):
    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    messages.reverse()

    return messages


# ============================================================
# BUILD CONVERSATION HISTORY
# ============================================================

def build_conversation_history(
    messages: list
):
    history_parts = []

    for message in messages:

        history_parts.append(
            f"{message.role.upper()}: {message.content}"
        )

    return "\n".join(history_parts)


# ============================================================
# ASK QUESTION
# ============================================================

@router.post("")
def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        )
    )
):

    question = request.question.strip()


    # ========================================================
    # VALIDATE QUESTION
    # ========================================================

    if not question:

        return {
            "success": False,
            "answer": "Question cannot be empty.",
            "sources": []
        }


    # ========================================================
    # VERIFY CONVERSATION OWNERSHIP
    # ========================================================

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        )
        .first()
    )


    if not conversation:

        return {
            "success": False,
            "message": "Conversation not found"
        }


    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=question
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)


    # ========================================================
    # GET CONVERSATION HISTORY
    # ========================================================

    conversation_messages = get_conversation_history(
        db=db,
        conversation_id=conversation.id,
        limit=20
    )


    conversation_history = build_conversation_history(
        conversation_messages
    )


    # ========================================================
    # RESOLVE DOCUMENT FROM CURRENT QUESTION
    # ========================================================

    document_ids = resolve_document_ids(
        db=db,
        query=question,
        user_id=current_user.id
    )


    # ========================================================
    # RESOLVE DOCUMENT FROM CONVERSATION HISTORY
    # ========================================================

    if not document_ids:

        document_ids = resolve_document_from_history(
            db=db,
            messages=conversation_messages,
            user_id=current_user.id
        )


    # ========================================================
    # HYBRID SEARCH
    # ========================================================

    results = hybrid_search(
        db=db,
        query=question,
        current_user=current_user,
        limit=10,
        document_ids=document_ids
    )


    # ========================================================
    # RERANK RESULTS
    # ========================================================

    results = rerank_results(
        query=question,
        results=results,
        top_k=request.limit
    )


    # ========================================================
    # BUILD DOCUMENT CONTEXT
    # ========================================================

    context_parts = []

    for result in results:

        context_parts.append(
            f"""
Document ID: {result.document_id}
Page: {result.page_number}
Chunk: {result.chunk_index}

Content:
{result.content}
"""
        )


    document_context = "\n".join(
        context_parts
    )


    # ========================================================
    # COMBINE HISTORY + DOCUMENT CONTEXT
    # ========================================================

    if conversation_history:

        context = f"""
CONVERSATION HISTORY
==================================================

{conversation_history}

==================================================

DOCUMENT CONTEXT
==================================================

{document_context}

==================================================
"""

    else:

        context = f"""
DOCUMENT CONTEXT
==================================================

{document_context}

==================================================
"""


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    if not results:

        answer = (
            "I could not find this information "
            "in the provided documents."
        )

    else:

        answer = generate_rag_answer(
            question=question,
            context=context
        )


    # ========================================================
    # SAVE ASSISTANT MESSAGE
    # ========================================================

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    )

    db.add(assistant_message)
    db.commit()


    # ========================================================
    # FORMAT CITATIONS
    # ========================================================

    citations = format_citations(
        results
    )


    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "success": True,
        "conversation_id": str(
            conversation.id
        ),
        "question": question,
        "answer": answer,
        "sources": citations
    }
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User


router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"]
)


# =========================================================
# 1. CREATE NEW CONVERSATION
# =========================================================

@router.post("")
def create_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversation = Conversation(
        user_id=current_user.id,
        title="New Conversation"
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "success": True,
        "conversation_id": str(conversation.id),
        "title": conversation.title
    }


# =========================================================
# 2. GET ALL USER CONVERSATIONS
# =========================================================

@router.get("")
def get_all_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == current_user.id
        )
        .order_by(
            Conversation.created_at.desc()
        )
        .all()
    )

    return {
        "success": True,
        "conversations": [
            {
                "id": str(conversation.id),
                "title": conversation.title,
                "created_at": conversation.created_at
            }
            for conversation in conversations
        ]
    }


# =========================================================
# 3. GET SINGLE CONVERSATION WITH MESSAGES
# =========================================================

@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        .first()
    )

    if not conversation:
        return {
            "success": False,
            "message": "Conversation not found"
        }

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation.id
        )
        .order_by(
            Message.created_at
        )
        .all()
    )

    return {
        "success": True,
        "conversation_id": str(conversation.id),
        "title": conversation.title,
        "messages": [
            {
                "id": str(message.id),
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at
            }
            for message in messages
        ]
    }
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    DateTime,
    Text,
    ForeignKey,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    visibility = Column(
    Text,
    nullable=False,
    default="PRIVATE"
    )

    filename = Column(
        Text,
        nullable=False
    )

    file_type = Column(
        String(50),
        nullable=True
    )

    file_size = Column(
        BigInteger,
        nullable=True
    )

    storage_url = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(30),
        default="PROCESSING"
    )

    page_count = Column(
        Integer,
        default=0
    )

    chunk_count = Column(
        Integer,
        default=0
    )
    analysis = Column(
        JSON,
        nullable=True
    )
    summary = Column(
    Text,
    nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )   
    chunks = relationship(
    "DocumentChunk",
    back_populates="document",
    cascade="all, delete-orphan"
)
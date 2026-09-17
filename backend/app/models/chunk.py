from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "documents.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # Relationship to the parent document
    document = relationship(
        "Document",
        back_populates="chunks"
    )

    content = Column(
        Text,
        nullable=False
    )

    page_number = Column(
        Integer,
        nullable=True
    )

    section = Column(
        Text,
        nullable=True
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )

    metadata_json = Column(
        "metadata",
        JSON,
        default=dict
    )

    embedding = Column(
        Vector(384),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
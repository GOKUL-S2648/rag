import uuid

from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        Text,
        nullable=False
    )

    email = Column(
        Text,
        unique=True,
        nullable=False
    )

    password_hash = Column(
        Text,
        nullable=False
    )

    role = Column(
        Text,
        nullable=False,
        default="EMPLOYEE"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector

import uuid


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    filename: Mapped[str]
    bucket: Mapped[str]
    object_key: Mapped[str]


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id")
    )

    page: Mapped[int]
    chunk_index: Mapped[int]
    content: Mapped[str] = mapped_column(Text)

    embedding: Mapped[list[float]] = mapped_column(
        Vector(768)
    )



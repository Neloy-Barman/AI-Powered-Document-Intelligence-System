import uuid
from typing import Any

from sqlalchemy.orm import Session

from backend.app.db.models.document import Document
from backend.app.db.models.image_document import ImageDocument
from backend.app.db.models.tabular_document import TabularDocument


def create_document_record(
    db: Session,
    file_name: str,
    file_type: str,
    storage_path: str,
    file_size_bytes: int,
    status: str = "uploaded",
    reason: str | None = None,
) -> Document:
    """Create and flush a document row, then return it."""
    document = Document(
        file_name=file_name,
        file_type=file_type,
        status=status,
        storage_path=storage_path,
        file_size_bytes=file_size_bytes,
        reason=reason,
    )
    db.add(document)
    db.flush()
    return document


def create_image_document_record(
    db: Session,
    document_id: Any,
    file_type: str,
    text_content: str,
    qdrant_point_id: str,
    bm25_entry_id: str,
) -> ImageDocument:
    """Create and add an image_documents row."""
    image_document = ImageDocument(
        document_id=document_id,
        file_type=file_type,
        text_content=text_content,
        qdrant_point_id=qdrant_point_id,
        bm25_entry_id=uuid.UUID(bm25_entry_id),
    )
    db.add(image_document)
    return image_document


def create_tabular_chunk_records(
    db: Session,
    document_id: Any,
    file_type: str,
    chunks: list[dict[str, Any]],
    point_ids: list[str],
) -> None:
    """Create one tabular_documents row per chunk."""
    for chunk, point_id in zip(chunks, point_ids):
        db.add(
            TabularDocument(
                document_id=document_id,
                file_type=file_type,
                sheet_name=chunk.get("sheet_name"),
                row_count=chunk["row_count"],
                column_count=chunk["column_count"],
                columns=chunk["columns"],
                chunk_index=chunk["chunk_index"],
                chunk_count=chunk["chunk_count"],
                chunk_range=chunk["chunk_range"],
                text_content=chunk["text_content"],
                qdrant_point_id=point_id,
                bm25_entry_id=uuid.UUID(chunk.get("id") or chunk.get("bm25_entry_id")),
            )
        )

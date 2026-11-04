from fastapi import APIRouter

from backend.app.db.models.document import Document
from backend.app.db.session import SessionLocal

router = APIRouter()


@router.get("/processing-history")
def get_processing_history() -> dict:
    """Return previously processed documents from the database."""
    with SessionLocal() as db:
        documents = (
            db.query(Document)
            .order_by(Document.created_at.desc())
            .all()
        )

    return {
        "status": "success",
        "documents": [
            {
                "id": str(document.id),
                "file_name": document.file_name,
                "file_type": document.file_type,
                "status": document.status,
                "file_size_bytes": document.file_size_bytes,
                "reason": document.reason,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
            }
            for document in documents
        ],
    }

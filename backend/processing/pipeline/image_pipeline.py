import logging
import uuid
from pathlib import Path

from backend.app.core.config import BM25_CORPUS_PATH
from backend.app.core.logging import configure_logging
from backend.app.db.document_repository import create_document_record, create_image_document_record
from backend.app.db.init_db import ensure_tables
from backend.app.db.session import SessionLocal
from backend.app.search.langchain_hybrid_search import create_langchain_hybrid_search
from backend.app.search.semantic_search import create_qdrant_service
from backend.processing.chunking.image_chunker import chunk_image
from backend.processing.parsers.image_parser import parse_image

configure_logging()
logger = logging.getLogger(__name__)


def process_image(file_path: str | Path) -> dict:
    """Parse, chunk, index, and store one image document."""
    source_path = Path(file_path)
    parsed = parse_image(source_path)

    if parsed.get("status") == "failed":
        ensure_tables()
        with SessionLocal() as db:
            create_document_record(
                db=db,
                file_name=source_path.name,
                file_type=source_path.suffix.lower(),
                storage_path=str(source_path),
                file_size_bytes=source_path.stat().st_size if source_path.exists() else 0,
                status="failed",
                reason=parsed.get("error_message"),
            )
            db.commit()
        logger.error("Image parsing failed for %s: %s", source_path, parsed.get("error_message"))
        return {
            "status": "failed",
            "file_name": source_path.name,
            "file_type": source_path.suffix.lower(),
            "file_size_bytes": source_path.stat().st_size if source_path.exists() else 0,
            "reason": parsed.get("error_message"),
        }

    chunks = chunk_image(parsed)

    for chunk in chunks:
        chunk.setdefault("id", str(uuid.uuid4()))

    qdrant_service = create_qdrant_service()
    upsert_result = qdrant_service.upsert_chunks(chunks)

    hybrid_search = create_langchain_hybrid_search(service=qdrant_service)
    hybrid_search.add_documents(chunks)

    ensure_tables()

    with SessionLocal() as db:
        document = create_document_record(
            db=db,
            file_name=source_path.name,
            file_type=source_path.suffix.lower(),
            storage_path=str(source_path),
            file_size_bytes=source_path.stat().st_size,
            status="completed",
        )
        create_image_document_record(
            db=db,
            document_id=document.id,
            file_type=source_path.suffix.lower(),
            text_content=chunks[0]["text_content"],
            qdrant_point_id=upsert_result["point_ids"][0],
            bm25_entry_id=chunks[0]["id"],
        )
        db.commit()

    return {
        "status": "success",
        "file_name": source_path.name,
        "file_type": source_path.suffix.lower(),
        "file_size_bytes": source_path.stat().st_size,
        "chunks_upserted": upsert_result["upserted"],
        "chunk_point_ids": upsert_result["point_ids"],
        "bm25_corpus_entries": len(hybrid_search.keyword_retriever._documents),
        "bm25_entry_ids": [chunk["id"] for chunk in chunks],
        "text_content": parsed.get("content", ""),
    }

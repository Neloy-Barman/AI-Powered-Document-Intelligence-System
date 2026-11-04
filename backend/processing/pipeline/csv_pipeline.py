import logging
import uuid
from pathlib import Path

from backend.app.core.config import BM25_CORPUS_PATH
from backend.app.core.logging import configure_logging
from backend.app.db.document_repository import (
    create_document_record,
    create_tabular_chunk_records,
)
from backend.app.db.init_db import ensure_tables
from backend.app.db.session import SessionLocal
from backend.app.search.langchain_hybrid_search import create_langchain_hybrid_search
from backend.app.search.semantic_search import create_qdrant_service
from backend.processing.chunking.csv_chunker import chunk_csv
from backend.processing.parsers.csv_parser import parse_csv

configure_logging()
logger = logging.getLogger(__name__)


def process_csv(file_path: str | Path) -> dict:
    """Parse, chunk, index, and store one CSV document."""
    source_path = Path(file_path)
    parsed = parse_csv(source_path)

    if parsed.get("status") == "failed":
        logger.error(
            f"CSV parsing failed for {source_path}: {parsed.get('error_message')}"
        )
        ensure_tables()
        with SessionLocal() as db:
            create_document_record(
                db=db,
                file_name=source_path.name,
                file_type=source_path.suffix.lower(),
                storage_path=str(source_path),
                file_size_bytes=(
                    source_path.stat().st_size if source_path.exists() else 0
                ),
                status="failed",
                reason=parsed.get("error_message"),
            )
            db.commit()
            logger.info("Stored failed document record for %s", source_path.name)
        return {
            "status": "failed",
            "file_name": source_path.name,
            "file_type": source_path.suffix.lower(),
            "file_size_bytes": (
                source_path.stat().st_size if source_path.exists() else 0
            ),
            "reason": parsed.get("error_message"),
        }

    logger.info(
        f"Parsed CSV: {source_path.name} ({parsed.get('rows')} rows, {parsed.get('columns')} columns)"
    )

    chunks = chunk_csv(parsed)
    logger.info(f"Created {len(chunks)} chunk(s) for {source_path.name}")

    for chunk in chunks:
        chunk.setdefault("id", str(uuid.uuid4()))

    qdrant_service = create_qdrant_service()
    upsert_result = qdrant_service.upsert_chunks(chunks)
    logger.info(
        f"Upserted {upsert_result['upserted']} chunk(s) to Qdrant for {source_path.name}"
    )

    hybrid_search = create_langchain_hybrid_search(service=qdrant_service)
    hybrid_search.add_documents(chunks)
    logger.info(
        f"Updated BM25 corpus for {source_path.name}; total entries: {len(hybrid_search.keyword_retriever._documents)}"
    )

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
        create_tabular_chunk_records(
            db=db,
            document_id=document.id,
            file_type=source_path.suffix.lower(),
            chunks=chunks,
            point_ids=upsert_result["point_ids"],
        )

        db.commit()
        logger.info(f"Stored {len(chunks)} database row(s) for {source_path.name}")

    return {
        "status": "success",
        "file_name": source_path.name,
        "file_type": "csv",
        "file_size_bytes": source_path.stat().st_size,
        "chunks_upserted": upsert_result["upserted"],
        "chunk_point_ids": upsert_result["point_ids"],
        "bm25_corpus_entries": len(hybrid_search.keyword_retriever._documents),
        "bm25_entry_ids": [chunk["id"] for chunk in chunks],
        "text_content": parsed,
    }

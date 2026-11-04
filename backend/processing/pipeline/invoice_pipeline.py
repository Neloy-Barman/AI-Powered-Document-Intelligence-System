import json
import logging
import uuid
from pathlib import Path

from backend.app.core.logging import configure_logging
from backend.app.db.document_repository import (
    create_document_record,
    create_invoice_document_record,
)
from backend.app.db.init_db import ensure_tables
from backend.app.db.session import SessionLocal
from backend.app.extraction.extractor import extract_invoice
from backend.app.search.langchain_hybrid_search import create_langchain_hybrid_search
from backend.app.search.semantic_search import create_qdrant_service
from backend.processing.chunking.invoice_chunker import chunk_invoice

configure_logging()
logger = logging.getLogger(__name__)

REVIEW_REASON_LABELS = (
    ("missing_fields", "Missing fields"),
    ("numeric_issues", "Numeric issues"),
    ("consistency_issues", "Consistency issues"),
    ("duplicate_issues", "Duplicate issues"),
)


def _build_review_reason(validation: dict) -> str:
    """Summarize the validation issues that require manual review."""
    reasons: list[str] = []

    for key, label in REVIEW_REASON_LABELS:
        _, issues = validation.get(key, (False, []))
        if issues:
            reasons.append(f"{label}: {json.dumps(issues, ensure_ascii=False)}")

    return "; ".join(reasons) or "Manual review required."


def process_invoice(file_path: str | Path, page_no: int | None = None) -> dict:
    """Extract, chunk, index, and store one invoice."""
    source_path = Path(file_path)
    file_type = source_path.suffix.lower()
    file_size_bytes = source_path.stat().st_size if source_path.exists() else 0

    extraction_result = extract_invoice(source_path)

    if extraction_result.get("status") == "failed":
        reason = extraction_result.get("error_message")
        logger.error("Invoice extraction failed for %s: %s", source_path, reason)

        ensure_tables()
        with SessionLocal() as db:
            create_document_record(
                db=db,
                file_name=source_path.name,
                file_type=file_type,
                storage_path=str(source_path),
                file_size_bytes=file_size_bytes,
                status="failed",
                reason=reason,
            )
            db.commit()

        return {
            "status": "failed",
            "file_name": source_path.name,
            "file_type": file_type,
            "file_size_bytes": file_size_bytes,
            "reason": reason,
        }

    extraction_status = extraction_result.get("status")
    validation = extraction_result.get("validation", {}) or {}

    if extraction_status == "needs_review":
        reason = _build_review_reason(validation)
        logger.warning("Invoice needs review for %s: %s", source_path, reason)

        ensure_tables()
        with SessionLocal() as db:
            create_document_record(
                db=db,
                file_name=source_path.name,
                file_type=file_type,
                storage_path=str(source_path),
                file_size_bytes=file_size_bytes,
                status="needs_review",
                reason=reason,
            )
            db.commit()

        return {
            "status": "needs_review",
            "file_name": source_path.name,
            "file_type": file_type,
            "file_size_bytes": file_size_bytes,
            "reason": reason,
        }

    status = "completed"

    chunks = chunk_invoice(extraction_result, page_no=page_no)

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
            file_type=file_type,
            storage_path=str(source_path),
            file_size_bytes=file_size_bytes,
            status=status,
        )
        create_invoice_document_record(
            db=db,
            document_id=document.id,
            file_type=file_type,
            extraction_result=extraction_result,
            page_no=page_no,
            qdrant_point_id=upsert_result["point_ids"][0],
            bm25_entry_id=chunks[0]["id"],
        )
        db.commit()

    logger.info("Stored invoice record for %s", source_path.name)

    invoice = extraction_result.get("invoice", {}) or {}

    return {
        "status": extraction_status or status,
        "file_name": source_path.name,
        "file_type": file_type,
        "file_size_bytes": file_size_bytes,
        "chunks_upserted": upsert_result["upserted"],
        "chunk_point_ids": upsert_result["point_ids"],
        "bm25_corpus_entries": len(hybrid_search.keyword_retriever._documents),
        "bm25_entry_ids": [chunk["id"] for chunk in chunks],
        "text_content": chunks[0]["text_content"],
        "invoice_number": invoice.get("invoice_number"),
        "supplier_name": invoice.get("supplier_name"),
        "total": invoice.get("total"),
        "currency": invoice.get("currency"),
        "validation": validation,
    }

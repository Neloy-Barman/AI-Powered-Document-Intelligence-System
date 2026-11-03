from pathlib import Path
import uuid

from backend.app.extraction.extractor import extract_invoice
from backend.app.services.invoice_extraction_service import set_processing_active
from backend.app.workers.queues import get_redis, get_processing_queue

ACTIVE_KEY = "processing_active"


def process_invoice_job(file_path: str) -> dict:
    """RQ worker entry point: extract structured data from one invoice image."""
    set_processing_active(True)
    try:
        return extract_invoice(file_path)
    finally:
        set_processing_active(False)


def process_document_job(file_path: str) -> dict:
    """Parse, chunk, index, and store one uploaded document."""
    set_processing_active(True)
    try:
        from backend.app.db.init_db import ensure_tables
        from backend.app.db.models.document import Document
        from backend.app.db.models.image_document import ImageDocument
        from backend.app.db.models.tabular_document import TabularDocument
        from backend.app.db.session import SessionLocal
        from backend.processing.file_detector import detect_file_type
        from backend.processing.router import route_file
        from backend.app.search.langchain_hybrid_search import create_langchain_hybrid_search
        from backend.app.search.semantic_search import create_qdrant_service
        from backend.processing.chunking.csv_chunker import chunk_csv
        from backend.processing.chunking.image_chunker import chunk_image
        from backend.processing.chunking.spreadsheet_chunker import chunk_spreadsheet

        parsed = route_file(file_path)
        if parsed.get("status") == "failed":
            return parsed

        file_type = detect_file_type(file_path)
        source_path = Path(file_path)
        file_size = source_path.stat().st_size

        if file_type == "csv":
            chunks = chunk_csv(parsed)
        elif file_type == "spreadsheet":
            chunks = chunk_spreadsheet(parsed)
        elif file_type == "image":
            chunks = chunk_image(parsed)
        else:
            return {
                "status": "success",
                "file_name": source_path.name,
                "file_type": file_type,
                "parsed": parsed,
            }

        for chunk in chunks:
            chunk.setdefault("bm25_entry_id", None)
            if chunk.get("bm25_entry_id") is None:
                import uuid

                chunk["bm25_entry_id"] = str(uuid.uuid4())

        qdrant_service = create_qdrant_service()
        upsert_result = qdrant_service.upsert_chunks(chunks)
        point_ids = upsert_result["point_ids"]

        hybrid_search = create_langchain_hybrid_search(service=qdrant_service)
        hybrid_search.add_documents(chunks)

        ensure_tables()

        with SessionLocal() as db:
            document = Document(
                file_name=source_path.name,
                file_type=file_type or source_path.suffix.lower(),
                status="completed",
                storage_path=str(source_path),
                file_size_bytes=file_size,
            )
            db.add(document)
            db.flush()

            if file_type == "image":
                chunk = chunks[0]
                db.add(
                    ImageDocument(
                        document_id=document.id,
                        file_type=document.file_type,
                        text_content=chunk["text_content"],
                        qdrant_point_id=point_ids[0],
                        bm25_entry_id=uuid.UUID(chunk["bm25_entry_id"]),
                    )
                )
            else:
                for chunk, point_id in zip(chunks, point_ids):
                    db.add(
                        TabularDocument(
                            document_id=document.id,
                            file_type=document.file_type,
                            sheet_name=chunk.get("sheet_name"),
                            row_count=chunk["row_count"],
                            column_count=chunk["column_count"],
                            columns=chunk["columns"],
                            chunk_index=chunk["chunk_index"],
                            chunk_count=chunk["chunk_count"],
                            chunk_range=chunk["chunk_range"],
                            text_content=chunk["text_content"],
                            qdrant_point_id=point_id,
                            bm25_entry_id=uuid.UUID(chunk["bm25_entry_id"]),
                        )
                    )

            db.commit()

        return {
            "status": "success",
            "file_name": source_path.name,
            "file_type": file_type,
            "chunks_upserted": upsert_result["upserted"],
            "bm25_corpus_entries": len(hybrid_search.keyword_retriever._documents),
            "parsed": parsed,
        }
    finally:
        set_processing_active(False)

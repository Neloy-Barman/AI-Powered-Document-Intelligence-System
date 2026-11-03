from pathlib import Path

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
    """Parse, chunk, and index one uploaded document."""
    set_processing_active(True)
    try:
        from backend.processing.file_detector import detect_file_type
        from backend.processing.router import route_file
        from backend.app.search.langchain_hybrid_search import create_langchain_hybrid_search
        from backend.app.search.semantic_search import create_qdrant_service

        parsed = route_file(file_path)
        if parsed.get("status") == "failed":
            return parsed

        file_type = detect_file_type(file_path)

        if file_type == "csv":
            from backend.processing.chunking.csv_chunker import chunk_csv

            chunks = chunk_csv(parsed)
        elif file_type == "spreadsheet":
            from backend.processing.chunking.spreadsheet_chunker import chunk_spreadsheet

            chunks = chunk_spreadsheet(parsed)
        elif file_type == "image":
            from backend.processing.chunking.image_chunker import chunk_image

            chunks = chunk_image(parsed)
        else:
            return {
                "status": "success",
                "file_name": Path(file_path).name,
                "file_type": file_type,
                "parsed": parsed,
            }

        qdrant_service = create_qdrant_service()
        upsert_result = qdrant_service.upsert_chunks(chunks)

        hybrid_search = create_langchain_hybrid_search(service=qdrant_service)
        hybrid_search.add_documents(chunks)

        return {
            "status": "success",
            "file_name": Path(file_path).name,
            "file_type": file_type,
            "chunks_upserted": upsert_result["upserted"],
            "bm25_corpus_entries": len(hybrid_search.keyword_retriever._documents),
            "parsed": parsed,
        }
    finally:
        set_processing_active(False)

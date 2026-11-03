from pathlib import Path

from backend.processing.router import route_file
from backend.app.extraction.extractor import extract_invoice
from backend.app.workers.queues import get_redis, get_processing_queue
from backend.app.services.invoice_extraction_service import set_processing_active

ACTIVE_KEY = "processing_active"


def process_invoice_job(file_path: str) -> dict:
    """RQ worker entry point: extract structured data from one invoice image."""
    set_processing_active(True)
    try:
        return extract_invoice(file_path)
    finally:
        set_processing_active(False)


def process_document_job(file_path: str) -> dict:
    """RQ worker entry point: parse one uploaded document."""
    set_processing_active(True)
    try:

        parsed = route_file(file_path)
        if parsed.get("status") == "failed":
            return parsed

        return {
            "status": "success",
            "file_name": Path(file_path).name,
            "parsed": parsed,
        }
    finally:
        set_processing_active(False)

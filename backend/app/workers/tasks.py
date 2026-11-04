from pathlib import Path

from backend.app.services.invoice_extraction_service import set_processing_active
from backend.app.workers.queues import get_redis, get_processing_queue


def process_invoice_job(file_path: str) -> dict:
    """RQ worker entry point: extract and store one invoice."""
    set_processing_active(True)
    try:
        from backend.processing.pipeline.invoice_pipeline import process_invoice

        return process_invoice(file_path)
    finally:
        set_processing_active(False)


def process_document_job(file_path: str) -> dict:
    """RQ worker entry point: process one uploaded document through its pipeline."""
    set_processing_active(True)
    try:
        from backend.processing.pipeline.document_pipeline import process_document

        return process_document(file_path)
    finally:
        set_processing_active(False)

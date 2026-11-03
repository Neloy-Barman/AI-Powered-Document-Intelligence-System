from pathlib import Path

from backend.app.extraction.extractor import extract_invoice
from backend.app.workers.queues import get_redis

ACTIVE_KEY = "invoice_processing_active"


def process_invoice_job(file_path: str) -> dict:
    """RQ worker entry point: extract structured data from one invoice image.

    Must stay a top-level function so RQ workers can import it by string path.
    Sets/clears an active flag so the API can guard against re-triggering.
    """
    redis = get_redis()
    redis.set(ACTIVE_KEY, "1", ex=600)
    try:
        return extract_invoice(file_path)
    finally:
        redis.delete(ACTIVE_KEY)
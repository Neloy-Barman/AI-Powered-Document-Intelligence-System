from pathlib import Path

from backend.app.extraction.extractor import extract_invoice


def process_invoice_job(file_path: str) -> dict:
    """RQ worker entry point: extract structured data from one invoice image.

    Must stay a top-level function so RQ workers can import it by string path.
    """
    return extract_invoice(file_path)
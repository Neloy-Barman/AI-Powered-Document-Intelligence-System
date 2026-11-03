from fastapi import APIRouter, HTTPException, Query

from backend.app.core.config import INVOICE_UPLOAD_DIR
from backend.app.services.invoice_extraction_service import (
    enqueue_invoice,
    is_processing_active,
    pop_all_pending,
    pop_next_pending,
    remove_from_pending,
)

router = APIRouter()


@router.post("/extract-invoice")
def trigger_extraction(file_name: str | None = Query(None)) -> dict:
    # Guard: do not trigger again while an invoice is already processing.
    if is_processing_active():
        return {"status": "busy", "message": "An invoice is already processing."}

    # Specific file requested.
    if file_name:
        file_path = INVOICE_UPLOAD_DIR / file_name
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Uploaded file not found.")
        remove_from_pending(file_name)
        job_id = enqueue_invoice(file_path)
        return {"status": "queued", "jobs": [{"file_name": file_name, "job_id": job_id}]}

    # Otherwise process all pending invoices in FIFO order.
    pending = pop_all_pending()
    if not pending:
        return {"status": "empty", "message": "No pending invoices to process."}

    jobs = []
    for name in pending:
        file_path = INVOICE_UPLOAD_DIR / name
        if not file_path.exists():
            continue
        job_id = enqueue_invoice(file_path)
        jobs.append({"file_name": name, "job_id": job_id})

    if not jobs:
        return {"status": "empty", "message": "No pending invoices to process."}
    return {"status": "queued", "jobs": jobs}
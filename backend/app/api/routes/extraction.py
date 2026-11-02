from fastapi import APIRouter, HTTPException, Query

from backend.app.core.config import INVOICE_UPLOAD_DIR
from backend.app.services.invoice_extraction_service import (
    enqueue_invoice,
    pop_next_pending,
)

router = APIRouter()


@router.post("/extract-invoice")
def trigger_extraction(file_name: str | None = Query(None)) -> dict:
    # If no file name given, take the next pending invoice in FIFO order.
    if not file_name:
        file_name = pop_next_pending()
        if not file_name:
            return {"status": "empty", "message": "No pending invoices to process."}

    file_path = INVOICE_UPLOAD_DIR / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Uploaded file not found.")

    job_id = enqueue_invoice(file_path)
    return {"status": "queued", "file_name": file_name, "job_id": job_id}
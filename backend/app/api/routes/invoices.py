from fastapi import APIRouter, File, UploadFile

from backend.app.services.storage_service import save_invoice
from backend.app.services.invoice_extraction_service import add_to_pending

router = APIRouter()


@router.post("/invoices")
def upload_invoice(file: UploadFile | None = File(None)) -> dict:
    result = save_invoice(file)
    if not result["saved"]:
        return {
            "status": "failed",
            "file_name": result["file_name"],
            "error_message": result["error"],
        }
    # Track upload order (FIFO) for later processing.
    add_to_pending(result["file_name"])
    return {
        "status": "success",
        "file_name": result["file_name"],
        "message": "Uploaded successfully.",
    }
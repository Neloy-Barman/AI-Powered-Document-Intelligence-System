from fastapi import APIRouter, File, UploadFile

from backend.app.services.storage_service import save_invoice

router = APIRouter()


@router.post("/invoices")
def upload_invoice(file: UploadFile | None = File(None)) -> dict[str, str]:
    result = save_invoice(file)
    if result["saved"]:
        return {
            "status": "success",
            "file_name": result["file_name"],
            "message": result["message"],
        }
    return {
        "status": "failed",
        "file_name": result["file_name"],
        "error_message": result["error"],
    }

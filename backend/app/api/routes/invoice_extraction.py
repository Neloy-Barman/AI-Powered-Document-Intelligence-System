from fastapi import APIRouter

from backend.app.services.invoice_extraction_service import run_invoice_extraction

router = APIRouter()


@router.post("/extract-invoice")
def extract_invoice_data() -> dict:
    result = run_invoice_extraction()
    if result["extracted"]:
        return {"status": "success", "extraction": result["data"]}
    return {"status": "failed", "error_message": result["error"]}
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.invoice_extraction_service import (
    add_document_to_pending,
    document_file_path,
    enqueue_document,
    is_processing_active,
    pop_all_pending_documents,
)
from backend.app.services.storage_service import save_documents

router = APIRouter()


@router.post("/documents")
def upload_documents(files: list[UploadFile] = File(...)) -> dict:
    results = save_documents(files)

    uploaded = [result for result in results if result["saved"]]
    failed = [result for result in results if not result["saved"]]

    for result in uploaded:
        add_document_to_pending(result["file_name"])

    if uploaded and not failed:
        status = "success"
    elif uploaded and failed:
        status = "partial"
    else:
        status = "failed"

    return {
        "status": status,
        "uploaded": uploaded,
        "failed": failed,
    }


@router.post("/process-documents")
def process_documents() -> dict:
    if is_processing_active():
        return {"status": "busy", "message": "A file is already processing."}

    pending = pop_all_pending_documents()
    if not pending:
        return {"status": "empty", "message": "No pending documents to process."}

    jobs = []
    for name in pending:
        file_path = document_file_path(name)
        if not file_path.exists():
            continue
        job_id = enqueue_document(file_path)
        jobs.append({"file_name": name, "job_id": job_id})

    if not jobs:
        return {"status": "empty", "message": "No pending documents to process."}

    return {"status": "queued", "jobs": jobs}

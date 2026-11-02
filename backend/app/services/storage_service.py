import shutil
from pathlib import Path

from fastapi import UploadFile

from backend.app.core.config import ALLOWED_INVOICE_EXTENSIONS, UPLOAD_DIR


def save_invoice(file: UploadFile | None) -> dict[str, str | bool | None]:
    # Handle the case where no file was sent at all.
    if file is None:
        return {"file_name": "", "saved": False, "error": "No file provided."}

    # Read the original filename; fall back to empty string if missing.
    file_name = file.filename or ""
    if not file_name:
        return {"file_name": "", "saved": False, "error": "No file provided."}

    # Check the file extension against the allowed set.
    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_INVOICE_EXTENSIONS:
        return {
            "file_name": file_name,
            "saved": False,
            "error": "Invalid invoice. We only accept PDF or PNG files.",
        }

    try:
        # Create the uploads directory if it does not exist yet.
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        destination = UPLOAD_DIR / file_name
        # Stream the uploaded file to disk.
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except (OSError, IOError) as error:
        return {
            "file_name": file_name,
            "saved": False,
            "error": f"{type(error).__name__}: {error}",
        }
    except Exception as error:
        return {
            "file_name": file_name,
            "saved": False,
            "error": f"{type(error).__name__}: {error}",
        }

    return {"file_name": file_name, "saved": True, "message": "Uploaded successfully."}

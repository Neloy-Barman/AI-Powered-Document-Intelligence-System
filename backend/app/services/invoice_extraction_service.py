from pathlib import Path

from backend.app.core.config import UPLOAD_DIR
from backend.app.extraction.extractor import extract_invoice


def run_invoice_extraction() -> dict:
    # Hardcoded input for now; will become dynamic later.
    image_path = UPLOAD_DIR / "invoice.png"

    if not image_path.exists():
        return {
            "extracted": False,
            "data": None,
            "error": f"FileNotFoundError: {image_path} not found.",
        }

    try:
        data = extract_invoice(image_path)
    except FileNotFoundError as error:
        return {
            "extracted": False,
            "data": None,
            "error": f"{type(error).__name__}: {error}",
        }
    except Exception as error:
        return {
            "extracted": False,
            "data": None,
            "error": f"{type(error).__name__}: {error}",
        }

    return {"extracted": True, "data": data, "error": None}
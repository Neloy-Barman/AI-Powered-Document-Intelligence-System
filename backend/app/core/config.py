from pathlib import Path

# Base directory points to the `backend/` folder.
BASE_DIR = Path(__file__).resolve().parents[2]
# Where uploaded files are stored on disk.
UPLOAD_DIR = BASE_DIR / "uploads"
# Invoices are stored in a dedicated subfolder.
INVOICE_UPLOAD_DIR = UPLOAD_DIR / "invoices"
# Extensions accepted for invoice uploads only.
ALLOWED_INVOICE_EXTENSIONS = {".pdf", ".png"}
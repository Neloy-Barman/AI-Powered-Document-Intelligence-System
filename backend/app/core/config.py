from pathlib import Path
import os

# Base directory points to the `backend/` folder.
BASE_DIR = Path(__file__).resolve().parents[2]

# Where uploaded files are stored on disk.
UPLOAD_DIR = BASE_DIR / "uploads"
# Invoices are stored in a dedicated subfolder.
INVOICE_UPLOAD_DIR = UPLOAD_DIR / "invoices"
# Extensions accepted for invoice uploads only.
ALLOWED_INVOICE_EXTENSIONS = {".pdf", ".png"}

# Qdrant vector database
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None

# Qdrant collection and search settings
QDRANT_COLLECTION_NAME = "document-intelligence-system"
QDRANT_SEARCH_LIMIT = 3

# Local embedding model for testing
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DEVICE = "cpu"
EMBEDDING_PROVIDER = "local"

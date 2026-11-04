from pathlib import Path
import os

from dotenv import load_dotenv

# Base directory points to the `backend/` folder.
BASE_DIR = Path(__file__).resolve().parents[2]

# Load the project .env so it is the single source of truth for local config.
# override=True ensures a stale DATABASE_URL set in the shell cannot shadow it.
load_dotenv(BASE_DIR.parent / ".env", override=True)

# Where uploaded files are stored on disk.
UPLOAD_DIR = BASE_DIR / "uploads"
# Invoices are stored in a dedicated subfolder.
INVOICE_UPLOAD_DIR = UPLOAD_DIR / "invoices"
# Documents are stored in a dedicated subfolder.
DOCUMENT_UPLOAD_DIR = UPLOAD_DIR / "documents"
# Extensions accepted for invoice uploads only.
ALLOWED_INVOICE_EXTENSIONS = {".pdf", ".png"}
# Extensions accepted for document uploads.
ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".png",
    ".tiff",
    ".xlsx",
    ".xls",
    ".csv",
}

# Qdrant vector database
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None

# Qdrant collection and search settings
QDRANT_COLLECTION_NAME = os.getenv(
    "QDRANT_COLLECTION_NAME", "ai_powered_document_intelligence_system"
)
QDRANT_SEARCH_LIMIT = 3

# PostgreSQL database
DATABASE_URL = os.getenv("DATABASE_URL")

# Semantic search
SEMANTIC_SEARCH_WEIGHT = 0.7
KEYWORD_SEARCH_WEIGHT = 0.3
HYBRID_SEARCH_LIMIT = 5
BM25_CORPUS_PATH = BASE_DIR / "data" / "bm25_corpus.json"

# Local embedding model for testing
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DEVICE = "cpu"
EMBEDDING_PROVIDER = "local"

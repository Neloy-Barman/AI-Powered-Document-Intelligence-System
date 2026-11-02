# Run: uvicorn app.main:app --host 127.0.0.1 --port 8000
# (run from the backend/ directory, with venv already activated)

from fastapi import FastAPI

from backend.app.api.routes import home, invoice_extraction, invoices

app = FastAPI(title="AI-Powered Document Intelligence System")

app.include_router(home.router)
app.include_router(invoices.router)
app.include_router(invoice_extraction.router)
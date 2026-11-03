# Run (from project root, venv activated):
#   1) Redis: docker start redis   (or docker run -d --name redis -p 6379:6379 redis:7-alpine)
#   2) API:   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
#   3) Worker (Windows uses SimpleWorker, no fork): rq worker invoices --worker-class rq.worker.SimpleWorker
#   4) Frontend (from project root): cd frontend && npm run dev   (opens http://localhost:5173)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import UPLOAD_DIR
from backend.app.api.routes import extraction, home, invoices, jobs, search

app = FastAPI(
    title="AI-Powered Document Intelligence System",
)

# Allow the Vite dev server (frontend) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home.router)
app.include_router(invoices.router)
app.include_router(extraction.router)
app.include_router(jobs.router)
app.include_router(search.router)

# Serve uploaded files so the frontend can download them directly.
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

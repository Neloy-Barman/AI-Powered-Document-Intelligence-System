# Run (from project root, venv activated):
#   1) Redis: docker start redis   (or docker run -d --name redis -p 6379:6379 redis:7-alpine)
#   2) API:   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
#   3) Worker (Windows uses SimpleWorker, no fork): rq worker invoices --worker-class rq.worker.SimpleWorker

from fastapi import FastAPI

from backend.app.api.routes import extraction, home, invoices, jobs

app = FastAPI(title="AI-Powered Document Intelligence System")

app.include_router(home.router)
app.include_router(invoices.router)
app.include_router(extraction.router)
app.include_router(jobs.router)
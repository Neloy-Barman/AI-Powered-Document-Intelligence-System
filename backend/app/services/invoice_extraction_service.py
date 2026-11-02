from pathlib import Path

from redis import Redis

from backend.app.core.config import INVOICE_UPLOAD_DIR
from backend.app.workers.queues import get_redis

PENDING_KEY = "pending_invoices"


def add_to_pending(file_name: str) -> None:
    # Append in upload order (FIFO).
    get_redis().rpush(PENDING_KEY, file_name)


def remove_from_pending(file_name: str) -> None:
    get_redis().lrem(PENDING_KEY, 0, file_name)


def pop_next_pending() -> str | None:
    # Remove and return the first (oldest) pending file name, or None if empty.
    value = get_redis().lpop(PENDING_KEY)
    if value is None:
        return None
    return value.decode()


def enqueue_invoice(file_path: str | Path) -> str:
    from backend.app.workers.queues import get_invoice_queue

    queue = get_invoice_queue()
    job = queue.enqueue(
        "backend.app.workers.tasks.process_invoice_job",
        str(file_path),
        result_ttl=3600,
    )
    return job.id


def invoice_file_path(file_name: str) -> Path:
    return INVOICE_UPLOAD_DIR / file_name
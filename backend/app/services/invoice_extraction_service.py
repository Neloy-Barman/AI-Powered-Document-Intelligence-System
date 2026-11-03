from pathlib import Path

from backend.app.core.config import INVOICE_UPLOAD_DIR
from backend.app.workers.queues import get_redis, get_invoice_queue

PENDING_KEY = "pending_invoices"
ACTIVE_KEY = "invoice_processing_active"


def add_to_pending(file_name: str) -> None:
    # Append in upload order (FIFO).
    get_redis().rpush(PENDING_KEY, file_name)


def pop_all_pending() -> list[str]:
    # Remove and return all pending file names in FIFO order.
    redis = get_redis()
    items = redis.lrange(PENDING_KEY, 0, -1)
    redis.delete(PENDING_KEY)
    return [b.decode() for b in items]


def pop_next_pending() -> str | None:
    value = get_redis().lpop(PENDING_KEY)
    if value is None:
        return None
    return value.decode()


def remove_from_pending(file_name: str) -> None:
    # Remove a specific file from the pending queue, if present.
    get_redis().lrem(PENDING_KEY, 0, file_name)


def is_processing_active() -> bool:
    return bool(get_redis().get(ACTIVE_KEY))


def set_processing_active(active: bool) -> None:
    if active:
        get_redis().set(ACTIVE_KEY, "1", ex=600)
    else:
        get_redis().delete(ACTIVE_KEY)


def enqueue_invoice(file_path: str | Path) -> str:
    queue = get_invoice_queue()
    job = queue.enqueue(
        "backend.app.workers.tasks.process_invoice_job",
        str(file_path),
        result_ttl=3600,
    )
    return job.id


def invoice_file_path(file_name: str) -> Path:
    return INVOICE_UPLOAD_DIR / file_name
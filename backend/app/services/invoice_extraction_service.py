from pathlib import Path

from backend.app.core.config import INVOICE_UPLOAD_DIR
from backend.app.workers.queues import get_redis, get_processing_queue

PENDING_INVOICES_KEY = "pending_invoices"
PENDING_DOCUMENTS_KEY = "pending_documents"
ACTIVE_KEY = "processing_active"


def add_to_pending(file_name: str) -> None:
    # Append in upload order (FIFO).
    get_redis().rpush(PENDING_INVOICES_KEY, file_name)


def add_document_to_pending(file_name: str) -> None:
    # Append in upload order (FIFO).
    get_redis().rpush(PENDING_DOCUMENTS_KEY, file_name)


def pop_all_pending() -> list[str]:
    # Remove and return all pending invoice file names in FIFO order.
    redis = get_redis()
    items = redis.lrange(PENDING_INVOICES_KEY, 0, -1)
    redis.delete(PENDING_INVOICES_KEY)
    return [b.decode() for b in items]


def pop_all_pending_documents() -> list[str]:
    # Remove and return all pending document file names in FIFO order.
    redis = get_redis()
    items = redis.lrange(PENDING_DOCUMENTS_KEY, 0, -1)
    redis.delete(PENDING_DOCUMENTS_KEY)
    return [b.decode() for b in items]


def pop_next_pending() -> str | None:
    value = get_redis().lpop(PENDING_INVOICES_KEY)
    if value is None:
        return None
    return value.decode()


def remove_from_pending(file_name: str) -> None:
    # Remove a specific invoice from the pending queue, if present.
    get_redis().lrem(PENDING_INVOICES_KEY, 0, file_name)


def remove_document_from_pending(file_name: str) -> None:
    # Remove a specific document from the pending queue, if present.
    get_redis().lrem(PENDING_DOCUMENTS_KEY, 0, file_name)


def is_processing_active() -> bool:
    return bool(get_redis().get(ACTIVE_KEY))


def set_processing_active(active: bool) -> None:
    if active:
        get_redis().set(ACTIVE_KEY, "1", ex=600)
    else:
        get_redis().delete(ACTIVE_KEY)


def enqueue_invoice(file_path: str | Path) -> str:
    queue = get_processing_queue()
    job = queue.enqueue(
        "backend.app.workers.tasks.process_invoice_job",
        str(file_path),
        result_ttl=3600,
    )
    return job.id


def enqueue_document(file_path: str | Path) -> str:
    queue = get_processing_queue()
    job = queue.enqueue(
        "backend.app.workers.tasks.process_document_job",
        str(file_path),
        result_ttl=3600,
    )
    return job.id


def document_file_path(file_name: str) -> Path:
    from backend.app.core.config import DOCUMENT_UPLOAD_DIR

    return DOCUMENT_UPLOAD_DIR / file_name
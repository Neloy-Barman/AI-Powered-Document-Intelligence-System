import os

from redis import Redis
from rq import Queue

# Redis connection URL; override via REDIS_URL env var.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def get_redis() -> Redis:
    """Return a Redis connection built from REDIS_URL."""
    return Redis.from_url(REDIS_URL)


def get_invoice_queue() -> Queue:
    """Return the dedicated queue used only for invoice processing jobs."""
    return Queue("invoices", connection=get_redis())
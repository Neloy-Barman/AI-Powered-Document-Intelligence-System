import os
from rq import Queue
from redis import Redis

# Redis connection URL; override via REDIS_URL env var.
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

def get_redis() -> Redis:
    """Return a Redis connection built from REDIS_URL."""
    return Redis.from_url(
        REDIS_URL,
    )


def get_processing_queue() -> Queue:
    """Return the shared queue used for invoice and document processing jobs."""
    return Queue(
        "processing",
        connection=get_redis(),
    )

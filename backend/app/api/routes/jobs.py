from fastapi import APIRouter, HTTPException
from rq.job import Job
from rq.exceptions import NoSuchJobError

from backend.app.workers.queues import get_redis

router = APIRouter()


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str) -> dict:
    # Fetch the job from Redis; 404 if it does not exist.
    try:
        job = Job.fetch(job_id, connection=get_redis())
    except NoSuchJobError:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.is_finished:
        return {"status": "finished", "result": job.result}
    if job.is_failed:
        return {"status": "failed", "error": str(job.exc_info)}
    if job.is_started:
        return {"status": "started"}
    return {"status": "queued"}

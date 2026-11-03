import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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


@router.get("/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    async def event_generator():
        while True:
            try:
                job = Job.fetch(job_id, connection=get_redis())
            except NoSuchJobError:
                yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
                break

            payload = {
                "status": "finished" if job.is_finished
                else "failed" if job.is_failed
                else "started" if job.is_started
                else "queued",
            }
            if job.is_finished:
                payload["result"] = job.result
            if job.is_failed:
                payload["error"] = str(job.exc_info)

            yield f"data: {json.dumps(payload)}\n\n"  # push one event

            if job.is_finished or job.is_failed:
                break  # terminal state, stop streaming

            await asyncio.sleep(1)  # poll Redis once per second

    return StreamingResponse(event_generator(), media_type="text/event-stream")
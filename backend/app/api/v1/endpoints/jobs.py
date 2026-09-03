import json
import logging
import asyncio
from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, FileResponse

from app.core.exceptions import ResourceNotFoundException, FileValidationException
from app.schemas.job import JobProgressResponse, JobStatus
from app.services.job_manager import job_manager
from app.services.storage import storage_manager
from app.utils.filename import get_docx_filename, build_content_disposition_header

router = APIRouter()
logger = logging.getLogger("pdf2docx.api.jobs")

DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@router.get(
    "/jobs/{job_id}",
    response_model=JobProgressResponse,
    summary="Job Status Telemetry",
    description="Returns current conversion progress, page status, and error details for a given job.",
)
async def get_job_status(job_id: str) -> JobProgressResponse:
    job = await job_manager.get_job(job_id)
    if not job:
        raise ResourceNotFoundException(f"Job with ID '{job_id}' was not found.")
    return job.to_progress_response()


@router.get(
    "/jobs/{job_id}/events",
    summary="Server-Sent Events (SSE) Live Progress Stream",
    description="Streams real-time per-page layout reconstruction progress directly to client browsers.",
)
async def get_job_event_stream(job_id: str, request: Request):
    job = await job_manager.get_job(job_id)
    if not job:
        raise ResourceNotFoundException(f"Job with ID '{job_id}' was not found.")

    queue = await job_manager.subscribe(job_id)

    async def event_generator():
        try:
            while True:
                # Disconnect check
                if await request.is_disconnected():
                    logger.info(f"Client disconnected from SSE stream for job {job_id}")
                    break

                try:
                    # Wait for next progress event with a heartbeat timeout
                    event_data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: progress\ndata: {json.dumps(event_data)}\n\n"

                    if event_data.get("status") in (JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value):
                        break
                except asyncio.TimeoutError:
                    # Send SSE keep-alive ping comment
                    yield ": keepalive ping\n\n"
        finally:
            await job_manager.unsubscribe(job_id, queue)

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",  # Disables Nginx reverse-proxy response buffering
    }

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=headers,
    )


@router.get(
    "/jobs/{job_id}/download",
    summary="Download Converted DOCX Binary",
    description="Streams the generated DOCX document as a download and registers ephemeral cleanup.",
)
async def download_converted_file(
    job_id: str,
    background_tasks: BackgroundTasks,
):
    job = await job_manager.get_job(job_id)
    if not job:
        raise ResourceNotFoundException(f"Job with ID '{job_id}' was not found.")

    if job.status != JobStatus.COMPLETED or not job.docx_path or not job.docx_path.exists():
        raise FileValidationException(
            message=f"Document is not ready for download (current status: {job.status}).",
            code="FILE_NOT_READY",
        )

    docx_name = get_docx_filename(job.filename)
    session_dir = job.docx_path.parent

    # Clean up session files in background after client completes download
    background_tasks.add_task(storage_manager.cleanup_session, session_dir)

    headers = {
        "Content-Disposition": build_content_disposition_header(docx_name),
        "Access-Control-Expose-Headers": "Content-Disposition",
    }

    return FileResponse(
        path=job.docx_path,
        media_type=DOCX_MIME_TYPE,
        filename=docx_name,
        headers=headers,
    )

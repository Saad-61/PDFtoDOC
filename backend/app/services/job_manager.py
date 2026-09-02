import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.schemas.job import JobStatus, JobProgressResponse

logger = logging.getLogger("pdf2docx.jobs")


class JobRecord:
    def __init__(
        self,
        job_id: str,
        session_id: str,
        filename: str,
        total_pages: int,
    ):
        self.job_id = job_id
        self.session_id = session_id
        self.filename = filename
        self.total_pages = total_pages
        self.current_page = 0
        self.status = JobStatus.QUEUED
        self.stage = "QUEUED"
        self.percent = 0
        self.error: Optional[str] = None
        self.docx_path: Optional[Path] = None
        self.created_at = time.time()
        self.completed_at: Optional[float] = None
        self.duration_seconds: Optional[float] = None

    def to_progress_response(self, base_url: str = "") -> JobProgressResponse:
        download_url = f"{base_url}/api/v1/jobs/{self.job_id}/download" if self.status == JobStatus.COMPLETED else None
        return JobProgressResponse(
            job_id=self.job_id,
            status=self.status,
            stage=self.stage,
            current_page=self.current_page,
            total_pages=self.total_pages,
            percent=self.percent,
            error=self.error,
            duration_seconds=self.duration_seconds,
            download_url=download_url,
        )


class JobManager:
    """
    In-memory registry managing asynchronous conversion job state and SSE event broadcasts.
    """

    def __init__(self):
        self._jobs: Dict[str, JobRecord] = {}
        self._listeners: Dict[str, List[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def create_job(
        self,
        job_id: str,
        session_id: str,
        filename: str,
        total_pages: int,
    ) -> JobRecord:
        async with self._lock:
            record = JobRecord(
                job_id=job_id,
                session_id=session_id,
                filename=filename,
                total_pages=total_pages,
            )
            self._jobs[job_id] = record
            self._listeners[job_id] = []
            logger.info(f"Registered job {job_id} for file '{filename}' ({total_pages} pages)")
            return record

    async def update_progress(
        self,
        job_id: str,
        current_page: int,
        total_pages: int,
        stage: str,
        percent: int,
    ) -> None:
        async with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return
            record.status = JobStatus.PROCESSING
            record.current_page = current_page
            record.total_pages = total_pages
            record.stage = stage
            record.percent = min(100, max(0, percent))

            data = record.to_progress_response().model_dump()

        # Broadcast to all active SSE queues for this job
        await self._broadcast(job_id, data)

    async def complete_job(
        self,
        job_id: str,
        docx_path: Path,
        duration_seconds: float,
    ) -> None:
        async with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return
            record.status = JobStatus.COMPLETED
            record.stage = "COMPLETED"
            record.percent = 100
            record.docx_path = docx_path
            record.completed_at = time.time()
            record.duration_seconds = duration_seconds

            data = record.to_progress_response().model_dump()

        await self._broadcast(job_id, data)
        logger.info(f"Job {job_id} marked as COMPLETED in {duration_seconds}s")

    async def fail_job(self, job_id: str, error_message: str) -> None:
        async with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return
            record.status = JobStatus.FAILED
            record.stage = "FAILED"
            record.error = error_message
            record.completed_at = time.time()
            if record.created_at:
                record.duration_seconds = round(time.time() - record.created_at, 2)

            data = record.to_progress_response().model_dump()

        await self._broadcast(job_id, data)
        logger.warning(f"Job {job_id} marked as FAILED: {error_message}")

    async def get_job(self, job_id: str) -> Optional[JobRecord]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def subscribe(self, job_id: str) -> asyncio.Queue:
        """
        Subscribes to live progress events for the given job_id.
        """
        queue = asyncio.Queue(maxsize=50)
        async with self._lock:
            if job_id not in self._listeners:
                self._listeners[job_id] = []
            self._listeners[job_id].append(queue)

            # Send current initial state immediately
            record = self._jobs.get(job_id)
            if record:
                await queue.put(record.to_progress_response().model_dump())

        return queue

    async def unsubscribe(self, job_id: str, queue: asyncio.Queue) -> None:
        async with self._lock:
            if job_id in self._listeners:
                try:
                    self._listeners[job_id].remove(queue)
                except ValueError:
                    pass
                if not self._listeners[job_id] and job_id in self._jobs and self._jobs[job_id].status in (JobStatus.COMPLETED, JobStatus.FAILED):
                    del self._listeners[job_id]

    async def _broadcast(self, job_id: str, data: dict) -> None:
        listeners = self._listeners.get(job_id, [])
        for q in list(listeners):
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                pass


job_manager = JobManager()

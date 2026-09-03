from enum import Enum
from typing import Optional
from pydantic import BaseModel


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobProgressResponse(BaseModel):
    """
    Real-time progress telemetry for an asynchronous conversion job.
    """
    job_id: str
    status: JobStatus
    stage: str = "INITIALIZING"
    current_page: int = 0
    total_pages: int = 0
    percent: int = 0
    error: Optional[str] = None
    duration_seconds: Optional[float] = None
    download_url: Optional[str] = None


class JobCreateResponse(BaseModel):
    """
    Response when a new conversion job is enqueued.
    """
    job_id: str
    status: JobStatus
    message: str = "Job accepted and queued for conversion."
    events_url: str
    status_url: str

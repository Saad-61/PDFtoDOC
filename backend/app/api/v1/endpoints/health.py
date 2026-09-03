import time
from datetime import datetime, timezone
import psutil
from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()
START_TIME = time.time()


class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_used_mb: float
    memory_total_mb: float
    memory_percent: float
    disk_free_gb: float
    disk_total_gb: float
    disk_percent: float
    active_temp_sessions: int
    process_uptime_seconds: float


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    metrics: SystemMetrics


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health & Telemetry Probe",
    description="Returns service availability, host metrics, memory stats, and ephemeral storage telemetry.",
)
async def health_check() -> HealthResponse:
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage(str(settings.TEMP_DIR_ROOT.parent))
    
    # Count active temp session folders
    active_sessions = 0
    if settings.TEMP_DIR_ROOT.exists():
        active_sessions = sum(1 for item in settings.TEMP_DIR_ROOT.iterdir() if item.is_dir())

    metrics = SystemMetrics(
        cpu_percent=psutil.cpu_percent(interval=None),
        memory_used_mb=round(vm.used / (1024 * 1024), 2),
        memory_total_mb=round(vm.total / (1024 * 1024), 2),
        memory_percent=vm.percent,
        disk_free_gb=round(disk.free / (1024 * 1024 * 1024), 2),
        disk_total_gb=round(disk.total / (1024 * 1024 * 1024), 2),
        disk_percent=disk.percent,
        active_temp_sessions=active_sessions,
        process_uptime_seconds=round(time.time() - START_TIME, 2),
    )

    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        metrics=metrics,
    )

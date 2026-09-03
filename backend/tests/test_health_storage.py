import io
import time
import pytest
from fastapi import UploadFile
from app.core.exceptions import FileValidationException


@pytest.mark.asyncio
async def test_root_endpoint(async_client):
    """Verifies that root endpoint returns service metadata."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data
    assert data["api_v1"] == "/api/v1"


@pytest.mark.asyncio
async def test_health_telemetry_endpoint(async_client):
    """Verifies health check endpoint and telemetry metrics structure."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "metrics" in data
    metrics = data["metrics"]
    assert "cpu_percent" in metrics
    assert "memory_used_mb" in metrics
    assert "disk_free_gb" in metrics
    assert "active_temp_sessions" in metrics
    assert "process_uptime_seconds" in metrics


@pytest.mark.asyncio
async def test_storage_manager_lifecycle(custom_storage):
    """Tests session creation, file writing, and session cleanup."""
    # 1. Create session
    session_dir = custom_storage.create_session("test-session-123")
    assert session_dir.exists()
    assert session_dir.is_dir()

    # 2. Simulate file upload
    dummy_content = b"%PDF-1.4 dummy pdf content for testing"
    upload_file = UploadFile(
        file=io.BytesIO(dummy_content),
        filename="sample_document.pdf",
    )

    saved_path = await custom_storage.save_upload_file(
        session_dir=session_dir,
        upload_file=upload_file,
    )

    assert saved_path.exists()
    assert saved_path.read_bytes() == dummy_content

    # 3. Test cleanup
    custom_storage.cleanup_session(session_dir)
    assert not session_dir.exists()


@pytest.mark.asyncio
async def test_storage_manager_file_size_limit(custom_storage):
    """Verifies that exceeding MAX_FILE_SIZE_MB raises FileValidationException."""
    session_dir = custom_storage.create_session("oversized-session")
    
    # 2 MB content with a 1 MB limit
    oversized_content = b"X" * (2 * 1024 * 1024)
    upload_file = UploadFile(
        file=io.BytesIO(oversized_content),
        filename="large.pdf",
    )

    with pytest.raises(FileValidationException) as exc_info:
        await custom_storage.save_upload_file(
            session_dir=session_dir,
            upload_file=upload_file,
            max_size_mb=1,
        )

    assert exc_info.value.code == "FILE_TOO_LARGE"
    # Ensure partial file is cleaned up
    files_in_dir = list(session_dir.iterdir())
    assert len(files_in_dir) == 0

    custom_storage.cleanup_session(session_dir)


def test_storage_expired_cleanup(custom_storage):
    """Tests automated cleanup of expired sessions based on timestamp."""
    old_session = custom_storage.create_session("old-session")
    new_session = custom_storage.create_session("new-session")

    # Artificially age the old session by setting mtime 30 minutes in the past
    thirty_mins_ago = time.time() - (30 * 60)
    import os
    os.utime(str(old_session), (thirty_mins_ago, thirty_mins_ago))

    pruned = custom_storage.cleanup_expired_sessions(max_age_minutes=15)
    assert pruned == 1
    assert not old_session.exists()
    assert new_session.exists()

    custom_storage.cleanup_session(new_session)

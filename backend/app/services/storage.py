import shutil
import time
import uuid
import logging
from pathlib import Path
from typing import Optional
import aiofiles
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileValidationException

logger = logging.getLogger("pdf2docx.storage")


class EphemeralStorageManager:
    """
    Manages temporary session directories and isolated file lifecycles.
    Ensures that uploaded PDFs and generated DOCX documents are strictly ephemeral.
    """

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or settings.TEMP_DIR_ROOT
        self._ensure_root_dir()

    def _ensure_root_dir(self) -> None:
        """Ensures the root temporary directory exists."""
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, session_id: Optional[str] = None) -> Path:
        """
        Creates a dedicated, isolated temporary directory for a single conversion session.
        """
        sid = session_id or str(uuid.uuid4())
        session_dir = self.root_dir / sid
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    async def save_upload_file(
        self,
        session_dir: Path,
        upload_file: UploadFile,
        custom_name: Optional[str] = None,
        max_size_mb: Optional[int] = None,
    ) -> Path:
        """
        Streams an uploaded file to disk in the session directory while enforcing file size limits.
        """
        max_bytes = (max_size_mb or settings.MAX_FILE_SIZE_MB) * 1024 * 1024
        target_name = custom_name or upload_file.filename or "document.pdf"
        # Sanitize target filename
        safe_name = "".join(c for c in target_name if c.isalnum() or c in "._- ")
        if not safe_name.lower().endswith(".pdf"):
            safe_name += ".pdf"

        target_path = session_dir / safe_name
        total_bytes = 0
        chunk_size = 1024 * 64  # 64 KB chunks

        try:
            async with aiofiles.open(target_path, "wb") as f:
                while chunk := await upload_file.read(chunk_size):
                    total_bytes += len(chunk)
                    if total_bytes > max_bytes:
                        raise FileValidationException(
                            message=f"File exceeds maximum allowed size of {max_size_mb or settings.MAX_FILE_SIZE_MB}MB.",
                            code="FILE_TOO_LARGE",
                            details={"max_size_mb": max_size_mb or settings.MAX_FILE_SIZE_MB, "received_bytes": total_bytes},
                        )
                    await f.write(chunk)
        except Exception:
            # If writing failed or size exceeded, clean up the partial file
            if target_path.exists():
                try:
                    target_path.unlink()
                except OSError:
                    pass
            raise

        return target_path

    def cleanup_session(self, session_dir: Path) -> None:
        """
        Safely removes an entire session directory and all its contents.
        """
        if not session_dir or not session_dir.exists():
            return
        try:
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.info(f"Cleaned up session directory: {session_dir.name}")
        except Exception as e:
            logger.warning(f"Failed to cleanup session directory {session_dir}: {e}")

    def cleanup_file(self, file_path: Path) -> None:
        """
        Safely removes a single file.
        """
        if not file_path or not file_path.exists():
            return
        try:
            file_path.unlink(missing_ok=True)
            logger.info(f"Cleaned up file: {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to delete file {file_path}: {e}")

    def cleanup_expired_sessions(self, max_age_minutes: Optional[int] = None) -> int:
        """
        Scans root temporary directory and removes any session directories older than max_age_minutes.
        Returns the count of pruned sessions.
        """
        age_minutes = max_age_minutes or settings.SESSION_EXPIRY_MINUTES
        cutoff_time = time.time() - (age_minutes * 60)
        pruned_count = 0

        if not self.root_dir.exists():
            return 0

        for item in self.root_dir.iterdir():
            if item.is_dir():
                try:
                    mtime = item.stat().st_mtime
                    if mtime < cutoff_time:
                        shutil.rmtree(item, ignore_errors=True)
                        pruned_count += 1
                        logger.info(f"Garbage collected expired session: {item.name}")
                except Exception as e:
                    logger.warning(f"Error during GC of session {item}: {e}")

        return pruned_count


# Global singleton storage manager
storage_manager = EphemeralStorageManager()

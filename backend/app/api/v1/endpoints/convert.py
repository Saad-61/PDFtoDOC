import uuid
import logging
import asyncio
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, status, Request
from fastapi.responses import FileResponse
from app.schemas.conversion import ValidationResult
from app.schemas.job import JobCreateResponse, JobStatus
from app.services.storage import storage_manager
from app.services.pdf_validator import pdf_validator
from app.services.converter_engine import convert_pdf_async, parse_page_range
from app.services.job_manager import job_manager
from app.utils.filename import get_docx_filename, build_content_disposition_header

router = APIRouter()
logger = logging.getLogger("pdf2docx.api.convert")

DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


async def process_async_job_worker(
    job_id: str,
    session_dir: Path,
    pdf_path: Path,
    docx_path: Path,
    pages: Optional[list],
    password: Optional[str],
):
    """
    Background worker function that executes conversion and updates JobManager progress.
    """
    logger.info(f"Starting background conversion task for job {job_id}")
    main_loop = asyncio.get_running_loop()

    def progress_callback(current_page: int, total_pages: int, stage: str, percent: int):
        try:
            asyncio.run_coroutine_threadsafe(
                job_manager.update_progress(
                    job_id=job_id,
                    current_page=current_page,
                    total_pages=total_pages,
                    stage=stage,
                    percent=percent,
                ),
                main_loop,
            )
        except Exception as e:
            logger.warning(f"Failed to post progress update for job {job_id}: {e}")

    try:
        result = await convert_pdf_async(
            pdf_path=pdf_path,
            docx_path=docx_path,
            pages=pages,
            password=password,
            progress_callback=progress_callback,
        )
        await job_manager.complete_job(
            job_id=job_id,
            docx_path=docx_path,
            duration_seconds=result["duration_seconds"],
        )
    except Exception as e:
        logger.error(f"Job {job_id} failed during async execution: {e}", exc_info=True)
        await job_manager.fail_job(job_id=job_id, error_message=str(e))


@router.post(
    "/convert/validate",
    response_model=ValidationResult,
    summary="PDF Preflight Validation",
    description="Validates PDF integrity, checks password requirements, page bounds, and scanned heuristic without initiating conversion.",
)
async def validate_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file to inspect"),
    password: Optional[str] = Form(None, description="Optional password for encrypted documents"),
) -> ValidationResult:
    session_id = str(uuid.uuid4())
    session_dir = storage_manager.create_session(session_id)
    background_tasks.add_task(storage_manager.cleanup_session, session_dir)

    pdf_path = await storage_manager.save_upload_file(
        session_dir=session_dir,
        upload_file=file,
    )

    validation_result = pdf_validator.validate(
        file_path=pdf_path,
        password=password,
        raise_on_encrypted=True,
    )
    return validation_result


@router.post(
    "/convert/stream",
    summary="Synchronous Direct Stream Conversion",
    description="Uploads and converts a PDF directly, streaming the resulting DOCX binary back in the response.",
)
async def convert_document_stream(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file to convert"),
    password: Optional[str] = Form(None, description="Optional password for encrypted documents"),
    page_range: Optional[str] = Form(None, description="Optional page range (e.g. '1-3, 5')"),
):
    session_id = str(uuid.uuid4())
    session_dir = storage_manager.create_session(session_id)

    pdf_path = await storage_manager.save_upload_file(
        session_dir=session_dir,
        upload_file=file,
    )

    # Validate structure & password
    validation = pdf_validator.validate(
        file_path=pdf_path,
        password=password,
        raise_on_encrypted=True,
    )

    target_pages = parse_page_range(page_range, validation.total_pages)

    docx_name = get_docx_filename(file.filename or "document.pdf")
    docx_path = session_dir / docx_name

    try:
        await convert_pdf_async(
            pdf_path=pdf_path,
            docx_path=docx_path,
            pages=target_pages,
            password=password,
        )
    except Exception:
        storage_manager.cleanup_session(session_dir)
        raise

    # Schedule session cleanup after streaming download completes
    background_tasks.add_task(storage_manager.cleanup_session, session_dir)

    headers = {
        "Content-Disposition": build_content_disposition_header(docx_name),
        "Access-Control-Expose-Headers": "Content-Disposition",
    }

    return FileResponse(
        path=docx_path,
        media_type=DOCX_MIME_TYPE,
        filename=docx_name,
        headers=headers,
    )


@router.post(
    "/convert/jobs",
    response_model=JobCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Asynchronous Conversion Job Creation",
    description="Enqueues a PDF conversion task with real-time SSE progress reporting.",
)
async def create_conversion_job(
    request: Request,
    file: UploadFile = File(..., description="PDF file to convert"),
    password: Optional[str] = Form(None, description="Optional password for encrypted documents"),
    page_range: Optional[str] = Form(None, description="Optional page range (e.g. '1-3, 5')"),
) -> JobCreateResponse:
    job_id = str(uuid.uuid4())
    session_id = job_id
    session_dir = storage_manager.create_session(session_id)

    pdf_path = await storage_manager.save_upload_file(
        session_dir=session_dir,
        upload_file=file,
    )

    # Validate document
    validation = pdf_validator.validate(
        file_path=pdf_path,
        password=password,
        raise_on_encrypted=True,
    )

    target_pages = parse_page_range(page_range, validation.total_pages)
    docx_name = get_docx_filename(file.filename or "document.pdf")
    docx_path = session_dir / docx_name

    # Register job
    await job_manager.create_job(
        job_id=job_id,
        session_id=session_id,
        filename=file.filename or "document.pdf",
        total_pages=len(target_pages),
    )

    # Launch background conversion task
    asyncio.create_task(
        process_async_job_worker(
            job_id=job_id,
            session_dir=session_dir,
            pdf_path=pdf_path,
            docx_path=docx_path,
            pages=target_pages,
            password=password,
        )
    )

    return JobCreateResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message="Conversion job enqueued successfully.",
        events_url=f"/api/v1/jobs/{job_id}/events",
        status_url=f"/api/v1/jobs/{job_id}",
    )

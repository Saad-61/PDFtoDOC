import os
import time
import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Callable
import fitz
from pdf2docx import Converter

from app.core.config import settings
from app.core.exceptions import ConversionException, FileValidationException

logger = logging.getLogger("pdf2docx.engine")


def parse_page_range(range_str: Optional[str], total_pages: int) -> List[int]:
    """
    Parses a user-supplied page range string (e.g. '1-3, 5, 8') into a sorted,
    deduplicated list of 0-indexed page indices.
    
    If range_str is empty or None, returns all pages [0, 1, ..., total_pages - 1].
    """
    if not range_str or not range_str.strip():
        return list(range(total_pages))

    indices = set()
    parts = range_str.split(",")

    for part in parts:
        clean_part = part.strip()
        if not clean_part:
            continue
        if "-" in clean_part:
            subparts = clean_part.split("-")
            if len(subparts) != 2:
                raise FileValidationException(
                    message=f"Invalid page range token: '{clean_part}'. Expected format 'X-Y'.",
                    code="INVALID_PAGE_RANGE",
                )
            try:
                start_p = int(subparts[0].strip())
                end_p = int(subparts[1].strip())
            except ValueError:
                raise FileValidationException(
                    message=f"Invalid page numbers in range: '{clean_part}'.",
                    code="INVALID_PAGE_RANGE",
                )
            if start_p < 1 or end_p < 1 or start_p > end_p:
                raise FileValidationException(
                    message=f"Invalid range bounds '{clean_part}': Start page must be >= 1 and <= End page.",
                    code="INVALID_PAGE_RANGE",
                )
            if end_p > total_pages:
                raise FileValidationException(
                    message=f"Page number {end_p} exceeds total document pages ({total_pages}).",
                    code="PAGE_OUT_OF_BOUNDS",
                    details={"total_pages": total_pages, "requested_page": end_p},
                )
            for p in range(start_p, end_p + 1):
                indices.add(p - 1)
        else:
            try:
                single_p = int(clean_part)
            except ValueError:
                raise FileValidationException(
                    message=f"Invalid page number token: '{clean_part}'.",
                    code="INVALID_PAGE_RANGE",
                )
            if single_p < 1 or single_p > total_pages:
                raise FileValidationException(
                    message=f"Page number {single_p} is out of bounds (document has {total_pages} pages).",
                    code="PAGE_OUT_OF_BOUNDS",
                    details={"total_pages": total_pages, "requested_page": single_p},
                )
            indices.add(single_p - 1)

    if not indices:
        raise FileValidationException(
            message="Parsed page range is empty.",
            code="EMPTY_PAGE_RANGE",
        )

    return sorted(list(indices))


def convert_pdf_sync(
    pdf_path: Path,
    docx_path: Path,
    pages: Optional[List[int]] = None,
    password: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str, int], None]] = None,
) -> dict:
    """
    Synchronous conversion engine function.
    Converts PDF layout to DOCX format page-by-page, invoking progress_callback after each page.
    """
    start_time = time.time()
    unlocked_pdf_path: Optional[Path] = None

    effective_pdf_path = pdf_path

    # Step 1: If password is provided, decrypt to a temporary unencrypted PDF
    if password:
        try:
            doc = fitz.open(str(pdf_path))
            if doc.is_encrypted:
                auth_success = doc.authenticate(password)
                if auth_success == 0:
                    raise FileValidationException(
                        message="Incorrect password for encrypted PDF.",
                        code="INVALID_PASSWORD",
                    )
                unlocked_pdf_path = pdf_path.parent / f"unlocked_{pdf_path.name}"
                doc.save(str(unlocked_pdf_path))
                effective_pdf_path = unlocked_pdf_path
            doc.close()
        except Exception as e:
            if isinstance(e, FileValidationException):
                raise
            raise ConversionException(
                message=f"Failed to decrypt password-protected PDF: {e}",
                code="DECRYPTION_ERROR",
            )

    cv: Optional[Converter] = None
    try:
        cv = Converter(str(effective_pdf_path))
        doc_page_count = len(cv.fitz_doc)
        
        target_pages = pages if pages is not None else list(range(doc_page_count))
        total_target_count = len(target_pages)

        if total_target_count == 0:
            raise ConversionException(
                message="No pages selected for conversion.",
                code="NO_PAGES_SELECTED",
            )

        cv_settings = cv.default_settings

        if progress_callback:
            progress_callback(0, total_target_count, "Initializing layout analyzer", 5)

        # Step 1: Load specific page indexes
        cv.load_pages(pages=target_pages)

        # Step 2: Parse document layout structure (margins, sections, headers)
        cv.parse_document(**cv_settings)

        # Step 3: Reconstruct page by page
        for idx, page in enumerate(cv.pages):
            page_num = idx + 1
            percent = 10 + int((idx / total_target_count) * 75)
            if progress_callback:
                progress_callback(
                    page_num,
                    total_target_count,
                    f"Reconstructing page {page_num} of {total_target_count}",
                    percent,
                )
            page.parse(**cv_settings)

        if progress_callback:
            progress_callback(
                total_target_count,
                total_target_count,
                "Packaging Word document layout and styles",
                90,
            )

        # Step 4: Make DOCX
        cv.make_docx(str(docx_path), **cv_settings)

        duration = round(time.time() - start_time, 2)
        docx_size = docx_path.stat().st_size if docx_path.exists() else 0

        if progress_callback:
            progress_callback(
                total_target_count,
                total_target_count,
                "Conversion completed successfully",
                100,
            )

        logger.info(
            f"Successfully converted {total_target_count} page(s) to {docx_path.name} in {duration}s ({docx_size} bytes)"
        )

        return {
            "success": True,
            "pages_converted": total_target_count,
            "duration_seconds": duration,
            "docx_size_bytes": docx_size,
        }

    except Exception as e:
        logger.error(f"Conversion failed for {pdf_path.name}: {e}", exc_info=True)
        if isinstance(e, (FileValidationException, ConversionException)):
            raise
        raise ConversionException(
            message=f"Layout reconstruction failed: {str(e)}",
            code="CONVERSION_ERROR",
            details={"error_detail": str(e)},
        )
    finally:
        if cv:
            try:
                cv.close()
            except Exception:
                pass
        # Clean up unencrypted temporary PDF if one was created
        if unlocked_pdf_path and unlocked_pdf_path.exists():
            try:
                unlocked_pdf_path.unlink(missing_ok=True)
            except Exception:
                pass


async def convert_pdf_async(
    pdf_path: Path,
    docx_path: Path,
    pages: Optional[List[int]] = None,
    password: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str, int], None]] = None,
    timeout_seconds: Optional[int] = None,
) -> dict:
    """
    Executes conversion asynchronously in a separate thread/process with a timeout watchdog.
    """
    timeout = timeout_seconds or settings.CONVERSION_TIMEOUT_SECONDS

    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(
                None,
                convert_pdf_sync,
                pdf_path,
                docx_path,
                pages,
                password,
                progress_callback,
            ),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        raise ConversionException(
            message=f"Conversion timed out after {timeout} seconds.",
            code="CONVERSION_TIMEOUT",
            details={"timeout_seconds": timeout},
        )

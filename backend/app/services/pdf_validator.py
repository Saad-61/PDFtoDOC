import logging
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF

from app.core.config import settings
from app.core.exceptions import FileValidationException, PasswordRequiredException
from app.schemas.conversion import ValidationResult, PageDimension

logger = logging.getLogger("pdf2docx.validator")


class PDFValidator:
    """
    Validates structural integrity, magic bytes, encryption, size, and raster/scanned nature of PDF files.
    """

    MAGIC_HEADER = b"%PDF-"

    @classmethod
    def verify_magic_bytes(cls, file_path: Path) -> None:
        """
        Validates the PDF magic bytes (%PDF-) at the file head.
        """
        if not file_path.exists():
            raise FileValidationException(
                message="File not found on server.",
                code="FILE_NOT_FOUND",
            )
        
        if file_path.stat().st_size == 0:
            raise FileValidationException(
                message="Uploaded file is empty (0 bytes).",
                code="EMPTY_FILE",
            )

        with open(file_path, "rb") as f:
            header = f.read(1024)
            if cls.MAGIC_HEADER not in header:
                raise FileValidationException(
                    message="Invalid file format: Missing '%PDF-' magic header.",
                    code="INVALID_PDF_HEADER",
                )

    @classmethod
    def validate(
        cls,
        file_path: Path,
        password: Optional[str] = None,
        raise_on_encrypted: bool = True,
    ) -> ValidationResult:
        """
        Inspects PDF structure, validates encryption/password, checks page counts,
        and determines whether the document is digital text or a scanned raster image.
        """
        cls.verify_magic_bytes(file_path)

        try:
            doc = fitz.open(str(file_path))
        except Exception as e:
            logger.warning(f"PyMuPDF failed to parse {file_path}: {e}")
            raise FileValidationException(
                message="Corrupt or malformed PDF structure.",
                code="MALFORMED_PDF",
                details={"error": str(e)},
            )

        try:
            is_encrypted = doc.is_encrypted
            is_authenticated = not is_encrypted

            if is_encrypted:
                if not password:
                    if raise_on_encrypted:
                        raise PasswordRequiredException(
                            message="The document is password-protected. Please provide the decryption password.",
                            details={"is_encrypted": True},
                        )
                else:
                    auth_result = doc.authenticate(password)
                    if auth_result == 0:
                        raise FileValidationException(
                            message="Incorrect password provided for encrypted PDF.",
                            code="INVALID_PASSWORD",
                            details={"is_encrypted": True},
                        )
                    is_authenticated = True

            total_pages = doc.page_count
            if total_pages == 0:
                raise FileValidationException(
                    message="Document contains 0 pages.",
                    code="EMPTY_PAGES",
                )

            if total_pages > settings.MAX_PAGE_COUNT:
                raise FileValidationException(
                    message=f"Document exceeds maximum allowed limit of {settings.MAX_PAGE_COUNT} pages (contains {total_pages} pages).",
                    code="PAGE_LIMIT_EXCEEDED",
                    details={"total_pages": total_pages, "max_allowed": settings.MAX_PAGE_COUNT},
                )

            # Heuristic check for Scanned / Raster Image PDF
            sample_page_count = min(5, total_pages)
            total_text_chars = 0
            total_images = 0

            dimensions = []
            for i in range(total_pages):
                page = doc[i]
                rect = page.rect
                dimensions.append(PageDimension(
                    page_number=i + 1,
                    width=round(rect.width, 2),
                    height=round(rect.height, 2),
                ))

                if i < sample_page_count and is_authenticated:
                    text = page.get_text().strip()
                    total_text_chars += len(text)
                    total_images += len(page.get_images())

            # If almost no selectable text characters exist across sampled pages and images are present
            is_scanned = (total_text_chars < 30 and total_images >= 1)

            # Metadata extraction
            meta = doc.metadata or {}
            title = meta.get("title")
            author = meta.get("author")
            creator = meta.get("creator")

            return ValidationResult(
                is_valid=True,
                filename=file_path.name,
                file_size_bytes=file_path.stat().st_size,
                total_pages=total_pages,
                is_encrypted=is_encrypted,
                is_scanned=is_scanned,
                title=title if title and title.strip() else None,
                author=author if author and author.strip() else None,
                creator=creator if creator and creator.strip() else None,
                page_dimensions=dimensions,
            )

        finally:
            doc.close()


pdf_validator = PDFValidator()

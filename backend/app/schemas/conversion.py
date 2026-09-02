from typing import List, Optional
from pydantic import BaseModel, Field


class PageDimension(BaseModel):
    page_number: int
    width: float
    height: float


class ValidationResult(BaseModel):
    """
    Metadata and security integrity metrics resulting from PDF validation.
    """
    is_valid: bool = True
    filename: str
    file_size_bytes: int
    total_pages: int
    is_encrypted: bool = False
    is_scanned: bool = False
    title: Optional[str] = None
    author: Optional[str] = None
    creator: Optional[str] = None
    page_dimensions: List[PageDimension] = Field(default_factory=list)


class ConversionOptions(BaseModel):
    """
    Options passed to customize the PDF to DOCX conversion process.
    """
    password: Optional[str] = Field(None, description="Password to decrypt protected PDFs")
    page_range: Optional[str] = Field(None, description="Page range filter (e.g. '1-3, 5, 8')")
    docx_filename: Optional[str] = Field(None, description="Custom name for the generated DOCX file")


class ConversionResult(BaseModel):
    """
    Outcome metadata of a completed conversion.
    """
    success: bool = True
    session_id: str
    docx_filename: str
    docx_size_bytes: int
    pages_converted: int
    conversion_duration_seconds: float

import urllib.parse
import re
from pathlib import Path


def sanitize_filename(filename: str, default_name: str = "converted_document") -> str:
    """
    Sanitizes a filename to avoid path traversal and illegal filesystem characters.
    Preserves Unicode characters for international languages.
    """
    if not filename or not filename.strip():
        return default_name

    # Strip directory paths
    base_name = Path(filename).name

    # Remove dangerous characters (/ \ : * ? " < > | \0)
    cleaned = re.sub(r'[/\\:*?"<>|\x00]', '_', base_name)
    cleaned = cleaned.strip('. ')

    return cleaned if cleaned else default_name


def get_docx_filename(pdf_filename: str) -> str:
    """
    Replaces .pdf extension with .docx while maintaining the base name.
    """
    safe_name = sanitize_filename(pdf_filename, default_name="document.pdf")
    if safe_name.lower().endswith(".pdf"):
        return safe_name[:-4] + ".docx"
    return safe_name + ".docx"


def build_content_disposition_header(filename: str, disposition: str = "attachment") -> str:
    """
    Constructs an RFC 5987 / RFC 6266 compliant Content-Disposition header.
    Provides an ASCII fallback alongside a UTF-8 encoded filename* parameter
    to safely support special and international characters (e.g., Arabic, Japanese, accents).
    
    Example output:
    attachment; filename="resume.docx"; filename*=UTF-8''r%C3%A9sum%C3%A9.docx
    """
    safe_name = sanitize_filename(filename)
    # ASCII-only fallback filename
    ascii_name = re.sub(r'[^\x20-\x7E]', '_', safe_name).replace('"', '\\"')
    if not ascii_name:
        ascii_name = "document.docx"

    # RFC 5987 percent-encoded UTF-8 filename
    encoded_utf8_name = urllib.parse.quote(safe_name, encoding="utf-8")

    return f'{disposition}; filename="{ascii_name}"; filename*=UTF-8\'\'{encoded_utf8_name}'

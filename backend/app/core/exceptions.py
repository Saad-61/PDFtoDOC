from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: dict = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class FileValidationException(AppException):
    """Raised when an uploaded file fails format or integrity validation."""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", details: dict = None):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class PasswordRequiredException(AppException):
    """Raised when a PDF is encrypted and requires a password to decrypt."""
    def __init__(self, message: str = "Document is password protected and requires unlocking.", details: dict = None):
        super().__init__(
            message=message,
            code="PASSWORD_REQUIRED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class ConversionException(AppException):
    """Raised when PDF-to-DOCX conversion fails."""
    def __init__(self, message: str, code: str = "CONVERSION_FAILED", details: dict = None):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ResourceNotFoundException(AppException):
    """Raised when a requested session or job does not exist."""
    def __init__(self, message: str = "The requested resource was not found.", code: str = "RESOURCE_NOT_FOUND"):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_404_NOT_FOUND,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Formats AppException into standardized JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during processing.",
                "details": {"error_type": type(exc).__name__},
            },
        },
    )

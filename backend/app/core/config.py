from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings for the PDF to DOCX Converter Backend.
    Values can be overridden via environment variables or a .env file.
    """
    # Core API metadata
    PROJECT_NAME: str = "Old Money PDF to DOCX Converter"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS configuration
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Ingestion & Conversion Guardrails
    MAX_FILE_SIZE_MB: int = 50
    MAX_PAGE_COUNT: int = 250
    CONVERSION_TIMEOUT_SECONDS: int = 120
    MAX_WORKERS: int = 4

    # Ephemeral Storage Management
    TEMP_DIR_ROOT: Path = Path(Path.home() / ".pdf2docx_temp")
    SESSION_EXPIRY_MINUTES: int = 15
    GC_INTERVAL_SECONDS: int = 300  # Run garbage collector every 5 mins

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()

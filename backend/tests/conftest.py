import os
import sys
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.storage import EphemeralStorageManager


@pytest.fixture
def custom_storage(tmp_path):
    """Provides an isolated EphemeralStorageManager backed by a tmp directory."""
    mgr = EphemeralStorageManager(root_dir=tmp_path / "pdf_temp_tests")
    return mgr


@pytest_asyncio.fixture
async def async_client():
    """Provides an async HTTP client for FastAPI testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

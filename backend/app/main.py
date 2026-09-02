import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler, generic_exception_handler
from app.api.v1.router import api_router
from app.services.storage import storage_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pdf2docx.main")


async def periodic_garbage_collector():
    """
    Background worker that runs periodically to sweep dangling expired temp files.
    """
    logger.info("Starting ephemeral storage garbage collector daemon...")
    while True:
        try:
            await asyncio.sleep(settings.GC_INTERVAL_SECONDS)
            pruned = storage_manager.cleanup_expired_sessions()
            if pruned > 0:
                logger.info(f"Garbage collector swept {pruned} expired session(s).")
        except asyncio.CancelledError:
            logger.info("Garbage collector daemon stopped.")
            break
        except Exception as e:
            logger.error(f"Error during periodic garbage collection: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown hooks.
    """
    # Startup
    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}")
    storage_manager._ensure_root_dir()
    # Prune any leftover sessions from previous server runs
    storage_manager.cleanup_expired_sessions(max_age_minutes=0)
    
    gc_task = asyncio.create_task(periodic_garbage_collector())
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    gc_task.cancel()
    try:
        await gc_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="High-performance, privacy-first PDF to DOCX conversion backend with an 'Old Money' tactile interface.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """Root status greeting with docs reference."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }

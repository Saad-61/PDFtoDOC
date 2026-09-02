from fastapi import APIRouter
from app.api.v1.endpoints import health, convert, jobs

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(health.router, tags=["Health & Telemetry"])
api_router.include_router(convert.router, tags=["PDF Ingestion & Conversion"])
api_router.include_router(jobs.router, tags=["Conversion Jobs & SSE Streams"])

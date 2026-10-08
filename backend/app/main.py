from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.documents import router as documents_router
from backend.app.core.config import settings
from backend.app.schemas.document import HealthCheckResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Documents",
            "description": "Document ingestion, preprocessing, OCR analysis, and data extraction endpoints.",
        },
        {
            "name": "System",
            "description": "Service health checks and diagnostics.",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)


@app.get(
    "/",
    tags=["System"],
    summary="API Root Information",
    description="Welcome endpoint providing API status and navigation links.",
)
def api_root():
    return {
        "service": f"{settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "samples": "/documents/samples",
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["System"],
    summary="Service Health Check",
    description="Check the availability and operational status of the DocuVoice backend API.",
)
def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(
        status="healthy",
        service=f"{settings.PROJECT_NAME} API",
        version=settings.VERSION,
    )
from fastapi import FastAPI

from backend.app.api.documents import router as documents_router


app = FastAPI(
    title="DocuVoice",
    description="Intelligent Document and Invoice Processing System",
    version="0.1.0",
)


app.include_router(documents_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DocuVoice API",
        "version": "0.1.0",
    }
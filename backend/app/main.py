from fastapi import FastAPI

app = FastAPI(
    title="DocuVoice",
    description="Intelligent Document and Invoice Processing System",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

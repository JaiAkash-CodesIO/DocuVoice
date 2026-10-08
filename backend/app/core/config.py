import os
from pathlib import Path
from typing import List


class Settings:
    PROJECT_NAME: str = "DocuVoice"
    PROJECT_DESCRIPTION: str = "Intelligent Document Processing (IDP) System"
    VERSION: str = "1.0.0"

    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))
    PROCESSED_DIR: Path = Path(os.getenv("PROCESSED_DIR", "processed"))
    SAMPLES_DIR: Path = Path(os.getenv("SAMPLES_DIR", "samples"))

    # File limitations
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg"}
    MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024))  # 10 MB default

    # CORS origins
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:80,http://localhost:3000,http://127.0.0.1:3000,http://localhost,http://127.0.0.1",
        ).split(",")
        if origin.strip()
    ]

    # Preprocessing defaults
    TARGET_WIDTH: int = int(os.getenv("TARGET_WIDTH", 1600))
    MINIMUM_WIDTH: int = int(os.getenv("MINIMUM_WIDTH", 1400))


settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

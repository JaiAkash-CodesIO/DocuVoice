from pathlib import Path
from uuid import uuid4
from backend.app.services.preprocessing.image_processor import ImageProcessor

from fastapi import APIRouter, File, HTTPException, UploadFile


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024

@router.post("/{document_id}/preprocess")
async def preprocess_document(document_id: str):
    matching_files = list(UPLOAD_DIR.glob(f"{document_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    input_file = matching_files[0]

    if input_file.suffix.lower() == ".pdf":
        raise HTTPException(
            status_code=400,
            detail="PDF preprocessing will be handled by the OCR pipeline",
        )

    processed_dir = Path("processed")
    output_file = processed_dir / f"{document_id}_processed.png"

    processor = ImageProcessor()

    try:
        result = processor.process(
            str(input_file),
            str(output_file),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "document_id": document_id,
        "status": "preprocessed",
        "preprocessing": result,
    }
@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file name provided",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Supported formats: PDF, PNG, JPG, JPEG",
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 10 MB limit",
        )

    document_id = str(uuid4())
    stored_filename = f"{document_id}{extension}"
    file_path = UPLOAD_DIR / stored_filename

    file_path.write_bytes(content)

    return {
        "document_id": document_id,
        "original_filename": file.filename,
        "stored_filename": stored_filename,
        "file_type": extension.lstrip("."),
        "file_size": len(content),
        "status": "uploaded",
    }

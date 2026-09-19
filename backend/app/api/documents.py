from pathlib import Path
from uuid import uuid4

from backend.app.services.ocr.ocr_service import OCRService
from backend.app.services.preprocessing.image_processor import ImageProcessor

from fastapi import APIRouter, File, HTTPException, UploadFile
from backend.app.services.extraction.document_extractor import DocumentExtractor

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024



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
@router.post("/{document_id}/preprocess")
async def preprocess_document(document_id: str):
    matching_files = list(UPLOAD_DIR.glob(f"{document_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )
#modified
    input_file = matching_files[0]

    processed_dir = Path("processed")
    processor = ImageProcessor()

    if input_file.suffix.lower() == ".pdf":
        try:
            pages = processor.process_pdf(
                str(input_file),
                str(processed_dir),
            )

        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc

        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"PDF preprocessing failed: {exc}",
            ) from exc

        return {
            "document_id": document_id,
            "status": "preprocessed",
            "preprocessing": {
                "file_type": "pdf",
                "page_count": len(pages),
                "pages": pages,
            },
        }

    output_file = (
        processed_dir
        / f"{document_id}_processed.png"
    )

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
@router.post("/{document_id}/ocr")
async def process_ocr(document_id: str):
    matching_files = list(UPLOAD_DIR.glob(f"{document_id}.*"))

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    input_file = matching_files[0]

    
    processed_dir = Path("processed")
    ocr_service = OCRService()

    if input_file.suffix.lower() == ".pdf":
        processed_files = sorted(
            processed_dir.glob(
                f"{document_id}_page_*.png"
            )
        )

        if not processed_files:
            raise HTTPException(
                status_code=400,
                detail="Document has not been preprocessed",
            )

        page_results = []

        try:
            for page_number, processed_file in enumerate(
                processed_files,
                start=1,
            ):
                result = ocr_service.extract(
                    str(processed_file)
                )

                page_results.append(
                    {
                        "page_number": page_number,
                        "text": result["text"],
                        "average_confidence": result[
                            "average_confidence"
                        ],
                        "word_count": result["word_count"],
                        "words": result["words"],
                    }
                )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"OCR processing failed: {exc}",
            ) from exc

        all_words = []

        for page in page_results:
            all_words.extend(page["words"])

        all_text = "\n\n".join(
            page["text"]
            for page in page_results
            if page["text"]
        )

        average_confidence = (
            sum(
                page["average_confidence"]
                for page in page_results
            )
            / len(page_results)
            if page_results
            else 0.0
        )

        return {
            "document_id": document_id,
            "status": "processed",
            "ocr": {
                "text": all_text,
                "average_confidence": round(
                    average_confidence,
                    2,
                ),
                "word_count": len(all_words),
                "words": all_words,
                "page_count": len(page_results),
                "pages": page_results,
            },
        }

    processed_file = (
        processed_dir
        / f"{document_id}_processed.png"
    )

    if not processed_file.exists():
        raise HTTPException(
            status_code=400,
            detail="Document has not been preprocessed",
        )

    try:
        result = ocr_service.extract(
            str(processed_file)
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {exc}",
        ) from exc

    return {
        "document_id": document_id,
        "status": "processed",
        "ocr": result,
    }

#new endpoint

@router.post("/{document_id}/extract")
async def extract_document(document_id: str):
    matching_files = list(
        UPLOAD_DIR.glob(f"{document_id}.*")
    )

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    input_file = matching_files[0]

    try:
        ocr_service = OCRService()
        extractor = DocumentExtractor()

        processed_dir = Path("processed")

        if input_file.suffix.lower() == ".pdf":
            processed_files = sorted(
                processed_dir.glob(
                    f"{document_id}_page_*.png"
                )
            )

            if not processed_files:
                raise HTTPException(
                    status_code=400,
                    detail="Document has not been preprocessed",
                )

            page_results = []

            for page_number, processed_file in enumerate(
                processed_files,
                start=1,
            ):
                ocr_result = ocr_service.extract(
                    str(processed_file)
                )

                page_results.append(
                    {
                        "page_number": page_number,
                        "ocr": ocr_result,
                    }
                )

            combined_text = "\n\n".join(
                page["ocr"]["text"]
                for page in page_results
                if page["ocr"]["text"]
            )

            combined_words = []

            for page in page_results:
                combined_words.extend(
                    page["ocr"]["words"]
                )

            combined_confidence = (
                sum(
                    page["ocr"]["average_confidence"]
                    for page in page_results
                )
                / len(page_results)
                if page_results
                else 0.0
            )

            combined_ocr_result = {
                "text": combined_text,
                "average_confidence": round(
                    combined_confidence,
                    2,
                ),
                "word_count": len(combined_words),
                "words": combined_words,
            }

            extraction_result = extractor.extract(
                combined_ocr_result
            )

            extraction_result["pages"] = page_results

        else:
            processed_file = (
                processed_dir
                / f"{document_id}_processed.png"
            )

            if not processed_file.exists():
                raise HTTPException(
                    status_code=400,
                    detail="Document has not been preprocessed",
                )

            ocr_result = ocr_service.extract(
                str(processed_file)
            )

            extraction_result = extractor.extract(
                ocr_result
            )

    except HTTPException:
        raise

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document extraction failed: {exc}",
        ) from exc

    return {
        "document_id": document_id,
        "status": "processed",
        "extraction": extraction_result,
    }
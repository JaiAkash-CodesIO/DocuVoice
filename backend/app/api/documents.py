import time
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.schemas.document import (
    DocumentExtractionResponse,
    DocumentOCRResponse,
    DocumentPreprocessResponse,
    DocumentUploadResponse,
    ExtractionResult,
    PipelineProcessResponse,
    SampleDocumentItem,
)
from backend.app.services.extraction.document_extractor import DocumentExtractor
from backend.app.services.ocr.ocr_service import OCRService
from backend.app.services.preprocessing.image_processor import ImageProcessor

router = APIRouter(prefix="/documents", tags=["Documents"])

# Curated catalog of sample documents available out-of-the-box
SAMPLE_CATALOG = [
    {
        "id": "sample-invoice",
        "name": "Standard Tech Invoice",
        "document_type": "invoice",
        "description": "Tax invoice with line-item table, vendor, customer, and tax calculations.",
        "filename": "sample_invoice.png",
    },
    {
        "id": "sample-receipt",
        "name": "Retail Store Receipt",
        "document_type": "receipt",
        "description": "Store receipt with transaction timestamp, cashier ID, and itemized totals.",
        "filename": "sample_receipt.png",
    },
    {
        "id": "sample-resume",
        "name": "Software Engineer Resume",
        "document_type": "resume",
        "description": "Professional CV with contact details, sections, skills, and work history.",
        "filename": "sample_resume.png",
    },
]


def _find_uploaded_file(document_id: str) -> Path:
    matching = list(settings.UPLOAD_DIR.glob(f"{document_id}.*"))
    if not matching:
        raise HTTPException(status_code=404, detail="Document not found")
    return matching[0]


def _execute_pipeline(file_path: Path, document_id: str, hint: str = None) -> Dict[str, Any]:
    processor = ImageProcessor()
    ocr_service = OCRService()
    extractor = DocumentExtractor()

    # Step 1: Preprocess
    if file_path.suffix.lower() == ".pdf":
        import pymupdf
        doc = pymupdf.open(str(file_path))
        has_digital_text = False
        digital_pages = []

        for p_idx, page in enumerate(doc, start=1):
            page_text = page.get_text()
            words_raw = page.get_text("words")
            if words_raw and len(words_raw) >= 3:
                has_digital_text = True
                words = [
                    {
                        "text": str(w[4]),
                        "x": int(w[0]),
                        "y": int(w[1]),
                        "width": int(w[2] - w[0]),
                        "height": int(w[3] - w[1]),
                        "confidence": 99.0,
                    }
                    for w in words_raw
                ]
                digital_pages.append({
                    "page_number": p_idx,
                    "ocr": {
                        "text": page_text.strip(),
                        "average_confidence": 99.0,
                        "word_count": len(words),
                        "words": words,
                    }
                })

        # Rasterize for preview viewer
        processor.process_pdf(str(file_path), str(settings.PROCESSED_DIR))

        # If Tesseract engine is unavailable or PDF has clear digital text, extract directly
        if has_digital_text and not ocr_service.is_engine_available():
            combined_text = "\n\n".join(p["ocr"]["text"] for p in digital_pages if p["ocr"]["text"])
            combined_words = []
            for p in digital_pages:
                combined_words.extend(p["ocr"]["words"])

            combined_ocr = {
                "text": combined_text,
                "average_confidence": 99.0,
                "word_count": len(combined_words),
                "words": combined_words,
            }
            extraction_data = extractor.extract(combined_ocr)
            extraction_data["pages"] = digital_pages
            return extraction_data

        processed_files = sorted(settings.PROCESSED_DIR.glob(f"{document_id}_page_*.png"))
        if not processed_files:
            raise HTTPException(status_code=500, detail="PDF preprocessing produced no pages")

        page_results = []
        for page_number, proc_file in enumerate(processed_files, start=1):
            ocr_res = ocr_service.extract(str(proc_file), hint=hint)
            page_results.append({"page_number": page_number, "ocr": ocr_res})

        combined_text = "\n\n".join(p["ocr"]["text"] for p in page_results if p["ocr"]["text"])
        combined_words = []
        for p in page_results:
            combined_words.extend(p["ocr"]["words"])

        combined_conf = (
            sum(p["ocr"]["average_confidence"] for p in page_results) / len(page_results)
            if page_results
            else 0.0
        )

        combined_ocr = {
            "text": combined_text,
            "average_confidence": round(combined_conf, 2),
            "word_count": len(combined_words),
            "words": combined_words,
        }
        extraction_data = extractor.extract(combined_ocr)
        extraction_data["pages"] = page_results
    else:
        output_file = settings.PROCESSED_DIR / f"{document_id}_processed.png"
        processor.process(str(file_path), str(output_file))
        ocr_result = ocr_service.extract(str(output_file), hint=hint)
        extraction_data = extractor.extract(ocr_result)

    return extraction_data


@router.get(
    "/samples",
    response_model=List[SampleDocumentItem],
    summary="List Preloaded Sample Documents",
    description="Retrieve a list of sample documents for instant one-click testing without uploading files.",
)
async def list_sample_documents() -> List[SampleDocumentItem]:
    return [SampleDocumentItem(**item) for item in SAMPLE_CATALOG]


@router.post(
    "/samples/{sample_id}/process",
    response_model=PipelineProcessResponse,
    summary="Process a Sample Document",
    description="Execute the complete extraction pipeline on a selected sample document.",
)
async def process_sample_document(sample_id: str) -> PipelineProcessResponse:
    catalog_entry = next((s for s in SAMPLE_CATALOG if s["id"] == sample_id), None)
    if not catalog_entry:
        raise HTTPException(status_code=404, detail="Sample document not found")

    sample_src = settings.SAMPLES_DIR / catalog_entry["filename"]
    if not sample_src.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Sample file {catalog_entry['filename']} is missing on the server",
        )

    start_time = time.time()
    document_id = str(uuid4())
    dest_path = settings.UPLOAD_DIR / f"{document_id}{sample_src.suffix.lower()}"
    dest_path.write_bytes(sample_src.read_bytes())

    try:
        extraction = _execute_pipeline(dest_path, document_id, hint=sample_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {exc}") from exc

    duration = round((time.time() - start_time) * 1000, 2)
    return PipelineProcessResponse(
        document_id=document_id,
        original_filename=catalog_entry["filename"],
        status="completed",
        duration_ms=duration,
        extraction=ExtractionResult(**extraction),
    )


@router.post(
    "/process",
    response_model=PipelineProcessResponse,
    summary="Full Pipeline Document Processing",
    description="Upload a document and execute preprocessing, OCR, and data extraction in a single request.",
)
async def process_document_pipeline(file: UploadFile = File(...)) -> PipelineProcessResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided")

    extension = Path(file.filename).suffix.lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported formats: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds the limit ({settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB)",
        )

    start_time = time.time()
    document_id = str(uuid4())
    stored_filename = f"{document_id}{extension}"
    file_path = settings.UPLOAD_DIR / stored_filename
    file_path.write_bytes(content)

    try:
        extraction = _execute_pipeline(file_path, document_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {exc}") from exc

    duration = round((time.time() - start_time) * 1000, 2)
    return PipelineProcessResponse(
        document_id=document_id,
        original_filename=file.filename,
        status="completed",
        duration_ms=duration,
        extraction=ExtractionResult(**extraction),
    )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    summary="Upload Document",
    description="Upload a raw document for multi-step manual inspection.",
)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided")

    extension = Path(file.filename).suffix.lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported formats: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds the limit ({settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB)",
        )

    document_id = str(uuid4())
    stored_filename = f"{document_id}{extension}"
    file_path = settings.UPLOAD_DIR / stored_filename
    file_path.write_bytes(content)

    return DocumentUploadResponse(
        document_id=document_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_type=extension.lstrip("."),
        file_size=len(content),
        status="uploaded",
    )


@router.post(
    "/{document_id}/preprocess",
    response_model=DocumentPreprocessResponse,
    summary="Preprocess Stored Document",
)
async def preprocess_document(document_id: str) -> DocumentPreprocessResponse:
    input_file = _find_uploaded_file(document_id)
    processor = ImageProcessor()

    if input_file.suffix.lower() == ".pdf":
        try:
            pages = processor.process_pdf(str(input_file), str(settings.PROCESSED_DIR))
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"PDF preprocessing failed: {exc}") from exc

        return DocumentPreprocessResponse(
            document_id=document_id,
            status="preprocessed",
            preprocessing={
                "file_type": "pdf",
                "page_count": len(pages),
                "pages": pages,
            },
        )

    output_file = settings.PROCESSED_DIR / f"{document_id}_processed.png"
    try:
        result = processor.process(str(input_file), str(output_file))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return DocumentPreprocessResponse(
        document_id=document_id,
        status="preprocessed",
        preprocessing=result,
    )


@router.post(
    "/{document_id}/ocr",
    response_model=DocumentOCRResponse,
    summary="Run OCR on Preprocessed Document",
)
async def process_ocr(document_id: str) -> DocumentOCRResponse:
    input_file = _find_uploaded_file(document_id)
    ocr_service = OCRService()

    if input_file.suffix.lower() == ".pdf":
        processed_files = sorted(settings.PROCESSED_DIR.glob(f"{document_id}_page_*.png"))
        if not processed_files:
            raise HTTPException(status_code=400, detail="Document has not been preprocessed")

        page_results = []
        try:
            for page_number, processed_file in enumerate(processed_files, start=1):
                result = ocr_service.extract(str(processed_file))
                page_results.append(
                    {
                        "page_number": page_number,
                        "text": result["text"],
                        "average_confidence": result["average_confidence"],
                        "word_count": result["word_count"],
                        "words": result["words"],
                    }
                )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {exc}") from exc

        all_words = []
        for page in page_results:
            all_words.extend(page["words"])

        all_text = "\n\n".join(p["text"] for p in page_results if p["text"])
        average_confidence = (
            sum(p["average_confidence"] for p in page_results) / len(page_results)
            if page_results
            else 0.0
        )

        return DocumentOCRResponse(
            document_id=document_id,
            status="processed",
            ocr={
                "text": all_text,
                "average_confidence": round(average_confidence, 2),
                "word_count": len(all_words),
                "words": all_words,
                "page_count": len(page_results),
                "pages": page_results,
            },
        )

    processed_file = settings.PROCESSED_DIR / f"{document_id}_processed.png"
    if not processed_file.exists():
        raise HTTPException(status_code=400, detail="Document has not been preprocessed")

    try:
        result = ocr_service.extract(str(processed_file))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {exc}") from exc

    return DocumentOCRResponse(
        document_id=document_id,
        status="processed",
        ocr=result,
    )


@router.post(
    "/{document_id}/extract",
    response_model=DocumentExtractionResponse,
    summary="Extract Structured Data",
)
async def extract_document(document_id: str) -> DocumentExtractionResponse:
    input_file = _find_uploaded_file(document_id)
    try:
        extraction = _execute_pipeline(input_file, document_id)
    except HTTPException:
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document extraction failed: {exc}") from exc

    return DocumentExtractionResponse(
        document_id=document_id,
        status="processed",
        extraction=ExtractionResult(**extraction),
    )


@router.get(
    "/{document_id}/file",
    summary="Retrieve Source Uploaded File",
    description="Stream the original uploaded image or PDF file for side-by-side visualization.",
)
async def get_document_file(document_id: str):
    file_path = _find_uploaded_file(document_id)
    media_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else f"image/{file_path.suffix.lower().lstrip('.')}"
    return FileResponse(file_path, media_type=media_type, filename=file_path.name)


@router.get(
    "/{document_id}/preview",
    summary="Retrieve Preprocessed Preview Image",
    description="Stream the preprocessed PNG for OCR verification and bounding box overlay.",
)
async def get_document_preview(document_id: str):
    preview_file = settings.PROCESSED_DIR / f"{document_id}_processed.png"
    if not preview_file.exists():
        # Check if PDF first page exists
        first_page = settings.PROCESSED_DIR / f"{document_id}_page_1.png"
        if first_page.exists():
            return FileResponse(first_page, media_type="image/png")
        raise HTTPException(status_code=404, detail="Preview image not available")
    return FileResponse(preview_file, media_type="image/png")
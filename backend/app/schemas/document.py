from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WordBox(BaseModel):
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float


class FieldItem(BaseModel):
    key: str
    value: str


class SectionItem(BaseModel):
    title: str
    content: str


class TableStructure(BaseModel):
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)


class EntitiesData(BaseModel):
    emails: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)


class OCRSummary(BaseModel):
    average_confidence: float = 0.0
    word_count: int = 0


class PageOCRResult(BaseModel):
    page_number: int
    text: str = ""
    average_confidence: float = 0.0
    word_count: int = 0
    words: List[WordBox] = Field(default_factory=list)


class OCRResult(BaseModel):
    text: str = ""
    average_confidence: float = 0.0
    word_count: int = 0
    words: List[WordBox] = Field(default_factory=list)
    selected_variant: Optional[str] = None
    selected_psm: Optional[int] = None
    page_count: Optional[int] = None
    pages: Optional[List[Dict[str, Any]]] = None


class ExtractionResult(BaseModel):
    document_type: str = "general_document"
    fields: List[FieldItem] = Field(default_factory=list)
    sections: List[SectionItem] = Field(default_factory=list)
    tables: List[TableStructure] = Field(default_factory=list)
    entities: EntitiesData = Field(default_factory=EntitiesData)
    text: str = ""
    ocr: OCRSummary = Field(default_factory=OCRSummary)
    pages: Optional[List[Dict[str, Any]]] = None


class DocumentUploadResponse(BaseModel):
    document_id: str
    original_filename: str
    stored_filename: str
    file_type: str
    file_size: int
    status: str = "uploaded"


class DocumentPreprocessResponse(BaseModel):
    document_id: str
    status: str = "preprocessed"
    preprocessing: Dict[str, Any]


class DocumentOCRResponse(BaseModel):
    document_id: str
    status: str = "processed"
    ocr: Dict[str, Any]


class DocumentExtractionResponse(BaseModel):
    document_id: str
    status: str = "processed"
    extraction: ExtractionResult


class PipelineProcessResponse(BaseModel):
    document_id: str
    original_filename: str
    status: str = "completed"
    duration_ms: float
    extraction: ExtractionResult


class SampleDocumentItem(BaseModel):
    id: str
    name: str
    document_type: str
    description: str
    filename: str


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str

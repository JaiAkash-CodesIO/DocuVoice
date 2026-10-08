from backend.app.services.extraction.document_extractor import DocumentExtractor


def test_detect_document_type_invoice():
    extractor = DocumentExtractor()
    text = "TAX INVOICE\nInvoice Number: INV-001\nSubtotal: 100\nAmount Due: 100"
    assert extractor._detect_document_type(text) == "invoice"


def test_detect_document_type_resume():
    extractor = DocumentExtractor()
    text = "Curriculum Vitae\nProfessional Experience\nEducation\nSkills"
    assert extractor._detect_document_type(text) == "resume"


def test_detect_document_type_receipt():
    extractor = DocumentExtractor()
    text = "Supermarket Receipt\nCashier: Mary\nThank you for your purchase"
    assert extractor._detect_document_type(text) == "receipt"


def test_detect_document_type_general():
    extractor = DocumentExtractor()
    text = "Random notes without recognizable keywords"
    assert extractor._detect_document_type(text) == "general_document"


def test_extract_fields():
    extractor = DocumentExtractor()
    text = "Invoice Number: INV-990\nVendor: Acme Corp\nTotal: $500"
    fields = extractor._extract_fields(text)
    field_keys = [f["key"] for f in fields]
    assert "Invoice Number" in field_keys
    assert "Vendor" in field_keys
    assert "Total" in field_keys


def test_extract_entities():
    extractor = DocumentExtractor()
    text = (
        "Contact us at support@example.com or sales@test.org. "
        "Call +1 800-555-1234. Meeting date is 12-10-2026. "
        "Visit https://example.com for info."
    )
    entities = extractor._extract_entities(text)
    assert "support@example.com" in entities["emails"]
    assert "sales@test.org" in entities["emails"]
    assert len(entities["phone_numbers"]) > 0
    assert "12-10-2026" in entities["dates"]
    assert "https://example.com" in entities["urls"]


def test_full_extraction(mock_ocr_invoice_payload):
    extractor = DocumentExtractor()
    result = extractor.extract(mock_ocr_invoice_payload)

    assert result["document_type"] == "invoice"
    assert len(result["fields"]) > 0
    assert "contact@acmecorp.com" in result["entities"]["emails"]
    assert len(result["tables"]) == 1
    assert result["tables"][0]["headers"] == ["Product", "Qty", "Price", "Total"]
    assert result["tables"][0]["rows"][0] == ["Widget", "5", "100", "500"]

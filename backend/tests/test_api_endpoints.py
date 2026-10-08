from unittest.mock import patch


def test_api_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "DocuVoice" in data["service"]
    assert data["status"] == "online"
    assert "/docs" in data["documentation"]


def test_favicon(client):
    response = client.get("/favicon.ico")
    assert response.status_code == 204


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "DocuVoice" in data["service"]
    assert "version" in data


def test_list_samples(client):
    response = client.get("/documents/samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 3
    sample_ids = [s["id"] for s in samples]
    assert "sample-invoice" in sample_ids
    assert "sample-receipt" in sample_ids
    assert "sample-resume" in sample_ids


def test_process_sample_document(client, mock_ocr_invoice_payload):
    with patch(
        "backend.app.api.documents.OCRService.extract",
        return_value=mock_ocr_invoice_payload,
    ):
        response = client.post("/documents/samples/sample-invoice/process")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "document_id" in data
        assert "duration_ms" in data
        assert "extraction" in data
        assert data["extraction"]["document_type"] == "invoice"


def test_process_pipeline_endpoint(client, sample_image_bytes, mock_ocr_invoice_payload):
    with patch(
        "backend.app.api.documents.OCRService.extract",
        return_value=mock_ocr_invoice_payload,
    ):
        response = client.post(
            "/documents/process",
            files={"file": ("invoice.png", sample_image_bytes, "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["original_filename"] == "invoice.png"
        assert data["extraction"]["document_type"] == "invoice"


def test_upload_invalid_file_type(client):
    response = client.post(
        "/documents/upload",
        files={"file": ("unsupported.txt", b"plain text", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_valid_document(client, sample_image_bytes):
    response = client.post(
        "/documents/upload",
        files={"file": ("test_doc.png", sample_image_bytes, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "uploaded"
    assert "document_id" in data
    assert data["file_type"] == "png"
    assert data["original_filename"] == "test_doc.png"


def test_fetch_document_file(client, sample_image_bytes):
    # Upload first
    upload_res = client.post(
        "/documents/upload",
        files={"file": ("stream_doc.png", sample_image_bytes, "image/png")},
    )
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["document_id"]

    # Stream back
    file_res = client.get(f"/documents/{doc_id}/file")
    assert file_res.status_code == 200
    assert file_res.headers["content-type"] == "image/png"

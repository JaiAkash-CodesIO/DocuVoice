import io
import pytest
from PIL import Image
from starlette.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    """Create a FastAPI test client instance."""
    return TestClient(app)


@pytest.fixture
def sample_image_bytes():
    """Generate a clean test image in memory as bytes."""
    img = Image.new("RGB", (300, 200), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def mock_ocr_invoice_payload():
    """Mock OCR extraction dictionary for testing invoice classification and parsing."""
    return {
        "text": """
        TAX INVOICE
        Invoice Number: INV-9901
        Invoice Date: 2026-10-15
        Vendor: Acme Corporation
        Customer: Globex International
        Email: contact@acmecorp.com
        Phone: +1 555-019-2834
        Website: https://acmecorp.com

        Product Qty Price Total
        Widget 5 100 500
        Gadget 2 250 500

        Subtotal: 1000
        Tax: 100
        Total: 1100
        """,
        "words": [
            {"text": "Product", "x": 10, "y": 100, "width": 50, "height": 15, "confidence": 95.0},
            {"text": "Qty", "x": 70, "y": 100, "width": 30, "height": 15, "confidence": 95.0},
            {"text": "Price", "x": 110, "y": 100, "width": 40, "height": 15, "confidence": 95.0},
            {"text": "Total", "x": 160, "y": 100, "width": 40, "height": 15, "confidence": 95.0},
            {"text": "Widget", "x": 10, "y": 130, "width": 50, "height": 15, "confidence": 92.0},
            {"text": "5", "x": 70, "y": 130, "width": 20, "height": 15, "confidence": 92.0},
            {"text": "100", "x": 110, "y": 130, "width": 30, "height": 15, "confidence": 92.0},
            {"text": "500", "x": 160, "y": 130, "width": 30, "height": 15, "confidence": 92.0},
        ],
        "average_confidence": 93.5,
        "word_count": 8,
    }

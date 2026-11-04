# Run: pytest backend/tests/unit/processing/chunking/test_invoice_chunker.py -v -s

"""Tests for preprocessing invoice extraction results into vector-ready chunks."""

from backend.processing.chunking.invoice_chunker import chunk_invoice


def make_extraction_result() -> dict:
    """Build an extractor-shaped result with header fields and line items."""
    return {
        "status": "auto_approved",
        "file_name": "invoice.png",
        "invoice": {
            "invoice_number": "INV-001",
            "invoice_date": "2026-01-01",
            "supplier_name": "Acme",
            "customer_name": None,
            "subtotal": "100.00",
            "tax": "10.00",
            "total": "110.00",
            "currency": "USD",
            "line_items": [
                {
                    "description": "Item A",
                    "quantity": 2.0,
                    "unit_price": "10.00",
                    "amount": "20.00",
                },
                {
                    "description": "Item B",
                    "quantity": 1.0,
                    "unit_price": "80.00",
                    "amount": "80.00",
                },
            ],
        },
    }


def test_chunk_invoice_returns_single_chunk() -> None:
    """One parsed invoice produces one chunk with only the requested keys."""
    chunks = chunk_invoice(make_extraction_result())

    assert len(chunks) == 1
    assert set(chunks[0]) == {"file_name", "file_type", "page_no", "text_content"}


def test_chunk_invoice_builds_text_content() -> None:
    """Header fields and line items become comma-separated text lines."""
    lines = chunk_invoice(make_extraction_result())[0]["text_content"].splitlines()

    assert lines[0] == (
        "invoice_number: INV-001, invoice_date: 2026-01-01, "
        "supplier_name: Acme, customer_name: , subtotal: 100.00, "
        "tax: 10.00, total: 110.00, currency: USD"
    )
    assert lines[1] == (
        "description: Item A, quantity: 2.0, unit_price: 10.00, amount: 20.00"
    )
    assert lines[2] == (
        "description: Item B, quantity: 1.0, unit_price: 80.00, amount: 80.00"
    )


def test_chunk_invoice_page_no() -> None:
    """The page number is stored when provided and defaults to None."""
    assert chunk_invoice(make_extraction_result(), page_no=2)[0]["page_no"] == 2
    assert chunk_invoice(make_extraction_result())[0]["page_no"] is None


def test_chunk_invoice_uses_lowercase_extension() -> None:
    """The file type is the lower-case invoice extension."""
    extraction_result = make_extraction_result()
    extraction_result["file_name"] = "invoice.PDF"

    assert chunk_invoice(extraction_result)[0]["file_type"] == ".pdf"


def test_chunk_invoice_without_invoice_returns_no_chunks() -> None:
    """A result without invoice data produces an empty chunk list."""
    assert chunk_invoice({"status": "failed", "file_name": "invoice.png"}) == []

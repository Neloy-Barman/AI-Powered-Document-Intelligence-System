# Run: pytest backend/tests/unit/processing/chunking/test_image_chunker.py -v -s

"""Tests for preprocessing parsed OCR content into vector-ready chunks."""

from backend.processing.chunking.image_chunker import chunk_image


def test_chunk_image_returns_single_chunk() -> None:
    """One parsed image produces one chunk containing its OCR content."""
    chunks = chunk_image(
        {
            "status": "success",
            "file_name": "invoice.png",
            "content": "Invoice INV-001\nTotal 100.50",
        }
    )

    assert chunks == [
        {
            "file_name": "invoice.png",
            "file_type": ".png",
            "text_content": "Invoice INV-001\nTotal 100.50",
        }
    ]


def test_chunk_image_uses_lowercase_extension() -> None:
    """The file type is the lower-case image extension."""
    chunks = chunk_image(
        {
            "status": "success",
            "file_name": "receipt.JPG",
            "content": "Total 42.00",
        }
    )

    assert chunks[0]["file_type"] == ".jpg"


def test_chunk_image_without_content_returns_no_chunks() -> None:
    """An empty OCR result produces an empty chunk list."""
    chunks = chunk_image(
        {
            "status": "success",
            "file_name": "blank.png",
            "content": "",
        }
    )

    assert chunks == []

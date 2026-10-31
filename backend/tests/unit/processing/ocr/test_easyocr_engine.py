# Run: pytest backend/tests/unit/processing/ocr/test_easyocr_engine.py -v -s

from pathlib import Path

from backend.processing.ocr.easyocr_engine import parse_image


def test_parse_image_success(valid_image_path: Path) -> None:
    """An image with text returns a success status and content."""
    result = parse_image(valid_image_path)
    assert result["status"] == "success"
    assert "content" in result


def test_parse_image_no_written_content(no_content_image_path: Path) -> None:
    """A blank image returns a failed status instead of raising."""
    result = parse_image(no_content_image_path)
    assert result["status"] == "failed"
    assert "error_message" in result


def test_parse_image_corrupted_file(corrupted_image_path: Path) -> None:
    """A corrupted image returns a failed status instead of raising."""
    result = parse_image(corrupted_image_path)
    assert result["status"] == "failed"
    assert "error_message" in result


def test_parse_image_missing_file(missing_image_path: Path) -> None:
    """A missing image returns a failed status instead of raising."""
    result = parse_image(missing_image_path)
    assert result["status"] == "failed"
    assert "error_message" in result

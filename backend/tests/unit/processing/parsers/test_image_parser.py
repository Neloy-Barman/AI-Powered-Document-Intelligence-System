# Run: pytest backend/tests/unit/processing/parsers/test_image_parser.py -v -s

"""Tests for the image parser's success and failure responses."""

from pathlib import Path

from backend.processing.parsers.image_parser import parse_image


def test_parse_image_success(valid_image_path: Path) -> None:
    """A valid image with text is parsed with a success status."""
    result = parse_image(valid_image_path)

    assert result["status"] == "success"
    assert result["file_name"] == valid_image_path.name
    assert "content" in result


def test_parse_image_no_written_content(no_content_image_path: Path) -> None:
    """An image with no readable text returns a failed status."""
    result = parse_image(no_content_image_path)

    assert result["status"] == "failed"
    assert result["file_name"] == no_content_image_path.name
    assert "error_message" in result


def test_parse_image_corrupted_file(corrupted_image_path: Path) -> None:
    """A corrupted image returns a failed status instead of raising."""
    result = parse_image(corrupted_image_path)

    assert result["status"] == "failed"
    assert result["file_name"] == corrupted_image_path.name
    assert "error_message" in result


def test_parse_image_missing_file(missing_image_path: Path) -> None:
    """A missing image returns a failed status instead of raising."""
    result = parse_image(missing_image_path)

    assert result["status"] == "failed"
    assert result["file_name"] == "missing.png"
    assert result["error_message"].startswith("FileNotFoundError")

# Run: pytest backend/tests/unit/processing/parsers/test_pdf_parser.py -v -s

"""Tests for the PDF parser's success and failure responses."""

from pathlib import Path

from backend.processing.parsers.pdf_parser import parse_pdf


def test_parse_pdf_success(valid_pdf_path: Path) -> None:
    """A valid PDF is parsed with a success status."""
    result = parse_pdf(valid_pdf_path)

    assert result["status"] == "success"


def test_parse_pdf_missing_file(missing_pdf_path: Path) -> None:
    """A missing file returns a failed status instead of raising."""
    result = parse_pdf(missing_pdf_path)

    assert result["status"] == "failed"
    assert result["file_name"] == "missing.pdf"
    assert result["error_message"].startswith("FileNotFoundError")


# def test_parse_pdf_corrupted_file(corrupted_pdf_path: Path) -> None:
#     """A corrupted PDF returns a failed status instead of raising."""
#     result = parse_pdf(corrupted_pdf_path)
#
#     assert result["status"] == "failed"
#     assert result["file_name"] == corrupted_pdf_path.name
#     assert "error_message" in result


def test_parse_pdf_without_written_content(no_content_pdf_path: Path) -> None:
    """A PDF with no extractable text returns a failed status."""
    result = parse_pdf(no_content_pdf_path)

    assert result["status"] == "failed"
    assert result["file_name"] == no_content_pdf_path.name
    assert "PDF has no written content" in result["error_message"]

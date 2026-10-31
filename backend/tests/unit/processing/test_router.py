# Run: pytest backend/tests/unit/processing/test_router.py -v -s

from pathlib import Path

from backend.processing.router import route_file


def test_route_file_pdf(valid_pdf_path: Path) -> None:
    """A valid PDF is routed to the PDF parser successfully."""
    result = route_file(valid_pdf_path)
    assert result["status"] == "success"
    assert result["file_name"] == valid_pdf_path.name


def test_route_file_csv(valid_csv_path: Path) -> None:
    """A valid CSV is routed to the CSV parser successfully."""
    result = route_file(valid_csv_path)
    assert result["status"] == "success"
    assert result["file_name"] == valid_csv_path.name


def test_route_file_spreadsheet(valid_spreadsheet_path: Path) -> None:
    """A valid spreadsheet is routed to the spreadsheet parser successfully."""
    result = route_file(valid_spreadsheet_path)
    assert result["status"] == "success"
    assert result["file_name"] == valid_spreadsheet_path.name


def test_route_file_image(valid_image_path: Path) -> None:
    """A valid image is routed to the image parser successfully."""
    result = route_file(valid_image_path)
    assert result["status"] == "success"
    assert result["file_name"] == valid_image_path.name


def test_route_file_missing_file(missing_pdf_path: Path) -> None:
    """A missing file returns a failed status instead of raising."""
    result = route_file(missing_pdf_path)
    assert result["status"] == "failed"
    assert result["file_name"] == "missing.pdf"
    assert "error_message" in result


def test_route_file_unsupported(tmp_path: Path) -> None:
    """An unsupported file type returns a failed status instead of raising."""
    path = tmp_path / "unknown.xyz"
    path.write_text("data")
    result = route_file(path)
    assert result["status"] == "failed"
    assert result["file_name"] == "unknown.xyz"
    assert "error_message" in result

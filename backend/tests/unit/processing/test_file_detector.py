# Run: pytest backend/tests/unit/processing/test_file_detector.py -v -s

from pathlib import Path

from backend.processing.file_detector import detect_file_type


def test_detect_file_type_pdf(valid_pdf_path: Path) -> None:
    """A PDF path is detected as the pdf type."""
    assert detect_file_type(valid_pdf_path) == "pdf"


def test_detect_file_type_csv(valid_csv_path: Path) -> None:
    """A CSV path is detected as the csv type."""
    assert detect_file_type(valid_csv_path) == "csv"


def test_detect_file_type_spreadsheet(valid_spreadsheet_path: Path) -> None:
    """A spreadsheet path is detected as the spreadsheet type."""
    assert detect_file_type(valid_spreadsheet_path) == "spreadsheet"


def test_detect_file_type_image(valid_image_path: Path) -> None:
    """An image path is detected as the image type."""
    assert detect_file_type(valid_image_path) == "image"


def test_detect_file_type_missing_file(missing_pdf_path: Path) -> None:
    """A missing file returns None instead of raising."""
    assert detect_file_type(missing_pdf_path) is None


def test_detect_file_type_unsupported(tmp_path: Path) -> None:
    """An unsupported extension returns None instead of raising."""
    path = tmp_path / "unknown.xyz"
    path.write_text("data")
    assert detect_file_type(path) is None

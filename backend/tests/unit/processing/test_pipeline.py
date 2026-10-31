# Run: pytest backend/tests/unit/processing/test_pipeline.py -v -s

from pathlib import Path

from backend.processing.pipeline import process_files


def test_process_files_all_success(
    valid_pdf_path: Path, valid_csv_path: Path, valid_spreadsheet_path: Path, valid_image_path: Path
) -> None:
    """All valid files are processed successfully."""
    result = process_files([valid_pdf_path, valid_csv_path, valid_spreadsheet_path, valid_image_path])
    assert result["status"] == "success"
    assert result["successful"] == 4
    assert result["failed"] == 0
    assert len(result["results"]) == 4


def test_process_files_with_failure(valid_csv_path: Path, missing_pdf_path: Path) -> None:
    """Failed files are skipped but counted."""
    result = process_files([valid_csv_path, missing_pdf_path])
    assert result["status"] == "success"
    assert result["successful"] == 1
    assert result["failed"] == 1
    assert len(result["results"]) == 1


def test_process_files_empty() -> None:
    """An empty input returns zero counts and an empty results list."""
    result = process_files([])
    assert result["status"] == "success"
    assert result["successful"] == 0
    assert result["failed"] == 0
    assert result["results"] == []

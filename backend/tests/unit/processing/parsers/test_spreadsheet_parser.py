"""Tests for the spreadsheet parser's success and failure responses."""

from pathlib import Path

from backend.processing.parsers.spreadsheet_parser import parse_spreadsheet


def test_parse_spreadsheet_success(valid_spreadsheet_path: Path) -> None:
    """A valid workbook returns every sheet with its row and column counts."""
    result = parse_spreadsheet(valid_spreadsheet_path)

    assert result["status"] == "success"
    assert result["file_name"] == valid_spreadsheet_path.name
    assert set(result["sheets"]) == {"Sheet1", "Sheet2"}
    assert result["sheets"]["Sheet1"]["rows"] == 2
    assert result["sheets"]["Sheet1"]["columns"] == 3


def test_parse_spreadsheet_corrupted_file(corrupted_spreadsheet_path: Path) -> None:
    """A corrupted workbook returns a failed status instead of raising."""
    result = parse_spreadsheet(corrupted_spreadsheet_path)

    assert result["status"] == "failed"
    assert result["file_name"] == corrupted_spreadsheet_path.name
    assert "error_message" in result


def test_parse_spreadsheet_missing_file(missing_spreadsheet_path: Path) -> None:
    """A missing workbook returns a failed status instead of raising."""
    result = parse_spreadsheet(missing_spreadsheet_path)

    assert result["status"] == "failed"
    assert result["file_name"] == "missing.xlsx"
    assert result["error_message"].startswith("FileNotFoundError")

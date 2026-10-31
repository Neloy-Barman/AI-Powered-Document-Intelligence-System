# Run: pytest backend/tests/unit/processing/parsers/test_csv_parser.py -v -s

"""Tests for the CSV parser's success and failure responses."""

from pathlib import Path

from backend.processing.parsers.csv_parser import parse_csv


def test_parse_csv_success(valid_csv_path: Path) -> None:
    """A valid CSV is parsed with the expected row and column counts."""
    result = parse_csv(valid_csv_path)

    assert result["status"] == "success"
    assert result["file_name"] == valid_csv_path.name
    assert result["rows"] == 2
    assert result["columns"] == 3


def test_parse_csv_corrupted_file(corrupted_csv_path: Path) -> None:
    """A malformed CSV returns a failed status instead of raising."""
    result = parse_csv(corrupted_csv_path)

    assert result["status"] == "failed"
    assert result["file_name"] == corrupted_csv_path.name
    assert "error_message" in result


def test_parse_csv_missing_file(missing_csv_path: Path) -> None:
    """A missing CSV returns a failed status instead of raising."""
    result = parse_csv(missing_csv_path)

    assert result["status"] == "failed"
    assert result["file_name"] == "missing.csv"
    assert result["error_message"].startswith("FileNotFoundError")

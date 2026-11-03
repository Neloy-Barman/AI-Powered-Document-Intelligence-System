# Run: pytest backend/tests/unit/processing/chunking/test_csv_chunker.py -v -s

"""Tests for preprocessing parsed CSV rows into vector-ready chunks."""

import pytest

from backend.processing.chunking.csv_chunker import chunk_csv


def make_parsed_csv(row_count: int) -> dict:
    """Build a parser-shaped CSV result with the requested number of rows."""
    content = [
        {
            "invoice_no": f"INV-{index:03d}",
            "supplier": f"Supplier {index}",
            "total": f"{index * 10}.00",
        }
        for index in range(row_count)
    ]
    return {
        "status": "success",
        "file_name": "test.csv",
        "rows": len(content),
        "columns": 3,
        "content": content,
    }


def test_chunk_csv_under_chunk_size() -> None:
    """Fewer than 25 rows produce one chunk containing every row."""
    chunks = chunk_csv(make_parsed_csv(10))

    assert len(chunks) == 1
    assert chunks[0]["chunk_range"] == [0, 9]
    assert len(chunks[0]["text_content"].splitlines()) == 10


def test_chunk_csv_exactly_chunk_size() -> None:
    """Exactly 25 rows produce one full chunk."""
    chunks = chunk_csv(make_parsed_csv(25))

    assert len(chunks) == 1
    assert chunks[0]["chunk_range"] == [0, 24]
    assert len(chunks[0]["text_content"].splitlines()) == 25


def test_chunk_csv_splits_remainder() -> None:
    """30 rows produce a full chunk and a five-row remainder."""
    chunks = chunk_csv(make_parsed_csv(30))

    assert [chunk["chunk_range"] for chunk in chunks] == [[0, 24], [25, 29]]
    assert [len(chunk["text_content"].splitlines()) for chunk in chunks] == [25, 5]
    assert [chunk["chunk_index"] for chunk in chunks] == [0, 1]
    assert [chunk["chunk_count"] for chunk in chunks] == [2, 2]


def test_chunk_csv_100_rows() -> None:
    """100 rows produce four chunks with inclusive ranges."""
    chunks = chunk_csv(make_parsed_csv(100))

    assert [chunk["chunk_range"] for chunk in chunks] == [
        [0, 24],
        [25, 49],
        [50, 74],
        [75, 99],
    ]
    assert [len(chunk["text_content"].splitlines()) for chunk in chunks] == [
        25,
        25,
        25,
        25,
    ]


def test_chunk_csv_metadata() -> None:
    """Every chunk carries the CSV metadata and no sheet-specific keys."""
    chunk = chunk_csv(make_parsed_csv(30))[0]

    assert chunk["file_name"] == "test.csv"
    assert chunk["file_type"] == ".csv"
    assert chunk["columns"] == ["invoice_no", "supplier", "total"]
    assert chunk["row_count"] == 30
    assert chunk["column_count"] == 3
    assert "sheet_name" not in chunk
    assert "content" not in chunk
    assert "text_content" in chunk


def test_chunk_csv_builds_text_content() -> None:
    """Every chunk contains one formatted text line per row."""
    chunks = chunk_csv(make_parsed_csv(30))
    first_lines = chunks[0]["text_content"].splitlines()
    second_lines = chunks[1]["text_content"].splitlines()

    assert len(first_lines) == 25
    assert len(second_lines) == 5
    assert first_lines[0] == "invoice_no: INV-000, supplier: Supplier 0, total: 0.00"
    assert (
        first_lines[-1]
        == "invoice_no: INV-024, supplier: Supplier 24, total: 240.00"
    )
    assert second_lines[0] == "invoice_no: INV-025, supplier: Supplier 25, total: 250.00"
    assert (
        second_lines[-1]
        == "invoice_no: INV-029, supplier: Supplier 29, total: 290.00"
    )
    assert not chunks[0]["text_content"].endswith("\n")


def test_chunk_csv_rejects_invalid_chunk_size() -> None:
    """A non-positive chunk size is rejected."""
    with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
        chunk_csv(make_parsed_csv(10), chunk_size=0)

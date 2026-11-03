from math import ceil
from pathlib import Path


def chunk_spreadsheet(
    parsed_spreadsheet: dict,
    chunk_size: int = 25,
) -> list[dict]:
    """Split each parsed sheet into row chunks ready for vector storage."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    chunks: list[dict] = []

    for sheet in parsed_spreadsheet["sheets"]:
        rows = sheet["content"]
        if not rows:
            continue

        columns = list(rows[0].keys())
        chunk_count = ceil(len(rows) / chunk_size)

        for chunk_index, start in enumerate(range(0, len(rows), chunk_size)):
            end = min(start + chunk_size, len(rows)) - 1
            chunk_rows = rows[start : end + 1]
            text_content = "\n".join(
                ", ".join(f"{column}: {row.get(column, '')}" for column in columns)
                for row in chunk_rows
            )

            chunks.append(
                {
                    "file_name": parsed_spreadsheet["file_name"],
                    "file_type": Path(parsed_spreadsheet["file_name"]).suffix.lower(),
                    "sheet_name": sheet["sheet_name"],
                    "columns": columns,
                    "row_count": sheet["rows"],
                    "column_count": sheet["columns"],
                    "chunk_index": chunk_index,
                    "chunk_count": chunk_count,
                    "chunk_range": [start, end],
                    "text_content": text_content,
                }
            )

    return chunks

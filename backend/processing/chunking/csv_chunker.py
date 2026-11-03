from math import ceil
from pathlib import Path


def chunk_csv(
    parsed_csv: dict,
    chunk_size: int = 25,
) -> list[dict]:
    """Split parsed CSV rows into chunks ready for vector storage."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    rows = parsed_csv["content"]
    if not rows:
        return []

    columns = list(rows[0].keys())
    chunk_count = ceil(len(rows) / chunk_size)
    chunks: list[dict] = []

    for chunk_index, start in enumerate(range(0, len(rows), chunk_size)):
        end = min(start + chunk_size, len(rows)) - 1
        chunk_rows = rows[start : end + 1]
        text_content = "\n".join(
            ", ".join(f"{column}: {row.get(column, '')}" for column in columns)
            for row in chunk_rows
        )

        chunks.append(
            {
                "file_name": parsed_csv["file_name"],
                "file_type": Path(parsed_csv["file_name"]).suffix.lower(),
                "columns": columns,
                "row_count": parsed_csv["rows"],
                "column_count": parsed_csv["columns"],
                "chunk_index": chunk_index,
                "chunk_count": chunk_count,
                "chunk_range": [start, end],
                "text_content": text_content,
            }
        )

    return chunks

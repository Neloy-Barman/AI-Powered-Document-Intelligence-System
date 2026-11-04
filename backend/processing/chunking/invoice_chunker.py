from pathlib import Path


def _format_value(value: object) -> str:
    """Render missing values as empty text and keep everything else readable."""
    return "" if value is None else str(value)


def chunk_invoice(
    extraction_result: dict,
    page_no: int | None = None,
) -> list[dict]:
    """Build one text chunk from a parsed invoice extraction result."""
    invoice = extraction_result.get("invoice") or {}
    if not invoice:
        return []

    file_name = extraction_result["file_name"]
    header_columns = [column for column in invoice if column != "line_items"]
    line_items = invoice.get("line_items") or []

    lines = [
        ", ".join(
            f"{column}: {_format_value(invoice.get(column))}"
            for column in header_columns
        )
    ]

    if line_items:
        line_item_columns = list(line_items[0])
        lines.extend(
            ", ".join(
                f"{column}: {_format_value(item.get(column))}"
                for column in line_item_columns
            )
            for item in line_items
        )

    return [
        {
            "file_name": file_name,
            "file_type": Path(file_name).suffix.lower(),
            "page_no": page_no,
            "text_content": "\n".join(lines),
        }
    ]

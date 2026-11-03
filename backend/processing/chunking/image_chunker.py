from pathlib import Path


def chunk_image(parsed_image: dict) -> list[dict]:
    """Wrap parsed OCR content in a vector-ready chunk."""
    text_content = parsed_image.get("content", "")
    if not text_content:
        return []

    return [
        {
            "file_name": parsed_image["file_name"],
            "file_type": Path(parsed_image["file_name"]).suffix.lower(),
            "text_content": text_content,
        }
    ]

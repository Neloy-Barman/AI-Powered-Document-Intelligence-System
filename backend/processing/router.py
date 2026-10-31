from pathlib import Path

from backend.processing.file_detector import detect_file_type
from backend.processing.parsers.csv_parser import parse_csv
from backend.processing.parsers.image_parser import parse_image
from backend.processing.parsers.pdf_parser import parse_pdf
from backend.processing.parsers.spreadsheet_parser import parse_spreadsheet


PARSERS = {
    "pdf": parse_pdf,
    "csv": parse_csv,
    "spreadsheet": parse_spreadsheet,
    "image": parse_image,
}


def route_file(file_path: str | Path) -> dict:
    path = Path(file_path)
    file_type = detect_file_type(path)
    if file_type is None:
        error_message = f"UnsupportedFileTypeError: Could not route file: {path}"
        print(error_message)
        return {
            "status": "failed",
            "file_name": path.name,
            "error_message": error_message,
        }
    return PARSERS[file_type](path)

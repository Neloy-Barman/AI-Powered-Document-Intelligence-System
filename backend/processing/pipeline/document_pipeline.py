from pathlib import Path

from backend.processing.file_detector import detect_file_type

from backend.processing.pipeline.csv_pipeline import process_csv
from backend.processing.pipeline.image_pipeline import process_image


PIPELINES = {
    "csv": process_csv,
    "image": process_image,
}


def process_document(file_path: str | Path) -> dict:
    """Dispatch a document to its file-type-specific pipeline."""
    file_type = detect_file_type(file_path)

    if file_type not in PIPELINES:
        return {
            "status": "failed",
            "file_name": Path(file_path).name,
            "error": f"Unsupported document type: {file_type}",
        }

    return PIPELINES[file_type](file_path)

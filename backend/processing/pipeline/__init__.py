from pathlib import Path

from backend.processing.router import route_file

from backend.processing.pipeline.csv_pipeline import process_csv
from backend.processing.pipeline.document_pipeline import process_document


def process_files(file_paths: list[str | Path]) -> dict[str, object]:
    results: list[dict[str, object]] = []
    successful = 0
    failed = 0
    for file_path in file_paths:
        response = route_file(file_path)
        if response.get("status") == "failed":
            failed += 1
            print(
                f"Failed to process {response.get('file_name')}: "
                f"{response.get('error_message')}"
            )
            continue
        successful += 1
        result = {key: value for key, value in response.items() if key != "status"}
        results.append(result)
    return {
        "status": "success",
        "successful": successful,
        "failed": failed,
        "results": results,
    }


__all__ = ["process_csv", "process_document", "process_files"]
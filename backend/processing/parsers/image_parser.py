from pathlib import Path
from backend.processing.ocr.easyocr_engine import parse_image as run_ocr


def parse_image(file_path: str | Path) -> dict[str, str]:
    path = Path(file_path)
    try:
        if not path.is_file():
            raise FileNotFoundError(f"No such file or directory: {path}")
        result = run_ocr(path)
        if result["status"] == "failed":
            return {
                "status": "failed",
                "file_name": path.name,
                "error_message": result["error_message"],
            }
        return {
            "status": "success",
            "file_name": path.name,
            "content": result["content"],
        }
    except FileNotFoundError as error:
        error_message = f"{type(error).__name__}: {error}"
        print(error_message)
        return {
            "status": "failed",
            "file_name": path.name,
            "error_message": error_message,
        }
    except Exception as error:
        error_message = f"{type(error).__name__}: {error}"
        print(error_message)
        return {
            "status": "failed",
            "file_name": path.name,
            "error_message": error_message,
        }


if __name__ == "__main__":
    import json
    import sys

    from backend.processing.chunking.image_chunker import chunk_image

    # Default to the test fixture, but allow a custom path:
    # python -m backend.processing.parsers.image_parser "path/to/file.png"
    DEFAULT_IMAGE_PATH = (
        Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "valid.png"
    )
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IMAGE_PATH

    parsed_result = parse_image(
        file_path=file_path,
    )
    print("Parsed image:")
    print(json.dumps(parsed_result, indent=2, ensure_ascii=False))

    if parsed_result["status"] != "failed":
        chunked_result = chunk_image(parsed_result)
        print("\nPreprocessed chunks:")
        print(json.dumps(chunked_result, indent=2, ensure_ascii=False))

# python -m backend.processing.parsers.image_parser

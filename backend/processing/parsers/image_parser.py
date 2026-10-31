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

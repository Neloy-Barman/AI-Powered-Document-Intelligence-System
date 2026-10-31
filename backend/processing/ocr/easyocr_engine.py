from pathlib import Path
import easyocr


reader = easyocr.Reader(["en", "bn"])


def parse_image(file_path: str | Path) -> dict[str, str]:
    try:
        results = reader.readtext(str(file_path), detail=0, paragraph=True)
        return {
            "status": "success",
            "content": results[0],
        }
    except Exception as error:
        error_message = f"{type(error).__name__}: {error}"
        print(error_message)
        return {
            "status": "failed",
            "error_message": error_message,
        }

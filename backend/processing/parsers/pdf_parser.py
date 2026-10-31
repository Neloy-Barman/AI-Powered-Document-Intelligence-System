from pathlib import Path
import pymupdf


def parse_pdf(file_path: str | Path) -> dict[str, str | int | list[str]]:
    path = Path(file_path)
    try:
        with pymupdf.open(path) as document:
            text_content = [page.get_text() for page in document]
            if not any(text.strip() for text in text_content):
                raise pymupdf.FileDataError("PDF has no written content")
            return {
                "status": "success",
                "file_name": path.name,
                "page_count": len(document),
                "text_content": text_content,
            }
    except (FileNotFoundError, pymupdf.FileNotFoundError) as error:
        error_message = f"{type(error).__name__}: {error}"
        print(error_message)
        return {
            "status": "failed",
            "file_name": path.name,
            "error_message": error_message,
        }
    except (pymupdf.FileDataError, RuntimeError) as error:
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

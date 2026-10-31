from pathlib import Path


EXTENSION_TO_TYPE: dict[str, str] = {
    ".pdf": "pdf",
    ".csv": "csv",
    ".xlsx": "spreadsheet",
    ".xls": "spreadsheet",
    ".ods": "spreadsheet",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".tiff": "image",
    ".tif": "image",
    ".bmp": "image",
    ".gif": "image",
    ".webp": "image",
}


def detect_file_type(file_path: str | Path) -> str | None:
    path = Path(file_path)
    if not path.is_file():
        print(f"FileNotFoundError: No such file or directory: {path}")
        return None
    file_type = EXTENSION_TO_TYPE.get(path.suffix.lower())
    if file_type is None:
        print(f"UnsupportedFileTypeError: Unsupported file type: {path.suffix}")
        return None
    return file_type

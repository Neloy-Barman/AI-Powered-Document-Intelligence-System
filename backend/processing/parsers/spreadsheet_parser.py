from pathlib import Path
import zipfile  # .xlsx files are ZIP archives, so BadZipFile signals a corrupted workbook
import pandas as pd
from xlrd.biffh import (
    XLRDError,
)  # raised by xlrd when a legacy .xls file is corrupt or invalid

SheetData = dict[str, str | int | list[dict[str, str]]]


def parse_spreadsheet(file_path: str | Path) -> dict[str, str | list[SheetData]]:
    path = Path(file_path)
    try:
        sheets = pd.read_excel(path, sheet_name=None, dtype=str, keep_default_na=False)
        sheet_data: list[SheetData] = []
        for sheet_name, dataframe in sheets.items():
            sheet_data.append(
                {
                    "sheet_name": sheet_name,
                    "rows": len(dataframe),
                    "columns": len(dataframe.columns),
                    # orient="records" turns the DataFrame into a list of row dictionaries,
                    # where each dictionary maps column names to that row's values.
                    "content": dataframe.to_dict(orient="records"),
                }
            )
        return {
            "status": "success",
            "file_name": path.name,
            "sheets": sheet_data,
        }
    except FileNotFoundError as error:
        error_message = f"{type(error).__name__}: {error}"
        print(error_message)
        return {
            "status": "failed",
            "file_name": path.name,
            "error_message": error_message,
        }
    # BadZipFile catches corrupted .xlsx files; XLRDError catches corrupted .xls files.
    except (pd.errors.ParserError, ValueError, zipfile.BadZipFile, XLRDError) as error:
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

    from backend.processing.chunking.spreadsheet_chunker import chunk_spreadsheet

    # Default to the test fixture, but allow a custom path:
    # python -m backend.processing.parsers.spreadsheet_parser "path/to/file.xlsx" "optional search query"
    DEFAULT_SPREADSHEET_PATH = (
        Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "valid.xlsx"
    )
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SPREADSHEET_PATH
    search_query = sys.argv[2] if len(sys.argv) > 2 else None

    parsed_result = parse_spreadsheet(
        file_path=file_path,
    )
    print("Parsed spreadsheet:")
    print(json.dumps(parsed_result, indent=2, ensure_ascii=False))

    if parsed_result["status"] != "failed":
        chunked_result = chunk_spreadsheet(parsed_result)
        print("\nPreprocessed chunks:")
        print(json.dumps(chunked_result, indent=2, ensure_ascii=False))

        from backend.app.search.semantic_search import create_qdrant_service

        vector_service = create_qdrant_service()
        # upsert_result = vector_service.upsert_chunks(chunked_result)
        # print("\nQdrant upsert result:")
        # print(json.dumps(upsert_result, indent=2, ensure_ascii=False))

    search_query = "invoice total amount"
    if search_query:
        search_results = vector_service.search(search_query)
        print("\nSimilarity search results:")
        print(json.dumps(search_results, indent=2, ensure_ascii=False))

# python -m backend.processing.parsers.spreadsheet_parser

from pathlib import Path
import pandas as pd


def parse_csv(file_path: str | Path) -> dict[str, str | int | list[dict[str, str]]]:
    path = Path(file_path)
    try:
        dataframe = pd.read_csv(path, dtype=str, keep_default_na=False)
        return {
            "status": "success",
            "file_name": path.name,
            "rows": len(dataframe),
            "columns": len(dataframe.columns),
            # orient="records" turns the DataFrame into a list of row dictionaries,
            # where each dictionary maps column names to that row's values.
            "content": dataframe.to_dict(orient="records"),
        }
    except FileNotFoundError as error:
        error_message = f"{type(error).__name__}: {error}"
        print(error_message)
        return {
            "status": "failed",
            "file_name": path.name,
            "error_message": error_message,
        }
    except (pd.errors.ParserError, pd.errors.EmptyDataError) as error:
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

    from backend.processing.chunking.csv_chunker import chunk_csv

    # Default to the test fixture, but allow a custom path:
    # python -m backend.processing.parsers.csv_parser "path/to/file.csv"
    DEFAULT_CSV_PATH = (
        Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "valid.csv"
    )
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV_PATH

    parsed_result = parse_csv(
        file_path=file_path,
    )
    print("Parsed CSV:")
    print(json.dumps(parsed_result, indent=2, ensure_ascii=False))

    if parsed_result["status"] != "failed":
        chunked_result = chunk_csv(parsed_result)
        print("\nPreprocessed chunks:")
        print(json.dumps(chunked_result, indent=2, ensure_ascii=False))

# python -m backend.processing.parsers.csv_parser

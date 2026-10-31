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

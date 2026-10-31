from pathlib import Path
import zipfile  # .xlsx files are ZIP archives, so BadZipFile signals a corrupted workbook
import pandas as pd
from xlrd.biffh import XLRDError  # raised by xlrd when a legacy .xls file is corrupt or invalid


SheetData = dict[str, int | list[dict[str, str]]]


def parse_spreadsheet(file_path: str | Path) -> dict[str, str | dict[str, SheetData]]:
    path = Path(file_path)
    try:
        sheets = pd.read_excel(path, sheet_name=None, dtype=str, keep_default_na=False)
        sheet_data: dict[str, SheetData] = {}
        for sheet_name, dataframe in sheets.items():
            sheet_data[sheet_name] = {
                "rows": len(dataframe),
                "columns": len(dataframe.columns),
                # orient="records" turns the DataFrame into a list of row dictionaries,
                # where each dictionary maps column names to that row's values.
                "content": dataframe.to_dict(orient="records"),
            }
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

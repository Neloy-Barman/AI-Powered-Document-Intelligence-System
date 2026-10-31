# Progress Tracker

Last updated: 2026-10-31

## Project

AI-Powered Document Intelligence System. Scope and deliverables: `docs/Ai Engineer Task 1.3.pdf`.

## Implemented

### Processing (`backend/processing/`)

- `file_detector.py`
  - `detect_file_type(file_path)` returns the file type as a string (`"pdf"`, `"csv"`, `"spreadsheet"`, `"image"`) based on extension.
  - Returns `None` and prints `TypeName: message` for missing files or unsupported types.

- `router.py`
  - `route_file(file_path)` detects the file type via `detect_file_type` and dispatches to the matching parser.
  - Returns the parser result; on routing failure returns `status`, `file_name`, `error_message`.

### Parsers (`backend/processing/parsers/`)

- `pdf_parser.py`
  - `parse_pdf(file_path)` using PyMuPDF.
  - Returns `status`, `file_name`, `page_count`, `text_content` (one string per page).
  - Errors: missing file, corrupt/unreadable PDF, PDF with no extractable text (`FileDataError`), generic. Returns `status`, `file_name`, `error_message`.

- `csv_parser.py`
  - `parse_csv(file_path)` using pandas.
  - Returns `status`, `file_name`, `rows`, `columns`, `content` (list of row dicts via `orient="records"`).
  - Reads values as strings (`dtype=str`, `keep_default_na=False`).
  - Errors: missing file, malformed/empty CSV, generic.

- `spreadsheet_parser.py`
  - `parse_spreadsheet(file_path)` using pandas, all sheets at once (`sheet_name=None`).
  - Returns `status`, `file_name`, `sheets` -> `{sheet_name: {rows, columns, content}}`.
  - Errors: missing file, corrupt `.xlsx` (`BadZipFile`), corrupt `.xls` (`XLRDError`), parse/format errors, generic.

- `image_parser.py`
  - `parse_image(file_path)` delegates to `easyocr_engine.parse_image`.
  - Returns `status`, `file_name`, `content`.
  - Errors: missing file, OCR/engine failure, generic; returns `status`, `file_name`, `error_message`.

### OCR (`backend/processing/ocr/`)

- `easyocr_engine.py`
  - `parse_image(file_path)` using EasyOCR with English and Bengali.
  - Calls `readtext(..., detail=0, paragraph=True)` and returns the first paragraph.
  - Returns `status`, `content`; on error returns `status`, `error_message`.

### Tests (`backend/tests/`)

- `conftest.py` — shared fixtures: `valid_pdf_path`, `missing_pdf_path`, `corrupted_pdf_path`, `no_content_pdf_path`, `valid_csv_path`, `corrupted_csv_path`, `valid_spreadsheet_path`, `corrupted_spreadsheet_path`.
- `unit/processing/test_file_detector.py` — 6 pytest cases: pdf, csv, spreadsheet, image, missing file, unsupported type.
- `unit/processing/test_router.py` — 6 pytest cases: pdf, csv, spreadsheet, image, missing file, unsupported type.
- `unit/processing/ocr/test_easyocr_engine.py` — 4 pytest cases: success, no written content, corrupted file, missing file.","oldString">
- `unit/processing/test_pipeline.py` — 3 pytest cases: all success, with failure, empty input.","path":"D:\AI-Powered-Document-Intelligence-System\docs\progress-tracker.md","oldString">
- `unit/processing/parsers/test_pdf_parser.py` — 3 active pytest cases: success, missing file, no written content. Corrupted test commented out.","path":"D:\AI-Powered-Document-Intelligence-System\docs\progress-tracker.md
- `unit/processing/parsers/test_csv_parser.py` — 2 pytest cases: success, corrupted file.
- `unit/processing/parsers/test_spreadsheet_parser.py` — 2 pytest cases: success, corrupted file.
- `fixtures/` — `valid.pdf`, `no_content.pdf`, `valid.csv`, `corrupted.csv`, `valid.xlsx` (2 sheets), `corrupted.xlsx`.
- `pytest.ini` (project root) — sets `pythonpath = .`.

### Docs (`docs/`)

- `developer-instructions.md` — coding, typing, error-handling, response-order, progress-tracking rules.
- `progress-tracker.md` — this file.

### Scratch

- `test.py` — dependency spikes: PyMuPDF page iteration, pandas multi-sheet read, pytesseract TIFF OCR.

## Pending

- Scanned PDF to OCR fallback.
- `pipeline.py`
  - `process_files(file_paths)` iterates over a list of file paths, routes each via `route_file`.
  - Skips failed files (counted + printed), keeps successful results with `status` stripped.
  - Returns `status`, `successful`, `failed`, `results`.","oldString">
- AI extraction, validation, database/search, frontend, automated tests, evaluation report.","oldString">
- `pipeline.py` — processing orchestration.","path":"D:\AI-Powered-Document-Intelligence-System\docs\progress-tracker.md","path":"D:\AI-Powered-Document-Intelligence-System\docs\progress-tracker.md
- AI extraction, validation, database/search, frontend, automated tests, evaluation report.

## Known Gaps

- Test assets are not invoices: `AI Engineering.pdf` (535-page digital book), `dummy_data.xls` (5000 x 8 generic table), `test_tiff.tiff` (single-frame photo).
- The OCR block in `test.py` returns empty text with default `--psm 3`; needs PSM/preprocessing.

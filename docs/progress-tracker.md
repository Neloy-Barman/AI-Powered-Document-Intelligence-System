# Progress Tracker

Last updated: 2026-11-01

## Project

AI-Powered Document Intelligence System. Scope and deliverables: `docs/Ai Engineer Task 1.3.pdf`.

## Implemented

### Schemas (`backend/app/schemas/`)

- `invoice.py`
  - `Money` — `Decimal` annotated with a serializer that emits a two-decimal string (e.g. `"1020.00"`); used because `float` cannot preserve trailing zeros.
  - `LineItem` — description, quantity, unit_price, amount (all optional).
  - `Invoice` — invoice_number, invoice_date, supplier_name, customer_name, subtotal, tax, total, currency, line_items (all optional, defaults to None/[]).
  - Money fields (`unit_price`, `amount`, `subtotal`, `tax`, `total`) serialize as two-decimal strings.

### Extraction (`backend/app/extraction/`)

- `llm_client.py` — Google Gen AI client wrapper: `get_client()`, `encode_image()`, `_mime_type()`, `vision_completion()` (uses `client.interactions.create` with image input and JSON schema response format).
- `extractor.py` — `extract_invoice(image_path)` runs Gemini vision extraction, runs missing-fields, numeric-sanity, and consistency validators, prints the results, and returns the invoice dict.
- `validation/` — `common.py` (`is_missing`, `missing_paths`), `missing_fields.py` (`validate_missing_fields`), `numeric_sanity.py` (`validate_numeric_sanity`), `consistency.py` (`validate_consistency`), `duplicates.py` (`validate_duplicates`, mocked hardcoded list).

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

### Frontend (`frontend/`)

- Vite + React app; `npm run dev` serves at http://localhost:5173.
- `src/App.jsx` — page title, Upload/Progress navigation (simple view switch, no router), queue hook, and the completion summary popup. Both views stay mounted so their state survives switching.
- `src/components/upload/UploadForm.jsx` — two independent sections with headings "Upload Documents" and "Upload Invoice".
  - Documents: multi-file picker, selections accumulate and are listed by name. Submit opens an in-page popup ("Documents uploaded successfully. Do you want to upload more documents?") with literal Yes/No buttons. Yes closes it and keeps the picker open; No hides the picker, keeps the file names, and relabels the button to "Process". Process sends the batch to the queue, resets the section, and opens Progress. Submit with no files does nothing.
  - Invoice: single `.pdf`/`.png` file; other types alert and are rejected. Submit shows a floating success box ("Invoice has been uploaded successfully.") that auto-hides after 1 second, hides the picker, and relabels the button to "Process". Process sends the invoice to the queue, resets the section, and opens Progress.
- `src/pages/ProgressPage.jsx` — one shared list for documents and invoices: "No processing in progress." when empty, otherwise a row per file showing Queued / Processing… / Successful / Failed.
- `src/hooks/useProcessingQueue.js` — one global FIFO queue, processes one file at a time, keeps per-run successful/failed counts, and exposes the completion summary.
- `src/lib/processingService.js` — mock processing: waits 2 seconds; the first file of a multi-file batch always fails, every other file succeeds (static test rule). Later this becomes the real API call.
- `src/styles/index.css` — off-white page background, centered layout, nav/view switching styles, progress list layout, floating popups, wide buttons; remaining class slots empty.
- No real upload logic, API client, or router yet; processing is mocked in the frontend.

### Tests (`backend/tests/`)

- `conftest.py` — shared fixtures: `valid_pdf_path`, `missing_pdf_path`, `corrupted_pdf_path`, `no_content_pdf_path`, `valid_csv_path`, `corrupted_csv_path`, `valid_spreadsheet_path`, `corrupted_spreadsheet_path`.
- `unit/processing/parsers/test_pdf_parser.py` — 3 active pytest cases: success, missing file, no written content. Corrupted test commented out.
- `unit/processing/parsers/test_csv_parser.py` — 2 pytest cases: success, corrupted file.
- `unit/processing/parsers/test_spreadsheet_parser.py` — 2 pytest cases: success, corrupted file.
- `unit/processing/test_file_detector.py` — 6 pytest cases: pdf, csv, spreadsheet, image, missing file, unsupported type.
- `unit/processing/test_router.py` — 6 pytest cases: pdf, csv, spreadsheet, image, missing file, unsupported type.
- `unit/processing/test_pipeline.py` — 3 pytest cases: all success, with failure, empty input.
- `unit/processing/ocr/test_easyocr_engine.py` — 4 pytest cases: success, no written content, corrupted file, missing file.
- `fixtures/` — `valid.pdf`, `no_content.pdf`, `valid.csv`, `corrupted.csv`, `valid.xlsx` (2 sheets), `corrupted.xlsx`, `valid.png`, `invoice.png`, `no_content.jpg`, `corrupted.tiff`.
- `pytest.ini` (project root) — sets `pythonpath = .`.

### Docs (`docs/`)

- `developer-instructions.md` — coding, typing, error-handling, response-order, progress-tracking rules.
- `progress-tracker.md` — this file.
- `folder-structure.md` — full project layout reference.
- `frontend-development-plan.md` — frontend requirements, API contract, data shapes, build order (F1–F7), and progress log.
- `validation-plan.md` — Task 3 validation rules, issue structure, statuses, tests, known gaps, and implementation checklist.
- `database-schema.md` — draft invoices table schema.

### Scratch

- `test.py` — dependency spikes: PyMuPDF page iteration, pandas multi-sheet read, pytesseract TIFF OCR.

## Pending

- Scanned PDF to OCR fallback.
- AI extraction (invoice schema + Gemini vision extractor done; prompt tuning pending).
- validation, database/search, automated tests, evaluation report.
- Rest of the frontend: documents table with per-page progress, detail page, validation review, corrections, search.

## Known Gaps

- Test assets are not invoices: `AI Engineering.pdf` (535-page digital book), `dummy_data.xls` (5000 x 8 generic table), `test_tiff.tiff` (single-frame photo).
- The OCR block in `test.py` returns empty text with default `--psm 3`; needs PSM/preprocessing.
- `GEMINI_API_KEY` not set; extraction cannot run until it is provided.

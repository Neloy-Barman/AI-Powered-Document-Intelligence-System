# Semantic Search & Spreadsheet Preprocessing Plan

Last updated: 2026-11-03
Status: Preprocessing implemented; embedding/Qdrant not implemented
Audience: next agent taking over the semantic-search and Qdrant work

## 1. Purpose

This document captures the separate semantic-search planning for the AI-Powered
Document Intelligence System. It is kept in `docs/` as a standalone handoff document so it
can be given to another agent without mixing it with the parser/frontend plans.

The immediate focus is **only the preprocessing/chunking layer** for spreadsheets, CSV
files, and images. Embedding generation and Qdrant ingestion are designed here for context,
but are not implemented yet.

## 2. Current state

### Implemented

- `backend/processing/parsers/spreadsheet_parser.py`
  - `parse_spreadsheet(file_path)` reads every sheet with pandas.
  - Returns:
    ```python
    {
        "status": "success",
        "file_name": "valid.xlsx",
        "sheets": [
            {
                "sheet_name": "Sheet1",
                "rows": 2,
                "columns": 3,
                "content": [{"invoice_no": "...", "supplier": "...", "total": "..."}],
            }
        ],
    }
    ```
  - `sheets` is a **list**, not a dictionary keyed by sheet name.
  - All cell values are strings (`dtype=str`, `keep_default_na=False`).
- `backend/processing/chunking/spreadsheet_chunker.py`
  - `chunk_spreadsheet(parsed_spreadsheet, chunk_size=25)` splits each sheet into
    row-based chunks and returns a flat list of chunk dictionaries.
- `backend/processing/chunking/csv_chunker.py`
  - `chunk_csv(parsed_csv, chunk_size=25)` splits a parsed CSV into row-based chunks.
  - Uses the same metadata and `text_content` format as the spreadsheet chunker, but omits
    `sheet_name` because a CSV has one dataframe.
- `backend/processing/chunking/image_chunker.py`
  - `chunk_image(parsed_image)` wraps parsed OCR content in one chunk.
  - Chunk keys are `file_name`, `file_type`, and `text_content`.
- `backend/tests/unit/processing/parsers/test_spreadsheet_parser.py`
  - Updated for the list-based `sheets` shape.
- `backend/tests/unit/processing/chunking/test_spreadsheet_chunker.py`
  - Covers <25, exactly 25, 30, 100, and multi-sheet chunking plus metadata and
    `text_content` validation.
- `backend/tests/unit/processing/chunking/test_csv_chunker.py`
  - Covers the same chunking rules for a single CSV dataframe without `sheet_name`.
- `backend/tests/unit/processing/chunking/test_image_chunker.py`
  - Covers one chunk per image, lower-case file type, and empty OCR content.
- `.env.example`
  - Contains placeholders:
    ```env
    QDRANT_URL=https://your-cluster-id.region.cloud.qdrant.io:6333
    QDRANT_API_KEY=your-qdrant-api-key
    ```
  - No real credentials are stored in the repo.

### Not implemented

- Embedding generation
- Qdrant client/service
- Qdrant collection creation or upsert
- Semantic search endpoint/API/frontend integration

### Dependency state

- `google-genai` is installed (`2.34.0`), so Gemini embeddings can use the existing
  `GEMINI_API_KEY` setup.
- `qdrant-client` is **not installed** yet.
- The app does not currently load `.env` with `python-dotenv`; environment variables are
  expected to be supplied by the shell/IDE/container. This must be decided before adding
  Qdrant runtime code.

## 3. Scope of the current handoff

The preprocessing function is implemented in the chunking package:

```text
parse_spreadsheet() output
        -> chunk_spreadsheet()
        -> list of chunk dictionaries
```

It does not call Qdrant, generate embeddings, or read the source file again.

## 4. Chunking rules (agreed)

- Input is the output of `parse_spreadsheet`.
- Process each sheet independently.
- Default chunk size: **25 rows**.
- Each chunk contains up to 25 row dictionaries.
- A Qdrant point will represent one **chunk**, not one sheet.
- `chunk_range` is **inclusive**:
  - first chunk of a 100-row sheet: `[0, 24]`
  - second chunk: `[25, 49]`
  - third chunk: `[50, 74]`
  - fourth chunk: `[75, 99]`
- Fewer than 25 rows -> one chunk.
- Exactly 25 rows -> one chunk.
- More than 25 rows -> multiple chunks.
- Example: 30 rows -> two chunks:
  - `[0, 24]` containing 25 rows
  - `[25, 29]` containing 5 rows
- Multiple sheets -> each chunk keeps its own `sheet_name`.
- Return one **flat list** of chunks across all sheets.
- `chunk_index` is 0-based and resets for each sheet.
- `chunk_count` is the number of chunks for that sheet.

### CSV rules

- Input is the output of `parse_csv`.
- A CSV has one dataframe, so there is no `sheet_name` key.
- The same 25-row chunk size, inclusive `chunk_range`, `chunk_index`, `chunk_count`, and
  `text_content` format apply.
- Return one flat list of chunks.

### Image rules

- Input is the output of `parse_image`.
- An image produces one chunk; row chunking does not apply to OCR content.
- The chunk keys are `file_name`, `file_type`, and `text_content`.
- Empty content produces an empty chunk list.

### Explicitly out of scope for now

- Empty-sheet special handling
- Duplicate-upload/idempotency handling
- Embedding generation
- Qdrant upload

Empty sheets and duplicate uploads are considered out of scope for this preprocessing step.

## 5. Output chunk contract

Each chunk should be a flat dictionary with these keys:

| Key | Type | Meaning |
|---|---|---|
| `file_name` | `str` | Original workbook filename |
| `file_type` | `str` | Derived extension, e.g. `.xlsx` or `.xls` |
| `sheet_name` | `str` | Sheet this chunk belongs to; omitted for CSV chunks |
| `columns` | `list[str]` | Column names from the sheet/row dictionaries |
| `row_count` | `int` | Total rows in the whole sheet |
| `column_count` | `int` | Total columns in the whole sheet |
| `chunk_index` | `int` | 0-based chunk number within the sheet |
| `chunk_count` | `int` | Total chunks for that sheet |
| `chunk_range` | `list[int]` | Inclusive `[start, end]` row range |
| `text_content` | `str` | All chunk rows formatted as `column: value` lines joined by `\n` |

Example for a 30-row sheet (`text_content` is abbreviated; the real first chunk contains
**25 lines**):

```json
{
  "file_name": "valid.xlsx",
  "file_type": ".xlsx",
  "sheet_name": "Sheet1",
  "columns": ["invoice_no", "supplier", "total"],
  "row_count": 30,
  "column_count": 3,
  "chunk_index": 0,
  "chunk_count": 2,
  "chunk_range": [0, 24],
  "text_content": "invoice_no: INV-001, supplier: Acme, total: 100.50\ninvoice_no: INV-002, supplier: Globex, total: 250.00\n... 25 lines in total ..."
}
```

The second chunk for the same sheet:

```json
{
  "file_name": "valid.xlsx",
  "file_type": ".xlsx",
  "sheet_name": "Sheet1",
  "columns": ["invoice_no", "supplier", "total"],
  "row_count": 30,
  "column_count": 3,
  "chunk_index": 1,
  "chunk_count": 2,
  "chunk_range": [25, 29],
  "text_content": "invoice_no: INV-026, supplier: Stark, total: 120.00\ninvoice_no: INV-027, supplier: Wayne, total: 300.00\n... 5 lines in total ..."
}
```

### Chunk text format

Every chunk includes a `text_content` string built from **all rows in that chunk**. Each row
becomes one line in this format:

```text
column1: value, column2: value, column3: value
```

Rows are joined with `\n`; there is no trailing newline. For example:

```text
invoice_no: INV-001, supplier: Acme, total: 100.50
invoice_no: INV-002, supplier: Globex, total: 250.00
```

This is the text representation that can later be sent to the embedding model. Spreadsheet
and CSV chunks do not store a separate `content` list; row data can be reconstructed from
`text_content` when needed. Image chunks use `text_content` directly because OCR text is already
a single block.

## 6. Implemented functions and modules

The chunkers live in:

```text
backend/processing/chunking/spreadsheet_chunker.py
backend/processing/chunking/csv_chunker.py
backend/processing/chunking/image_chunker.py
```

Public functions:

```python
def chunk_spreadsheet(
    parsed_spreadsheet: dict,
    chunk_size: int = 25,
) -> list[dict]:
    ...


def chunk_csv(
    parsed_csv: dict,
    chunk_size: int = 25,
) -> list[dict]:
    ...


def chunk_image(parsed_image: dict) -> list[dict]:
    ...
```

All functions are pure: no file I/O, no network, no Qdrant, no embeddings.

### Algorithm

```python
validate chunk_size > 0

chunks = []
for sheet in parsed_spreadsheet["sheets"]:
    rows = sheet["content"]
    if not rows:
        continue  # no special handling needed; no chunks for this sheet

    columns = list(rows[0].keys())
    chunk_count = ceil(len(rows) / chunk_size)

    for chunk_index, start in enumerate(range(0, len(rows), chunk_size)):
        end = min(start + chunk_size, len(rows)) - 1
        chunk_rows = rows[start : end + 1]
        text_content = "\n".join(
            ", ".join(f"{column}: {row.get(column, '')}" for column in columns)
            for row in chunk_rows
        )
        chunks.append({
            "file_name": parsed_spreadsheet["file_name"],
            "file_type": Path(parsed_spreadsheet["file_name"]).suffix.lower(),
            "sheet_name": sheet["sheet_name"],
            "columns": columns,
            "row_count": sheet["rows"],
            "column_count": sheet["columns"],
            "chunk_index": chunk_index,
            "chunk_count": chunk_count,
            "chunk_range": [start, end],
            "text_content": text_content,
        })

return chunks
```

Notes:

- `sheet["rows"]` and `sheet["columns"]` are the parser's sheet totals.
- `len(rows[start:end+1])` is the chunk row count, which may be less than 25 for the
  final chunk.
- `chunk_count` uses `ceil(len(rows) / chunk_size)` so it matches the generated chunks.
- If the parser ever returns a sheet with zero rows, the loop generates no chunks. No
  additional empty-sheet behavior is required for this phase.

## 7. Tests for preprocessing

Implemented tests build parser-like input directly, without relying on fixture files:

1. **10 rows** -> one chunk, `chunk_range == [0, 9]`, `text_content` has 10 lines.
2. **25 rows** -> one chunk, `chunk_range == [0, 24]`, `text_content` has 25 lines.
3. **30 rows** -> two chunks:
   - `[0, 24]`, `text_content` has 25 lines
   - `[25, 29]`, `text_content` has 5 lines
4. **100 rows** -> four chunks:
   - `[0, 24]`, `[25, 49]`, `[50, 74]`, `[75, 99]`
5. **Multiple sheets** -> flat list contains chunks from both sheets; `sheet_name`
   distinguishes them; `chunk_index` resets for each sheet.
6. **Metadata** -> `file_name`, `file_type`, `columns`, `row_count`, `column_count`,
   `chunk_count` are correct.
7. **Chunk text** -> every chunk has one `column: value, ...` line per row; a 30-row
   sheet yields 25 lines in the first chunk and 5 lines in the second.
8. **Invalid chunk size** -> `chunk_size <= 0` raises `ValueError`.
9. **CSV** -> the same 10/25/30/100-row rules apply without a `sheet_name` key or
   per-sheet chunk index resets.

The helpers create synthetic sheets/CSV data instead of adding large fixtures.

## 8. Future embedding and Qdrant design (not yet implemented)

This section is context for the next agent; do not build it as part of the preprocessing
task unless the user asks.

### Embedding

- Use the existing Gemini setup (`GEMINI_API_KEY`, `google-genai`).
- Candidate model: `gemini-embedding-001` (dimension must be chosen and confirmed).
- One embedding vector per chunk, generated from the compact text representation of that
  chunk's rows.
- Do not embed the entire sheet in one request.
- Watch the model's input-token limit; if a 25-row chunk is too large, split it further or
  use a compact text format.

### Qdrant

- Install `qdrant-client`.
- Use the existing env vars:
  - `QDRANT_URL`
  - `QDRANT_API_KEY`
- Candidate collection: `document_chunks`
- Distance: `Cosine`
- Vector size: must match the chosen embedding dimension.
- One point per chunk.
- Payload: the chunk dictionary from preprocessing (metadata + `text_content`).
- Recommended payload indexes:
  - `file_name` (keyword)
  - `file_type` (keyword)
  - `sheet_name` (keyword)
  - `document_id` if/when added
  - optionally `chunk_index` (integer)
  - optionally `columns` (keyword) only if filtering by column names is needed
- Point ID strategy is undecided because the user says duplicate re-uploads are not a
  current concern. Options: UUID4 per upload, or deterministic ID from
  file fingerprint + sheet name + chunk index.
- Semantic search flow (future): embed the query -> Qdrant top-k search -> return payload
  chunks and scores, with optional filters for file/sheet/type.

### Suggested additional config (future)

```env
QDRANT_COLLECTION_NAME=document_chunks
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIMENSION=768
SPREADSHEET_CHUNK_ROWS=25
```

These are not required by the preprocessing-only implementation.

## 9. Non-goals for this handoff

Do not implement or spend time on:

- Empty-sheet handling
- Duplicate-upload handling
- Embedding generation
- Qdrant client/collection/upsert/search
- API routes or frontend changes
- Re-parsing the source file outside the parser

## 10. Handoff checklist

Before implementing, read:

1. `backend/processing/parsers/spreadsheet_parser.py`
2. `backend/processing/parsers/csv_parser.py`
3. `backend/processing/chunking/spreadsheet_chunker.py`
4. `backend/processing/chunking/csv_chunker.py`
5. `backend/tests/unit/processing/parsers/test_spreadsheet_parser.py`
6. `backend/tests/unit/processing/parsers/test_csv_parser.py`
7. `backend/tests/unit/processing/chunking/test_spreadsheet_chunker.py`
8. `backend/tests/unit/processing/chunking/test_csv_chunker.py`
9. `.env.example`
10. `requirements.txt`

Implementation checklist:

- [x] Add `chunk_spreadsheet` to `backend/processing/chunking/spreadsheet_chunker.py`
- [x] Add `chunk_csv` to `backend/processing/chunking/csv_chunker.py`
- [x] Export/import the chunkers where appropriate
- [x] Add unit tests for the chunking rules above
- [x] Run the targeted pytest suite
- [x] Run the chunkers manually against `backend/tests/fixtures/valid.xlsx` and `valid.csv`
- [x] Confirm metadata values and `text_content` line counts
- [x] Do not add Qdrant/embedding code yet

Definition of done for this phase:

- A parsed spreadsheet becomes a flat list of chunk dictionaries.
- A parsed CSV becomes a flat list of chunk dictionaries without `sheet_name`.
- 100 rows produce the ranges `[0,24]`, `[25,49]`, `[50,74]`, `[75,99]`.
- 30 rows produce `[0,24]` and `[25,29]`.
- Every chunk’s `text_content` has the correct number of lines.
- All preprocessing tests pass.

## 11. Open decisions

- Exact embedding model and output dimension.
- Whether to add `python-dotenv` for loading `.env`.
- Qdrant point ID strategy (deferred because duplicates are out of scope).
- Whether to add a top-level `document_id` later for grouping chunks from one file.
- Whether to send `text_content` directly to the embedding model or transform it further.

## 12. Change log

- 2026-11-03: Created this separate semantic-search/preprocessing handoff document.
  Recorded the parser's list-based `sheets` shape, the 25-row chunk rules, the exact chunk
  metadata contract, the `text_content` field, and the future Qdrant/embedding context.
- 2026-11-03: Moved the handoff document from the agent plan directory into `docs/` at the
  user's request.
- 2026-11-03: Implemented `chunk_spreadsheet` in
  `backend/processing/parsers/spreadsheet_parser.py`, added chunking tests, and updated
  the parser CLI to print preprocessed chunks.
- 2026-11-03: Added per-chunk `text_content`, formatted as one
  `column: value, column: value` line per row, joined with `\n`.
- 2026-11-03: Removed the redundant `content` key from emitted chunks; row data can be
  reconstructed from `text_content`.
- 2026-11-03: Moved `chunk_spreadsheet` from the parser module into
  `backend/processing/chunking/spreadsheet_chunker.py` and moved its tests to
  `backend/tests/unit/processing/chunking/test_spreadsheet_chunker.py`.
- 2026-11-03: Added `chunk_csv` in `backend/processing/chunking/csv_chunker.py`, tests in
  `backend/tests/unit/processing/chunking/test_csv_chunker.py`, and a CSV preview CLI in
  `backend/processing/parsers/csv_parser.py`. CSV chunks omit `sheet_name`.
- 2026-11-03: Added `chunk_image` in `backend/processing/chunking/image_chunker.py`, tests
  in `backend/tests/unit/processing/chunking/test_image_chunker.py`, and image-chunk output
  in the image parser CLI. Image chunks use `file_name`, `file_type`, and `text_content`.
- 2026-11-03: Renamed the emitted chunk text key from `chunk_text` (tabular chunks) and
  `content` (image chunks) to `text_content` across all chunkers, so every embedding input
  uses the same key.

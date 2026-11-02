# Project Folder Structure

Reference layout for the AI-Powered Document Intelligence System.

```
document-intelligence/
├── backend/
├── frontend/
├── docs/
├── evaluation/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md

backend/
├── app/
│   ├── main.py                  # FastAPI app creation, router registration
│   ├── core/
│   │   ├── config.py            # settings, BASE_DIR, paths, env vars
│   │   ├── logging.py
│   │   └── exceptions.py        # custom exceptions
│   │
│   ├── api/
│   │   ├── deps.py              # shared dependencies (db session, etc.)
│   │   └── routes/
│   │       ├── documents.py     # upload, status, results, reprocess
│   │       ├── search.py
│   │       └── corrections.py
│   │
│   ├── schemas/                 # Pydantic models (API + LLM output)
│   │   ├── document.py
│   │   ├── invoice.py           # the structured extraction schema
│   │   └── validation.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── models/              # SQLAlchemy tables
│   │   │   ├── document.py
│   │   │   ├── page.py
│   │   │   ├── extraction.py
│   │   │   ├── validation_issue.py
│   │   │   └── processing_event.py
│   │   └── migrations/          # Alembic
│   │
│   ├── processing/              # Task 1: turning files into text
│   │   ├── pipeline.py          # orchestrates: detect -> route -> parse
│   │   ├── file_detector.py     # magic-bytes type detection
│   │   ├── router.py            # maps file type to the right parser
│   │   ├── types.py             # shared PageResult / ParsedDocument models
│   │   ├── parsers/
│   │   │   ├── base.py          # abstract BaseParser interface
│   │   │   ├── pdf_parser.py    # digital PDF text + per-page scan detection
│   │   │   ├── image_parser.py  # JPG/PNG/TIFF
│   │   │   ├── spreadsheet_parser.py  # XLSX/XLS
│   │   │   └── csv_parser.py
│   │   └── ocr/
│   │       ├── base.py          # abstract OCREngine interface
│   │       ├── tesseract_engine.py
│   │       ├── easyocr_engine.py
│   │       ├── preprocessing.py # grayscale, threshold, deskew
│   │       └── fallback.py      # tiered logic: tesseract -> easyocr -> vision LLM
│   │
│   ├── extraction/              # Task 2: text into structured JSON
│   │   ├── extractor.py         # calls the LLM with structured output
│   │   ├── chunking.py          # splits large documents
│   │   ├── prompts/
│   │   │   └── invoice_extraction.md
│   │   └── llm_client.py        # one wrapper around the provider
│   │
│   ├── validation/              # Task 3
│   │   ├── validator.py         # runs all checks, builds the report
│   │   ├── rules/
│   │   │   ├── required_fields.py
│   │   │   ├── numeric_format.py
│   │   │   ├── totals_consistency.py
│   │   │   └── duplicates.py
│   │   ├── cross_verification.py  # PDF vs PDF, PDF vs Excel
│   │   └── review_flag.py
│   │
│   ├── search/                  # Task 5
│   │   ├── keyword_search.py
│   │   ├── embeddings.py
│   │   └── semantic_search.py
│   │
│   ├── services/                # business logic the routes call
│   │   ├── document_service.py
│   │   ├── correction_service.py
│   │   └── storage_service.py   # saving uploaded files
│   │
│   └── workers/                 # background processing
│       ├── celery_app.py
│       └── tasks.py             # process_document, reprocess_document
│
├── tests/
│   ├── unit/                    # mirrors app/ (processing, validation, ...)
│   ├── integration/             # API + DB + worker
│   ├── fixtures/                # small sample files
│   └── conftest.py
├── scripts/                     # one-off scripts, e.g. run_evaluation.py
├── pyproject.toml
├── Dockerfile
└── .env.example

frontend/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.jsx                 # entry point, mounts the app
│   ├── App.jsx                  # route definitions (React Router)
│   ├── pages/                   # one file per screen
│   │   ├── DocumentsPage.jsx    # upload + documents table
│   │   ├── DocumentDetailPage.jsx
│   │   └── SearchPage.jsx
│   ├── components/
│   │   ├── upload/
│   │   │   └── UploadForm.jsx
│   │   ├── documents/
│   │   │   ├── DocumentTable.jsx
│   │   │   ├── StatusBadge.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   ├── InvoiceFields.jsx
│   │   │   └── LineItemsTable.jsx
│   │   ├── validation/
│   │   │   └── ValidationIssueList.jsx
│   │   ├── search/
│   │   │   ├── SearchBar.jsx
│   │   │   └── SearchResults.jsx
│   │   └── ui/                  # small generic pieces (Button, Card, Spinner)
│   ├── hooks/
│   │   ├── useDocuments.js
│   │   └── useDocumentStatus.js
│   ├── lib/
│   │   ├── apiClient.js         # all backend calls (fake first, real later)
│   │   ├── mockData.js          # fake documents for early development
│   │   └── constants.js         # status values, API base URL
│   └── styles/
│       └── index.css

docs/
├── architecture.md              # diagram + explanation
├── database-schema.md           # ERD
├── design-decisions.md
└── ai-usage.md                  # prompts and AI-assisted-development disclosure

evaluation/
├── dataset/                     # labeled files
├── labels/                      # ground-truth JSON
├── results/                     # measured metrics
└── report.md
```

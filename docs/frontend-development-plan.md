# Frontend Development Plan

Last updated: 2026-11-01

## Overview

React + Vite single-page app for the AI-Powered Document Intelligence System (Task 6 of the spec).
Users can upload documents, monitor processing, inspect and correct extractions, review validation
issues, and search processed documents.

Stack (per `docs/folder-structure.md`): React (JSX), Vite, React Router, plain CSS (`styles/index.css`).

## Requirements

| # | Requirement | What the screen needs | Backend |
|---|---|---|---|
| 1 | Upload multiple documents | Multi-file picker (optionally drag-and-drop), selected-files list, submit button | `POST /documents` (multipart) |
| 2 | Monitor processing progress | Documents table with status badge (queued, processing, completed, needs review, failed) + progress ("pages 40 / 120") | `GET /documents`, `GET /documents/{id}`, polled while any job runs |
| 3 | Inspect extracted information | Detail page: invoice fields, line-items table, per-page source text | `GET /documents/{id}` |
| 4 | Review validation errors | Issues panel (missing field, total mismatch, duplicate) with severity + "needs manual review" badge | Included in `GET /documents/{id}` |
| 5 | Correct values | Editable inputs per field and line item, save button, hand-corrected indicator | `PATCH /documents/{id}/extraction` |
| 6 | Search processed documents | Search box with keyword/semantic toggle, filters (status, supplier, date), results list | `GET /search?q=...` |

## Architecture

Per `docs/folder-structure.md`:

- `src/pages/` — `DocumentsPage.jsx` (upload + table), `DocumentDetailPage.jsx`, `SearchPage.jsx`
- `src/components/` — `upload/UploadForm`, `documents/{DocumentTable, StatusBadge, ProgressBar, InvoiceFields, LineItemsTable}`, `validation/ValidationIssueList`, `search/{SearchBar, SearchResults}`, `ui/` (Button, Card, Spinner)
- `src/hooks/` — `useDocuments.js`, `useDocumentStatus.js`
- `src/lib/` — `apiClient.js` (mock first, real later), `mockData.js`, `constants.js`

## API contract the frontend expects

- `POST /documents` — multipart upload of several files → created records with `id`, `status: "queued"`
- `GET /documents` — list: `id`, `file_name`, `file_type`, `status`, `progress`, `created_at`
- `GET /documents/{id}` — detail: metadata, status, progress, `extraction` (Invoice schema), `validation_issues`, per-page `text_content`
- `PATCH /documents/{id}/extraction` — body: corrected fields/line items → saved record marked hand-corrected
- `GET /search?q=...&mode=keyword|semantic&status=&supplier=&date_from=&date_to=` — matching documents

## Data shapes

- Status enum: `queued | processing | completed | needs_review | failed`
- Progress: `{ pages_done, pages_total }` (null for non-paged types)
- Extraction: `Invoice` schema from `backend/app/schemas/invoice.py` plus `corrected_fields: list[str]`
- ValidationIssue: `{ field, issue_type: missing_field | total_mismatch | duplicate | invalid_numeric, severity, message }`

## Development strategy

- Mock-first: `apiClient.js` serves `mockData.js`; switch to real endpoints via `constants.js` once the backend API (Task 4) exists.
- Polling: `useDocumentStatus` polls `GET /documents/{id}` while status is `queued`/`processing`.
- One task at a time, with the user's approval before starting each task; each verified by the user before starting the next.

## Build order

- [x] F1 — Scaffold: Vite app, folder layout, upload screen (`UploadForm`: file picker + submit alert). Router, mock layer, and API client deferred until needed.
- [ ] F2 — DocumentsPage: `DocumentTable` + `StatusBadge` + `ProgressBar` (req 1, 2; `UploadForm` already exists). Partial: mock progress view with a shared queue is built.
- [ ] F3 — DocumentDetailPage: `InvoiceFields` + `LineItemsTable` + per-page source text (req 3)
- [ ] F4 — `ValidationIssueList` panel + needs-review badge (req 4)
- [ ] F5 — Corrections: editable fields/line items + save + corrected indicator (req 5)
- [ ] F6 — SearchPage: `SearchBar` + keyword/semantic toggle + filters + `SearchResults` (req 6)
- [ ] F7 — Wire to real backend, polling polish

## Progress log

- 2026-11-01 — F1: Vite + React scaffold in `frontend/`; `UploadForm` with multi-file picker and success alert; dependencies installed; `npm run build` passes; dev server verified at http://localhost:5173. Selected-file list, upload logic, and API layer intentionally not built yet.
- 2026-11-01 — `UploadForm`: repeated file selections accumulate and are shown as a name list, so multiple files can be added across separate picks. No upload logic yet.
- 2026-11-01 — `UploadForm`: added a single-invoice uploader accepting only `.pdf`/`.png`; other types alert and are rejected; its Submit shows the invoice success popup. No upload logic yet.
- 2026-11-01 — `UploadForm`: added section headings "Upload Documents" and "Upload Invoice" to separate the two upload sections.
- 2026-11-01 — `UploadForm`: submit flows added. Documents Submit asks via `window.confirm` whether to upload more; "No" locks the picker (names stay) and relabels the button "Processed Documents". Invoice Submit locks its picker and relabels its button "Process". Each reset button returns only its own section to the initial state; the sections are independent.
- 2026-11-01 — `UploadForm`: documents flow now uses a custom in-page popup with literal Yes/No buttons (replacing `window.confirm`); the locked button label is "Process" for both sections.
- 2026-11-01 — `styles/index.css`: minimal CSS positions the documents Yes/No prompt as a centered floating box; all other elements remain unstyled.
- 2026-11-01 — `UploadForm`: invoice success message now uses the same floating box style and auto-hides after 1 second (browser alert removed).
- 2026-11-01 — `styles/index.css`: off-white page background and centered layout (all content centered on screen, forms stacked with spacing).
- 2026-11-01 — `styles/index.css`: reduced vertical gaps (16px between forms, 8px within forms) and widened both buttons (140px minimum width, 8px/16px padding).
- 2026-11-01 — Progress monitoring (mock): `App.jsx` gained an Upload/Progress view switch (no router); `useProcessingQueue` keeps one shared queue and runs one file at a time; `processingService` waits 2 seconds, always fails the first file of a multi-file batch, and succeeds for the rest, so both states are visible; `ProgressPage` lists each file as Queued/Processing/Successful/Failed; Process enqueues, resets its own upload section, and navigates to Progress; a completion popup shows the run's successful/failed counts. No backend calls yet.

## Decisions

- React + Vite (not Next.js): matches `docs/folder-structure.md`; spec allows either.
- Plain CSS via `styles/index.css`: matches reference layout; no UI library unless requested.
- Drag-and-drop: optional per req 1; native multi-file input first, drag-drop only if it stays dependency-free.
- React/frontend files use line-level plain-language comments so the user can learn the codebase.
- Build strictly one requested step at a time; no extra features or scaffolding until asked.

## Maintenance

- Update this file whenever a frontend task is completed, a requirement changes, or an API/data-shape assumption changes.
- Also keep `docs/progress-tracker.md` and `docs/developer-instructions.md` in sync.

# Invoice Validation Plan

Last updated: 2026-11-02

Scope: Task 3 validation for invoice extraction. Source brief: `docs/Ai Engineer Task 1.3.pdf`.

## Current Status

### Implemented

- Missing-fields validator in `backend/app/extraction/validation/missing_fields.py`.
  - Field names are read dynamically from `Invoice.model_fields` and `LineItem.model_fields`.
  - Returns `(has_missing, missing_fields)`.
  - `None`, empty strings, and whitespace-only strings count as missing.
  - Empty `line_items` is flagged once as `{"field": "line_items"}`.
  - Missing line-item values include `index` and `key`.
- Numeric sanity validator in `backend/app/extraction/validation/numeric_sanity.py`.
  - Detects numeric fields dynamically with `numbers.Number`.
  - Flags negative values, and zero `quantity`/`unit_price`.
  - Skips fields already reported as missing.
  - Zero rule is declared in the schema with `json_schema_extra={"non_zero": True}`.
- Shared helpers in `backend/app/extraction/validation/common.py`: `is_missing()`, `missing_paths()`.
- `extract_invoice` calls both validators after `model_dump()` and prints the results.
- Tax optional handling is currently commented out, so `tax` is checked as a required field.

### Current File Layout

```
backend/app/extraction/validation/
├── common.py
├── missing_fields.py
└── numeric_sanity.py
```

## Design

- Each rule is a small pure function: extracted invoice data in, list of issues out.
- Only the duplicate rule touches the database. All other rules are DB-free and unit-testable.
- Normalise before validating: parse numbers like `$1,020.00` and `1.234,56`, convert dates to ISO, map currency symbols to ISO codes. Use `Decimal` (or round to 2 dp) for money, never float comparison.
- Thresholds and tolerances live in config, not in the rule code.

## Rules

### 1. Missing fields

- Flag required fields that are null or empty, and list their names.
- Tax may legitimately be null, so treat it as optional.
- Current implementation checks every field dynamically, including tax, because the optional-tax logic is commented out.

### 2. Consistency

- `sum(line item amounts) = subtotal`
- `subtotal + tax (+ shipping - discount, if those fields exist) = total`
- `quantity x unit_price = amount`, for each line item.
- Allow a small tolerance (about 0.01 to 0.02).
- If the data a check needs is null, skip that check and note why. Do not report a mismatch.

### 3. Numeric sanity

- Negative or zero quantity or price.
- Tax greater than subtotal.
- Absurdly large totals.
- Values that cannot be parsed as numbers.
- Currency is not a valid ISO code.
- Date is unparseable or in the future.

### 4. Duplicates (needs DB)

- Match on normalised supplier name (case and whitespace) + invoice number, optionally + total.
- Also compare the file hash, to catch exact re-uploads.
- Add a DB constraint or lock so two files processed at once cannot both pass.
- Flag the duplicate. Never delete it.

### 5. Low OCR confidence

- A source page below the confidence threshold produces a warning.

## Issue Structure

Each issue has:

- `rule`
- `field`
- `severity` (`error` or `warning`)
- `message`
- `expected`
- `actual`

`needs_review = true` if any issue has severity `error`. The issue list explains why.

## Statuses

- No issues: `auto_approved`.
- Any error: `needs_review`.
- After a human decides: `approved` or `rejected`.
- Always save the extraction and its issues to the database, flagged or not.

## Optimisation

- If the consistency checks fail, re-run extraction once (for example with the vision model) before flagging.
- The re-run must be guarded so it cannot loop.

## Tests

- For each rule: one passing case, one failing case, one case at the tolerance boundary.
- Test null handling (skipped checks) and the combined review flag.

## Known Gaps to Resolve

- Normalisation must happen before `Invoice.model_validate`, because `Decimal` will not accept values like `"$1,020.00"` directly.
- `shipping` and `discount` do not exist in `Invoice`; consistency should omit them unless they are added.
- No database or repository layer exists yet for duplicate detection or persistence.
- `easyocr_engine.parse_image` currently discards confidence values (`detail=0`), so the low-confidence rule needs OCR metadata.
- No config module exists for tolerances, maximum totals, OCR threshold, or future-date drift.
- No issue/result schema exists yet.
- The current instruction keeps all validators in `backend/app/extraction/validation/`; `docs/folder-structure.md` targets a separate `backend/app/validation/` package later.

## Implementation Checklist

- [x] Missing fields
- [x] Numeric sanity — negative values and zero quantity/price
- [ ] Numeric sanity — tax > subtotal, absurd totals, unparseable values
- [ ] Issue/result model
- [ ] Validation config and thresholds
- [ ] Normalizer
- [x] Consistency rule
- [x] Duplicate rule (mocked)
- [ ] Low OCR confidence rule
- [ ] Orchestrator and one-time re-extraction
- [ ] Persistence, statuses, and human review
- [ ] Unit tests per rule

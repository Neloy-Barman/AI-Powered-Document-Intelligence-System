# Database Schema (Draft)

## invoices

- `id` (PK)
- `invoice_number`
- `invoice_date`
- `supplier_name`
- `customer_name`
- `subtotal`
- `tax`
- `total`
- `currency`
- `line_items` (JSON)
- `has_missing_fields`
- `has_numeric_issues`
- `has_consistency_issues`
- `has_duplicate_issues`
- `missing_fields` (JSON)
- `numeric_issues` (JSON)
- `consistency_issues` (JSON)
- `duplicate_issues` (JSON)
- `status` (auto_approved / needs_review / approved / rejected)
- `created_at`
- `updated_at`

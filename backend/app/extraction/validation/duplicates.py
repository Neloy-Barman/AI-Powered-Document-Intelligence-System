# Duplicate detection rule.
# Mocked without a database: checks whether the invoice number already exists
# in a known list. In production this will query the database and also compare
# supplier name, total, and file hash.

# Mock "database" of already-seen invoice numbers.
EXISTING_INVOICE_NUMBERS: list[str] = ["INV-001", "INV-002", "INV-100"]


def _normalize(value: object) -> str:
    # Normalise for comparison: strip whitespace and ignore case.
    return str(value).strip().casefold()


def validate_duplicates(
    invoice: dict,
    existing_invoice_numbers: list[str] | None = None,
) -> tuple[bool, list[dict[str, object]]]:
    duplicates: list[dict[str, object]] = []

    invoice_number = invoice.get("invoice_number")

    # Do not check when the invoice number is missing or empty.
    if invoice_number is None or (
        isinstance(invoice_number, str) and not invoice_number.strip()
    ):
        return False, duplicates

    known = (
        existing_invoice_numbers
        if existing_invoice_numbers is not None
        else EXISTING_INVOICE_NUMBERS
    )

    normalized_invoice = _normalize(invoice_number)

    for known_id in known:
        if _normalize(known_id) == normalized_invoice:
            # Only the reason and the duplicate invoice id are needed here,
            # since the duplicate check is specifically about the invoice id.
            duplicates.append(
                {
                    "reason": "duplicate",
                    "duplicate_id": known_id,
                }
            )
            break

    return bool(duplicates), duplicates

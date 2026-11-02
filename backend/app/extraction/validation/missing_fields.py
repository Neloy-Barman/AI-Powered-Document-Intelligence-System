# Missing-fields rule.
# Checks every field of the Invoice and LineItem schemas dynamically, so the
# rule follows schema changes without editing this file.

from backend.app.extraction.validation.common import is_missing
from backend.app.schemas.invoice import Invoice, LineItem

# OPTIONAL_FIELDS = {"tax"}  # commented out: tax is currently required


def validate_missing_fields(invoice: dict) -> tuple[bool, list[dict[str, object]]]:
    missing_fields: list[dict[str, object]] = []

    # Read field names from the Pydantic models instead of hardcoding them.
    top_level_fields = list(Invoice.model_fields)
    line_item_fields = list(LineItem.model_fields)

    for field in top_level_fields:
        # if field in OPTIONAL_FIELDS:  # skipped while tax is required
        #     continue

        value = invoice.get(field)

        if field == "line_items":
            # An empty/missing line_items list counts as missing.
            if not value:
                missing_fields.append({"field": field})
            continue

        if is_missing(value):
            missing_fields.append({"field": field})

    line_items = invoice.get("line_items") or []

    # Nested check: for each line item, record which key is missing and where.
    for index, item in enumerate(line_items):
        for key in line_item_fields:
            if is_missing(item.get(key)):
                missing_fields.append(
                    {"field": "line_items", "index": index, "key": key}
                )

    return bool(missing_fields), missing_fields

# Consistency rule.
# Checks that the numbers in an invoice add up correctly:
#   1. quantity x unit_price = amount (per line item)
#   2. sum(line item amounts) = subtotal
#   3. subtotal + tax (+ shipping - discount) = total
# Checks that fail are skipped when their inputs are missing or already
# flagged by the missing-fields or numeric-sanity rules.

from decimal import Decimal

from backend.app.extraction.validation.common import missing_paths

# Maximum allowed difference between two money values before we flag a
# mismatch. Kept here for now; can move to a config module later.
TOLERANCE = Decimal("0.02")


def _to_decimal(value: object) -> Decimal | None:
    # Safely convert a value to Decimal. Returns None if it cannot be parsed.
    try:
        return Decimal(str(value))
    except Exception:
        return None


def validate_consistency(
    invoice: dict,
    missing_fields: list[dict[str, object]],
    numeric_issues: list[dict[str, object]],
) -> tuple[bool, list[dict[str, object]]]:
    flagged_fields: list[dict[str, object]] = []

    # Combine the paths already flagged as missing or numerically invalid,
    # so this rule skips anything that already failed an earlier check.
    skipped = missing_paths(missing_fields) | missing_paths(numeric_issues)

    line_items = invoice.get("line_items") or []

    # ------------------------------------------------------------------
    # Check 1: quantity x unit_price = amount, for each line item.
    # ------------------------------------------------------------------
    for index, item in enumerate(line_items):
        quantity = item.get("quantity")
        unit_price = item.get("unit_price")
        amount = item.get("amount")

        # Skip this line item if any of the three values is missing or
        # was already flagged by an earlier rule.
        if (
            ("line_items", index, "quantity") in skipped
            or ("line_items", index, "unit_price") in skipped
            or ("line_items", index, "amount") in skipped
            or quantity is None
            or unit_price is None
            or amount is None
        ):
            continue

        q = _to_decimal(quantity)
        u = _to_decimal(unit_price)
        a = _to_decimal(amount)

        # If any value cannot be parsed as a number, skip this check.
        if q is None or u is None or a is None:
            continue

        # Flag when the product differs from the stated amount by more than
        # the tolerance.
        if abs(q * u - a) > TOLERANCE:
            flagged_fields.append(
                {
                    "field": "line_items",
                    "index": index,
                    "key": "amount",
                    "reason": "quantity_x_unit_price",
                    "expected": f"{q * u:.2f}",  # what amount should be
                    "actual": f"{a:.2f}",        # what amount was given
                }
            )

    # ------------------------------------------------------------------
    # Check 2: sum(line item amounts) = subtotal.
    # ------------------------------------------------------------------
    subtotal = invoice.get("subtotal")
    amounts = [item.get("amount") for item in line_items]

    # Only run when subtotal and every amount are present and not already
    # flagged by an earlier rule.
    if (
        subtotal is not None
        and amounts
        and all(amount is not None for amount in amounts)
        and ("subtotal",) not in skipped
        and not any(
            ("line_items", i, "amount") in skipped for i in range(len(line_items))
        )
    ):
        subtotal_dec = _to_decimal(subtotal)
        amount_sum = sum(_to_decimal(a) for a in amounts)  # type: ignore[arg-type]

        if subtotal_dec is not None and amount_sum is not None:
            if abs(amount_sum - subtotal_dec) > TOLERANCE:
                flagged_fields.append(
                    {
                        "field": "subtotal",
                        "reason": "line_items_sum",
                        "expected": f"{amount_sum:.2f}",  # sum of line items
                        "actual": f"{subtotal_dec:.2f}",  # stated subtotal
                    }
                )

    # ------------------------------------------------------------------
    # Check 3: subtotal + tax (+ shipping - discount) = total.
    # ------------------------------------------------------------------
    total = invoice.get("total")
    tax = invoice.get("tax")
    shipping = invoice.get("shipping")   # included only if present
    discount = invoice.get("discount")   # included only if present

    # Only run when subtotal and total are present and not already flagged.
    if (
        subtotal is not None
        and total is not None
        and ("subtotal",) not in skipped
        and ("total",) not in skipped
    ):
        subtotal_dec = _to_decimal(subtotal)
        total_dec = _to_decimal(total)

        if subtotal_dec is not None and total_dec is not None:
            expected = subtotal_dec

            # Add tax if present and not flagged.
            if tax is not None and ("tax",) not in skipped:
                tax_dec = _to_decimal(tax)
                if tax_dec is not None:
                    expected += tax_dec

            # Add shipping if present.
            if shipping is not None:
                shipping_dec = _to_decimal(shipping)
                if shipping_dec is not None:
                    expected += shipping_dec

            # Subtract discount if present.
            if discount is not None:
                discount_dec = _to_decimal(discount)
                if discount_dec is not None:
                    expected -= discount_dec

            if abs(expected - total_dec) > TOLERANCE:
                flagged_fields.append(
                    {
                        "field": "total",
                        "reason": "subtotal_plus_tax",
                        "expected": f"{expected:.2f}",  # computed total
                        "actual": f"{total_dec:.2f}",   # stated total
                    }
                )

    return bool(flagged_fields), flagged_fields

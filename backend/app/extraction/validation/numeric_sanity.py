# Numeric sanity rule.
# Checks numeric fields for negative values and zero where the schema disallows
# it. Fields already flagged as missing are skipped.

from decimal import Decimal
from numbers import Number
from types import UnionType
from typing import Annotated, Union, get_args, get_origin

from pydantic.fields import FieldInfo

from backend.app.extraction.validation.common import missing_paths
from backend.app.schemas.invoice import Invoice, LineItem


def _is_numeric_annotation(annotation: object) -> bool:
    # Unwrap Annotated/Union to reach the underlying type, then check whether
    # it is a numeric type using numbers.Number instead of a hardcoded list.
    if get_origin(annotation) is Annotated:
        return _is_numeric_annotation(get_args(annotation)[0])
    if get_origin(annotation) in (Union, UnionType):
        return any(_is_numeric_annotation(arg) for arg in get_args(annotation))
    return isinstance(annotation, type) and issubclass(annotation, Number)


def _numeric_fields(model: type) -> list[tuple[str, FieldInfo]]:
    # Returns only the numeric fields of a Pydantic model.
    return [
        (name, field)
        for name, field in model.model_fields.items()
        if _is_numeric_annotation(field.annotation)
    ]


def _zero_not_allowed(field: FieldInfo) -> bool:
    # Read the "non_zero" flag from the schema's json_schema_extra instead of
    # maintaining a list of field names in the validator.
    extra = field.json_schema_extra or {}
    return bool(extra.get("non_zero"))


def validate_numeric_sanity(
    invoice: dict, missing_fields: list[dict[str, object]]
) -> tuple[bool, list[dict[str, object]]]:
    flagged_fields: list[dict[str, object]] = []
    missing = missing_paths(missing_fields)

    # Top-level numeric fields: flag negatives.
    for field_name, _ in _numeric_fields(Invoice):
        if (field_name,) in missing:
            continue  # already reported as missing, skip

        value = Decimal(str(invoice.get(field_name)))

        if value < 0:
            flagged_fields.append(
                {
                    "field": field_name,
                    "value": invoice.get(field_name),
                    "reason": "negative",
                }
            )

    line_items = invoice.get("line_items") or []

    # Line-item numeric fields: flag negatives and zeros where disallowed.
    for index, item in enumerate(line_items):
        for key, field in _numeric_fields(LineItem):
            if ("line_items", index, key) in missing:
                continue  # already reported as missing, skip

            value = Decimal(str(item.get(key)))

            if value < 0:
                flagged_fields.append(
                    {
                        "field": "line_items",
                        "index": index,
                        "key": key,
                        "value": item.get(key),
                        "reason": "negative",
                    }
                )
            elif value == 0 and _zero_not_allowed(field):
                flagged_fields.append(
                    {
                        "field": "line_items",
                        "index": index,
                        "key": key,
                        "value": item.get(key),
                        "reason": "zero",
                    }
                )

    return bool(flagged_fields), flagged_fields

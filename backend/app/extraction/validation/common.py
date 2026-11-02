# Shared helpers used by more than one validation rule.
# Keep rule logic out of here; this file only holds common plumbing.


def is_missing(value: object) -> bool:
    # True when a value is None or an empty/whitespace-only string.
    # Used by every rule that needs to decide whether a field has usable data.
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def missing_paths(
    missing_fields: list[dict[str, object]],
) -> set[tuple[object, ...]]:
    # Turns the missing-field list into a lookup set so other rules can
    # quickly check whether a (top-level or line-item) field was already
    # reported as missing and skip it.
    paths: set[tuple[object, ...]] = set()

    for item in missing_fields:
        field = item.get("field")
        if field == "line_items" and "index" in item:
            paths.add(("line_items", item["index"], item.get("key")))
        else:
            paths.add((field,))

    return paths

# Run: python backend/app/extraction/extractor.py (requires GEMINI_API_KEY)

from pathlib import Path

from backend.app.schemas.invoice import Invoice
from backend.app.extraction.llm_client import vision_completion
from backend.app.extraction.validation.missing_fields import validate_missing_fields
from backend.app.extraction.validation.numeric_sanity import validate_numeric_sanity
from backend.app.extraction.validation.consistency import validate_consistency
from backend.app.extraction.validation.duplicates import validate_duplicates

# MODEL = "gemini-2.5-flash-lite"
# MODEL = "gemini-3.1-flash-lite"
MODEL = "gemini-3-flash-preview"

SYSTEM_PROMPT = (
    "You are an invoice data extractor. "
    "Extract the requested fields from the invoice image. "
    "Return JSON only, matching the schema. "
    "Use null for any field that is missing or uncertain. Never invent values."
)


def extract_invoice(image_path: str | Path) -> dict:
    path = Path(image_path)
    try:
        raw = vision_completion(
            MODEL, SYSTEM_PROMPT, path, Invoice.model_json_schema()
        )
        invoice = Invoice.model_validate_json(raw)
        invoice_data = invoice.model_dump()

        has_missing, missing_fields = validate_missing_fields(invoice_data)
        has_numeric_issues, numeric_issues = validate_numeric_sanity(
            invoice_data, missing_fields
        )
        has_consistency_issues, consistency_issues = validate_consistency(
            invoice_data, missing_fields, numeric_issues
        )
        has_duplicate_issues, duplicate_issues = validate_duplicates(invoice_data)

        # Print validation results for inspection.
        print(f"Has missing fields: {has_missing}")
        print(f"Missing fields: {missing_fields}")
        print(f"Has numeric issues: {has_numeric_issues}")
        print(f"Numeric issues: {numeric_issues}")
        print(f"Has consistency issues: {has_consistency_issues}")
        print(f"Consistency issues: {consistency_issues}")
        print(f"Has duplicate issues: {has_duplicate_issues}")
        print(f"Duplicate issues: {duplicate_issues}")

        needs_review = (
            has_missing
            or has_numeric_issues
            or has_consistency_issues
            or has_duplicate_issues
        )

        status = "needs_review" if needs_review else "auto_approved"

        return {
            "status": status,
            "file_name": path.name,
            "invoice": invoice_data,
            "validation": {
                "missing_fields": (has_missing, missing_fields),
                "numeric_issues": (has_numeric_issues, numeric_issues),
                "consistency_issues": (has_consistency_issues, consistency_issues),
                "duplicate_issues": (has_duplicate_issues, duplicate_issues),
            },
        }
    except FileNotFoundError as error:
        error_message = f"{type(error).__name__}: {error}"
        print(error_message)
        return {
            "status": "failed",
            "file_name": path.name,
            "error_message": error_message,
        }
    except Exception as error:
        error_message = f"{type(error).__name__}: {error}"
        print(error_message)
        return {
            "status": "failed",
            "file_name": path.name,
            "error_message": error_message,
        }


if __name__ == "__main__":
    import pprint

    result = extract_invoice("backend/tests/fixtures/invoice.png")

    # result = extract_invoice(
    #     "backend/tests/fixtures/invoice_no_supplier_customer_invoice_no.png"
    # )

    pprint.pprint(result)

import base64
from pathlib import Path

from google import genai

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


def encode_image(image_path: str | Path) -> str:
    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def _mime_type(image_path: str | Path) -> str:
    suffix = Path(image_path).suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
    }.get(suffix, "image/png")


def vision_completion(
    model: str, system_prompt: str, image_path: str | Path, json_schema: dict
) -> str:
    client = get_client()
    interaction = client.interactions.create(
        model=model,
        system_instruction=system_prompt,
        input=[
            {"type": "text", "text": "Extract the invoice fields from this image."},
            {
                "type": "image",
                "data": encode_image(image_path),
                "mime_type": _mime_type(image_path),
            },
        ],
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": json_schema,
        },
    )
    return interaction.output_text or "{}"

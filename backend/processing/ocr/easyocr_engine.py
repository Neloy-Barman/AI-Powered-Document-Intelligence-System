from pathlib import Path
import warnings

# EasyOCR and PyTorch emit CPU-only noise that is not actionable on this machine.
# Keep the filters narrow so unrelated warnings still surface.
warnings.filterwarnings(
    "ignore",
    message=r"torch\.quantize_per_tensor.*",
    category=UserWarning,
    module=r"torch\.ao\.nn\.quantized\.dynamic\.modules\.rnn",
)
warnings.filterwarnings(
    "ignore",
    message=r"'pin_memory' argument is set as true but no accelerator is found.*",
    category=UserWarning,
    module=r"torch\.utils\.data\.dataloader",
)

import easyocr

reader = easyocr.Reader(["en", "bn"], verbose=False)


def parse_image(file_path: str | Path) -> dict[str, str]:
    try:
        results = reader.readtext(str(file_path), detail=0, paragraph=True)
        return {
            "status": "success",
            "content": results[0],
        }
    except Exception as error:
        error_message = f"{type(error).__name__}: {error}"
        print(error_message)
        return {
            "status": "failed",
            "error_message": error_message,
        }

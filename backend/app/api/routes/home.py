from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def home() -> dict[str, str]:
    return {
        "status": "success",
        "message": "AI-Powered Document Intelligence System API is running.",
    }

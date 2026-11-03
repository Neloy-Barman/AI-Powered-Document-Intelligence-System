from fastapi import APIRouter, HTTPException, Query

from backend.app.core.config import QDRANT_SEARCH_LIMIT
from backend.app.search.semantic_search import create_qdrant_service

router = APIRouter()


@router.get("/search")
def search_documents(
    q: str = Query(..., min_length=1, description="Semantic search query"),
    limit: int = Query(QDRANT_SEARCH_LIMIT, ge=1, le=10),
) -> dict:
    """Return the top matching previously processed documents."""
    try:
        service = create_qdrant_service()
        results = service.search(q, limit=limit)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return {
        "status": "success",
        "query": q,
        "limit": limit,
        "results": [
            {
                "file_name": result["payload"].get("file_name"),
                "score": result["score"],
            }
            for result in results
        ],
    }

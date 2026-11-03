from typing import Any
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from backend.app.core.config import (
    QDRANT_API_KEY,
    QDRANT_COLLECTION_NAME,
    QDRANT_SEARCH_LIMIT,
    QDRANT_URL,
    SEMANTIC_SEARCH_WEIGHT,
    KEYWORD_SEARCH_WEIGHT,
)
from backend.app.search.embeddings import EmbeddingModel, create_embedding_model


class QdrantVectorService:
    """Small Qdrant service for collection setup, upsert, and search."""

    def __init__(
        self,
        url: str = QDRANT_URL,
        api_key: str | None = QDRANT_API_KEY,
        collection_name: str = QDRANT_COLLECTION_NAME,
        embedding_model: EmbeddingModel | None = None,
        search_limit: int = QDRANT_SEARCH_LIMIT,
    ) -> None:
        if url == ":memory:":
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.embedding_model = embedding_model or create_embedding_model()
        self.search_limit = search_limit

    def ensure_collection(self) -> None:
        """Create the collection if it does not exist; reuse it if it does."""
        if self.client.collection_exists(self.collection_name):
            collection = self.client.get_collection(self.collection_name)
            existing_size = collection.config.params.vectors.size
            if existing_size != self.embedding_model.dimension:
                raise ValueError(
                    f"Collection '{self.collection_name}' has vector size "
                    f"{existing_size}, but the embedding model produces "
                    f"{self.embedding_model.dimension}."
                )
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embedding_model.dimension,
                distance=Distance.COSINE,
            ),
        )

    def upsert_chunks(
        self,
        chunks: list[dict[str, Any]],
        batch_size: int = 100,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Embed chunks and upsert them into Qdrant.

        batch_size controls how many points are sent in one upsert request.
        metadata is merged into every point payload.
        """
        if not chunks:
            return {
                "collection_name": self.collection_name,
                "upserted": 0,
                "point_ids": [],
            }

        self.ensure_collection()

        point_ids: list[str] = []

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            vectors = self.embedding_model.embed_texts(
                [chunk["text_content"] for chunk in batch]
            )

            points = [
                PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={**chunk, **(metadata or {})},
                )
                for chunk, vector in zip(batch, vectors)
            ]

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )
            point_ids.extend(str(point.id) for point in points)

        return {
            "collection_name": self.collection_name,
            "upserted": len(point_ids),
            "point_ids": point_ids,
        }

    def search(
        self,
        query: str,
        limit: int | None = None,
        filters: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Run a basic top-k similarity search."""
        self.ensure_collection()

        query_vector = self.embedding_model.embed_query(query)
        qdrant_filter = None

        if filters:
            qdrant_filter = Filter(
                must=[
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                    for key, value in filters.items()
                ]
            )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit or self.search_limit,
            query_filter=qdrant_filter,
            with_payload=True,
        )

        return [
            {
                "id": str(point.id),
                "score": point.score,
                "payload": point.payload,
            }
            for point in response.points
        ]

    def hybrid_search(
        self,
        query: str,
        limit: int | None = None,
        semantic_weight: float = SEMANTIC_SEARCH_WEIGHT,
        keyword_weight: float = KEYWORD_SEARCH_WEIGHT,
    ) -> list[dict[str, Any]]:
        """Run LangChain-based hybrid search using Qdrant + BM25."""
        from backend.app.search.langchain_hybrid_search import LangChainHybridSearch

        hybrid = LangChainHybridSearch(
            service=self,
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight,
            limit=limit or self.search_limit,
        )
        return hybrid.search(query=query, limit=limit)


def create_qdrant_service() -> QdrantVectorService:
    """Convenience factory using the configured settings."""
    return QdrantVectorService()

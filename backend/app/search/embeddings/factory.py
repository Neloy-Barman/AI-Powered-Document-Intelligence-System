from backend.app.core.config import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
)
from backend.app.search.embeddings.base import EmbeddingModel
from backend.app.search.embeddings.google import GoogleGeminiEmbedding
from backend.app.search.embeddings.local import SentenceTransformerEmbedding


def create_embedding_model(
    provider: str = EMBEDDING_PROVIDER,
    model_name: str = EMBEDDING_MODEL,
    device: str = EMBEDDING_DEVICE,
    api_key: str | None = None,
    output_dimensionality: int | None = None,
) -> EmbeddingModel:
    """Create the configured embedding provider."""
    if provider == "local":
        return SentenceTransformerEmbedding(
            model_name=model_name,
            device=device,
        )

    if provider == "google":
        return GoogleGeminiEmbedding(
            model_name=model_name,
            api_key=api_key,
            output_dimensionality=output_dimensionality,
        )

    raise ValueError(f"Unsupported embedding provider: {provider}")

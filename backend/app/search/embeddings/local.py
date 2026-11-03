from typing import Sequence

from sentence_transformers import SentenceTransformer

from backend.app.core.config import EMBEDDING_MODEL, EMBEDDING_DEVICE
from backend.app.search.embeddings.base import EmbeddingModel


class SentenceTransformerEmbedding(EmbeddingModel):
    """Local embedding model used for development and testing."""

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        device: str = EMBEDDING_DEVICE,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.model = SentenceTransformer(model_name, device=device)

    @property
    def dimension(self) -> int:
        dimension = self.model.get_embedding_dimension()
        if dimension is None:
            raise RuntimeError(
                f"Could not determine embedding dimension for {self.model_name}"
            )
        return dimension

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

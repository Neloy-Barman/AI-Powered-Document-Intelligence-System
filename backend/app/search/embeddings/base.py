from abc import ABC, abstractmethod
from typing import Sequence


class EmbeddingModel(ABC):
    """Common interface for local and cloud embedding providers."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector size produced by this model."""
        ...

    @abstractmethod
    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed a list of texts into normalized vectors."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        return self.embed_texts([text])[0]

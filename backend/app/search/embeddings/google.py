from typing import Sequence

from backend.app.search.embeddings.base import EmbeddingModel


class GoogleGeminiEmbedding(EmbeddingModel):
    """Cloud embedding model using Google Gemini.

    This is optional and is only used when EMBEDDING_PROVIDER is set to
    "google".
    """

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        output_dimensionality: int | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("An API key is required for Google Gemini embeddings")

        from google import genai

        self.model_name = model_name
        self.output_dimensionality = output_dimensionality
        self.client = genai.Client(api_key=api_key)
        self._dimension: int | None = None

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = len(self.embed_texts(["dimension probe"])[0])
        return self._dimension

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        config = None
        if self.output_dimensionality is not None:
            config = {"output_dimensionality": self.output_dimensionality}

        response = self.client.models.embed_content(
            model=self.model_name,
            contents=list(texts),
            config=config,
        )

        return [embedding.values for embedding in response.embeddings]

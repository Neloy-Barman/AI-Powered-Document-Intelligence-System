import json
import tempfile
from pathlib import Path

from backend.app.search.embeddings.base import EmbeddingModel
from backend.app.search.langchain_hybrid_search import LangChainHybridSearch
from backend.app.search.semantic_search import QdrantVectorService


class FakeEmbeddingModel(EmbeddingModel):
    def __init__(self, dimension: int = 3) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def _vector_for_text(self, text: str) -> list[float]:
        lowered = text.lower()
        if "invoice" in lowered:
            return [1.0, 0.0, 0.0]
        if "supplier" in lowered:
            return [0.0, 1.0, 0.0]
        if "payment" in lowered:
            return [0.0, 0.0, 1.0]
        return [0.0, 0.0, 0.0]

    def embed_texts(self, texts):
        return [self._vector_for_text(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector_for_text(text)


def test_langchain_hybrid_search_returns_expected_shape(tmp_path: Path) -> None:
    corpus_path = tmp_path / "bm25_corpus.json"
    service = QdrantVectorService(
        url=":memory:",
        collection_name="test-hybrid",
        embedding_model=FakeEmbeddingModel(),
    )

    chunks = [
        {
            "file_name": "a.csv",
            "file_type": ".csv",
            "text_content": "invoice total amount",
        },
        {
            "file_name": "b.xlsx",
            "file_type": ".xlsx",
            "text_content": "supplier report",
        },
        {
            "file_name": "c.png",
            "file_type": ".png",
            "text_content": "payment record",
        },
    ]

    service.upsert_chunks(chunks)

    hybrid = LangChainHybridSearch(
        service=service,
        corpus_path=corpus_path,
        limit=2,
    )
    hybrid.add_documents(chunks)

    results = hybrid.search("invoice", limit=2)

    assert len(results) >= 1
    assert "file_name" in results[0]
    assert "score" in results[0]
    assert "text_content" in results[0]
    assert results[0]["file_name"] == "a.csv"

    assert corpus_path.exists()
    saved_corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    assert len(saved_corpus) == 3

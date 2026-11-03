from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from pydantic import ConfigDict, PrivateAttr

from backend.app.core.config import (
    BM25_CORPUS_PATH,
    HYBRID_SEARCH_LIMIT,
    KEYWORD_SEARCH_WEIGHT,
    SEMANTIC_SEARCH_WEIGHT,
)
from backend.app.search.bm25_corpus import load_corpus_documents, append_chunks
from backend.app.search.semantic_search import QdrantVectorService


class SemanticRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    service: QdrantVectorService
    limit: int = 10

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> list[Document]:
        results = self.service.search(query=query, limit=self.limit)
        documents: list[Document] = []

        for result in results:
            payload = result.get("payload", {}) or {}
            text_content = payload.get("text_content", "")
            if not text_content:
                continue

            metadata = {
                key: value
                for key, value in payload.items()
                if key != "text_content"
            }
            documents.append(Document(page_content=text_content, metadata=metadata))

        return documents


class KeywordRetriever(BaseRetriever):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    corpus_path: Path = BM25_CORPUS_PATH
    limit: int = 10
    _documents: list[Document] = PrivateAttr(default_factory=list)
    _bm25: BM25Retriever | None = PrivateAttr(default=None)

    def _ensure_index(self) -> None:
        if not self._documents:
            self._documents = load_corpus_documents(self.corpus_path)

        if self._bm25 is None and self._documents:
            self._bm25 = BM25Retriever.from_documents(self._documents)
            self._bm25.k = self.limit

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> list[Document]:
        self._ensure_index()
        if self._bm25 is None:
            return []
        return self._bm25.invoke(query)

    def add_documents(self, documents: list[Document]) -> None:
        self._documents.extend(documents)
        self._bm25 = None


class LangChainHybridSearch:
    def __init__(
        self,
        service: QdrantVectorService,
        corpus_path: Path = BM25_CORPUS_PATH,
        semantic_weight: float = SEMANTIC_SEARCH_WEIGHT,
        keyword_weight: float = KEYWORD_SEARCH_WEIGHT,
        limit: int = HYBRID_SEARCH_LIMIT,
    ) -> None:
        self.service = service
        self.corpus_path = corpus_path
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.limit = limit

        self._documents = load_corpus_documents(corpus_path)

        self.semantic_retriever = SemanticRetriever(
            service=service,
            limit=limit * 3,
        )
        self.keyword_retriever = KeywordRetriever(
            corpus_path=corpus_path,
            limit=limit * 3,
        )
        self.keyword_retriever._documents = self._documents
        self.keyword_retriever._ensure_index()

        self.ensemble = EnsembleRetriever(
            retrievers=[self.keyword_retriever, self.semantic_retriever],
            weights=[keyword_weight, semantic_weight],
        )

    def add_documents(self, chunks: list[dict[str, Any]]) -> None:
        """Persist new chunks and update the keyword index."""
        append_chunks(chunks, self.corpus_path)

        new_documents = [
            Document(
                page_content=chunk["text_content"],
                metadata={
                    key: value
                    for key, value in chunk.items()
                    if key != "text_content"
                },
            )
            for chunk in chunks
        ]

        self._documents.extend(new_documents)
        self.keyword_retriever._documents = self._documents
        self.keyword_retriever._bm25 = None

    def search(self, query: str, limit: int | None = None) -> list[dict[str, Any]]:
        final_limit = limit or self.limit

        semantic_docs = self.semantic_retriever.invoke(query)
        keyword_docs = self.keyword_retriever.invoke(query)
        ensemble_docs = self.ensemble.invoke(query)

        ranks: dict[int, float] = {}
        for retriever_index, docs in enumerate((keyword_docs, semantic_docs)):
            weight = (
                self.keyword_weight
                if retriever_index == 0
                else self.semantic_weight
            )
            for rank, document in enumerate(docs):
                key = id(document)
                ranks[key] = ranks.get(key, 0.0) + weight / (rank + 1)

        results: list[dict[str, Any]] = []
        for index, document in enumerate(ensemble_docs[:final_limit]):
            key = id(document)
            results.append(
                {
                    "file_name": document.metadata.get("file_name"),
                    "score": ranks.get(key, 1.0 / (index + 1)),
                    "text_content": document.page_content,
                    "metadata": document.metadata,
                }
            )

        return results


def create_langchain_hybrid_search(
    service: QdrantVectorService | None = None,
    corpus_path: Path = BM25_CORPUS_PATH,
    semantic_weight: float = SEMANTIC_SEARCH_WEIGHT,
    keyword_weight: float = KEYWORD_SEARCH_WEIGHT,
    limit: int = HYBRID_SEARCH_LIMIT,
) -> "LangChainHybridSearch":
    if service is None:
        from backend.app.search.semantic_search import create_qdrant_service

        service = create_qdrant_service()

    return LangChainHybridSearch(
        service=service,
        corpus_path=corpus_path,
        semantic_weight=semantic_weight,
        keyword_weight=keyword_weight,
        limit=limit,
    )

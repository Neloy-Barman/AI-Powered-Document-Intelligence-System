import json
import uuid
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from backend.app.core.config import BM25_CORPUS_PATH


def load_corpus(path: Path = BM25_CORPUS_PATH) -> list[dict[str, Any]]:
    """Load the persisted BM25 corpus, or return an empty list."""
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        return []

    return data


def save_corpus(corpus: list[dict[str, Any]], path: Path = BM25_CORPUS_PATH) -> None:
    """Persist the BM25 corpus to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(corpus, file, ensure_ascii=False, indent=2)


def append_chunks(
    chunks: list[dict[str, Any]],
    path: Path = BM25_CORPUS_PATH,
) -> list[dict[str, Any]]:
    """Append chunks to the corpus, replacing old entries for the same file."""
    corpus = load_corpus(path)

    new_file_names = {chunk.get("file_name") for chunk in chunks}
    corpus = [
        entry for entry in corpus
        if entry.get("file_name") not in new_file_names
    ]

    for chunk in chunks:
        chunk.setdefault("id", chunk.get("bm25_entry_id") or str(uuid4()))
        chunk.setdefault("bm25_entry_id", chunk["id"])

    corpus.extend(chunks)

    save_corpus(corpus, path)
    return corpus


def load_corpus_documents(path: Path = BM25_CORPUS_PATH) -> list[Document]:
    """Convert the persisted corpus into LangChain documents."""
    documents: list[Document] = []

    for entry in load_corpus(path):
        text_content = entry.get("text_content", "")
        if not text_content:
            continue

        metadata = {
            key: value
            for key, value in entry.items()
            if key != "text_content"
        }
        documents.append(Document(page_content=text_content, metadata=metadata))

    return documents

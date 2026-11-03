from backend.app.search.embeddings.base import EmbeddingModel
from backend.app.search.semantic_search import QdrantVectorService


class FakeEmbeddingModel(EmbeddingModel):
    """Small deterministic embedding model for tests."""

    def __init__(self, dimension: int = 4) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts):
        return [[float(index + 1)] * self._dimension for index, _ in enumerate(texts)]

    def embed_query(self, text: str) -> list[float]:
        return [1.0] * self._dimension


def make_service(collection_name: str = "test-collection") -> QdrantVectorService:
    return QdrantVectorService(
        url=":memory:",
        collection_name=collection_name,
        embedding_model=FakeEmbeddingModel(),
        search_limit=3,
    )


def test_ensure_collection_creates_when_missing() -> None:
    service = make_service()

    assert not service.client.collection_exists(service.collection_name)

    service.ensure_collection()

    assert service.client.collection_exists(service.collection_name)


def test_ensure_collection_reuses_existing_collection() -> None:
    service = make_service()

    service.ensure_collection()
    service.ensure_collection()

    collection = service.client.get_collection(service.collection_name)
    assert collection.config.params.vectors.size == 4


def test_ensure_collection_raises_on_dimension_mismatch() -> None:
    service = make_service()
    service.ensure_collection()

    service.embedding_model._dimension = 8

    try:
        service.ensure_collection()
    except ValueError as error:
        assert "vector size" in str(error)
    else:
        raise AssertionError("Expected ValueError for dimension mismatch")


def test_upsert_chunks_returns_empty_result_for_empty_input() -> None:
    service = make_service()

    result = service.upsert_chunks([])

    assert result == {
        "collection_name": "test-collection",
        "upserted": 0,
        "point_ids": [],
    }


def test_upsert_chunks_stores_payload_and_metadata() -> None:
    service = make_service()
    chunks = [
        {
            "file_name": "data.csv",
            "file_type": ".csv",
            "text_content": "invoice_no: INV-001, total: 100.00",
        },
        {
            "file_name": "data.csv",
            "file_type": ".csv",
            "text_content": "invoice_no: INV-002, total: 200.00",
        },
    ]

    result = service.upsert_chunks(chunks, batch_size=1, metadata={"source": "test"})

    assert result["upserted"] == 2
    assert len(result["point_ids"]) == 2

    points = service.client.retrieve(
        collection_name=service.collection_name,
        ids=result["point_ids"],
        with_payload=True,
    )

    assert len(points) == 2
    assert all(point.payload["source"] == "test" for point in points)
    assert {
        point.payload["text_content"] for point in points
    } == {
        "invoice_no: INV-001, total: 100.00",
        "invoice_no: INV-002, total: 200.00",
    }


def test_search_returns_score_and_payload() -> None:
    service = make_service()
    chunks = [
        {
            "file_name": "data.csv",
            "file_type": ".csv",
            "text_content": "invoice total amount",
        }
    ]

    service.upsert_chunks(chunks)

    results = service.search("invoice", limit=1)

    assert len(results) == 1
    assert "score" in results[0]
    assert "payload" in results[0]
    assert results[0]["payload"]["text_content"] == "invoice total amount"


def test_search_filters_by_payload_field() -> None:
    service = make_service()
    chunks = [
        {
            "file_name": "data.csv",
            "file_type": ".csv",
            "text_content": "csv invoice",
        },
        {
            "file_name": "image.png",
            "file_type": ".png",
            "text_content": "image invoice",
        },
    ]

    service.upsert_chunks(chunks)

    results = service.search("invoice", filters={"file_type": ".png"})

    assert len(results) == 1
    assert results[0]["payload"]["file_type"] == ".png"

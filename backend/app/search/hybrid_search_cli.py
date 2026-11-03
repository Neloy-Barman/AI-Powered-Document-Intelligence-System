import json
import sys
from pathlib import Path

from backend.app.core.config import QDRANT_URL
from backend.processing.file_detector import detect_file_type
from backend.processing.router import route_file
from backend.app.search.langchain_hybrid_search import create_langchain_hybrid_search
from backend.app.search.semantic_search import create_qdrant_service
from backend.processing.chunking.csv_chunker import chunk_csv
from backend.processing.chunking.image_chunker import chunk_image
from backend.processing.chunking.spreadsheet_chunker import chunk_spreadsheet


def ingest_file(file_path: Path) -> list[dict]:
    parsed = route_file(file_path)
    if parsed.get("status") == "failed":
        raise RuntimeError(parsed.get("error_message", "Failed to parse file"))

    file_type = detect_file_type(file_path)
    if file_type == "csv":
        chunks = chunk_csv(parsed)
    elif file_type == "spreadsheet":
        chunks = chunk_spreadsheet(parsed)
    elif file_type == "image":
        chunks = chunk_image(parsed)
    else:
        raise RuntimeError(f"Unsupported file type: {file_type}")

    service = create_qdrant_service()
    upsert_result = service.upsert_chunks(chunks)

    hybrid = create_langchain_hybrid_search(service=service)
    hybrid.add_documents(chunks)

    print(f"Ingested {upsert_result['upserted']} chunks from {file_path.name}")
    return chunks


def main() -> None:
    if len(sys.argv) == 3:
        file_path = Path(sys.argv[1])
        query = sys.argv[2]

        ingest_file(file_path)

        hybrid = create_langchain_hybrid_search()
        results = hybrid.search(query)
        print("\nHybrid search results:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    if len(sys.argv) == 2:
        query = sys.argv[1]
        hybrid = create_langchain_hybrid_search()
        results = hybrid.search(query)
        print("Hybrid search results:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print("Usage:")
    print('  python -m backend.app.search.hybrid_search_cli "search query"')
    print('  python -m backend.app.search.hybrid_search_cli "path/to/file.xlsx" "search query"')


if __name__ == "__main__":
    main()

import json
from pathlib import Path

from adapters.vector_store import VectorStore
from core.config import Settings
from ingestion.identity import generate_chunk_ids, generate_document_id
from ingestion.loaders.markdown_loader import MarkdownLoader

EVALS_DIR = Path(__file__).parent
CORPUS_DIR = EVALS_DIR / "corpus"
GOLDEN_FILE = EVALS_DIR / "golden_qa.jsonl"


def load_corpus(vector_store: VectorStore, markdonw_loader: MarkdownLoader) -> None:
    for path in sorted(CORPUS_DIR.glob("*.md")):
        content = path.read_bytes()
        document_id = generate_document_id(content)
        if vector_store.count_by_document(document_id=document_id):
            continue

        docs = markdonw_loader.load_documents(path.name, content, document_id)
        split_docs = markdonw_loader.split_documents(docs)
        chunk_ids = generate_chunk_ids(document_id, len(split_docs))
        vector_store.add_documents(split_docs, chunk_ids)
        print(f"Stored {len(chunk_ids)} chunks from file {path.name}")


def load_golden_set() -> list[dict]:
    with GOLDEN_FILE.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def is_hit(vector_store: VectorStore, row: dict, top_k: int) -> bool:
    results = vector_store.query(row["question"], top_k)
    found = [doc.metadata.get("source") for doc, score in results]
    return any(expected_source in found for expected_source in row["expected_sources"])


def hit_rate(vector_store: VectorStore, rows: list[dict], top_k: int):
    hit: int = 0
    checked: int = 0

    for row in rows:
        # Skip unanswerable questions, the ones that has [] expected_sources
        if not row["expected_sources"]:
            continue
        checked += 1
        if is_hit(vector_store, row, top_k):
            hit += 1

    return hit / checked


if __name__ == "__main__":
    setttings = Settings()
    setttings.qdrant_collection = setttings.qdrant_collection_eval
    store = VectorStore(setttings)
    loader = MarkdownLoader(setttings)
    try:
        load_corpus(vector_store=store, markdonw_loader=loader)
        rows = load_golden_set()
        for k in (1, 3, 5):
            print(f"Hit rate @ K:{k} is {hit_rate(store, rows, k)}")
    finally:
        store.close()

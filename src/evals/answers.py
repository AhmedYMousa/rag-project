
from datetime import datetime
import json
from pathlib import Path
from adapters.llm import Llm
from adapters.vector_store import VectorStore
from core.config import Settings
from evals.retrieval import load_corpus, load_golden_set
from ingestion.loaders.markdown_loader import MarkdownLoader
from rag.pipeline import RagPipeline

EVALS_DIR = Path(__file__).parent
RESULTS_DIR = EVALS_DIR / "results"
TOP_K = 4


def run_golden_set(pipeline: RagPipeline, rows: list[dict]) -> list[dict]:
    results = []
    for row in rows:
        response = pipeline.answer(row["question"], TOP_K)
        results.append(
            {
                "id": row["id"],
                "type": row["type"],
                "question": row["question"],
                "reply": response.answer,
                "sources": [s.source for s in response.sources],
                "expected_sources": row["expected_sources"],
                "reference_answer": row["reference_answer"]

            })
    return results


def save_results(results: list[dict], model: str) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    path = RESULTS_DIR / f"results-{model.replace(":", "-")}-{stamp}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
    return path


def is_refusal(reply: str) -> bool:
    stripped_text = reply.lower().replace("'", "").replace("’", "")
    return "i dont know" in stripped_text


def refusal_report(results: list[dict]):
    answered = [result for result in results if result["type"] != "unanswerable"]
    unanswered = [
        result for result in results if result["type"] == "unanswerable"]

    refused = [r for r in unanswered if is_refusal(r["reply"])]
    wrongly_refused = [r for r in answered if is_refusal(r["reply"])]

    print(f"Right reply {len(refused)}/{len(unanswered)}")
    print(f"Gave up early  {len(wrongly_refused)}/{len(answered)}")

    for s in wrongly_refused:
        print(f"{s["id"]}: {s["question"]}")


if __name__ == "__main__":
    settings = Settings()
    settings.qdrant_collection = settings.qdrant_collection_eval
    settings.ollama_temperature = 0
    settings.ollama_seed = 42
    store = VectorStore(settings)
    loader = MarkdownLoader(settings)
    try:
        load_corpus(vector_store=store, markdonw_loader=loader)
        rows = load_golden_set()
        pipelie = RagPipeline(store, Llm(settings))
        results = run_golden_set(pipelie, rows)
        save_results(results, settings.ollama_model)
        refusal_report(results)
    finally:
        store.close()

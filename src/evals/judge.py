import json
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from core.config import Settings
from evals.answers import RESULTS_DIR
from evals.retrieval import EVALS_DIR

RESULTS_FILE = RESULTS_DIR / "results-llama3.2-3b-2026-11-05-1312.jsonl"
LABELS_FILE = EVALS_DIR / "labels" / "labels-llama3.2-3b-2026-11-05-1312.jsonl"
JUDGE_MODEL = "gemma4:e4b"
JUDGE_PROMPT = (
    "You are grading answers from a question-answering app.\n"
    "You get a question, a reference answer that is correct, and the app's reply.\n"
    "The reply FAILS if any of these is true:\n"
    "- It states a fact that contradicts the reference answer.\n"
    "- It leaves out part of the reference answer (for example a missing step or a missing item).\n"
    "- It says it does not know, but the reference answer has an answer.\n"
    "- It is empty or makes no sense.\n"
    "Extra details that do not contradict the reference are fine.\n"
    "If the reference says the system should not know, the reply PASSES only if it says it does not know.\n"
    'Reply with JSON only: {"critique": "<one sentence>", "verdict": "pass" or "fail"}'
)


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_judge_message(result: dict):
    return (
        f"Question:\n{result['question']}\n\n"
        f"Reference Answer:\n{result['reference_answer']} \n\n"
        # limit the reply by 4000 chars using slice
        f"App Answer:\n{result['reply'][:4000]}"
    )


def judge_reply(judge: ChatOllama, result: dict):
    messages = [SystemMessage(JUDGE_PROMPT), HumanMessage(build_judge_message(result))]
    response = judge.invoke(messages)
    text_content = json.loads(response.content)
    return {
        "id": result["id"],
        "verdict": str(text_content["verdict"]).lower().strip(),
        "critique": str(text_content["critique"]),
    }


def agreement_report(verdicts: list[dict], labels: dict[str, str]):
    # Split veridcts into pass and fail lists
    failed = [v for v in verdicts if labels[v["id"]] == "fail"]
    passed = [v for v in verdicts if labels[v["id"]] == "pass"]
    # Create two list that agrees with your labeling
    caught = [v for v in failed if v["verdict"] == "fail"]
    kept = [v for v in passed if v["verdict"] == "pass"]
    print(f"caught {len(caught)}/{len(failed)}")
    print(f"kept {len(kept)}/{len(passed)}")

    for v in verdicts:
        if v["verdict"] != labels[v["id"]]:
            print(
                f"{v['id']} User label:{labels[v['id']]} Judge label: {v['verdict']} , Reason: {v['critique']}"
            )


def main() -> None:
    settings = Settings()
    judge = ChatOllama(
        base_url=settings.ollama_url,
        model=JUDGE_MODEL,
        temperature=0,
        seed=42,
        format="json",
        reasoning=False,
    )

    labels = {row["id"]: row["label"] for row in load_jsonl(LABELS_FILE)}
    verdicts = []
    for result in load_jsonl(RESULTS_FILE):
        verdicts.append(judge_reply(judge, result))
        print(f"Judged {result['id']}")

    agreement_report(verdicts, labels)


if __name__ == "__main__":
    main()

from adapters.llm import Llm
from adapters.vector_store import VectorStore
from api.schemas import QueryResponse, Source
from rag.prompt import build_prompt


class RagPipeline:
    def __init__(self, vector_store: VectorStore, llm: Llm):
        self.vector_store = vector_store
        self.llm = llm

    def retrieve(self, question: str, top_k: int) -> list[Source]:
        results = self.vector_store.query(query_text=question, k=top_k)
        return [
            Source(
                source=d.metadata.get("source"),
                page=d.metadata.get("page"),
                score=score,
                text=d.page_content,
            )
            for d, score in results
        ]

    def generate(self, question: str, sources: list[Source]) -> str:
        prompt = build_prompt(question, sources)
        return self.llm.generate(prompt)

    def answer(self, question: str, top_k: int) -> QueryResponse:
        sources = self.retrieve(question, top_k)
        llm_answer = self.generate(question=question, sources=sources)
        return QueryResponse(answer=llm_answer, sources=sources)

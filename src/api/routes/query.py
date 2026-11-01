from typing import Annotated

from fastapi import APIRouter, Depends

from adapters.llm import Llm
from adapters.vector_store import VectorStore
from api.dependencies import get_llm, get_vector_store
from api.schemas import QueryRequest, QueryResponse, Source
from rag.prompt import build_prompt

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(
    query_request: QueryRequest,
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
    llm: Annotated[Llm, Depends(get_llm)],
):
    result = vector_store.query(
        query_text=query_request.question, k=query_request.top_k
    )
    sources_list: list[Source] = [
        Source(
            source=d.metadata.get("source"),
            page=d.metadata.get("page"),
            score=score,
            text=d.page_content,
        )
        for d, score in result
    ]

    prompt = build_prompt(query_request.question, sources_list)
    answer = llm.generate(prompt)

    return QueryResponse(answer=answer, sources=sources_list)

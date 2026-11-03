from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_rag_pipeline
from api.schemas import QueryRequest, QueryResponse
from rag.pipeline import RagPipeline

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(
    query_request: QueryRequest,
    pipeline: Annotated[RagPipeline, Depends(get_rag_pipeline)],
):
    return pipeline.answer(query_request.question, query_request.top_k)

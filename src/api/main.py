import uvicorn
from fastapi import FastAPI, File, Request, UploadFile, Depends
from adapters.llm import Llm
from adapters.vector_store import VectorStore
from api.schemas import QueryRequest, QueryResponse, Source
from core.logger import request_id_var, setup_logging
import uuid
from core.config import Settings
from api.dependencies import get_document_loader, get_vector_store, get_llm
from ingestion.document_loader import DocumentLoader
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from rag.prompt import build_prompt

logger = logging.getLogger(__name__)
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.vector_store = VectorStore(settings)
    app.state.document_loader = DocumentLoader(settings)
    app.state.llm = Llm(settings)
    # Everything before `yield` runs once at startup
    yield
    # everything after it runs at shutdown
    app.state.vector_store.close()


def main() -> None:
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    return app


app = create_app()


# middleware sets request_id_var
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Endpoint
@app.get("/")
def home():
    return "Hello world"


@app.post("/ingest")
async def ingest(
    vector_store: VectorStore = Depends(get_vector_store),
    document_loader: DocumentLoader = Depends(get_document_loader),
    file: UploadFile = File(...),
):
    try:
        content = await file.read()
        docs = document_loader.load_documents(file_name=file.filename, content=content)
        split_docs = document_loader.split_documents(docs)
        docIds = vector_store.add_documents(split_docs)

    except Exception as exc:
        logger.exception("Ingestion failed for %s", file.filename)
        raise Exception(exc)
    finally:
        await file.close()

    logger.info("Ingested %s chunks from %s", len(docIds), file.filename)
    return {"chunks": len(docIds)}


@app.post("/query", response_model=QueryResponse)
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

import uvicorn
from fastapi import FastAPI, File, Request, UploadFile, Depends
from adapters.vector_store import VectorStore
from core.logger import request_id_var, setup_logging
import uuid
from core.config import Settings
from api.dependencies import get_document_loader, get_vector_store
from ingestion.document_loader import DocumentLoader
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.vector_store = VectorStore(settings)
    app.state.document_loader = DocumentLoader(settings)
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
async def ingest(vector_store: VectorStore = Depends(get_vector_store),
                 document_loader: DocumentLoader = Depends(
                     get_document_loader),
                 file: UploadFile = File(...)):
    try:
        content = await file.read()
        docs = document_loader.load_documents(
            file_name=file.filename, content=content)
        split_docs = document_loader.split_documents(docs)
        docIds = vector_store.add_documents(split_docs)

    except Exception as exc:
        logger.exception("Ingestion failed for %s", file.filename)
        raise Exception(exc)
    finally:
        await file.close()

    logger.info("Ingested %s chunks from %s", len(docIds), file.filename)
    return {"chunks": len(docIds)}

from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, File, Request, UploadFile
from adapters.vector_store import VectorStore
from core.logger import request_id_var, setup_logging
import uuid
from core.config import Settings
from ingestion.document_loader import DocumentLoader
import logging


logger = logging.getLogger(__name__)
settings = Settings()


def main() -> None:
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)


def create_app() -> FastAPI:

    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name)
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


@app.get("/")
def home():
    return "Hello world"


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    try:
        content = await file.read()
        documentLoader = DocumentLoader(settings)
        docs = documentLoader.load_documents(
            file_name=file.filename, content=content)
        split_docs = documentLoader.split_documents(docs)
        vector_store = VectorStore()
        docIds = vector_store.add_documents(split_docs)

    except Exception as exc:
        logger.exception("Ingestion failed for %s", file.filename)
        raise Exception(exc)
    finally:
        await file.close()

    logger.info("Ingested %s chunks from %s", len(docIds), file.filename)
    return {"chunks", len(docIds)}

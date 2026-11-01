from contextlib import asynccontextmanager

from fastapi import FastAPI

from adapters.llm import Llm
from adapters.vector_store import VectorStore
from core.config import Settings
from core.file_service import FileService
from ingestion.document_loader import DocumentLoader


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = Settings()
    app.state.vector_store = VectorStore(app.state.settings)
    app.state.document_loader = DocumentLoader(app.state.settings)
    app.state.llm = Llm(app.state.settings)
    app.state.file_service = FileService(app.state.settings)

    try:
        # Everything before `yield` runs once at startup
        yield
    # everything after it runs at shutdown
    # Guarantees cleanup even if something happen
    finally:
        app.state.vector_store.close()

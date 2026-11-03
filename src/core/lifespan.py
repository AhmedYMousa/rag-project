from contextlib import asynccontextmanager

from fastapi import FastAPI

from adapters.llm import Llm
from adapters.vector_store import VectorStore
from core.config import Settings
from core.file_service import FileService
from ingestion.loaders.markdown_loader import MarkdownLoader
from ingestion.loaders.pdf_loader import PdfLoader
from rag.pipeline import RagPipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = Settings()
    app.state.vector_store = VectorStore(app.state.settings)
    app.state.pdf_loader = PdfLoader(app.state.settings)
    app.state.markdown_loader = MarkdownLoader(app.state.settings)
    app.state.llm = Llm(app.state.settings)
    app.state.file_service = FileService(app.state.settings)
    app.state.rag_pipeline = RagPipeline(app.state.vector_store, app.state.llm)

    try:
        # Everything before `yield` runs once at startup
        yield
    # everything after it runs at shutdown
    # Guarantees cleanup even if something happen
    finally:
        app.state.vector_store.close()

from fastapi import Request

from adapters.llm import Llm
from adapters.vector_store import VectorStore
from core.config import Settings
from core.file_service import FileService
from ingestion.loaders.markdown_loader import MarkdownLoader
from ingestion.loaders.pdf_loader import PdfLoader
from rag.pipeline import RagPipeline


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_pdf_loader(request: Request) -> PdfLoader:
    return request.app.state.pdf_loader


def get_llm(request: Request) -> Llm:
    return request.app.state.llm


def get_file_service(request: Request) -> FileService:
    return request.app.state.file_service


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_markdown_loader(request: Request) -> MarkdownLoader:
    return request.app.state.markdown_loader


def get_rag_pipeline(request: Request) -> RagPipeline:
    return request.app.state.rag_pipeline

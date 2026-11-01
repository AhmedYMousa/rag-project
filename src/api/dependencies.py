from fastapi import Request

from adapters.llm import Llm
from adapters.vector_store import VectorStore
from core.config import Settings
from core.file_service import FileService
from ingestion.document_loader import DocumentLoader


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_document_loader(request: Request) -> DocumentLoader:
    return request.app.state.document_loader


def get_llm(request: Request) -> Llm:
    return request.app.state.llm


def get_file_service(request: Request) -> FileService:
    return request.app.state.file_service


def get_settings(request: Request) -> Settings:
    return request.app.state.settings

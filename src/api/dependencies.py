from fastapi import Request

from adapters.llm import Llm
from adapters.vector_store import VectorStore
from ingestion.document_loader import DocumentLoader


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_document_loader(request: Request) -> DocumentLoader:
    return request.app.state.document_loader


def get_llm(request: Request) -> Llm:
    return request.app.state.llm

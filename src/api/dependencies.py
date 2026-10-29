from fastapi import Request

from adapters.vector_store import VectorStore
from ingestion.document_loader import DocumentLoader


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_document_loader(request: Request) -> DocumentLoader:
    return request.app.state.document_loader

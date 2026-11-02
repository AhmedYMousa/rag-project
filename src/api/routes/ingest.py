import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from adapters.vector_store import VectorStore
from api.dependencies import (
    get_document_loader,
    get_file_service,
    get_settings,
    get_vector_store,
)
from api.schemas import IngestResponse
from core.config import Settings
from core.errors import FileTooLargeException
from core.file_service import FileService
from ingestion.document_loader import DocumentLoader
from ingestion.identity import generate_chunk_ids, generate_document_id

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
    document_loader: Annotated[DocumentLoader, Depends(get_document_loader)],
    file_service: Annotated[FileService, Depends(get_file_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    file: Annotated[UploadFile, File(...)],
):
    max_mb = settings.max_upload_mb
    try:
        file_service.validate(file=file, max_bytes=max_mb)
        content = await file.read()
        if len(content) > max_mb:
            raise FileTooLargeException(max_mb)
        document_id = generate_document_id(content)
        existing = vector_store.count_by_document(document_id)
        if existing:
            return IngestResponse(
                document_id=document_id, chunks=existing, status="existing"
            )

        docs = document_loader.load_documents(
            file_name=file.filename, content=content, document_id=document_id
        )
        split_docs = document_loader.split_documents(docs)
        ids = generate_chunk_ids(document_id, len(split_docs))
        document_ids = vector_store.add_documents(split_docs, ids)

    finally:
        await file.close()

    logger.info("Ingested %s chunks from %s", len(document_ids), file.filename)
    return IngestResponse(
        document_id=document_id, chunks=len(document_ids), status="ingested"
    )

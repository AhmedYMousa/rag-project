import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from adapters.vector_store import VectorStore
from api.dependencies import (
    get_file_service,
    get_markdown_loader,
    get_pdf_loader,
    get_settings,
    get_vector_store,
)
from api.schemas import IngestResponse
from core.config import Settings
from core.errors import FileTooLargeException, UnsupportedFileTypeException
from core.file_service import FileService
from ingestion.identity import generate_chunk_ids, generate_document_id
from ingestion.loaders.markdown_loader import MarkdownLoader
from ingestion.loaders.pdf_loader import PdfLoader

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
    pdf_loader: Annotated[PdfLoader, Depends(get_pdf_loader)],
    markdown_loader: Annotated[MarkdownLoader, Depends(get_markdown_loader)],
    file_service: Annotated[FileService, Depends(get_file_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    file: Annotated[UploadFile, File(...)],
):
    max_bytes = settings.max_upload_bytes
    try:
        file_service.validate(file=file, max_bytes=max_bytes)
        content = await file.read()
        if len(content) > max_bytes:
            raise FileTooLargeException(max_bytes)
        document_id = generate_document_id(content)
        existing = vector_store.count_by_document(document_id)
        if existing:
            return IngestResponse(
                document_id=document_id, chunks=existing, status="existing"
            )
        extension = file_service.get_file_extension(file.filename)
        loader = None

        match extension:
            case ".pdf":
                loader = pdf_loader
            case ".md":
                loader = markdown_loader
            case _:
                raise UnsupportedFileTypeException(extension)

        docs = loader.load_documents(
            file_name=file.filename, content=content, document_id=document_id
        )
        split_docs = loader.split_documents(docs)
        ids = generate_chunk_ids(document_id, len(split_docs))
        document_ids = vector_store.add_documents(split_docs, ids)

    finally:
        await file.close()

    logger.info("Ingested %s chunks from %s", len(document_ids), file.filename)
    return IngestResponse(
        document_id=document_id, chunks=len(document_ids), status="ingested"
    )

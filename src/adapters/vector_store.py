from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    VectorParams,
)

from core.config import Settings
from core.errors import VectorStoreUnavailableException
from ingestion.embeddings import SentenceTransformerEmbeddings

_QDRANT_ERRORS = (ConnectionError, ResponseHandlingException)


class VectorStore:
    def __init__(self, settings: Settings):
        self.client = QdrantClient(settings.qdrant_url)
        self.collection_name = settings.qdrant_collection
        self.embeddings = SentenceTransformerEmbeddings()
        self._ensure_collection()
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
            distance=Distance.COSINE,
        )

    def _ensure_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                self.collection_name,
                vectors_config=VectorParams(
                    size=self.embeddings.dimension, distance=Distance.COSINE
                ),
            )

    def add_documents(self, documents: list[Document], ids: list[str]) -> list[str]:
        # uuids = [str(uuid.uuid4()) for _ in documents]
        try:
            doc_ids = self.vector_store.add_documents(documents, ids=ids)
            return doc_ids
        except _QDRANT_ERRORS as exc:
            raise VectorStoreUnavailableException() from exc

    def query(self, query_text: str, k: int) -> list[tuple[Document, float]]:
        try:
            return self.vector_store.similarity_search_with_score(query_text, k=k)
        except _QDRANT_ERRORS as exc:
            raise VectorStoreUnavailableException() from exc

    def close(self) -> None:
        self.client.close()

    def count_by_document(self, document_id: str) -> int:
        try:
            result = self.client.count(
                self.collection_name,
                count_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.document_id",
                            match=MatchValue(value=document_id),
                        )
                    ]
                ),
                exact=True,
            )
            return result.count
        except _QDRANT_ERRORS as exc:
            raise VectorStoreUnavailableException() from exc

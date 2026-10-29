import uuid
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import QdrantVectorStore
from core.config import Settings
from ingestion.embeddings import SentenceTransformerEmbeddings


class VectorStore:
    def __init__(self):
        settings = Settings()
        self.client = QdrantClient(settings.qdrant_url)
        self.collection_name = settings.qdrant_collection
        self.embeddings = SentenceTransformerEmbeddings()
        self._ensure_collection()
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
            distance=Distance.COSINE)

    def _ensure_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(self.collection_name,
                                          vectors_config=VectorParams(size=self.embeddings.dimension, distance=Distance.COSINE))

    def add_documents(self, documents: list[Document]) -> list[str]:
        uuids = [str(uuid.uuid4()) for _ in documents]
        docIds = self.vector_store.add_documents(documents, ids=uuids)
        return docIds

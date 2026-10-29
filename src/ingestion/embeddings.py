from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_embedding_dimension()

    def embed_documents(self, texts: list[str]):
        ebmeddings = self.model.encode(texts)
        return ebmeddings.tolist()

    def embed_query(self, text):
        ebmeddings = self.model.encode(text)
        return ebmeddings.tolist()

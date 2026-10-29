import tempfile
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import Settings


class DocumentLoader:

    def __init__(self, settings: Settings):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_documents(self, file_name: str, content: bytes):
        """Process PDF Document into a langchain document"""

        documents: list[Document] = []
        # Create temp_file so the Loader could process it
        # temp_file is defined as an ephemeral object when using "with"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "upload.pdf")
            with open(temp_path, "wb") as temp_file:
                temp_file.write(content)

            loader = PyMuPDFLoader(temp_path)
            docList = loader.load()
            documents.extend(docList)

        return documents

    def split_documents(self, documents: list[Document]):
        """Split document into smaller chunks to be stored as embeddings"""
        split_docs = self.text_splitter.split_documents(documents)

        return split_docs

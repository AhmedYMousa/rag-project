from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from core.config import Settings


class MarkdownLoader:
    extensions = ".md"

    def __init__(self, settings: Settings):
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
            strip_headers=False,
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
        )

    def load_documents(self, file_name: str, content: bytes, document_id: str):
        """Process Markdown Document into a langchain document"""
        text = content.decode("utf-8")
        return [
            Document(
                page_content=text,
                metadata={"source": file_name, "document_id": document_id},
            )
        ]

    def split_documents(self, documents: list[Document]):
        """Split document into smaller chunks to be stored as embeddings"""
        sections: list[Document] = []

        for doc in documents:
            for section in self.header_splitter.split_text(doc.page_content):
                section.metadata = {**doc.metadata, **section.metadata}
                sections.append(section)

        split_docs = self.text_splitter.split_documents(sections)

        return split_docs

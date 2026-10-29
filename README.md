# RAG API

A local-first Retrieval-Augmented Generation (RAG) API built with FastAPI and Qdrant.

The goal of this project is to show what a production-ready RAG service looks like beyond a notebook demo: clear module boundaries, typed configuration, structured logging with request tracing, and dependency injection. The pipeline is a thin layer of my own code rather than a heavy framework, so the architecture stays visible.

> **Status:** work in progress. PDF ingestion into Qdrant works; retrieval and answer generation are next (see Roadmap).

## Features

- **PDF ingestion:** upload a PDF; it is parsed with PyMuPDF, split into overlapping chunks, embedded, and stored in Qdrant.
- **Local embeddings:** `sentence-transformers/all-MiniLM-L6-v2` runs in-process, with no external API keys. The Qdrant collection is created automatically with a vector size that matches the model.
- **Typed configuration:** `pydantic-settings` reads `RAG_*` environment variables or a `.env` file.
- **Structured logging:** every log line is a single JSON object stamped with the current request ID.
- **Request tracing:** middleware gives each request a UUID and returns it in the `X-Request-ID` response header.
- **Dependency injection:** the vector store and document loader are created once in the app lifespan, injected into routes with `Depends`, and closed cleanly at shutdown.

## Architecture

```
src/
├── api/
│   ├── main.py            # App factory, lifespan, middleware, routes
│   └── dependencies.py    # FastAPI dependency providers
├── core/
│   ├── config.py          # Settings (pydantic-settings)
│   └── logger.py          # JSON logging + request ID context
├── ingestion/
│   ├── document_loader.py # PDF loading and chunking
│   └── embeddings.py      # SentenceTransformer embeddings adapter
└── adapters/
    └── vector_store.py    # Qdrant vector store wrapper
```

Ingestion flow:

```
POST /ingest (PDF) → DocumentLoader.load_documents → DocumentLoader.split_documents
                   → VectorStore.add_documents (embed + upsert) → Qdrant
```

## Tech stack

| Concern         | Choice                                        |
| --------------- | --------------------------------------------- |
| Language        | Python 3.14, managed with uv |
| API             | FastAPI + Uvicorn, Pydantic v2                |
| Vector store    | Qdrant (Docker)                               |
| Embeddings      | sentence-transformers (`all-MiniLM-L6-v2`)    |
| PDF parsing     | PyMuPDF via LangChain community loaders       |
| Chunking        | LangChain `RecursiveCharacterTextSplitter`    |

## Getting started

### Prerequisites

- Python 3.14
- uv
- Docker

### 1. Start Qdrant

```bash
docker compose up -d
```

Qdrant listens on `http://localhost:6333` (dashboard at `http://localhost:6333/dashboard`).

### 2. Configure

Create a `.env` file in the project root:

```env
RAG_QDRANT_URL=http://localhost:6333
RAG_QDRANT_COLLECTION=documents
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
```

| Variable                | Required | Default   | Description                         |
| ----------------------- | -------- | --------- | ----------------------------------- |
| `RAG_QDRANT_URL`        | yes      | none      | Qdrant server URL                   |
| `RAG_QDRANT_COLLECTION` | yes      | none      | Collection to store chunks in       |
| `RAG_CHUNK_SIZE`        | no       | `1000`    | Max characters per chunk            |
| `RAG_CHUNK_OVERLAP`     | no       | `200`     | Characters shared between chunks    |
| `RAG_LOG_LEVEL`         | no       | `INFO`    | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `RAG_APP_NAME`          | no       | `rag-api` | Title shown in the OpenAPI docs     |

### 3. Install and run

```bash
uv sync
uv run serve
```

Run these from the project root so the `.env` file is found. The API starts at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`. The first start downloads the embedding model, so it takes a little longer.

## Usage

Ingest a PDF:

```bash
curl -X POST http://127.0.0.1:8000/ingest -F "file=@path/to/document.pdf"
```

Response:

```json
{ "chunks": 42 }
```

Example log line:

```json
{"timestamp": "2026-10-29T10:15:02.123456+00:00", "level": "INFO", "logger": "api.main", "message": "Ingested 42 chunks from document.pdf", "request_id": "3f1c..."}
```

## Roadmap

- [x] Typed settings and JSON logging with request IDs
- [x] PDF ingestion into Qdrant
- [x] Dependency injection through the app lifespan
- [ ] `/query` endpoint: retrieve relevant chunks and generate a grounded answer with an LLM (Ollama), with source citations and streaming
- [ ] Ingestion hardening: file type and size validation, deduplication by content hash, source and page metadata
- [ ] Consistent error responses and health/readiness endpoints
- [ ] Tests (unit + integration against Qdrant), Ruff, mypy, pre-commit
- [ ] GitHub Actions CI
- [ ] Dockerfile for the API, running alongside Qdrant in Docker Compose
- [ ] Retrieval evaluation (question/answer set with retrieval and answer quality metrics)
- [ ] Hybrid search (dense + BM25) and reranking

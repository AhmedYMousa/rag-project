# Production-style, local-first RAG API.

## Tech stack

- Python 3.11+, managed with uv and pyproject.toml
- FastAPI + Uvicorn, with Pydantic v2 and pydantic-settings for config
- Ollama for the LLM (e.g. llama3.1) and embeddings (nomic-embed-text)
- Qdrant for the vector store (Docker, runs locally). Chroma is simpler but less “production”.
- Light orchestration: your own thin pipeline, optionally LlamaIndex or LangChain loaders. I’d avoid heavy frameworks so the architecture is visible.
- Ruff, mypy, pytest, pre-commit, GitHub Actions, Docker Compose

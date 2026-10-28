import uvicorn
from fastapi import FastAPI


def main() -> None:
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)


def create_app() -> FastAPI:
    app = FastAPI(title="RAG Production-ready")
    return app


app = create_app()


@app.get("/")
def home():
    return "Hello world"
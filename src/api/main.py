import uvicorn
from fastapi import FastAPI, Request
from core.logger import request_id_var, setup_logging
import uuid
from core.config import Settings


def main() -> None:
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)


def create_app() -> FastAPI:
    settings = Settings()
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name)
    return app


app = create_app()


# middleware sets request_id_var
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/")
def home():
    return "Hello world"

import uvicorn
from fastapi import FastAPI

from api.error_handlers import register_error_handlers
from api.routes import ingest, query
from core.config import Settings
from core.lifespan import lifespan
from core.logger import setup_logging
from middlewares.request_id import add_request_id

settings = Settings()


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    # middleware sets request_id_var
    # decorator can't be followed by a function call,
    app.middleware("http")(add_request_id)
    app.include_router(query.router)
    app.include_router(ingest.router)
    register_error_handlers(app)
    return app


app = create_app()


def main() -> None:
    uvicorn.run("main:app", host="127.0.0.1", port=8000)

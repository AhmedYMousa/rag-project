from contextvars import ContextVar
import json
import logging
from datetime import datetime, UTC
import sys

# per-request IDs, a variable whose value is specific to the current request, even when many requests are handled concurrently.
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Attach the current request ID to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    """Render each log record as a single JSON line."""

    def format(self, record: logging.LogRecord):
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-")
        }
        return json.dumps(payload)
    

# 1. Create a handler that prints to the terminal (stdout).
# 2. Tell it to format every record with our JsonFormatter.
# 3. Tell it to run our filter first, which stamps the request ID on each record.
# 4. Get the root logger, the top-level logger that all other loggers pass their messages up to.
# 5. Remove any handlers already attached, so we never print each line twice.
# 6. Attach our handler to the root logger.
# 7. Set the minimum level. With "INFO", DEBUG messages are dropped.

def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)   # 1
    handler.setFormatter(JsonFormatter())         # 2
    handler.addFilter(RequestIdFilter())          # 3

    root = logging.getLogger()                    # 4
    root.handlers.clear()                         # 5
    root.addHandler(handler)                      # 6
    root.setLevel(level)                          # 7

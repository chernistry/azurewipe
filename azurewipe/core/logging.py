"""Structured logging with JSON support and correlation IDs."""
import json
import logging
import uuid
import functools
import time
from datetime import datetime, timezone
from typing import Optional

_RUN_ID: Optional[str] = None


def get_run_id() -> str:
    global _RUN_ID
    if _RUN_ID is None:
        _RUN_ID = str(uuid.uuid4())[:8]
    return _RUN_ID


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "run_id": get_run_id(),
            "message": record.getMessage(),
        }
        for key in ("subscription", "resource_group", "resource_type", "resource_id", "action"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging(verbosity: int = 0, json_format: bool = False) -> None:
    level = {0: logging.WARNING, 1: logging.INFO}.get(verbosity, logging.DEBUG)
    handler = logging.StreamHandler()
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(run_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.run_id = get_run_id()
        return record
    logging.setLogRecordFactory(record_factory)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

"""Retry utilities with exponential backoff."""
import time
import random
import logging
from functools import wraps
from typing import Callable, TypeVar, Any
from azure.core.exceptions import HttpResponseError, ServiceRequestError

T = TypeVar("T")


def retry_with_backoff(
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_codes: tuple = (429, 503, 504),
):
    """Decorator for retrying Azure operations with exponential backoff."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except HttpResponseError as e:
                    if e.status_code not in retryable_codes:
                        raise
                    if attempt == max_attempts - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                    logging.warning(f"{func.__name__} got {e.status_code}, retrying in {delay:.1f}s")
                    time.sleep(delay)
                except ServiceRequestError as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logging.warning(f"{func.__name__} connection error, retrying in {delay:.1f}s")
                    time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator

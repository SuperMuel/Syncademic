from typing import Any


class SyncademicError(Exception):
    """Base exception for all Syncademic errors"""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        original_exception: Exception | None = None,
    ):
        self.message = message
        self.details = details or {}
        self.original_exception = original_exception
        super().__init__(self.message)

import logging
from typing import cast
import sys

from firebase_functions import logger as firebase_logger

_BASE_LOG_RECORD_ATTRS = set(logging.makeLogRecord({}).__dict__)
_RESERVED_LOG_RECORD_ATTRS = _BASE_LOG_RECORD_ATTRS | {"message", "asctime"}


_LEVEL_TO_SEVERITY = {
    logging.CRITICAL: firebase_logger.LogSeverity.CRITICAL,
    logging.ERROR: firebase_logger.LogSeverity.ERROR,
    logging.WARNING: firebase_logger.LogSeverity.WARNING,
    logging.INFO: firebase_logger.LogSeverity.INFO,
    logging.DEBUG: firebase_logger.LogSeverity.DEBUG,
}


class FirebaseFunctionsHandler(logging.Handler):
    """
    Logging handler that forwards stdlib logging records to the Firebase
    Cloud Functions structured logger, preserving extra context stored on
    the LogRecord.
    """

    def emit(self, record: logging.LogRecord) -> None:
        severity = _LEVEL_TO_SEVERITY.get(
            record.levelno, firebase_logger.LogSeverity.INFO
        )
        message = self.format(record)

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _RESERVED_LOG_RECORD_ATTRS and not key.startswith("_")
        }

        entry: dict[str, object] = {"severity": severity}
        if message:
            entry["message"] = message
        if extras:
            entry.update(extras)

        firebase_logger.write(cast(firebase_logger.LogEntry, entry))


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the FastAPI application.

    Args:
        log_level: The logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get the root logger
    root_logger = logging.getLogger()

    # Clear any existing handlers
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Set the log level
    level = getattr(logging, log_level.upper())
    root_logger.setLevel(level)

    # Create a handler that writes to stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    root_logger.addHandler(handler)

    # Set Uvicorn access logs to the specified level
    logging.getLogger("uvicorn").setLevel(level)

    # Set FastAPI logs to the specified level
    logging.getLogger("fastapi").setLevel(level)


def configure_firebase_functions_logging(log_level: str = "INFO") -> None:
    """
    Configure logging so stdlib log calls are routed through the Firebase logger.

    Args:
        log_level: The logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    root_logger = logging.getLogger()

    # Clear existing handlers to avoid duplicate logging
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    level = getattr(logging, log_level.upper())
    root_logger.setLevel(level)

    handler = FirebaseFunctionsHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)

__all__ = [
    "configure_logging",
    "configure_firebase_functions_logging",
    "FirebaseFunctionsHandler",
]

import logging
import sys


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
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(level)

    # Set FastAPI logs to the specified level
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(level)

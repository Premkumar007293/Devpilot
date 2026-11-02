"""Centralized logging configuration for DevPilot."""

import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure and return the root logger for DevPilot."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("devpilot")
    logger.setLevel(log_level)

    # Avoid duplicate handlers if reconfigured
    if not logger.handlers:
        logger.addHandler(handler)

    # Also adjust uvicorn loggers
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.error").handlers = [handler]

    return logger


logger = setup_logging()

"""Logger configuration using Python standard logging."""

import logging
import sys
from pathlib import Path


def setup_logger(
    log_dir: Path | None = None,
    log_file: str = "lakehouse.log",
    level: str = "INFO",
) -> logging.Logger:
    """Configure Python logger with file and console handlers.

    Args:
        log_dir: Directory for log files. If None, uses ./logs
        log_file: Name of the log file
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("lakehouse")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler
    log_path = log_dir or Path("logs")
    log_path.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path / log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    logger.info(f"Logger initialized. Log file: {log_path / log_file}")

    return logger


# Create default logger instance
logger = setup_logger()

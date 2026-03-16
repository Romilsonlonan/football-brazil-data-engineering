"""Logger configuration using loguru."""

from pathlib import Path
from loguru import logger
import sys


def setup_logger(
    log_dir: Path | None = None,
    log_file: str = "lakehouse.log",
    rotation: str = "10 MB",
    retention: str = "7 days",
    level: str = "INFO",
) -> None:
    """Configure loguru logger with file and console handlers.
    
    Args:
        log_dir: Directory for log files. If None, uses ./logs
        log_file: Name of the log file
        rotation: When to rotate the log file
        retention: How long to keep logs
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Remove default handler
    logger.remove()
    
    # Console handler with colors
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True,
    )
    
    # File handler
    log_path = log_dir or Path("logs")
    log_path.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_path / log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=rotation,
        retention=retention,
        level=level,
        encoding="utf-8",
    )
    
    logger.info(f"Logger initialized. Log file: {log_path / log_file}")


# Default configuration
setup_logger()

"""Standardized Python Logging Utility.

Provides consistent logging setup across all backend modules.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import config


def setup_logger(name: str = "ResumeScreening", log_file: Optional[Path] = None) -> logging.Logger:
    """Configures and returns a standardized Python Logger.

    Args:
        name (str): Name of the logger, typically __name__ or module name.
        log_file (Optional[Path]): Optional file path to store logs on disk.

    Returns:
        logging.Logger: Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(config.LOG_LEVEL)

        formatter = logging.Formatter(
            fmt=config.LOG_FORMAT,
            datefmt=config.LOG_DATE_FORMAT,
        )

        # Stream Handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Optional File Handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

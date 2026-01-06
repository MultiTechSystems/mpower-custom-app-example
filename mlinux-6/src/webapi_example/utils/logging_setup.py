"""Logging setup utilities for mLinux syslog integration."""

from __future__ import annotations

import logging
from logging.handlers import SysLogHandler
from typing import Optional

from webapi_example.models.config import LogConfig


def setup_logging(
    config: Optional[LogConfig] = None, app_name: str = "webapi-example"
) -> logging.Logger:
    """Configure logging for mLinux or development.

    Args:
        config: Logging configuration. Uses defaults if None.
        app_name: Application name for syslog ident.

    Returns:
        Configured root logger.
    """
    if config is None:
        config = LogConfig()

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create handler based on config
    handler: logging.Handler
    if config.use_syslog:
        try:
            # mLinux syslog
            handler = SysLogHandler(address="/dev/log")
            handler.ident = f"{app_name}: "
        except (FileNotFoundError, OSError):
            # Fallback for development/non-Linux
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    handler.setLevel(getattr(logging, config.level.upper(), logging.INFO))
    logger.addHandler(handler)

    return logger

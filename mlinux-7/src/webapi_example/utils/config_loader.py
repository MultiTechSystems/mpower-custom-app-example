"""Configuration loading utilities."""

import json
import logging
import os
from pathlib import Path

from webapi_example.models.config import AppConfig

logger = logging.getLogger(__name__)


def load_config(config_path: str | None = None) -> AppConfig:
    """Load application configuration from JSON file.

    Args:
        config_path: Path to configuration file. If None, searches in
            standard locations.

    Returns:
        AppConfig instance.

    Raises:
        FileNotFoundError: If config file not found.
        json.JSONDecodeError: If config file is invalid JSON.
    """
    if config_path is None:
        # Search standard locations
        app_dir = os.environ.get("APP_DIR", ".")
        search_paths = [
            Path(app_dir) / "config" / "config.json",
            Path(app_dir) / "config.json",
            Path("config") / "config.json",
            Path("config.json"),
        ]
        for path in search_paths:
            if path.exists():
                config_path = str(path)
                break
        else:
            logger.warning("No config file found, using defaults")
            return AppConfig()

    logger.info("Loading configuration from %s", config_path)
    with open(config_path, "r") as f:
        data = json.load(f)

    return AppConfig.from_dict(data)

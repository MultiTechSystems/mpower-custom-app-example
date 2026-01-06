"""Pytest configuration and fixtures."""

import os
import sys
import tempfile
from typing import TYPE_CHECKING, Generator

import pytest

# Add mlinux-7 source to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mlinux-7", "src"))

from webapi_example.app import create_app, init_db
from webapi_example.models.config import AppConfig, DatabaseConfig, LogConfig, ServerConfig

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient


@pytest.fixture
def app_config() -> AppConfig:
    """Create test application configuration."""
    return AppConfig(
        server=ServerConfig(host="127.0.0.1", port=5000, debug=True),
        database=DatabaseConfig(path="test.db"),
        log=LogConfig(level="DEBUG", use_syslog=False),
    )


@pytest.fixture
def app(app_config: AppConfig) -> Generator["Flask", None, None]:
    """Create test Flask application."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["APP_DIR"] = tmpdir
        app_config.database.path = os.path.join(tmpdir, "test.db")
        
        app = create_app(app_config)
        app.config["TESTING"] = True
        init_db(app)
        
        yield app
        
        # Cleanup
        if "APP_DIR" in os.environ:
            del os.environ["APP_DIR"]


@pytest.fixture
def client(app: "Flask") -> "FlaskClient":
    """Create test client."""
    return app.test_client()

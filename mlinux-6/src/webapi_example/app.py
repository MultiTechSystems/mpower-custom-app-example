"""Flask application factory and setup."""

from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

from flask import Flask, g

from webapi_example.models.config import AppConfig

logger = logging.getLogger(__name__)


def create_app(config: Optional[AppConfig] = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Application configuration. Uses defaults if None.

    Returns:
        Configured Flask application instance.
    """
    if config is None:
        config = AppConfig()

    app = Flask(__name__)

    # Configure database
    app_dir = os.environ.get("APP_DIR", ".")
    db_path = os.path.join(app_dir, config.database.path)
    app.config["DATABASE"] = db_path
    app.config["JSON_SORT_KEYS"] = False

    # Store config in app context
    app.config["APP_CONFIG"] = config

    # Register database functions
    app.teardown_appcontext(_close_db)

    # Register routes
    from webapi_example.routes import register_routes

    register_routes(app)

    logger.info("Application created with database at %s", db_path)
    return app


def get_db() -> sqlite3.Connection:
    """Get database connection for current request context.

    Returns:
        SQLite database connection.
    """
    from flask import current_app

    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def _close_db(exception: Optional[BaseException] = None) -> None:
    """Close database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


@contextmanager
def get_db_connection(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections outside request context.

    Args:
        db_path: Path to SQLite database file.

    Yields:
        SQLite database connection.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(app: Flask) -> None:
    """Initialize the database schema.

    Args:
        app: Flask application instance.
    """
    db_path = app.config["DATABASE"]

    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    with get_db_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lora_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT,
                deveui TEXT NOT NULL,
                appeui TEXT,
                data TEXT,
                size INTEGER,
                timestamp TEXT,
                sequence_number INTEGER
            )
        """)
        conn.commit()
        logger.info("Database initialized at %s", db_path)

"""Simple HTTP server using Python's built-in http.server module."""

import json
import logging
import os
import sqlite3
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any
from urllib.parse import parse_qs, urlparse

from webapi_example.models.config import AppConfig

logger = logging.getLogger(__name__)


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the REST API."""

    def __init__(self, *args: Any, config: AppConfig, db_path: str, **kwargs: Any) -> None:
        """Initialize the handler with configuration."""
        self.config = config
        self.db_path = db_path
        super().__init__(*args, **kwargs)

    def _get_db(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _send_json(self, data: Any, status: int = 200) -> None:
        """Send JSON response."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any] | None:
        """Read JSON from request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))

    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._send_json({"message": "Welcome to the Web API Example"})
        elif path == "/health":
            self._send_json({"status": "ok"})
        elif path == "/users":
            self._get_users()
        elif path.startswith("/users/"):
            username = path[7:]
            self._get_user(username)
        elif path == "/messages":
            self._get_messages()
        elif path.startswith("/messages/"):
            deveui = path[10:]
            self._get_messages_by_device(deveui)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        """Handle POST requests."""
        if self.path == "/users":
            self._create_user()
        elif self.path == "/messages":
            self._create_message()
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_DELETE(self) -> None:
        """Handle DELETE requests."""
        if self.path.startswith("/users/"):
            username = self.path[7:]
            self._delete_user(username)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _get_users(self) -> None:
        """Get all users."""
        conn = self._get_db()
        try:
            cursor = conn.execute("SELECT id, username FROM users")
            users = [{"id": row["id"], "username": row["username"]} for row in cursor]
            self._send_json({"users": users})
        finally:
            conn.close()

    def _get_user(self, username: str) -> None:
        """Get a specific user."""
        conn = self._get_db()
        try:
            cursor = conn.execute(
                "SELECT id, username FROM users WHERE username = ?", (username,)
            )
            row = cursor.fetchone()
            if row:
                self._send_json({"user": {"id": row["id"], "username": row["username"]}})
            else:
                self._send_json({"error": "User not found"}, 404)
        finally:
            conn.close()

    def _create_user(self) -> None:
        """Create a new user."""
        data = self._read_json()
        if not data:
            self._send_json({"error": "No data provided"}, 400)
            return

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            self._send_json({"error": "Username and password required"}, 400)
            return

        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = self._get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            conn.commit()
            logger.info("Created user: %s", username)
            self._send_json({"message": "User created", "username": username}, 201)
        except sqlite3.IntegrityError:
            self._send_json({"error": "User already exists"}, 400)
        finally:
            conn.close()

    def _delete_user(self, username: str) -> None:
        """Delete a user."""
        conn = self._get_db()
        try:
            cursor = conn.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            if cursor.rowcount > 0:
                logger.info("Deleted user: %s", username)
                self._send_json({"message": "User deleted"})
            else:
                self._send_json({"error": "User not found"}, 404)
        finally:
            conn.close()

    def _get_messages(self) -> None:
        """Get all messages."""
        conn = self._get_db()
        try:
            cursor = conn.execute("""
                SELECT id, device_name, deveui, appeui, data, size, timestamp, sequence_number
                FROM lora_messages ORDER BY id DESC
            """)
            messages = [
                {
                    "id": row["id"],
                    "deviceName": row["device_name"],
                    "deveui": row["deveui"],
                    "appeui": row["appeui"],
                    "data": row["data"],
                    "size": row["size"],
                    "timestamp": row["timestamp"],
                    "sqn": row["sequence_number"],
                }
                for row in cursor
            ]
            self._send_json({"messages": messages})
        finally:
            conn.close()

    def _get_messages_by_device(self, deveui: str) -> None:
        """Get messages for a specific device."""
        conn = self._get_db()
        try:
            cursor = conn.execute("""
                SELECT id, device_name, deveui, appeui, data, size, timestamp, sequence_number
                FROM lora_messages WHERE deveui = ? ORDER BY id DESC
            """, (deveui,))
            messages = [
                {
                    "id": row["id"],
                    "deviceName": row["device_name"],
                    "deveui": row["deveui"],
                    "appeui": row["appeui"],
                    "data": row["data"],
                    "size": row["size"],
                    "timestamp": row["timestamp"],
                    "sqn": row["sequence_number"],
                }
                for row in cursor
            ]
            if messages:
                self._send_json({"messages": messages})
            else:
                self._send_json({"error": "No messages found"}, 404)
        finally:
            conn.close()

    def _create_message(self) -> None:
        """Create a new message."""
        data = self._read_json()
        if not data:
            self._send_json({"error": "No data provided"}, 400)
            return

        deveui = data.get("deveui")
        if not deveui:
            self._send_json({"error": "deveui is required"}, 400)
            return

        from datetime import datetime
        timestamp = data.get("timestamp", datetime.utcnow().isoformat() + "Z")

        conn = self._get_db()
        try:
            conn.execute(
                """INSERT INTO lora_messages 
                   (device_name, deveui, appeui, data, size, timestamp, sequence_number)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    data.get("deviceName", ""),
                    deveui,
                    data.get("appeui", ""),
                    data.get("data", ""),
                    data.get("size", 0),
                    timestamp,
                    data.get("sqn", 0),
                ),
            )
            conn.commit()
            logger.info("Created message from device: %s", deveui)
            self._send_json({"message": "Message created"}, 201)
        finally:
            conn.close()

    def log_message(self, format: str, *args: Any) -> None:
        """Log HTTP requests."""
        logger.debug("%s - %s", self.address_string(), format % args)


def create_handler(config: AppConfig, db_path: str) -> type[APIHandler]:
    """Create a handler class with the given configuration."""

    class ConfiguredHandler(APIHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, config=config, db_path=db_path, **kwargs)

    return ConfiguredHandler


def init_db(db_path: str) -> None:
    """Initialize the database schema."""
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
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
    finally:
        conn.close()


def run_server(config: AppConfig, db_path: str) -> None:
    """Run the HTTP server with optional TLS support."""
    init_db(db_path)
    handler = create_handler(config, db_path)
    server = HTTPServer((config.server.host, config.server.port), handler)

    if config.server.tls.enabled:
        # Create SSL context for TLS
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            context.load_cert_chain(
                certfile=config.server.tls.cert_file,
                keyfile=config.server.tls.key_file,
            )
            server.socket = context.wrap_socket(server.socket, server_side=True)
            logger.info("TLS enabled with cert: %s", config.server.tls.cert_file)
        except FileNotFoundError as e:
            logger.error("TLS certificate not found: %s", e)
            raise
        except ssl.SSLError as e:
            logger.error("TLS configuration error: %s", e)
            raise

    protocol = "https" if config.server.tls.enabled else "http"
    logger.info("Server running on %s://%s:%d", protocol, config.server.host, config.server.port)
    server.serve_forever()

"""API route definitions."""

import hashlib
import logging
from typing import Any

from flask import Flask, jsonify, request

from webapi_example.app import get_db
from webapi_example.models.data import LoraMessage, User

logger = logging.getLogger(__name__)


def register_routes(app: Flask) -> None:
    """Register all API routes with the Flask application.

    Args:
        app: Flask application instance.
    """

    @app.route("/")
    def index() -> str:
        """Root endpoint."""
        return "Welcome to the Web API Example"

    @app.route("/health")
    def health() -> dict[str, Any]:
        """Health check endpoint."""
        return {"status": "ok"}

    # User endpoints
    @app.route("/users", methods=["GET"])
    def get_users() -> Any:
        """Get all users."""
        db = get_db()
        cursor = db.execute("SELECT id, username, password_hash FROM users")
        users = [
            User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
            ).to_dict()
            for row in cursor.fetchall()
        ]
        return jsonify({"users": users})

    @app.route("/users", methods=["POST"])
    def create_user() -> tuple[Any, int]:
        """Create a new user."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        # Simple password hashing (use proper hashing in production)
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            db.commit()
            logger.info("Created user: %s", username)
            return jsonify({"message": "User created", "username": username}), 201
        except Exception as e:
            logger.error("Failed to create user: %s", e)
            return jsonify({"error": "Failed to create user"}), 500

    @app.route("/users/<username>", methods=["GET"])
    def get_user(username: str) -> Any:
        """Get a specific user by username."""
        db = get_db()
        cursor = db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "User not found"}), 404

        user = User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
        )
        return jsonify({"user": user.to_dict()})

    @app.route("/users/<username>", methods=["DELETE"])
    def delete_user(username: str) -> Any:
        """Delete a user by username."""
        db = get_db()
        cursor = db.execute("DELETE FROM users WHERE username = ?", (username,))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        logger.info("Deleted user: %s", username)
        return jsonify({"message": "User deleted"})

    # LoRa Message endpoints
    @app.route("/messages", methods=["GET"])
    def get_messages() -> Any:
        """Get all LoRa messages."""
        db = get_db()
        cursor = db.execute("""
            SELECT id, device_name, deveui, appeui, data, size, timestamp, sequence_number
            FROM lora_messages
            ORDER BY id DESC
        """)
        messages = [
            LoraMessage(
                id=row["id"],
                device_name=row["device_name"],
                deveui=row["deveui"],
                appeui=row["appeui"],
                data=row["data"],
                size=row["size"],
                timestamp=row["timestamp"],
                sequence_number=row["sequence_number"],
            ).to_dict()
            for row in cursor.fetchall()
        ]
        return jsonify({"messages": messages})

    @app.route("/messages", methods=["POST"])
    def create_message() -> tuple[Any, int]:
        """Create a new LoRa message."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        message = LoraMessage.from_dict(data)

        if not message.deveui:
            return jsonify({"error": "deveui is required"}), 400

        db = get_db()
        try:
            db.execute(
                """INSERT INTO lora_messages 
                   (device_name, deveui, appeui, data, size, timestamp, sequence_number)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    message.device_name,
                    message.deveui,
                    message.appeui,
                    message.data,
                    message.size,
                    message.timestamp,
                    message.sequence_number,
                ),
            )
            db.commit()
            logger.info("Created message from device: %s", message.deveui)
            return jsonify({"message": "Message created", "data": message.to_dict()}), 201
        except Exception as e:
            logger.error("Failed to create message: %s", e)
            return jsonify({"error": "Failed to create message"}), 500

    @app.route("/messages/<deveui>", methods=["GET"])
    def get_messages_by_device(deveui: str) -> Any:
        """Get all messages for a specific device."""
        db = get_db()
        cursor = db.execute(
            """SELECT id, device_name, deveui, appeui, data, size, timestamp, sequence_number
               FROM lora_messages WHERE deveui = ?
               ORDER BY id DESC""",
            (deveui,),
        )
        messages = [
            LoraMessage(
                id=row["id"],
                device_name=row["device_name"],
                deveui=row["deveui"],
                appeui=row["appeui"],
                data=row["data"],
                size=row["size"],
                timestamp=row["timestamp"],
                sequence_number=row["sequence_number"],
            ).to_dict()
            for row in cursor.fetchall()
        ]

        if not messages:
            return jsonify({"error": "No messages found for device"}), 404

        return jsonify({"messages": messages})

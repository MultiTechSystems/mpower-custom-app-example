"""Tests for API routes."""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from flask.testing import FlaskClient


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_ok(self, client: "FlaskClient") -> None:
        """Test that health endpoint returns ok status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json == {"status": "ok"}


class TestIndexEndpoint:
    """Tests for the root endpoint."""

    def test_index_returns_welcome(self, client: "FlaskClient") -> None:
        """Test that index endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Welcome" in response.data


class TestUserEndpoints:
    """Tests for user management endpoints."""

    def test_get_users_empty(self, client: "FlaskClient") -> None:
        """Test getting users when database is empty."""
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json == {"users": []}

    def test_create_user(self, client: "FlaskClient") -> None:
        """Test creating a new user."""
        response = client.post(
            "/users",
            json={"username": "testuser", "password": "testpass"},
        )
        assert response.status_code == 201
        assert response.json["message"] == "User created"
        assert response.json["username"] == "testuser"

    def test_create_user_missing_fields(self, client: "FlaskClient") -> None:
        """Test creating user with missing fields."""
        response = client.post("/users", json={"username": "testuser"})
        assert response.status_code == 400
        assert "error" in response.json

    def test_get_user(self, client: "FlaskClient") -> None:
        """Test getting a specific user."""
        # Create user first
        client.post(
            "/users",
            json={"username": "testuser", "password": "testpass"},
        )
        
        # Get the user
        response = client.get("/users/testuser")
        assert response.status_code == 200
        assert response.json["user"]["username"] == "testuser"

    def test_get_user_not_found(self, client: "FlaskClient") -> None:
        """Test getting a non-existent user."""
        response = client.get("/users/nonexistent")
        assert response.status_code == 404

    def test_delete_user(self, client: "FlaskClient") -> None:
        """Test deleting a user."""
        # Create user first
        client.post(
            "/users",
            json={"username": "testuser", "password": "testpass"},
        )
        
        # Delete the user
        response = client.delete("/users/testuser")
        assert response.status_code == 200
        assert response.json["message"] == "User deleted"
        
        # Verify user is gone
        response = client.get("/users/testuser")
        assert response.status_code == 404


class TestMessageEndpoints:
    """Tests for LoRa message endpoints."""

    def test_get_messages_empty(self, client: "FlaskClient") -> None:
        """Test getting messages when database is empty."""
        response = client.get("/messages")
        assert response.status_code == 200
        assert response.json == {"messages": []}

    def test_create_message(self, client: "FlaskClient") -> None:
        """Test creating a new message."""
        response = client.post(
            "/messages",
            json={
                "deviceName": "TestDevice",
                "deveui": "00-11-22-33-44-55-66-77",
                "appeui": "aa-bb-cc-dd-ee-ff-00-11",
                "data": "SGVsbG8=",
                "size": 5,
                "sqn": 1,
            },
        )
        assert response.status_code == 201
        assert response.json["message"] == "Message created"

    def test_create_message_missing_deveui(self, client: "FlaskClient") -> None:
        """Test creating message without deveui."""
        response = client.post(
            "/messages",
            json={"deviceName": "TestDevice"},
        )
        assert response.status_code == 400
        assert "error" in response.json

    def test_get_messages_by_device(self, client: "FlaskClient") -> None:
        """Test getting messages for a specific device."""
        # Create message first
        client.post(
            "/messages",
            json={
                "deviceName": "TestDevice",
                "deveui": "00-11-22-33-44-55-66-77",
                "data": "SGVsbG8=",
            },
        )
        
        # Get messages by device
        response = client.get("/messages/00-11-22-33-44-55-66-77")
        assert response.status_code == 200
        assert len(response.json["messages"]) == 1

    def test_get_messages_by_device_not_found(self, client: "FlaskClient") -> None:
        """Test getting messages for non-existent device."""
        response = client.get("/messages/non-existent-device")
        assert response.status_code == 404

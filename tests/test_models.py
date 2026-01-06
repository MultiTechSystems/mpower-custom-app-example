"""Tests for data models."""

from typing import TYPE_CHECKING

import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mlinux-7", "src"))

from webapi_example.models.config import AppConfig, DatabaseConfig, LogConfig, ServerConfig
from webapi_example.models.data import LoraMessage, User


class TestServerConfig:
    """Tests for ServerConfig model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = ServerConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 5000
        assert config.debug is False

    def test_from_dict(self) -> None:
        """Test creating from dictionary."""
        data = {"host": "127.0.0.1", "port": 8080, "debug": True}
        config = ServerConfig.from_dict(data)
        assert config.host == "127.0.0.1"
        assert config.port == 8080
        assert config.debug is True

    def test_from_dict_partial(self) -> None:
        """Test creating from partial dictionary."""
        data = {"port": 8080}
        config = ServerConfig.from_dict(data)
        assert config.host == "0.0.0.0"  # Default
        assert config.port == 8080


class TestAppConfig:
    """Tests for AppConfig model."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = AppConfig()
        assert config.server.host == "0.0.0.0"
        assert config.database.path == "data.db"
        assert config.log.level == "INFO"

    def test_from_dict(self) -> None:
        """Test creating from dictionary."""
        data = {
            "server": {"host": "127.0.0.1", "port": 8080},
            "database": {"path": "custom.db"},
            "log": {"level": "DEBUG", "use_syslog": False},
        }
        config = AppConfig.from_dict(data)
        assert config.server.host == "127.0.0.1"
        assert config.server.port == 8080
        assert config.database.path == "custom.db"
        assert config.log.level == "DEBUG"
        assert config.log.use_syslog is False


class TestUser:
    """Tests for User model."""

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        user = User(id=1, username="testuser", password_hash="hash123")
        result = user.to_dict()
        assert result["id"] == 1
        assert result["username"] == "testuser"
        assert "password_hash" not in result

    def test_to_dict_with_password(self) -> None:
        """Test converting to dictionary with password."""
        user = User(id=1, username="testuser", password_hash="hash123")
        result = user.to_dict(include_password=True)
        assert result["password_hash"] == "hash123"

    def test_from_dict(self) -> None:
        """Test creating from dictionary."""
        data = {"id": 1, "username": "testuser", "password_hash": "hash123"}
        user = User.from_dict(data)
        assert user.id == 1
        assert user.username == "testuser"
        assert user.password_hash == "hash123"


class TestLoraMessage:
    """Tests for LoraMessage model."""

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        message = LoraMessage(
            id=1,
            device_name="TestDevice",
            deveui="00-11-22-33-44-55-66-77",
            appeui="aa-bb-cc-dd-ee-ff-00-11",
            data="SGVsbG8=",
            size=5,
            timestamp="2024-01-15T10:00:00Z",
            sequence_number=42,
        )
        result = message.to_dict()
        assert result["id"] == 1
        assert result["deviceName"] == "TestDevice"
        assert result["deveui"] == "00-11-22-33-44-55-66-77"
        assert result["sqn"] == 42

    def test_from_dict(self) -> None:
        """Test creating from dictionary."""
        data = {
            "deviceName": "TestDevice",
            "deveui": "00-11-22-33-44-55-66-77",
            "appeui": "aa-bb-cc-dd-ee-ff-00-11",
            "data": "SGVsbG8=",
            "size": 5,
            "sqn": 42,
        }
        message = LoraMessage.from_dict(data)
        assert message.device_name == "TestDevice"
        assert message.deveui == "00-11-22-33-44-55-66-77"
        assert message.sequence_number == 42

    def test_from_dict_alternative_keys(self) -> None:
        """Test creating from dictionary with alternative keys."""
        data = {
            "device_name": "TestDevice",
            "deveui": "00-11-22-33-44-55-66-77",
            "sequence_number": 42,
        }
        message = LoraMessage.from_dict(data)
        assert message.device_name == "TestDevice"
        assert message.sequence_number == 42

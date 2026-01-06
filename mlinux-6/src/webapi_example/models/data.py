"""Data models for API resources."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class User:
    """User data model.

    Attributes:
        id: Unique user ID.
        username: Username.
        password_hash: Hashed password.
    """

    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""

    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """Convert to dictionary.

        Args:
            include_password: Include password hash in output.

        Returns:
            Dictionary representation.
        """
        result: Dict[str, Any] = {
            "id": self.id,
            "username": self.username,
        }
        if include_password:
            result["password_hash"] = self.password_hash
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> User:
        """Create User from dictionary.

        Args:
            data: User dictionary.

        Returns:
            User instance.
        """
        return cls(
            id=data.get("id"),
            username=data.get("username", ""),
            password_hash=data.get("password_hash", ""),
        )


@dataclass
class LoraMessage:
    """LoRa message data model.

    Attributes:
        id: Unique message ID.
        device_name: Friendly device name.
        deveui: Device EUI.
        appeui: Application EUI.
        data: Message payload data.
        size: Payload size in bytes.
        timestamp: Message timestamp.
        sequence_number: Message sequence number.
    """

    id: Optional[int] = None
    device_name: str = ""
    deveui: str = ""
    appeui: str = ""
    data: str = ""
    size: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    sequence_number: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "id": self.id,
            "deviceName": self.device_name,
            "deveui": self.deveui,
            "appeui": self.appeui,
            "data": self.data,
            "size": self.size,
            "timestamp": self.timestamp,
            "sqn": self.sequence_number,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LoraMessage:
        """Create LoraMessage from dictionary.

        Args:
            data: Message dictionary.

        Returns:
            LoraMessage instance.
        """
        return cls(
            id=data.get("id"),
            device_name=data.get("deviceName", data.get("device_name", "")),
            deveui=data.get("deveui", ""),
            appeui=data.get("appeui", ""),
            data=data.get("data", ""),
            size=data.get("size", 0),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            sequence_number=data.get("sqn", data.get("sequence_number", 0)),
        )

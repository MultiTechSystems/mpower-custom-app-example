"""Configuration models using dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class TlsConfig:
    """TLS/SSL configuration.

    Attributes:
        enabled: Enable TLS/HTTPS.
        cert_file: Path to certificate file (PEM format).
        key_file: Path to private key file (PEM format).
    """

    enabled: bool = False
    cert_file: str = "/var/config/server.pem"
    key_file: str = "/var/config/server.pem"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TlsConfig:
        """Create TlsConfig from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            TlsConfig instance.
        """
        return cls(
            enabled=data.get("enabled", False),
            cert_file=data.get("cert_file", "/var/config/server.pem"),
            key_file=data.get("key_file", "/var/config/server.pem"),
        )


@dataclass
class ServerConfig:
    """HTTP server configuration.

    Attributes:
        host: Host address to bind to.
        port: Port number to listen on.
        debug: Enable debug mode.
        tls: TLS/SSL configuration.
    """

    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    tls: TlsConfig = field(default_factory=TlsConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ServerConfig:
        """Create ServerConfig from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            ServerConfig instance.
        """
        return cls(
            host=data.get("host", "0.0.0.0"),
            port=data.get("port", 5000),
            debug=data.get("debug", False),
            tls=TlsConfig.from_dict(data.get("tls", {})),
        )


@dataclass
class DatabaseConfig:
    """Database configuration.

    Attributes:
        path: Path to SQLite database file.
    """

    path: str = "data.db"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DatabaseConfig:
        """Create DatabaseConfig from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            DatabaseConfig instance.
        """
        return cls(
            path=data.get("path", "data.db"),
        )


@dataclass
class LogConfig:
    """Logging configuration.

    Attributes:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        use_syslog: Use syslog for logging on mLinux.
    """

    level: str = "INFO"
    use_syslog: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LogConfig:
        """Create LogConfig from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            LogConfig instance.
        """
        return cls(
            level=data.get("level", "INFO"),
            use_syslog=data.get("use_syslog", True),
        )


@dataclass
class AppConfig:
    """Main application configuration.

    Attributes:
        server: HTTP server configuration.
        database: Database configuration.
        log: Logging configuration.
    """

    server: ServerConfig = field(default_factory=ServerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    log: LogConfig = field(default_factory=LogConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AppConfig:
        """Create AppConfig from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            AppConfig instance.
        """
        return cls(
            server=ServerConfig.from_dict(data.get("server", {})),
            database=DatabaseConfig.from_dict(data.get("database", {})),
            log=LogConfig.from_dict(data.get("log", {})),
        )

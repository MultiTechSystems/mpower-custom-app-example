"""Main entry point for the Web API Example application."""

import argparse
import logging
import os
import signal
import sys
from types import FrameType

from webapi_example.utils.config_loader import load_config
from webapi_example.utils.logging_setup import setup_logging
from webapi_example.utils.status_writer import StatusWriter

logger = logging.getLogger(__name__)

# Global status writer for signal handler access
_status_writer: StatusWriter | None = None


def signal_handler(signum: int, frame: FrameType | None) -> None:
    """Handle shutdown signals gracefully.

    Args:
        signum: Signal number.
        frame: Current stack frame.
    """
    logger.info("Received signal %d, shutting down...", signum)
    if _status_writer:
        _status_writer.stop()
    sys.exit(0)


def main() -> None:
    """Run the Web API Example application."""
    global _status_writer

    parser = argparse.ArgumentParser(description="Web API Example for mPower gateways")
    parser.add_argument(
        "-c",
        "--config",
        help="Path to configuration file",
        default=None,
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Setup logging
    setup_logging(config.log, app_name="webapi-example")
    logger.info("Starting Web API Example")

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start status writer for app-manager integration
    _status_writer = StatusWriter()
    _status_writer.start()
    _status_writer.set_status("Initializing")

    # Get database path
    app_dir = os.environ.get("APP_DIR", ".")
    db_path = os.path.join(app_dir, config.database.path)

    # Update status
    protocol = "https" if config.server.tls.enabled else "http"
    _status_writer.set_status(f"Running on {config.server.host}:{config.server.port} ({protocol})")

    try:
        # Import and run the stdlib-based server (no Flask dependency)
        from webapi_example.server import run_server
        logger.info(
            "Starting server on %s:%d", config.server.host, config.server.port
        )
        run_server(config, db_path)
    except Exception as e:
        logger.error("Application error: %s", e)
        if _status_writer:
            _status_writer.set_status(f"Error: {e}")
        raise
    finally:
        if _status_writer:
            _status_writer.stop()


if __name__ == "__main__":
    main()

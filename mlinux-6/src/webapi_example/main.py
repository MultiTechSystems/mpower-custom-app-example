"""Main entry point for the Web API Example application."""

from __future__ import annotations

import argparse
import logging
import signal
import sys
from types import FrameType
from typing import Optional

from webapi_example.app import create_app, init_db
from webapi_example.utils.config_loader import load_config
from webapi_example.utils.logging_setup import setup_logging
from webapi_example.utils.status_writer import StatusWriter

logger = logging.getLogger(__name__)

# Global status writer for signal handler access
_status_writer: Optional[StatusWriter] = None


def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
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

    # Create and initialize application
    app = create_app(config)
    init_db(app)

    # Update status
    _status_writer.set_status(f"Running on {config.server.host}:{config.server.port}")

    try:
        # Run the Flask development server
        # Note: In production, use a proper WSGI server like gunicorn
        logger.info(
            "Starting server on %s:%d", config.server.host, config.server.port
        )
        app.run(
            host=config.server.host,
            port=config.server.port,
            debug=config.server.debug,
            use_reloader=False,  # Disable reloader for production
        )
    except Exception as e:
        logger.error("Application error: %s", e)
        _status_writer.set_status(f"Error: {e}")
        raise
    finally:
        _status_writer.stop()


if __name__ == "__main__":
    main()

"""Status writer for mLinux app-manager integration."""

import json
import logging
import os
import threading
from datetime import datetime

logger = logging.getLogger(__name__)


class StatusWriter:
    """Write status.json for mLinux app-manager integration.

    The status.json file is used by the mLinux app-manager to monitor
    application health and display status information.

    Attributes:
        app_dir: Application directory path.
        status_file: Path to status.json file.
        update_interval: Seconds between status updates.
    """

    def __init__(
        self, app_dir: str | None = None, update_interval: float = 10.0
    ) -> None:
        """Initialize the status writer.

        Args:
            app_dir: Application directory. Uses APP_DIR env var or "." if None.
            update_interval: Seconds between automatic status updates.
        """
        self.app_dir = app_dir if app_dir else (os.getenv("APP_DIR") or ".")
        self.status_file = os.path.join(self.app_dir, "status.json")
        self.update_interval = update_interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._status_info = "Starting..."

    def start(self) -> None:
        """Start background status update thread."""
        self._running = True
        self._write_status(self._status_info)
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()
        logger.info("Status writer started, writing to %s", self.status_file)

    def stop(self) -> None:
        """Stop background thread and write final status."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        self._write_status("Stopped")
        logger.info("Status writer stopped")

    def set_status(self, info: str) -> None:
        """Update the status info (thread-safe).

        Args:
            info: Status information string (max 160 chars).
        """
        with self._lock:
            self._status_info = info

    def _update_loop(self) -> None:
        """Background loop to periodically write status."""
        while self._running:
            with self._lock:
                info = self._status_info
            timestamp = datetime.now().strftime("%H:%M:%S")
            self._write_status(f"{info} @ {timestamp}")
            # Use Event.wait for interruptible sleep
            threading.Event().wait(self.update_interval)

    def _write_status(self, app_info: str) -> None:
        """Write status.json atomically.

        Args:
            app_info: Status information to write.
        """
        # pid must be integer for app-manager
        status_data = {"pid": os.getpid(), "AppInfo": app_info[:160]}
        temp_file = self.status_file + ".tmp"
        try:
            with open(temp_file, "w") as f:
                json.dump(status_data, f)
            os.replace(temp_file, self.status_file)
        except OSError as e:
            logger.warning("Failed to write status: %s", e)

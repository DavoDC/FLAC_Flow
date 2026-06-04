"""Lockfile to prevent concurrent runs.

Uses a PID-based lockfile. If the lockfile exists and the PID is still running,
the lock is considered held. Stale lockfiles (PID no longer running) are cleaned
up automatically.
"""

import logging
import os
from pathlib import Path


class LockFile:
    """Simple PID-based lockfile."""

    def __init__(self, path: Path):
        self.path = path

    def acquire(self) -> bool:
        """Try to acquire the lock. Returns True if acquired, False if already held."""
        if self.path.exists():
            try:
                old_pid = int(self.path.read_text().strip())
                if self._pid_alive(old_pid):
                    logging.warning("Lock held by PID %d", old_pid)
                    return False
                else:
                    logging.info("Removing stale lockfile (PID %d no longer running)", old_pid)
            except (ValueError, OSError):
                logging.info("Removing invalid lockfile")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(str(os.getpid()))
        return True

    def release(self) -> None:
        """Release the lock (only if owned by this process)."""
        try:
            if self.path.exists():
                pid = int(self.path.read_text().strip())
                if pid == os.getpid():
                    self.path.unlink()
        except (ValueError, OSError) as e:
            logging.warning("Failed to release lockfile: %s", e)

    def _pid_alive(self, pid: int) -> bool:
        """Return True if the given PID is still running."""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def __enter__(self) -> "LockFile":
        if not self.acquire():
            raise RuntimeError(
                "Another FLAC Flow instance is already running. "
                f"If this is incorrect, delete the lockfile: {self.path}"
            )
        return self

    def __exit__(self, *args) -> None:
        self.release()

"""Tests for LockFile."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lockfile import LockFile


def _tmp_lock(tmp_dir):
    return LockFile(Path(tmp_dir) / "test.lock")


def test_acquire_creates_lockfile(tmp_path):
    lock = LockFile(tmp_path / "sub" / "test.lock")
    result = lock.acquire()
    assert result is True
    assert lock.path.exists()
    lock.release()


def test_lockfile_contains_current_pid(tmp_path):
    lock = LockFile(tmp_path / "test.lock")
    lock.acquire()
    pid = int(lock.path.read_text().strip())
    assert pid == os.getpid()
    lock.release()


def test_release_removes_lockfile(tmp_path):
    lock = LockFile(tmp_path / "test.lock")
    lock.acquire()
    lock.release()
    assert not lock.path.exists()


def test_acquire_blocked_when_other_pid_alive(tmp_path):
    lock = LockFile(tmp_path / "test.lock")
    # Write a fake lock owned by PID 1 (init/kernel - always alive)
    lock.path.parent.mkdir(parents=True, exist_ok=True)
    lock.path.write_text("1")
    with patch.object(lock, "_pid_alive", return_value=True):
        result = lock.acquire()
    assert result is False


def test_acquire_succeeds_on_stale_lockfile(tmp_path):
    lock = LockFile(tmp_path / "test.lock")
    lock.path.parent.mkdir(parents=True, exist_ok=True)
    lock.path.write_text("99999999")  # PID that almost certainly doesn't exist
    with patch.object(lock, "_pid_alive", return_value=False):
        result = lock.acquire()
    assert result is True
    lock.release()


def test_acquire_succeeds_on_invalid_lockfile_content(tmp_path):
    lock = LockFile(tmp_path / "test.lock")
    lock.path.parent.mkdir(parents=True, exist_ok=True)
    lock.path.write_text("not-a-pid")
    result = lock.acquire()
    assert result is True
    lock.release()


def test_release_only_removes_own_lock(tmp_path):
    lock = LockFile(tmp_path / "test.lock")
    lock.path.parent.mkdir(parents=True, exist_ok=True)
    lock.path.write_text("99999")  # different PID
    lock.release()
    # Should still exist - we don't own it
    assert lock.path.exists()


def test_context_manager_acquires_and_releases(tmp_path):
    lock = LockFile(tmp_path / "test.lock")
    with lock:
        assert lock.path.exists()
    assert not lock.path.exists()


def test_context_manager_raises_if_locked(tmp_path):
    lock = LockFile(tmp_path / "test.lock")
    with patch.object(lock, "acquire", return_value=False):
        try:
            with lock:
                pass
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "already running" in str(e)


def test_flac_flow_exits_if_lock_held(tmp_path):
    """flac_flow.main() prints error and exits 1 when lock cannot be acquired."""
    import flac_flow as ff
    import pytest
    from io import StringIO

    output = StringIO()
    with patch.object(sys, "argv", ["flac_flow.py"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow.LockFile") as MockLock, \
         patch("sys.stdout", output):
        instance = MagicMock()
        instance.acquire.return_value = False
        MockLock.return_value = instance
        with pytest.raises(SystemExit) as exc_info:
            ff.main()
    assert exc_info.value.code == 1
    assert "already running" in output.getvalue()

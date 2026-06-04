"""Tests for --since date filter flag."""

import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import flac_flow as ff

_BEFORE = datetime(2020, 6, 1).timestamp()   # Jan 2020 - old
_AFTER = datetime(2025, 6, 1).timestamp()    # Jun 2025 - recent
_SINCE = "2024-01-01"
_SINCE_TS = datetime(2024, 1, 1).timestamp()


# --- _parse_since unit tests ---

def test_parse_since_returns_none_for_none():
    assert ff._parse_since(None) is None


def test_parse_since_returns_none_for_empty_string():
    assert ff._parse_since("") is None


def test_parse_since_returns_correct_timestamp():
    ts = ff._parse_since("2024-01-01")
    assert ts == datetime(2024, 1, 1).timestamp()


def test_parse_since_different_dates():
    ts_a = ff._parse_since("2023-06-15")
    ts_b = ff._parse_since("2024-06-15")
    assert ts_b > ts_a


# --- _filter_by_since unit tests with real files ---

def test_filter_excludes_file_before_since(tmp_path):
    old = tmp_path / "old.flac"
    old.touch()
    os.utime(str(old), (_BEFORE, _BEFORE))
    result = ff._filter_by_since([old], _SINCE_TS)
    assert old not in result


def test_filter_includes_file_after_since(tmp_path):
    new = tmp_path / "new.flac"
    new.touch()
    os.utime(str(new), (_AFTER, _AFTER))
    result = ff._filter_by_since([new], _SINCE_TS)
    assert new in result


def test_filter_includes_file_exactly_on_since_boundary(tmp_path):
    exact = tmp_path / "exact.flac"
    exact.touch()
    os.utime(str(exact), (_SINCE_TS, _SINCE_TS))
    result = ff._filter_by_since([exact], _SINCE_TS)
    assert exact in result


def test_filter_with_none_since_returns_all(tmp_path):
    old = tmp_path / "old.flac"
    new = tmp_path / "new.flac"
    old.touch()
    new.touch()
    os.utime(str(old), (_BEFORE, _BEFORE))
    os.utime(str(new), (_AFTER, _AFTER))
    result = ff._filter_by_since([old, new], None)
    assert old in result
    assert new in result


def test_filter_mixed_keeps_only_new(tmp_path):
    old = tmp_path / "old.flac"
    new = tmp_path / "new.flac"
    old.touch()
    new.touch()
    os.utime(str(old), (_BEFORE, _BEFORE))
    os.utime(str(new), (_AFTER, _AFTER))
    result = ff._filter_by_since([old, new], _SINCE_TS)
    assert result == [new]


# --- CLI parsing ---

def test_parse_args_since_flag():
    with patch.object(sys, "argv", ["flac_flow.py", "--since", "2024-06-01"]):
        args = ff._parse_args()
    assert args.since == "2024-06-01"


def test_parse_args_since_default_is_none():
    with patch.object(sys, "argv", ["flac_flow.py"]):
        args = ff._parse_args()
    assert args.since is None

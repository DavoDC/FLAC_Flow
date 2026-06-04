"""Tests for --verbose flag."""

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import flac_flow as ff


def test_parse_args_verbose_flag():
    with patch.object(sys, "argv", ["flac_flow.py", "--verbose"]):
        args = ff._parse_args()
    assert args.verbose is True


def test_parse_args_verbose_default_is_false():
    with patch.object(sys, "argv", ["flac_flow.py"]):
        args = ff._parse_args()
    assert args.verbose is False


def test_fmt_size_megabytes(tmp_path):
    f = tmp_path / "big.flac"
    f.write_bytes(b"x" * (2 * 1024 * 1024))  # 2 MB
    result = ff._fmt_size(f)
    assert "MB" in result
    assert "2.0" in result


def test_fmt_size_kilobytes(tmp_path):
    f = tmp_path / "small.flac"
    f.write_bytes(b"x" * 512)  # 512 bytes = 0.5 KB -> "0 KB" due to int rounding
    result = ff._fmt_size(f)
    assert "KB" in result


def test_fmt_size_returns_empty_on_missing_file():
    result = ff._fmt_size(Path("nonexistent/path.flac"))
    assert result == ""


def _make_cfg():
    cfg = MagicMock()
    cfg.scrub_art_and_padding = False
    cfg.convert_to_mp3 = True
    cfg.destination_root = Path("C:/Music/MP3")
    cfg.source_folders = [Path("C:/Music/FLAC/Album")]
    return cfg


def _run_verbose(cfg, extra_argv=None):
    argv = ["flac_flow.py", "--verbose", "--no-confirm"] + (extra_argv or [])
    flac = Path("C:/Music/FLAC/Album/track.flac")
    with patch.object(sys, "argv", argv), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow._validate_destination"), \
         patch("flac_flow.LockFile") as MockLock, \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=[flac]), \
         patch("flac_flow._filter_by_since", return_value=[flac]), \
         patch("flac_flow.transcode_file", return_value=True), \
         patch("flac_flow.mirror_path", return_value=MagicMock(exists=lambda: False)), \
         patch.object(Path, "open", return_value=MagicMock()), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        MockLock.return_value.acquire.return_value = True
        ff.main()
        return mock_stdout.getvalue()


def test_verbose_shows_destination():
    cfg = _make_cfg()
    output = _run_verbose(cfg)
    assert "C:/Music/MP3" in output or "C:\\Music\\MP3" in output


def test_verbose_shows_source_folder_count():
    cfg = _make_cfg()
    output = _run_verbose(cfg)
    assert "[VERBOSE]" in output


def test_verbose_shows_since_when_set():
    cfg = _make_cfg()
    output = _run_verbose(cfg, ["--since", "2024-01-01"])
    assert "2024-01-01" in output


def test_verbose_not_shown_without_flag():
    cfg = _make_cfg()
    flac = Path("C:/Music/FLAC/Album/track.flac")
    with patch.object(sys, "argv", ["flac_flow.py", "--no-confirm"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow._validate_destination"), \
         patch("flac_flow.LockFile") as MockLock, \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=[flac]), \
         patch("flac_flow._filter_by_since", return_value=[flac]), \
         patch("flac_flow.transcode_file", return_value=True), \
         patch("flac_flow.mirror_path", return_value=MagicMock(exists=lambda: False)), \
         patch.object(Path, "open", return_value=MagicMock()), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        MockLock.return_value.acquire.return_value = True
        ff.main()
        output = mock_stdout.getvalue()
    assert "[VERBOSE]" not in output

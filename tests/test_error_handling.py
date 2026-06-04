"""Tests for error handling improvements (TIER 2)."""

import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import flac_flow as ff
import transcode as transcode_mod


# ── transcode.py - mkdir failure ──────────────────────────────────────────────

def test_transcode_mkdir_failure_returns_false():
    """If the output directory can't be created, transcode_file returns False."""
    ffmpeg = Path("ffmpeg.exe")
    flac_file = Path("C:/Music/FLAC/Album/track01.flac")
    source = Path("C:/Music/FLAC/Album")
    dest = Path("C:/Music/MP3")

    with patch("transcode.mirror_path", return_value=Path("C:/Music/MP3/Album/track01.mp3")), \
         patch.object(Path, "mkdir", side_effect=PermissionError("Access denied")):
        result = transcode_mod.transcode_file(flac_file, source, dest, ffmpeg)

    assert result is False


def test_transcode_mkdir_oserror_returns_false():
    """Generic OSError from mkdir also returns False."""
    ffmpeg = Path("ffmpeg.exe")
    flac_file = Path("C:/Music/FLAC/Album/track01.flac")
    source = Path("C:/Music/FLAC/Album")
    dest = Path("C:/Music/MP3")

    with patch("transcode.mirror_path", return_value=Path("C:/Music/MP3/Album/track01.mp3")), \
         patch.object(Path, "mkdir", side_effect=OSError("Read-only filesystem")):
        result = transcode_mod.transcode_file(flac_file, source, dest, ffmpeg)

    assert result is False


# ── flac_flow.py - unreadable file ────────────────────────────────────────────

def _make_config(scrub=True, transcode=True):
    cfg = MagicMock()
    cfg.scrub_art_and_padding = scrub
    cfg.convert_to_mp3 = transcode
    cfg.destination_root = Path("C:/Music/MP3")
    cfg.source_folders = [Path("C:/Music/FLAC/Album")]
    return cfg


def _run_main_with_files(flac_files, cfg, extra_argv=None):
    argv = ["flac_flow.py"] + (extra_argv or [])
    with patch.object(sys, "argv", argv), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=flac_files), \
         patch("flac_flow.scrub_file", return_value=True), \
         patch("flac_flow.transcode_file", return_value=True), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        ff.main()
        return mock_stdout.getvalue()


def test_unreadable_flac_is_counted_as_error():
    """A file that raises OSError on open is counted as an error."""
    cfg = _make_config(scrub=False, transcode=True)
    flac_files = [
        Path("C:/Music/FLAC/Album/locked.flac"),
        Path("C:/Music/FLAC/Album/ok.flac"),
    ]

    def fake_open(path, *args, **kwargs):
        if "locked" in str(path):
            raise PermissionError("Access denied")
        return MagicMock().__enter__.return_value

    with patch.object(sys, "argv", ["flac_flow.py", "--no-confirm"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=flac_files), \
         patch("flac_flow.transcode_file", return_value=True), \
         patch("builtins.open", side_effect=fake_open), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        ff.main()
        output = mock_stdout.getvalue()

    assert "READ ERROR" in output


def test_error_summary_lists_failed_files():
    """The end-of-run summary lists the paths of each failed file."""
    cfg = _make_config(scrub=False, transcode=True)
    flac_file = Path("C:/Music/FLAC/Album/bad.flac")

    with patch.object(sys, "argv", ["flac_flow.py", "--no-confirm"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=[flac_file]), \
         patch("flac_flow.transcode_file", return_value=False), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        ff.main()
        output = mock_stdout.getvalue()

    assert "bad.flac" in output


def test_error_count_shown_in_summary():
    """Error count appears in the end-of-run summary."""
    cfg = _make_config(scrub=False, transcode=True)
    flac_files = [
        Path("C:/Music/FLAC/Album/bad1.flac"),
        Path("C:/Music/FLAC/Album/bad2.flac"),
    ]

    with patch.object(sys, "argv", ["flac_flow.py", "--no-confirm"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=flac_files), \
         patch("flac_flow.transcode_file", return_value=False), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        ff.main()
        output = mock_stdout.getvalue()

    assert "2" in output
    assert "failed" in output.lower() or "error" in output.lower()

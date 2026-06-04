"""Tests for --dry-run mode."""

import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock, call

# Add src/ to path so flac_flow can be imported
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import flac_flow as ff


def test_parse_args_dry_run_flag():
    with patch.object(sys, "argv", ["flac_flow.py", "--dry-run"]):
        args = ff._parse_args()
    assert args.dry_run is True


def test_parse_args_no_dry_run_by_default():
    with patch.object(sys, "argv", ["flac_flow.py"]):
        args = ff._parse_args()
    assert args.dry_run is False


def test_parse_args_dry_run_and_no_confirm_together():
    with patch.object(sys, "argv", ["flac_flow.py", "--dry-run", "--no-confirm"]):
        args = ff._parse_args()
    assert args.dry_run is True
    assert args.no_confirm is True


def _make_config(scrub=True, transcode=True):
    cfg = MagicMock()
    cfg.scrub_art_and_padding = scrub
    cfg.convert_to_mp3 = transcode
    cfg.destination_root = Path("C:/Music/MP3")
    cfg.source_folders = [Path("C:/Music/FLAC/Album")]
    return cfg


def _run_dry_run_main(flac_files, cfg):
    """Helper: run main() in dry-run mode, return captured stdout lines."""
    with patch.object(sys, "argv", ["flac_flow.py", "--dry-run"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=flac_files), \
         patch("flac_flow.scrub_file") as mock_scrub, \
         patch("flac_flow.transcode_file") as mock_transcode, \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        ff.main()
        output = mock_stdout.getvalue()
    return output, mock_scrub, mock_transcode


def test_dry_run_does_not_call_scrub():
    cfg = _make_config(scrub=True, transcode=True)
    flac_files = [Path("C:/Music/FLAC/Album/track01.flac")]
    output, mock_scrub, mock_transcode = _run_dry_run_main(flac_files, cfg)
    mock_scrub.assert_not_called()


def test_dry_run_does_not_call_transcode():
    cfg = _make_config(scrub=True, transcode=True)
    flac_files = [Path("C:/Music/FLAC/Album/track01.flac")]
    output, mock_scrub, mock_transcode = _run_dry_run_main(flac_files, cfg)
    mock_transcode.assert_not_called()


def test_dry_run_output_contains_dry_run_prefix():
    cfg = _make_config()
    flac_files = [Path("C:/Music/FLAC/Album/track01.flac")]
    output, _, _ = _run_dry_run_main(flac_files, cfg)
    assert "[DRY RUN]" in output


def test_dry_run_output_shows_mirror_path():
    cfg = _make_config()
    flac_files = [Path("C:/Music/FLAC/Album/track01.flac")]
    output, _, _ = _run_dry_run_main(flac_files, cfg)
    assert "track01.mp3" in output


def test_dry_run_counts_files_correctly():
    cfg = _make_config()
    flac_files = [
        Path("C:/Music/FLAC/Album/track01.flac"),
        Path("C:/Music/FLAC/Album/track02.flac"),
    ]
    output, _, _ = _run_dry_run_main(flac_files, cfg)
    assert "2" in output

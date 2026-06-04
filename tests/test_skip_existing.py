"""Tests for --skip-existing flag."""

import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import flac_flow as ff


def test_parse_args_skip_existing_flag():
    with patch.object(sys, "argv", ["flac_flow.py", "--skip-existing"]):
        args = ff._parse_args()
    assert args.skip_existing is True


def test_parse_args_no_skip_existing_by_default():
    with patch.object(sys, "argv", ["flac_flow.py"]):
        args = ff._parse_args()
    assert args.skip_existing is False


def _make_config(scrub=False, transcode=True):
    cfg = MagicMock()
    cfg.scrub_art_and_padding = scrub
    cfg.convert_to_mp3 = transcode
    cfg.destination_root = Path("C:/Music/MP3")
    cfg.source_folders = [Path("C:/Music/FLAC/Album")]
    return cfg


def _run_skip_existing(flac_files, existing_outputs, cfg):
    """Run main() with --skip-existing; existing_outputs is a set of mp3 Path names to treat as existing."""
    def make_mirror_path(f, s, d):
        mp3 = Path("C:/Music/MP3/Album") / f.with_suffix(".mp3").name
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = mp3 in existing_outputs
        mock_path.__str__ = lambda self: str(mp3)
        mock_path.name = mp3.name
        return mock_path

    with patch.object(sys, "argv", ["flac_flow.py", "--skip-existing", "--no-confirm"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow._validate_destination"), \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=flac_files), \
         patch("flac_flow.scrub_file", return_value=True) as mock_scrub, \
         patch("flac_flow.transcode_file", return_value=True) as mock_transcode, \
         patch("flac_flow.mirror_path", side_effect=make_mirror_path), \
         patch.object(Path, "open", return_value=MagicMock()), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        ff.main()
        return mock_stdout.getvalue(), mock_scrub, mock_transcode


def test_skip_existing_skips_transcode_when_output_exists():
    """When output MP3 already exists, transcode_file is NOT called."""
    cfg = _make_config(scrub=False, transcode=True)
    flac = Path("C:/Music/FLAC/Album/track01.flac")
    existing_mp3 = Path("C:/Music/MP3/Album/track01.mp3")
    output, _, mock_transcode = _run_skip_existing([flac], {existing_mp3}, cfg)
    mock_transcode.assert_not_called()


def test_skip_existing_processes_when_output_missing():
    """When output MP3 does not exist, transcode_file IS called."""
    cfg = _make_config(scrub=False, transcode=True)
    flac = Path("C:/Music/FLAC/Album/track01.flac")
    output, _, mock_transcode = _run_skip_existing([flac], set(), cfg)
    mock_transcode.assert_called_once()


def test_skip_existing_output_shows_skipped_label():
    """Output shows SKIPPED for files whose output already exists."""
    cfg = _make_config(scrub=False, transcode=True)
    flac = Path("C:/Music/FLAC/Album/track01.flac")
    existing_mp3 = Path("C:/Music/MP3/Album/track01.mp3")
    output, _, _ = _run_skip_existing([flac], {existing_mp3}, cfg)
    assert "SKIPPED" in output


def test_skip_existing_summary_shows_skipped_count():
    """End-of-run summary includes the count of skipped files."""
    cfg = _make_config(scrub=False, transcode=True)
    flacs = [
        Path("C:/Music/FLAC/Album/track01.flac"),
        Path("C:/Music/FLAC/Album/track02.flac"),
    ]
    existing = {
        Path("C:/Music/MP3/Album/track01.mp3"),
        Path("C:/Music/MP3/Album/track02.mp3"),
    }
    output, _, _ = _run_skip_existing(flacs, existing, cfg)
    assert "skip" in output.lower()


def test_skip_existing_skips_scrub_when_output_exists():
    """When output already exists and scrub is enabled, scrub is also skipped."""
    cfg = _make_config(scrub=True, transcode=True)
    flac = Path("C:/Music/FLAC/Album/track01.flac")
    existing_mp3 = Path("C:/Music/MP3/Album/track01.mp3")
    output, mock_scrub, _ = _run_skip_existing([flac], {existing_mp3}, cfg)
    mock_scrub.assert_not_called()

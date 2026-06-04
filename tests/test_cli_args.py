"""Tests for --config and --quality CLI flags."""

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import flac_flow as ff


def test_parse_args_config_flag():
    with patch.object(sys, "argv", ["flac_flow.py", "--config", "/path/to/config.json"]):
        args = ff._parse_args()
    assert args.config == "/path/to/config.json"


def test_parse_args_config_default_is_none():
    with patch.object(sys, "argv", ["flac_flow.py"]):
        args = ff._parse_args()
    assert args.config is None


def test_parse_args_quality_v2():
    with patch.object(sys, "argv", ["flac_flow.py", "--quality", "V2"]):
        args = ff._parse_args()
    assert args.quality == "V2"


def test_parse_args_quality_v4():
    with patch.object(sys, "argv", ["flac_flow.py", "--quality", "V4"]):
        args = ff._parse_args()
    assert args.quality == "V4"


def test_parse_args_quality_default_is_none():
    with patch.object(sys, "argv", ["flac_flow.py"]):
        args = ff._parse_args()
    assert args.quality is None


def _make_cfg(scrub=False, transcode=True):
    cfg = MagicMock()
    cfg.scrub_art_and_padding = scrub
    cfg.convert_to_mp3 = transcode
    cfg.destination_root = Path("C:/Music/MP3")
    cfg.source_folders = [Path("C:/Music/FLAC/Album")]
    return cfg


def test_config_flag_passes_path_to_load_config():
    """When --config is set, load_config is called with that path."""
    cfg = _make_cfg()
    flac = Path("C:/Music/FLAC/Album/track.flac")
    with patch.object(sys, "argv", ["flac_flow.py", "--config", "C:/custom/config.json", "--no-confirm"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow._validate_destination"), \
         patch("flac_flow.LockFile") as MockLock, \
         patch("flac_flow.load_config", return_value=cfg) as mock_load, \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=[flac]), \
         patch("flac_flow.transcode_file", return_value=True), \
         patch.object(Path, "open", return_value=MagicMock()), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO):
        MockLock.return_value.acquire.return_value = True
        ff.main()
    mock_load.assert_called_once_with(Path("C:/custom/config.json"))


def test_quality_flag_passed_to_transcode():
    """When --quality V2 is set, transcode_file is called with quality='V2'."""
    cfg = _make_cfg(scrub=False, transcode=True)
    flac = Path("C:/Music/FLAC/Album/track.flac")
    with patch.object(sys, "argv", ["flac_flow.py", "--quality", "V2", "--no-confirm"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow._validate_destination"), \
         patch("flac_flow.LockFile") as MockLock, \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=[flac]), \
         patch("flac_flow.transcode_file", return_value=True) as mock_transcode, \
         patch("flac_flow.mirror_path", return_value=MagicMock(exists=lambda: False)), \
         patch.object(Path, "open", return_value=MagicMock()), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO):
        MockLock.return_value.acquire.return_value = True
        ff.main()
    _, kwargs = mock_transcode.call_args
    assert kwargs.get("quality") == "V2"


def test_quality_defaults_to_v0():
    """When --quality is not set, transcode_file is called with quality='V0'."""
    cfg = _make_cfg(scrub=False, transcode=True)
    flac = Path("C:/Music/FLAC/Album/track.flac")
    with patch.object(sys, "argv", ["flac_flow.py", "--no-confirm"]), \
         patch("flac_flow._validate_platform"), \
         patch("flac_flow._validate_destination"), \
         patch("flac_flow.LockFile") as MockLock, \
         patch("flac_flow.load_config", return_value=cfg), \
         patch("flac_flow.ensure_deps", return_value=(Path("ffmpeg.exe"), Path("metaflac.exe"))), \
         patch("flac_flow.setup_logging", return_value=Path("test.log")), \
         patch("flac_flow._find_flac_files", return_value=[flac]), \
         patch("flac_flow.transcode_file", return_value=True) as mock_transcode, \
         patch("flac_flow.mirror_path", return_value=MagicMock(exists=lambda: False)), \
         patch.object(Path, "open", return_value=MagicMock()), \
         patch("sys.exit"), \
         patch("sys.stdout", new_callable=StringIO):
        MockLock.return_value.acquire.return_value = True
        ff.main()
    _, kwargs = mock_transcode.call_args
    assert kwargs.get("quality") == "V0"

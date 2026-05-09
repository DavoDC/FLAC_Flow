from pathlib import Path
from unittest.mock import patch, MagicMock

import transcode as transcode_mod

_FFMPEG = Path("dependencies/ffmpeg/ffmpeg.exe")
_SOURCE = Path("C:/Music/FLAC/Album")
_DEST = Path("C:/Music/MP3")
_FILE = _SOURCE / "track01.flac"
_OUTPUT = _DEST / "Album" / "track01.mp3"


def test_correct_ffmpeg_command_built():
    cmd = transcode_mod.build_transcode_command(_FILE, _OUTPUT, _FFMPEG)
    assert str(_FFMPEG) in cmd
    assert "-i" in cmd
    assert str(_FILE) in cmd
    assert "-codec:a" in cmd
    assert "libmp3lame" in cmd
    assert "-qscale:a" in cmd
    assert "0" in cmd
    assert str(_OUTPUT) in cmd


def test_output_path_uses_mp3_extension():
    cmd = transcode_mod.build_transcode_command(_FILE, _OUTPUT, _FFMPEG)
    assert cmd[-1].endswith(".mp3")


def test_transcode_file_returns_true_on_success():
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("transcode.subprocess.run", return_value=mock_result):
        with patch("transcode.mirror_path", return_value=_OUTPUT):
            with patch.object(Path, "mkdir"):
                result = transcode_mod.transcode_file(_FILE, _SOURCE, _DEST, _FFMPEG)
    assert result is True


def test_transcode_file_returns_false_on_failure():
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = b"ffmpeg: No such encoder"
    with patch("transcode.subprocess.run", return_value=mock_result):
        with patch("transcode.mirror_path", return_value=_OUTPUT):
            with patch.object(Path, "mkdir"):
                result = transcode_mod.transcode_file(_FILE, _SOURCE, _DEST, _FFMPEG)
    assert result is False

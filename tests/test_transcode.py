from pathlib import Path
from unittest.mock import patch, MagicMock

import transcode as transcode_mod

_FFMPEG = Path("dependencies/ffmpeg/ffmpeg.exe")
_SOURCE = Path("C:/Music/FLAC/Album")
_DEST = Path("C:/Music/MP3")
_FILE = _SOURCE / "track01.flac"


def test_correct_ffmpeg_command_built():
    pass


def test_output_path_uses_mp3_extension():
    pass


def test_transcode_file_returns_true_on_success():
    pass


def test_transcode_file_returns_false_on_failure():
    pass

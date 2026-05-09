from pathlib import Path
from unittest.mock import patch, MagicMock

import scrub as scrub_mod

_METAFLAC = Path("dependencies/flac/metaflac.exe")
_FILE = Path("test.flac")


def test_correct_metaflac_commands_built():
    cmds = scrub_mod.build_scrub_commands(_FILE, _METAFLAC)
    assert len(cmds) == 3
    assert "--block-type=PICTURE" in cmds[0]
    assert "--dont-use-padding" in cmds[0]
    assert "--block-type=PADDING" in cmds[1]
    assert "--dont-use-padding" in cmds[1]
    assert any("--add-padding=4096" in arg for arg in cmds[2])


def test_scrub_order_picture_then_padding_then_add():
    cmds = scrub_mod.build_scrub_commands(_FILE, _METAFLAC)
    assert "PICTURE" in " ".join(cmds[0])
    assert "PADDING" in " ".join(cmds[1])
    assert "add-padding" in " ".join(cmds[2])


def test_scrub_file_returns_true_on_success():
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("scrub.subprocess.run", return_value=mock_result):
        assert scrub_mod.scrub_file(_FILE, _METAFLAC) is True


def test_scrub_file_returns_false_on_failure():
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = b"metaflac: ERROR"
    with patch("scrub.subprocess.run", return_value=mock_result):
        assert scrub_mod.scrub_file(_FILE, _METAFLAC) is False

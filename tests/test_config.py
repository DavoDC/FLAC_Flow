import json
import pytest
from pathlib import Path

import config as config_mod


def _write_cfg(tmp_path, data):
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))
    return p


def _valid_data(src_path):
    return {
        "source_folders": [str(src_path)],
        "destination_root": str(src_path.parent / "dest"),
        "options": {"scrub_art_and_padding": True, "convert_to_mp3": True},
    }


def test_valid_config_loads_correctly(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    cfg = _write_cfg(tmp_path, _valid_data(src))
    c = config_mod.load(cfg)
    assert c.source_folders == [src]
    assert c.destination_root == tmp_path / "dest"
    assert c.scrub_art_and_padding is True
    assert c.convert_to_mp3 is True


def test_missing_source_folders_key_raises(tmp_path):
    cfg = _write_cfg(tmp_path, {
        "destination_root": str(tmp_path),
        "options": {"scrub_art_and_padding": True, "convert_to_mp3": True},
    })
    with pytest.raises(SystemExit):
        config_mod.load(cfg)


def test_empty_source_folders_raises(tmp_path):
    cfg = _write_cfg(tmp_path, {
        "source_folders": [],
        "destination_root": str(tmp_path),
        "options": {"scrub_art_and_padding": True, "convert_to_mp3": True},
    })
    with pytest.raises(SystemExit):
        config_mod.load(cfg)


def test_missing_destination_root_raises(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    cfg = _write_cfg(tmp_path, {
        "source_folders": [str(src)],
        "options": {"scrub_art_and_padding": True, "convert_to_mp3": True},
    })
    with pytest.raises(SystemExit):
        config_mod.load(cfg)


def test_both_options_false_raises(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    cfg = _write_cfg(tmp_path, {
        "source_folders": [str(src)],
        "destination_root": str(tmp_path / "dest"),
        "options": {"scrub_art_and_padding": False, "convert_to_mp3": False},
    })
    with pytest.raises(SystemExit):
        config_mod.load(cfg)


def test_nonexistent_source_folder_raises(tmp_path):
    cfg = _write_cfg(tmp_path, {
        "source_folders": [str(tmp_path / "does_not_exist")],
        "destination_root": str(tmp_path / "dest"),
        "options": {"scrub_art_and_padding": True, "convert_to_mp3": True},
    })
    with pytest.raises(SystemExit):
        config_mod.load(cfg)


def test_invalid_json_raises(tmp_path):
    bad = tmp_path / "config.json"
    bad.write_text("not valid json {{{{")
    with pytest.raises(SystemExit):
        config_mod.load(bad)

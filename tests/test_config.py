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
    pass


def test_missing_source_folders_key_raises(tmp_path):
    pass


def test_empty_source_folders_raises(tmp_path):
    pass


def test_missing_destination_root_raises(tmp_path):
    pass


def test_both_options_false_raises(tmp_path):
    pass


def test_nonexistent_source_folder_raises(tmp_path):
    pass


def test_invalid_json_raises(tmp_path):
    pass

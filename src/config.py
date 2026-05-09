import json
import sys
import logging
from pathlib import Path
from typing import List

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.json"


class Config:
    def __init__(
        self,
        source_folders: List[Path],
        destination_root: Path,
        scrub_art_and_padding: bool,
        convert_to_mp3: bool,
    ):
        self.source_folders = source_folders
        self.destination_root = destination_root
        self.scrub_art_and_padding = scrub_art_and_padding
        self.convert_to_mp3 = convert_to_mp3


def load(path: Path = _CONFIG_PATH) -> Config:
    """Load and validate config.json. Calls sys.exit(1) on any error."""
    if not path.exists():
        print(f"Error: Config file not found: {path}")
        print(f"Tip: Copy config/config.example.json to {path} and edit your paths.")
        sys.exit(1)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config: {e}")
        sys.exit(1)

    if "source_folders" not in data:
        print("Error: 'source_folders' key missing from config.")
        sys.exit(1)

    if not isinstance(data["source_folders"], list) or not data["source_folders"]:
        print("Error: 'source_folders' must be a non-empty list of folder paths.")
        sys.exit(1)

    if not data.get("destination_root", "").strip():
        print("Error: 'destination_root' key missing or empty in config.")
        sys.exit(1)

    options = data.get("options", {})
    scrub = bool(options.get("scrub_art_and_padding", True))
    convert = bool(options.get("convert_to_mp3", True))

    if not scrub and not convert:
        print("Error: At least one of 'scrub_art_and_padding' or 'convert_to_mp3' must be true.")
        sys.exit(1)

    source_folders = []
    for folder_str in data["source_folders"]:
        folder = Path(folder_str)
        if not folder.exists():
            print(f"Error: Source folder not found: {folder}")
            sys.exit(1)
        source_folders.append(folder)

    config = Config(
        source_folders=source_folders,
        destination_root=Path(data["destination_root"]),
        scrub_art_and_padding=scrub,
        convert_to_mp3=convert,
    )
    logging.info(
        "Config: %d source folder(s), destination=%s, scrub=%s, convert=%s",
        len(source_folders),
        config.destination_root,
        scrub,
        convert,
    )
    return config

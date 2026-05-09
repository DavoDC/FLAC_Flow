import subprocess
import logging
from pathlib import Path
from typing import List


def build_scrub_commands(file_path: Path, metaflac_exe: Path) -> List[List[str]]:
    """Return the three metaflac commands required to scrub one FLAC file."""
    f = str(file_path)
    m = str(metaflac_exe)
    return [
        [m, "--remove", "--block-type=PICTURE", "--dont-use-padding", f],
        [m, "--remove", "--block-type=PADDING", "--dont-use-padding", f],
        [m, "--add-padding=8192", f],
    ]


def scrub_file(file_path: Path, metaflac_exe: Path) -> bool:
    """Remove PICTURE and PADDING blocks, then add 8192-byte padding. Returns True on success."""
    for cmd in build_scrub_commands(file_path, metaflac_exe):
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            stderr = result.stderr.decode(errors="replace")
            logging.error("metaflac failed on %s: %s", file_path.name, stderr.strip())
            return False
    return True

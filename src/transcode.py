import subprocess
import logging
from pathlib import Path
from typing import List

from mirror import mirror_path


def build_transcode_command(file_path: Path, output_path: Path, ffmpeg_exe: Path) -> List[str]:
    """Return the ffmpeg command list for LAME V0 transcoding."""
    return [
        str(ffmpeg_exe),
        "-i", str(file_path),
        "-codec:a", "libmp3lame",
        "-qscale:a", "0",
        str(output_path),
    ]


def transcode_file(
    file_path: Path,
    source_folder: Path,
    destination_root: Path,
    ffmpeg_exe: Path,
) -> bool:
    """Transcode FLAC to MP3 V0. Creates output directory as needed. Returns True on success."""
    output_path = mirror_path(file_path, source_folder, destination_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = build_transcode_command(file_path, output_path, ffmpeg_exe)
    result = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL)
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace")
        logging.error("ffmpeg failed on %s: %s", file_path.name, stderr.strip())
        return False
    logging.info("Transcoded: %s -> %s", file_path.name, output_path.name)
    return True

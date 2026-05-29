"""
deps.py - Ensure FFmpeg and metaflac binaries are present; auto-download if missing.

Pattern-copied from RivalsVidMaker/src/ffmpeg_setup.py and extended for metaflac.
"""

import logging
import os
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Tuple

_REPO_ROOT = Path(__file__).parent.parent
_ffkit = _REPO_ROOT.parent / "ffkit"
FFMPEG_DIR = _ffkit / "dependencies" / "ffmpeg" if _ffkit.exists() else _REPO_ROOT / "dependencies" / "ffmpeg"
FLAC_DIR = _REPO_ROOT / "dependencies" / "flac"

_FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
_FFMPEG_BINS = {"ffmpeg.exe", "ffprobe.exe", "ffplay.exe"}

_METAFLAC_BINS = {"metaflac.exe", "flac.exe", "libFLAC.dll", "libFLAC++.dll"}


def ensure_deps() -> Tuple[Path, Path]:
    """
    Ensure ffmpeg.exe and metaflac.exe are present. Auto-downloads if missing.
    Returns (ffmpeg_exe, metaflac_exe) on success. Calls sys.exit(1) on failure.
    """
    ffmpeg_ok = _ensure_ffmpeg(FFMPEG_DIR)
    metaflac_ok = _ensure_metaflac(FLAC_DIR)
    if not ffmpeg_ok or not metaflac_ok:
        sys.exit(1)
    return FFMPEG_DIR / "ffmpeg.exe", FLAC_DIR / "metaflac.exe"


def _ensure_ffmpeg(ffmpeg_dir: Path) -> bool:
    if (ffmpeg_dir / "ffmpeg.exe").exists():
        logging.info("FFmpeg found at %s", ffmpeg_dir)
        return True
    print("FFmpeg not found - downloading...")
    logging.info("FFmpeg not found at %s - downloading...", ffmpeg_dir)
    return _download_and_extract(
        url=_FFMPEG_URL,
        dest_dir=ffmpeg_dir,
        bins=_FFMPEG_BINS,
        name="FFmpeg",
        manual_url="https://ffmpeg.org/download.html",
    )


def _ensure_metaflac(flac_dir: Path) -> bool:
    if (flac_dir / "metaflac.exe").exists():
        logging.info("metaflac found at %s", flac_dir)
        return True
    print("metaflac not found - downloading...")
    logging.info("metaflac not found at %s - downloading...", flac_dir)
    url = _resolve_metaflac_url()
    if not url:
        print("Error: Could not resolve metaflac download URL.")
        print("Download manually from https://github.com/xiph/flac/releases/latest")
        print(f"Extract metaflac.exe and flac.exe into {flac_dir}")
        return False
    return _download_and_extract(
        url=url,
        dest_dir=flac_dir,
        bins=_METAFLAC_BINS,
        name="FLAC tools",
        manual_url="https://github.com/xiph/flac/releases/latest",
    )


def _resolve_metaflac_url() -> str:
    """Use the GitHub API to find the latest FLAC Windows zip download URL."""
    import json
    api = "https://api.github.com/repos/xiph/flac/releases/latest"
    try:
        with urllib.request.urlopen(api, timeout=10) as resp:
            data = json.loads(resp.read())
        for asset in data.get("assets", []):
            if asset["name"].endswith("-win.zip"):
                return asset["browser_download_url"]
    except Exception as e:
        logging.error("Could not resolve metaflac URL from GitHub API: %s", e)
    return ""


def _download_and_extract(
    url: str, dest_dir: Path, bins: set, name: str, manual_url: str
) -> bool:
    dest_dir.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_name = tempfile.mkstemp(suffix=".zip")
    tmp_path = Path(tmp_name)
    os.close(tmp_fd)
    try:
        print(f"Downloading {name} from GitHub (this may take a minute)...")
        urllib.request.urlretrieve(url, str(tmp_path), _progress_cb)
        print()  # newline after inline progress

        logging.info("Extracting %s binaries...", name)
        extracted = 0
        with zipfile.ZipFile(str(tmp_path)) as zf:
            for member in zf.namelist():
                bin_name = Path(member).name
                if bin_name in bins:
                    data = zf.read(member)
                    out = dest_dir / bin_name
                    out.write_bytes(data)
                    logging.info(
                        "  Extracted: %s (%.1f MB)", bin_name, len(data) / 1024 / 1024
                    )
                    extracted += 1

        if extracted == 0:
            logging.error("No %s binaries found in downloaded archive.", name)
            print(f"Error: No {name} binaries found in downloaded archive.")
            return False

        logging.info("%s ready at %s", name, dest_dir)
        return True

    except Exception as e:
        logging.error("Failed to download %s: %s", name, e)
        print(f"Error: Failed to download {name}: {e}")
        print(f"Download manually from {manual_url} and place in {dest_dir}")
        return False
    finally:
        tmp_path.unlink(missing_ok=True)


def _progress_cb(count: int, block_size: int, total_size: int) -> None:
    """urllib progress callback - prints inline pct and MB."""
    if total_size > 0:
        pct = min(count * block_size * 100 / total_size, 100)
        downloaded_mb = count * block_size / 1024 / 1024
        total_mb = total_size / 1024 / 1024
        print(
            f"\r  {pct:.0f}%  ({downloaded_mb:.1f} / {total_mb:.0f} MB)",
            end="",
            flush=True,
        )

"""
flac_flow.py - Main entry point for FLAC Flow.

Batch converts FLAC files to MP3 (VBR V0) with optional art/padding scrub.
Config-driven: reads config/config.json on startup.
"""

import argparse
import os
import shutil
import signal
import sys
import time
import logging
from pathlib import Path

# Add src/ to path when invoked as "python src/flac_flow.py"
sys.path.insert(0, str(Path(__file__).parent))

from log import setup_logging
from config import load as load_config
from deps import ensure_deps
from scrub import scrub_file
from transcode import transcode_file

_interrupted = False


def _handle_interrupt(sig, frame):
    global _interrupted
    _interrupted = True
    print("\nInterrupted by user. Finishing current file...")


def _validate_platform() -> None:
    """TIER 0: Reject non-Windows (V1 is Windows-only)."""
    if sys.platform != "win32":
        print("Error: FLAC Flow V1 is Windows-only.")
        print(f"  Detected platform: {sys.platform}")
        sys.exit(1)


def _validate_destination(destination_root: Path) -> None:
    """TIER 0: Check destination is writable and has enough disk space."""
    check_path = destination_root
    while not check_path.exists() and check_path.parent != check_path:
        check_path = check_path.parent

    if not os.access(str(check_path), os.W_OK):
        print(f"Error: Destination is not writable: {check_path}")
        sys.exit(1)

    try:
        usage = shutil.disk_usage(str(check_path))
        pct_free = usage.free / usage.total * 100
        free_gb = usage.free / 1024 ** 3
        if pct_free < 1.0:
            print(
                f"Error: Less than 1% disk space free on destination drive "
                f"({free_gb:.1f} GB, {pct_free:.1f}% free). Aborting."
            )
            sys.exit(1)
        if pct_free < 10.0:
            print(
                f"Warning: Low disk space on destination drive "
                f"({free_gb:.1f} GB free, {pct_free:.1f}%)."
            )
    except Exception:
        pass  # Non-fatal if disk check fails; proceed with the run


def _find_flac_files(source_folder: Path) -> list:
    return sorted(source_folder.rglob("*.flac"))


def _fmt(seconds: float) -> str:
    return f"{seconds:.1f}s"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--no-confirm", action="store_true")
    args, _ = parser.parse_known_args()
    return args


def main() -> None:
    global _interrupted
    _validate_platform()
    args = _parse_args()

    log_file = setup_logging()

    print("######################")
    print("     FLAC Flow")
    print("######################")
    print()

    config = load_config()
    _validate_destination(config.destination_root)

    if config.scrub_art_and_padding and not args.no_confirm:
        import msvcrt
        print("Warning: scrub_art_and_padding is enabled.")
        print("Source FLAC files will be modified in-place.")
        print("Album art and padding will be permanently removed.")
        print("Make sure you have a backup.")
        print()
        print("Press Y to continue or any other key to abort: ", end="", flush=True)
        ch = msvcrt.getwch()
        print()
        if ch.lower() != "y":
            print("Aborted.")
            sys.exit(0)
        print()

    ffmpeg_exe, metaflac_exe = ensure_deps()
    print()

    signal.signal(signal.SIGINT, _handle_interrupt)

    total_files = 0
    error_files = 0
    t_scrub = 0.0
    t_transcode = 0.0
    run_start = time.monotonic()

    folder_count = len(config.source_folders)

    try:
        for fi, source_folder in enumerate(config.source_folders, 1):
            flac_files = _find_flac_files(source_folder)
            print(f"[{fi}/{folder_count} folders] {source_folder.name}  ({len(flac_files)} files)")
            logging.info(
                "Folder %d/%d: %s (%d files)", fi, folder_count, source_folder, len(flac_files)
            )

            file_count = len(flac_files)
            for fj, flac_file in enumerate(flac_files, 1):
                if _interrupted:
                    break

                rel = flac_file.relative_to(source_folder)
                print(f"  [{fj}/{file_count}] {rel}", end="", flush=True)
                file_start = time.monotonic()
                had_error = False

                if config.scrub_art_and_padding:
                    t0 = time.monotonic()
                    ok = scrub_file(flac_file, metaflac_exe)
                    t_scrub += time.monotonic() - t0
                    if not ok:
                        print(" ... SCRUB ERROR")
                        error_files += 1
                        total_files += 1
                        had_error = True

                if not had_error and config.convert_to_mp3:
                    t0 = time.monotonic()
                    ok = transcode_file(flac_file, source_folder, config.destination_root, ffmpeg_exe)
                    t_transcode += time.monotonic() - t0
                    if not ok:
                        print(" ... TRANSCODE ERROR")
                        error_files += 1
                        total_files += 1
                        had_error = True

                if not had_error:
                    elapsed = time.monotonic() - file_start
                    print(f" ... done ({_fmt(elapsed)})")
                    total_files += 1

            if _interrupted:
                break

    except KeyboardInterrupt:
        _interrupted = True
        print("\nInterrupted by user.")

    total_time = time.monotonic() - run_start
    print()

    if _interrupted:
        print("Run interrupted.")

    print(
        f"Done. {folder_count} folder(s), {total_files} file(s) processed. "
        f"Total: {_fmt(total_time)}"
    )

    if t_scrub > 0 or t_transcode > 0:
        print(f"  Scrub: {_fmt(t_scrub)}  |  Transcode: {_fmt(t_transcode)}")

    if error_files:
        print(f"  Errors: {error_files} file(s) failed - see log for details.")

    print(f"  Log: {log_file}")

    logging.info(
        "Run complete: %d files, %d errors, scrub=%.1fs, transcode=%.1fs, total=%.1fs",
        total_files,
        error_files,
        t_scrub,
        t_transcode,
        total_time,
    )

    if _interrupted:
        sys.exit(1)
    elif error_files == 0:
        sys.exit(0)
    elif error_files < total_files:
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

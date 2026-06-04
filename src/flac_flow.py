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
from lockfile import LockFile
from mirror import mirror_path
from scrub import scrub_file
from transcode import transcode_file

_LOCK_PATH = Path(__file__).parent.parent / "data" / "flac_flow.lock"

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


def _parse_since(since_str: str) -> float:
    """Parse YYYY-MM-DD to a Unix timestamp (midnight, local time). Returns None for None input."""
    if not since_str:
        return None
    from datetime import datetime
    return datetime(int(since_str[:4]), int(since_str[5:7]), int(since_str[8:10])).timestamp()


def _filter_by_since(flac_files: list, since_ts: float) -> list:
    """Return only files whose mtime is >= since_ts. Skips unreadable files (no stat)."""
    if since_ts is None:
        return flac_files
    result = []
    for f in flac_files:
        try:
            if f.stat().st_mtime >= since_ts:
                result.append(f)
        except OSError:
            result.append(f)  # include if stat fails - safer to process than silently skip
    return result


def _fmt(seconds: float) -> str:
    return f"{seconds:.1f}s"


def _fmt_size(path: Path) -> str:
    """Return human-readable file size string, or empty string if stat fails."""
    try:
        size = path.stat().st_size
        if size >= 1024 * 1024:
            return f" ({size / 1024 / 1024:.1f} MB)"
        return f" ({size / 1024:.0f} KB)"
    except OSError:
        return ""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--no-confirm", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--config", default=None, metavar="PATH")
    parser.add_argument("--quality", default=None, choices=["V0", "V2", "V4"])
    parser.add_argument("--since", default=None, metavar="YYYY-MM-DD")
    parser.add_argument("--verbose", action="store_true")
    args, _ = parser.parse_known_args()
    return args


def main() -> None:
    global _interrupted
    _validate_platform()
    args = _parse_args()
    dry_run = args.dry_run
    skip_existing = args.skip_existing
    quality = args.quality or "V0"
    since_ts = _parse_since(args.since)
    verbose = args.verbose

    lock = LockFile(_LOCK_PATH)
    if not lock.acquire():
        print("Error: Another FLAC Flow instance is already running.")
        print(f"  If this is incorrect, delete the lockfile: {_LOCK_PATH}")
        sys.exit(1)

    log_file = setup_logging()

    print("######################")
    print("     FLAC Flow")
    print("######################")
    print()

    if dry_run:
        print("[DRY RUN] No files will be modified or created.")
        print()

    config = load_config(Path(args.config)) if args.config else load_config()

    if verbose:
        print(f"[VERBOSE] Source folders: {len(config.source_folders)}")
        for sf in config.source_folders:
            print(f"  {sf}")
        print(f"[VERBOSE] Destination: {config.destination_root}")
        print(f"[VERBOSE] Scrub: {config.scrub_art_and_padding}  Convert: {config.convert_to_mp3}  Quality: {quality}")
        if args.since:
            print(f"[VERBOSE] Since filter: {args.since}")
        print()

    if not dry_run:
        _validate_destination(config.destination_root)

    if config.scrub_art_and_padding and not args.no_confirm and not dry_run:
        import msvcrt
        print("Warning: scrub_art_and_padding is enabled. Source FLAC files will be modified in-place.")
        print("Album art and padding will be permanently removed. Make sure you have a backup.")
        print()
        print("Press Y to continue or any other key to abort: ", end="", flush=True)
        ch = msvcrt.getwch()
        print()
        if ch.lower() != "y":
            print("Aborted.")
            lock.release()
            sys.exit(0)

    ffmpeg_exe, metaflac_exe = ensure_deps()
    print()

    signal.signal(signal.SIGINT, _handle_interrupt)

    total_files = 0
    skipped_files = 0
    error_files = 0
    error_paths: list = []
    t_scrub = 0.0
    t_transcode = 0.0
    run_start = time.monotonic()

    folder_count = len(config.source_folders)

    try:
        for fi, source_folder in enumerate(config.source_folders, 1):
            flac_files = _filter_by_since(_find_flac_files(source_folder), since_ts)
            prefix = "[DRY RUN] " if dry_run else ""
            print(f"{prefix}[{fi}/{folder_count} folders] {source_folder.name}  ({len(flac_files)} files)")
            logging.info(
                "Folder %d/%d: %s (%d files)", fi, folder_count, source_folder, len(flac_files)
            )

            file_count = len(flac_files)
            for fj, flac_file in enumerate(flac_files, 1):
                if _interrupted:
                    break

                rel = flac_file.relative_to(source_folder)

                if dry_run:
                    if config.convert_to_mp3:
                        out = mirror_path(flac_file, source_folder, config.destination_root)
                        print(f"  [{fj}/{file_count}] [DRY RUN] {rel} -> {out}")
                    else:
                        action = "scrub" if config.scrub_art_and_padding else "no-op"
                        print(f"  [{fj}/{file_count}] [DRY RUN] {rel} ({action}, no transcode)")
                    total_files += 1
                    continue

                size_str = _fmt_size(flac_file) if verbose else ""
                print(f"  [{fj}/{file_count}] {rel}{size_str}", end="", flush=True)
                file_start = time.monotonic()
                had_error = False

                if skip_existing and config.convert_to_mp3:
                    output_path = mirror_path(flac_file, source_folder, config.destination_root)
                    if output_path.exists():
                        print(" ... SKIPPED (output exists)")
                        skipped_files += 1
                        continue

                try:
                    flac_file.open("rb").close()
                except OSError as e:
                    logging.error("Cannot read %s: %s", flac_file.name, e)
                    print(" ... READ ERROR")
                    error_files += 1
                    total_files += 1
                    error_paths.append(flac_file)
                    continue

                if config.scrub_art_and_padding:
                    t0 = time.monotonic()
                    ok = scrub_file(flac_file, metaflac_exe)
                    t_scrub += time.monotonic() - t0
                    if not ok:
                        print(" ... SCRUB ERROR")
                        error_files += 1
                        total_files += 1
                        error_paths.append(flac_file)
                        had_error = True

                if not had_error and config.convert_to_mp3:
                    t0 = time.monotonic()
                    ok = transcode_file(flac_file, source_folder, config.destination_root, ffmpeg_exe, quality=quality)
                    t_transcode += time.monotonic() - t0
                    if not ok:
                        print(" ... TRANSCODE ERROR")
                        error_files += 1
                        total_files += 1
                        error_paths.append(flac_file)
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

    if dry_run:
        ops = []
        if config.scrub_art_and_padding:
            ops.append("scrub")
        if config.convert_to_mp3:
            ops.append("transcode")
        ops_str = " + ".join(ops) if ops else "no-op"
        print(
            f"[DRY RUN] {folder_count} folder(s), {total_files} file(s) would be processed "
            f"({ops_str}). No files modified."
        )
    else:
        skip_note = f", {skipped_files} skipped" if skipped_files else ""
        print(
            f"Done. {folder_count} folder(s), {total_files} file(s) processed"
            f"{skip_note}. Total: {_fmt(total_time)}"
        )

    if t_scrub > 0 or t_transcode > 0:
        print(f"Scrub: {_fmt(t_scrub)}  |  Transcode: {_fmt(t_transcode)}")

    if error_paths:
        print(f"Errors: {len(error_paths)} file(s) failed:")
        for p in error_paths:
            print(f"  - {p}")
        print("See log for details.")

    print(f"\nLog: {log_file}")
    print()
    print("Finished!")

    logging.info(
        "Run complete: %d files, %d errors, scrub=%.1fs, transcode=%.1fs, total=%.1fs",
        total_files,
        error_files,
        t_scrub,
        t_transcode,
        total_time,
    )

    lock.release()

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

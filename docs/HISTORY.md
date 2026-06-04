# HISTORY: FLAC_Flow

Completed features and settled design decisions. Active work -> `docs/IDEAS.md`.

---

## 2026-06-05 - TIER 2: Windows Terminal run.bat

Upgraded `scripts/run.bat` to open in Windows Terminal with Git Bash (wt.exe pattern, same as RivalsVidMaker and SBS_Download). Added `scripts/run.sh` - cd to repo root, runs `python src/flac_flow.py`, then `exec bash` to keep the terminal open. Replaces the bare cmd.exe window with a proper Git Bash terminal.

## 2026-06-05 - TIER 2: PID-based lockfile (prevent double-run)

Added `src/lockfile.py` (pattern-copied from SpotifyPlaylistGen). Acquired early in `main()` before config load; released before final exit. Stale lockfiles (PID no longer running) are cleaned up automatically. If lock is held: prints clear error with path to delete, exits 1. 10 new tests (49 total, all passing). Lock file: `data/flac_flow.lock`.

## 2026-06-05 - TIER 2: --skip-existing flag

Added `--skip-existing` flag. When active: checks whether the output MP3 already exists at the mirror path before scrubbing or transcoding. If it does, prints `SKIPPED (output exists)` and increments a separate skipped counter. End-of-run summary appends `, N skipped` to the done line when any files were skipped. Useful for incremental runs that add new FLACs without re-processing the whole library. 7 new tests (39 total, all passing).

## 2026-06-05 - TIER 2: error handling + per-file error summary

Added three error handling improvements:
- **Unreadable FLAC pre-check**: before processing each file, attempts `open('rb')`. If `OSError` (locked, permissions), prints `READ ERROR`, counts as error, continues to next file.
- **Output directory creation failure**: `transcode.py` now catches `OSError` from `mkdir` and returns `False` instead of raising an uncaught exception.
- **Per-file error summary**: end-of-run report now lists each failed file path (`- /path/to/bad.flac`) instead of just a count. Makes diagnosing batch failures easier.
- Also removed "Scrub-in-place startup warning" from IDEAS.md - it was already fully implemented (msvcrt Y/N prompt with `--no-confirm` bypass).
5 new tests (32 total, all passing).

## 2026-06-05 - TIER 2: --dry-run mode

Added `--dry-run` flag to `flac_flow.py`. When active: skips scrub and transcode calls, prints `[DRY RUN]` prefixed output showing each file's mirror path (`track.flac -> Album\track.mp3`), skips destination writability check and scrub confirmation prompt. Config validation and dependency checks still run. Final summary reports how many files would be processed without modifying anything. 8 new tests (27 total, all passing). Useful for verifying folder mirror paths before committing to a real run.

## 2026-06-02 - Thin bat: --no-pause contract added to run.bat

`scripts/run.bat` had an unconditional `cmd /k` at the end, blocking any headless invocation. Added the two-mode contract: no args = `cmd /k` (human), `--no-pause` = `exit /b 0` (Claude/scripted). Standard pattern across the repo family.

## 2026-05-09 - TIER 0 + TIER 1 MVP (complete foundation)

Implemented all TIER 0 blocking checks and TIER 1 MVP modules in one session. The program is now fully runnable.

**TIER 0 (environment validation):**
- Platform check: Windows-only V1, exits with clear message on Linux/Mac
- Destination writability check: finds first existing parent, verifies os.access
- Disk space check: warns if <10% free, aborts if <1% free (shutil.disk_usage)
- Config and source folder existence validated in config.load()

**TIER 1 (MVP modules):**
- `src/config.py` - loads and validates config/config.json; clear per-field error messages; exits on first failure
- `src/log.py` - file-only logging to `data/logs/run_YYYYMMDD_HHMMSS.log`; returns log path for end-of-run display
- `src/deps.py` - auto-downloads ffmpeg and metaflac from GitHub if missing; inline progress pct+MB; pattern-copied from RivalsVidMaker/src/ffmpeg_setup.py
- `src/mirror.py` - leaf folder name reproduced under destination_root; nested subfolders preserved
- `src/scrub.py` - three metaflac commands per file in correct order (PICTURE remove -> PADDING remove -> add-padding=8192); returns bool
- `src/transcode.py` - ffmpeg LAME V0 (-qscale:a 0); calls mirror_path for output path; creates output dirs as needed
- `src/flac_flow.py` - main entry: validates env, loads config, ensures deps, processes all source folders with per-file progress, Ctrl+C handling, timing summary, exit codes (0/1/2)

**Tests:** 19 tests across 4 files; all passing. Covers config validation, mirror path logic, scrub command order, transcode command format.

**Design decisions:**
- File-only logging (no stream handler) keeps progress output clean and uncluttered
- `transcode_file` accepts source_folder for mirror_path computation - keeps mirror logic in one place
- run.bat uses `cmd /k` - window stays open after run so the user can read the summary
- Dependencies gitignored - auto-downloaded fresh on any machine, no binary bloat in repo

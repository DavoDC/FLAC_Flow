# HISTORY: FLAC_Flow

Completed features and settled design decisions. Active work -> `docs/IDEAS.md`.

---

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

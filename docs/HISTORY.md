# HISTORY: FLAC_Flow

Completed features and settled design decisions. Active work -> `docs/IDEAS.md`.

---

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
- run.bat uses `cmd /k` - window stays open after run so Billy can see the summary
- Dependencies gitignored - auto-downloaded fresh on any machine, no binary bloat in repo

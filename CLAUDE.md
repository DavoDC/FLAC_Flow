# FLAC_Flow - Project Instructions

## Project Summary

Python CLI tool that batch-converts FLAC files to MP3 (VBR V0 using LAME) and optionally scrubs album art and padding blocks. Config-driven, folder-mirroring output.

## Language and Runtime

- Python 3.x
- No external Python packages required for MVP (stdlib only: `json`, `subprocess`, `pathlib`, `shutil`, `time`)

## External Tools (auto-downloaded, NOT required on PATH)

- `ffmpeg` - handles LAME V0 encoding. Auto-downloaded to `dependencies/ffmpeg/ffmpeg.exe` on first run.
- `metaflac` - scrubs PICTURE and PADDING blocks. Auto-downloaded to `dependencies/flac/metaflac.exe` on first run.

Both are downloaded by `src/deps.py` at startup if not already present. Always call via full path, never via PATH lookup. Pattern: `RivalsVidMaker/src/ffmpeg_setup.py`.

## Architecture

```
src/
  flac_flow.py      # main entry point
  config.py         # JSON config loader and validator
  scrub.py          # metaflac PICTURE + PADDING removal
  transcode.py      # ffmpeg LAME V0 conversion
  mirror.py         # folder-mirroring path logic
  log.py            # timestamped logging to data/logs/

tests/
  test_config.py
  test_mirror.py
  test_scrub.py
  test_transcode.py

config/
  config.example.json   # template - never commit config.json

data/
  logs/     # run_YYYYMMDD_HHMMSS.log (gitignored)
  output/   # (gitignored - user sets destination_root in config)

dependencies/
  README.md   # install instructions for ffmpeg, metaflac, LAME
```

## Config Format

```json
{
  "source_folders": ["C:\\path\\to\\flac"],
  "destination_root": "C:\\path\\to\\mp3",
  "options": {
    "scrub_art_and_padding": true,
    "convert_to_mp3": true
  }
}
```

Config lives at `config/config.json` (gitignored). Copy from `config.example.json`.

## Key Logic

**Scrub order (must happen first):**
1. `metaflac --remove --block-type=PICTURE --dont-use-padding <file>`
2. `metaflac --remove --block-type=PADDING --dont-use-padding <file>`
3. `metaflac --add-padding=8192 <file>`

**Transcode:**
- `ffmpeg -i <input.flac> -codec:a libmp3lame -qscale:a 0 <output.mp3>`
- Output path mirrors source folder name under `destination_root`

**Folder mirroring:**
- Source: `source_folders[0]/Album/` -> output: `destination_root/Album/`
- The leaf folder name from the source entry is mirrored, not the full path

## Development Rules

- TDD: write tests first for all new modules
- Log all runs to `data/logs/run_YYYYMMDD_HHMMSS.log`
- Include start/end timestamp and per-step timing in logs
- Print progress to stdout during runs
- Dependency check on startup: verify ffmpeg and metaflac are on PATH before processing
- Never hardcode paths - all paths come from config.json
- `config/config.json` must never be committed (gitignored)

## MVP Scope

TIER 1 only for initial release:
- Config loader
- Scrub step (metaflac)
- Transcode step (ffmpeg LAME V0)
- Folder mirroring
- Startup dependency check
- Timing and progress output

GUI (TIER 3) is a future addition - do not add GUI code until CLI is fully tested.

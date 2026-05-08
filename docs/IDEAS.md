# IDEAS: FLAC_Flow

Work organised by explicit safety tiers. Within each tier, items can be done in any order. Do not move to the next tier until current tier is verified on real data.

---

## TIER 0 (BLOCKING)

None currently.

---

## TIER 1 (MVP) - Config-based CLI

---

**Config loader**

Read and validate `config/config.json` on startup. Expected shape:

```json
{
  "source_folders": ["C:\\Music\\FLAC\\Artist"],
  "destination_root": "C:\\Music\\MP3",
  "options": {
    "scrub_art_and_padding": true,
    "convert_to_mp3": true
  }
}
```

Validation rules:
- `source_folders` must be a non-empty list of strings
- Each source folder must exist on disk
- `destination_root` must be a non-empty string (need not exist yet - create it)
- At least one of `scrub_art_and_padding` or `convert_to_mp3` must be true

On failure: print a clear message (missing key, wrong type, folder not found), then exit. Do not process any files.

---

**Auto-download dependencies**

On startup, check if `ffmpeg.exe` and `metaflac.exe` exist in `dependencies/`. If missing, download and extract them automatically - no manual install required.

Pattern to follow: `RivalsVidMaker/src/ffmpeg_setup.py` (already working, pattern-copy it).

Module: `src/deps.py`

**FFmpeg:**
- Check: `dependencies/ffmpeg/ffmpeg.exe` exists
- Download from: `https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip`
- Extract: `ffmpeg.exe`, `ffprobe.exe`, `ffplay.exe` into `dependencies/ffmpeg/`
- Show inline download progress (pct + MB) same as RivalsVidMaker `_progress_cb`

**metaflac:**
- Check: `dependencies/flac/metaflac.exe` exists
- Download from: `https://github.com/xiph/flac/releases/latest/download/flac-win.zip` (contains `metaflac.exe` and `flac.exe`)
- Extract: `metaflac.exe` and `flac.exe` into `dependencies/flac/`

**Fallback:** if either download fails, print the manual download URL and exit cleanly. Do not proceed without both binaries.

**Path strategy:** do NOT rely on system PATH. Always call binaries by their full `dependencies/` path. This means the tool works out of the box on any machine without touching PATH.

---

**Scrub step**

Modifies FLAC files in-place. Must run before transcode (smaller file = faster encode).

Per file, in order:
```
metaflac --remove --block-type=PICTURE --dont-use-padding <file>
metaflac --remove --block-type=PADDING --dont-use-padding <file>
metaflac --add-padding=8192 <file>
```

The `--dont-use-padding` flag forces a full rewrite rather than zero-filling the removed blocks, so the file actually shrinks. The final `--add-padding=8192` leaves a small standard padding block so future tag editors don't have to rewrite the entire file.

If `scrub_art_and_padding` is false in config, skip this step entirely.

---

**Transcode step**

Convert each FLAC to MP3 VBR V0 (highest VBR quality) using LAME via FFmpeg:

```
ffmpeg -i <input.flac> -codec:a libmp3lame -qscale:a 0 <output.mp3>
```

- Output filename: same basename as input, extension changed to `.mp3`
- Output path: determined by folder mirror logic (see below)
- If `convert_to_mp3` is false in config, skip this step entirely

---

**Folder mirror logic**

For each entry in `source_folders`, the leaf folder name is reproduced under `destination_root`.

Example:
```
source_folders: ["C:\\Music\\FLAC\\Artist1\\Album"]
destination_root: "C:\\Music\\MP3"

Input:  C:\Music\FLAC\Artist1\Album\track01.flac
Output: C:\Music\MP3\Album\track01.mp3
```

If source has nested subfolders, mirror the full subtree:
```
Input:  C:\Music\FLAC\Artist1\Album\Disc1\track01.flac
Output: C:\Music\MP3\Album\Disc1\track01.mp3
```

Create output directories as needed before writing. Never delete or overwrite existing output files without the `--skip-existing` flag logic (TIER 2).

---

**Progress output**

Print to stdout during the run. Format:

```
[1/3 folders] Artist1\Album
  [1/12 files] track01.flac ... done (1.2s)
  [2/12 files] track02.flac ... done (1.1s)
  ...
[2/3 folders] Artist2
  ...
Done. 3 folders, 34 files. Total: 42.3s
```

Print a timing summary at the end: total time, scrub time, transcode time.

Pattern to follow: `RivalsVidMaker/src/progress.py` - `AnimatedTicker` class. Animated N/total dots on a background thread via a context manager. Pattern-copy the whole module, it is self-contained and has no dependencies beyond stdlib.

---

**Log to file**

Write a log to `data/logs/run_YYYYMMDD_HHMMSS.log` for every run.

Log contents:
- Start timestamp
- Config loaded (source folders, destination root, options)
- Per-file result: path, scrub result (ok/skipped/error), transcode result (ok/skipped/error), duration
- End timestamp
- Summary: folders processed, files processed, errors, total time

Pattern to follow: `SBS_Download/src/download_sbs.py` `setup_logging()` - dual handler (file + console) via Python `logging` module. Single call at startup wires up both. Pattern-copy the function, no external deps.

---

## TIER 2 (QUALITY)

---

**Error handling**

Handle each failure mode without crashing the whole run:

| Scenario | Behaviour |
|----------|-----------|
| FLAC file is locked / unreadable | Log error for that file, skip it, continue |
| metaflac exits non-zero | Log stderr output, mark file as scrub-failed, still attempt transcode |
| ffmpeg exits non-zero | Log stderr output, mark file as transcode-failed, continue to next |
| Output directory can't be created (permissions) | Log error, skip entire source folder |
| Disk full during transcode | Print warning immediately, abort run (don't leave partial files) |

At end of run, print a summary of any errors and their file paths.

---

**Dry-run mode**

`--dry-run` flag: print what would happen without calling metaflac or ffmpeg or writing any files.

Output format mirrors the normal progress output but prefixed with `[DRY RUN]`. Still validates config and checks dependencies.

Useful for verifying folder mirror paths before a real run.

---

**Skip-existing flag**

`--skip-existing`: if the output MP3 already exists at the destination path, skip that file entirely (no scrub, no transcode).

Log skipped files separately in the summary.

---

**Dataclass config**

Upgrade config from plain dict to a `@dataclass` so fields are typed and IDE-autocomplete works.

Pattern to follow: `RivalsVidMaker/src/config.py` - `@dataclass class Config` + `def load(path) -> Config`. Path fields as `pathlib.Path`, not strings. Validation stays in `load()`.

---

**Lockfile - prevent double-run**

Use a PID-based lockfile to prevent two parallel runs from clobbering the same output files (e.g. run.bat double-clicked).

Pattern to follow: `SpotifyPlaylistGen/src/lockfile.py` - self-contained, stdlib only, handles stale lockfiles (PID no longer running). Pattern-copy wholesale. Lock file goes in `data/flac_flow.lock`.

---

**Windows Terminal run.bat**

Upgrade `scripts/run.bat` to open in Windows Terminal with Git Bash (same as RivalsVidMaker and SBS_Download):

```bat
@echo off
wt.exe -p "Git Bash" -d "%~dp0.." "C:\Program Files\Git\bin\bash.exe" --login -i "%~dp0run.sh"
```

Then add `scripts/run.sh` that calls `python src/flac_flow.py`. Gives a proper terminal vs bare cmd.exe.

---

**Tests**

- `tests/test_config.py` - valid config loads correctly; missing keys raise; non-existent source folder raises; both options false raises
- `tests/test_mirror.py` - flat folder mirrors correctly; nested subfolders mirror correctly; destination path constructed correctly
- `tests/test_scrub.py` - correct metaflac commands built per file; skipped when option is false
- `tests/test_transcode.py` - correct ffmpeg command built per file; output path uses .mp3 extension; skipped when option is false

Use `unittest.mock.patch('subprocess.run')` to avoid needing real ffmpeg/metaflac in tests.

---

## TIER 3 (FUTURE - GUI)

---

**Folder picker GUI**

Replace manual config editing with a GUI. Library choice: **CustomTkinter** (simpler install, pure Python, no Qt dependency).

Main window layout:
- Source folders list with Add / Remove buttons (each opens a Windows folder picker dialog via `tkinter.filedialog.askdirectory`)
- Destination root field with a Browse button
- Checkboxes for `scrub_art_and_padding` and `convert_to_mp3`
- Run button (disabled while a run is in progress)

Config is still saved to/from `config/config.json` so the CLI path keeps working.

---

**GUI progress bar**

During a run, show:
- Overall progress bar (files completed / total files)
- Current file label
- Elapsed time label

Run the conversion in a background thread so the GUI stays responsive.

---

**Per-source toggles**

In the source folders list, each row has its own scrub/convert checkboxes, overriding the global options for that folder only.

---

## TIER 2 (QUALITY) - Additional

---

**Tag preservation**

Copy ID3 tags from source FLAC to output MP3 so the music library stays organized (artist, album, title, track number, etc).

Use `mutagen` library: read FLAC vorbis comments, map to ID3v2 tags, write to MP3. Log any tags that couldn't be preserved.

---

**Concurrent conversion**

Use `concurrent.futures.ThreadPoolExecutor` to process multiple files in parallel. Default: 4 threads (configurable).

Scrubbing stays sequential per file (metaflac is slow), but transcodes can overlap. Speeds up large batches.

---

**Output quality options**

Config option to choose LAME VBR quality: V0 (highest, ~245 kbps), V2 (~190 kbps), V4 (~165 kbps). Useful for different devices or storage constraints.

```json
"options": {
  "mp3_quality": "V0"  // or "V2", "V4"
}
```

CLI flag: `--quality V2` to override config.

---

**File size report**

After each run, print before/after disk usage:
```
Summary:
  Input:  12.5 GB (456 FLAC files)
  Output: 3.2 GB (456 MP3 files at V0)
  Savings: 9.3 GB (74%)
```

Helps Billy understand storage impact.

---

**Filter by date modified**

Only process FLACs modified after a certain date (useful for incremental updates):

```json
"options": {
  "since_date": "2024-01-01"
}
```

CLI flag: `--since 2024-01-01`

---

## TIER 3 (FUTURE - GUI) - Additional

---

**Watch folder mode**

Monitor source folders for new FLACs and auto-convert them on arrival (daemon mode). Useful if Billy adds music to his library frequently.

Runs as a background process, checks every N seconds (configurable, default 30s). Logs conversions to `data/logs/watch_YYYYMMDD.log`.

Start with: `flac_flow --watch config/config.json`

---

**Preset configs**

Save/load named config presets in `config/presets/`:
- "fast" - high bitrate, no scrub
- "archive" - V2 quality, scrub enabled, checksum log
- "portable" - V4 quality, smaller files

GUI has a Preset dropdown to load predefined configs quickly.

---

**Before/after preview**

Dry-run output shows a sample conversion (first file only) with actual timings, so user can estimate total time before running full batch.

```
[DRY RUN - SAMPLE]
File: track01.flac (12.3 MB)
  Scrub: 0.5s
  Transcode: 2.1s
  Output: track01.mp3 (3.8 MB)
Total estimated time for 456 files: ~18 minutes
```

---

## TIER 4 (SOMEDAY)

---

**ID3 tag verification**

After each transcode, read the output MP3 with a Python ID3 library (e.g. `mutagen`) and verify that artist, album, and title tags survived the conversion. Log any missing tags.

---

**Checksum log**

After each run, write a sidecar file `data/logs/run_YYYYMMDD_HHMMSS_checksums.txt` with SHA256 hashes of every converted MP3. Allows verification that files haven't been corrupted.

---

**Resume/checkpoint**

If a run is interrupted (crash, manual stop), store checkpoint file `data/flac_flow.checkpoint` with the last successfully converted file. Next run picks up from there instead of restarting.

Useful for very large libraries (thousands of files) where a single run might take hours.

---

**Conversion database**

Store a JSON database in `data/conversion_log.json` mapping source FLAC path -> output MP3 path + conversion timestamp. Lets user query which FLACs were converted when, useful for auditing or re-runs.

```json
{
  "C:\\Music\\FLAC\\Artist\\Album\\track.flac": {
    "output": "C:\\Music\\MP3\\Album\\track.mp3",
    "converted": "2024-01-15T14:23:45",
    "input_size": 12345678,
    "output_size": 3456789
  }
}
```

---

**Cloud sync integration**

Support syncing output MPs to OneDrive/Dropbox after successful conversion (optional, configurable per source folder).

```json
"source_folders": [
  {
    "path": "C:\\Music\\FLAC\\Artist1",
    "sync_to_cloud": "onedrive"
  }
]
```

---

**Auto-cleanup old outputs**

Option to delete old MP3s if the source FLAC is deleted or moved (keep destination in sync with source).

```json
"options": {
  "cleanup_orphaned_mp3s": true
}
```

Logs deleted files for safety.

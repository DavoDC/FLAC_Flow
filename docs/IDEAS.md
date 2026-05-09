# IDEAS: FLAC_Flow

Work organised by explicit safety tiers. Within each tier, items can be done in any order. Do not move to the next tier until current tier is verified on real data.

TIER 0 and TIER 1 are complete - see HISTORY.md.

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

**Command-line arguments**

Allow overriding config on the command line. Flag format: `--key value`

```
flac-flow --config /path/to/custom_config.json --quality V2 --dry-run
```

Supported flags:
- `--config <path>` - load config from different file (default: `config/config.json`)
- `--quality <V0|V2|V4>` - override MP3 quality for this run
- `--since <YYYY-MM-DD>` - only process FLACs modified after this date
- `--verbose` - print extra debug info
- `--help` - show usage

Flags override config file values.

---

**Filename edge cases**

Handle special cases in FLAC filenames:
- Filenames with spaces, accents, emoji, Unicode - transcode correctly with proper escaping
- Very long filenames (Windows 260-char limit) - truncate output filename if needed, log warning
- Duplicate filenames across source folders - each gets its own output folder, no collision
- Read-only source files - log warning, skip that file
- Symlinks - decide: follow them or skip (recommend follow for music libraries with linked albums)

---

**Statistics summary**

At the end of each run, print stats to console and log:

```
Statistics:
  Folders: 3 processed
  Files: 456 total, 450 succeeded, 6 skipped (read-only), 0 errors
  Input size: 12.5 GB
  Output size: 3.2 GB (74% savings)
  Scrub time: 4m23s
  Transcode time: 18m45s
  Total time: 23m8s
  Avg file time: 3.1s per FLAC
  Throughput: 1.3 files/sec
```

---

**ETA and speed display**

During progress, show estimated time remaining:

```
[2/3 folders] Artist2\Album
  Processing 450 files
  [234/450 files] track123.flac ... 1.2s
  Processed: 52% (234 files)
  Throughput: 1.4 files/sec
  ETA: 2m45s remaining
```

---

**Tests**

- `tests/test_config.py` - valid config loads correctly; missing keys raise; non-existent source folder raises; both options false raises
- `tests/test_mirror.py` - flat folder mirrors correctly; nested subfolders mirror correctly; destination path constructed correctly
- `tests/test_scrub.py` - correct metaflac commands built per file; skipped when option is false
- `tests/test_transcode.py` - correct ffmpeg command built per file; output path uses .mp3 extension; skipped when option is false

Use `unittest.mock.patch('subprocess.run')` to avoid needing real ffmpeg/metaflac in tests.

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

Shows storage impact at a glance.

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

**GUI run history**

Show a list of recent runs (last 10) with:
- Date and time
- Number of files processed
- Success/error count
- Total duration
- Click to view detailed log file

---

**GUI settings panel**

Tab or side panel for global options:
- MP3 quality (V0/V2/V4 radio buttons)
- Concurrent threads slider (1-8)
- Scrub art/padding checkbox
- Convert to MP3 checkbox
- Verbose logging toggle
- Save button (writes to config.json)

---

**Drag and drop folders**

Allow dragging folders from Windows Explorer into the source folders list. Automatically adds them to the list.

---

**Cancel button**

During a run, show a Cancel button. Clicking it gracefully stops processing after current file, logs summary, exits.

---

## TIER 3 (FUTURE - GUI) - Additional

---

**Watch folder mode**

Monitor source folders for new FLACs and auto-convert them on arrival (daemon mode). Useful for libraries that receive frequent additions.

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

---

**Batch re-encode**

Re-convert existing MP3s to a different bitrate. Use cases:
- Create a "high-quality" archive (convert V4 back to V0)
- Create a "portable" version (convert V0 to V4 for storage on phone)
- Test quality differences

Config flag: `"encode_existing_mp3s": true` (default false).

---

**Web UI / remote access**

Instead of GUI, serve a web interface (Flask) running on `localhost:5000`. Access from phone/tablet on same network:
- Same source folder picker
- Same progress display
- Run history, logs

Useful if the music library lives on a NAS or server.

---

**Music library integration**

Query external music databases for tag data:
- MusicBrainz API - look up artist/album and get canonical tags
- Discogs API - get release info, track numbering
- Apply these tags to output MP3s automatically

Tag mapping: FLAC vorbis comments -> ID3v2.4 on output MP3.

---

**Statistics dashboard**

After accumulating many conversions, show insights:
- Total files converted (all time)
- Total storage saved (input vs output)
- Most frequently transcoded artist
- Average transcode time trends (getting faster? slower?)
- Quality distribution (how many V0, V2, V4)

Store in `data/stats.json`, display in GUI or HTML report.

---

**Plugin system**

Allow custom processing steps:
- Pre-scrub: custom metadata cleanup scripts
- Post-transcode: apply custom effects (normalize loudness, add crossfade)
- Custom tag mapping: user-defined FLAC->ID3 rules

Load plugins from `plugins/` folder. Simple interface: JSON config + Python callable.

---

**Scheduled runs**

Set up cron-like scheduled conversions:
- Daily at 2am, convert new FLACs added since last run
- Weekly archive backup to cloud
- Monthly stats report email

Config: 
```json
"scheduled_runs": [
  {"time": "02:00", "days": ["Mon", "Wed", "Fri"], "action": "convert_new"}
]
```

---

**Network/cloud upload**

After successful conversion, upload MP3 to:
- Nextcloud / OwnCloud server
- Plex library (add to Plex immediately after conversion)
- Synology NAS
- SMB network share

Configurable per source folder.

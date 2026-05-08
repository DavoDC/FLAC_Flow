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

**Startup dependency check**

Before touching any files, verify `ffmpeg` and `metaflac` are on PATH.

Check method (Windows): `where ffmpeg` and `where metaflac` via subprocess. Exit code 0 = found.

On failure: print each missing tool by name and a one-line hint pointing to `dependencies/README.md`. Exit cleanly.

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

---

**Log to file**

Write a log to `data/logs/run_YYYYMMDD_HHMMSS.log` for every run.

Log contents:
- Start timestamp
- Config loaded (source folders, destination root, options)
- Per-file result: path, scrub result (ok/skipped/error), transcode result (ok/skipped/error), duration
- End timestamp
- Summary: folders processed, files processed, errors, total time

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

## TIER 4 (SOMEDAY)

---

**ID3 tag verification**

After each transcode, read the output MP3 with a Python ID3 library (e.g. `mutagen`) and verify that artist, album, and title tags survived the conversion. Log any missing tags.

---

**Checksum log**

After each run, write a sidecar file `data/logs/run_YYYYMMDD_HHMMSS_checksums.txt` with SHA256 hashes of every converted MP3. Allows verification that files haven't been corrupted.

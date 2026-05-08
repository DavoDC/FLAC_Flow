# IDEAS: FLAC_Flow

Work organised by explicit safety tiers. Within each tier, items can be done in any order. Do not move to the next tier until current tier is verified on real data.

---

## TIER 0 (BLOCKING)

None currently.

---

## TIER 1 (MVP) - Config-based CLI

- [ ] **Config loader** - read `config/config.json`: validate source_folders list, destination_root, and options flags (scrub, convert). Clear error if file missing or malformed.
- [ ] **Startup dependency check** - verify `ffmpeg` and `metaflac` are on PATH before processing any files. Print missing tool names and exit cleanly.
- [ ] **Scrub step** - per FLAC file: `metaflac --remove --block-type=PICTURE --dont-use-padding`, then `--block-type=PADDING`, then `--add-padding=8192`. Scrub runs BEFORE transcode.
- [ ] **Transcode step** - `ffmpeg -i input.flac -codec:a libmp3lame -qscale:a 0 output.mp3`. V0 VBR quality.
- [ ] **Folder mirror logic** - for each source_folder entry, create an identically-named folder under destination_root and place converted files there.
- [ ] **Progress output** - print current file, folder count, file count. Print timing summary at end (total, per-step).
- [ ] **Log to file** - write each run to `data/logs/run_YYYYMMDD_HHMMSS.log` with timestamps and per-file results.

---

## TIER 2 (QUALITY)

- [ ] **Error handling** - graceful handling of: unreadable FLAC file, metaflac/ffmpeg non-zero exit, missing destination directory permissions, malformed config.
- [ ] **Dry-run mode** - `--dry-run` flag: log what would happen without writing any files or running metaflac/ffmpeg.
- [ ] **Skip-existing flag** - `--skip-existing`: skip transcoding if output MP3 already exists at destination path.
- [ ] **Tests** - `tests/test_config.py`, `tests/test_mirror.py`, `tests/test_scrub.py`, `tests/test_transcode.py`.

---

## TIER 3 (FUTURE - GUI)

- [ ] **Folder picker GUI** - Windows folder selector dialog (CustomTkinter or PyQt) to replace manual config editing.
- [ ] **GUI progress bar** - per-file and overall progress bar during batch run.
- [ ] **Per-source toggles** - toggle scrub-only or convert-only per source folder entry in GUI.

---

## TIER 4 (SOMEDAY)

- [ ] **ID3 tag verification** - after conversion, verify key tags (artist, album, title) are intact in output MP3.
- [ ] **Checksum log** - write SHA256 checksums of converted files to a sidecar log for integrity verification.

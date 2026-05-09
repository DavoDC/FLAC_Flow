# FLAC_Flow

Batch FLAC-to-MP3 converter with folder mirroring and album art scrubbing.

## What it does

- Converts FLAC files to MP3 (Variable Bit Rate, V0 quality using LAME via FFmpeg)
- Mirrors the input folder structure into the output location - each source folder becomes an identically-named output folder
- Optionally scrubs embedded album art and padding from FLAC files before conversion (uses `metaflac`)
- Processes multiple source folders in one run via a config file
- FFmpeg and metaflac are downloaded automatically on first run - no manual install needed

## Requirements

- Python 3.x - https://python.org
- Windows (V1 only)

That's it. FFmpeg and metaflac are downloaded automatically to the `dependencies/` folder on first run.

## Setup

**1. Clone or download the repo**

**2. Copy the example config**

```
config\config.example.json  ->  config\config.json
```

**3. Edit config.json with your paths**

Recommended: open `config\config.json` in **Visual Studio Code**. When you copy a path from Windows Explorer and paste it inside the JSON string quotes, VS Code automatically converts the backslashes to the double-backslash format that JSON requires.

Without VS Code, you need to manually double every backslash:
- Windows path: `C:\Music\FLAC\Artist1`
- JSON value:   `C:\\Music\\FLAC\\Artist1`

**4. Run**

Double-click `scripts\run.bat`, or from a terminal:

```
python src\flac_flow.py
```

On first run it downloads FFmpeg (~120 MB) and metaflac automatically. Subsequent runs start immediately.

## Config reference

```json
{
  "source_folders": [
    "C:\\Music\\FLAC\\Artist1",
    "C:\\Music\\FLAC\\Artist2"
  ],
  "destination_root": "C:\\Music\\MP3",
  "options": {
    "scrub_art_and_padding": true,
    "convert_to_mp3": true
  }
}
```

| Field | Description |
|-------|-------------|
| `source_folders` | List of folders to convert (scanned recursively for .flac files) |
| `destination_root` | Parent folder where mirrored output is created |
| `scrub_art_and_padding` | Remove embedded album art and padding from source FLACs before converting. Modifies source files in-place. |
| `convert_to_mp3` | Transcode each FLAC to MP3 V0 using LAME via FFmpeg |

At least one option must be true.

## Output structure

```
source_folders entry:  C:\Music\FLAC\Artist1\Album
destination_root:      C:\Music\MP3

Output:                C:\Music\MP3\Album\track01.mp3
                       C:\Music\MP3\Album\track02.mp3
```

Each source folder's leaf name is reproduced under `destination_root`. Nested subfolders are preserved.

## Notes

- Scrubbing modifies source FLAC files in-place (removes art and padding blocks, adds a small standard padding block). This is intentional - smaller source files encode faster.
- A log is written to `data\logs\run_YYYYMMDD_HHMMSS.log` for every run.
- Exit codes: `0` = success, `1` = fatal error, `2` = partial failure (some files failed).

## License

MIT

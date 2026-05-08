# FLAC_Flow

Batch FLAC-to-MP3 converter with folder mirroring and album art scrubbing.

## What it does

- Converts FLAC files to MP3 (Variable Bit Rate, V0 quality using LAME via FFmpeg)
- Mirrors the input folder structure into the output location - each source folder becomes an identically-named output folder
- Optionally scrubs embedded album art and padding from FLAC files before conversion (uses `metaflac`)
- Processes multiple source folders in one run via a config file

## Dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.x | Runtime | https://python.org |
| FFmpeg | LAME V0 transcoding | https://ffmpeg.org/download.html |
| FLAC tools | `metaflac.exe` for scrubbing art/padding | https://xiph.org/flac/download.html |

All three must be on your system `PATH`. See `dependencies/README.md` for setup instructions.

## Quick Start

1. Copy `config/config.example.json` to `config/config.json`
2. Edit `config/config.json` with your source folders and destination root
3. Run: `python src/flac_flow.py`

## Config Reference

```json
{
  "source_folders": ["C:\\Music\\FLAC\\Artist1", "C:\\Music\\FLAC\\Artist2"],
  "destination_root": "C:\\Music\\MP3",
  "options": {
    "scrub_art_and_padding": true,
    "convert_to_mp3": true
  }
}
```

- `source_folders` - list of root folders to process (scanned recursively)
- `destination_root` - parent folder where mirrored output folders are created
- `scrub_art_and_padding` - remove PICTURE and PADDING blocks from FLACs before converting
- `convert_to_mp3` - run the FFmpeg LAME V0 transcode step

## Output Structure

Source: `C:\Music\FLAC\Artist1\Album`
Output: `C:\Music\MP3\Album`

Each source folder name is reproduced under `destination_root`. Nested structures are flattened one level per source entry.

## License

MIT

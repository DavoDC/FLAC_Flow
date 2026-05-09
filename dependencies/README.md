# Dependencies

FFmpeg and metaflac are downloaded automatically by FLAC Flow on first run. You do not need to install anything manually.

They are saved to this folder (`dependencies/`) and used directly by the program. No PATH changes required.

---

## Manual install (if auto-download fails)

If the automatic download fails, you can place the files here manually.

### FFmpeg

Download a Windows build from https://ffmpeg.org/download.html (choose "Windows builds from gyan.dev", essentials build).

Extract and copy `ffmpeg.exe`, `ffprobe.exe`, and `ffplay.exe` into `dependencies/ffmpeg/`.

### metaflac

Download the latest Windows release from https://github.com/xiph/flac/releases/latest (the file ending in `-win.zip`).

Extract and copy `metaflac.exe`, `flac.exe`, `libFLAC.dll`, and `libFLAC++.dll` into `dependencies/flac/`.

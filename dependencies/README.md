# Dependencies

FLAC_Flow requires three external tools on your system PATH.

---

## 1. Python 3.x

Download from https://python.org/downloads/

During install, tick "Add Python to PATH". Verify with:
```
python --version
```

---

## 2. FFmpeg (includes LAME encoding support)

1. Download a Windows build from https://ffmpeg.org/download.html (choose "Windows builds from gyan.dev" or "BtbN builds")
2. Extract the zip
3. Add the `bin/` folder inside the extracted directory to your system PATH
4. Verify with: `ffmpeg -version`

FFmpeg includes libmp3lame (LAME encoder) in the standard Windows builds - no separate LAME download needed.

---

## 3. FLAC tools (metaflac)

`metaflac.exe` is the metadata editor used to scrub album art and padding blocks.

1. Download from https://xiph.org/flac/download.html (Windows binary)
2. Extract and place `metaflac.exe` (and `flac.exe`) in a folder on your PATH
3. Verify with: `metaflac --version`

---

## PATH setup on Windows

If you're not sure how to add a folder to PATH:

1. Press Win+R, type `sysdm.cpl`, press Enter
2. Advanced tab -> Environment Variables
3. Under "System variables", find `Path`, click Edit
4. Add the folder containing your executable
5. Click OK, then open a new terminal to test

---

## Verify all tools

Run this in a terminal after setup:
```
python --version
ffmpeg -version
metaflac --version
```

All three should print version info with no errors. FLAC_Flow will also check these on startup.

# FLAC Flow - Setup Guide (Beginner)

This guide covers everything from scratch. No accounts required for any step.

---

## Prerequisites (install once)

### Git

Git is what you use to download FLAC Flow and keep it updated.

Download: https://git-scm.com/download/win

Run the installer. All defaults are fine.

### Python 3

Download: https://www.python.org/downloads/

Run the installer. On the first screen, tick **"Add Python to PATH"** before clicking Install. This is important.

---

## First-time setup

### 1. Choose where to put FLAC Flow

Open File Explorer and navigate to a folder where you want FLAC Flow to live, e.g. `C:\Tools\`.

Right-click in an empty area inside that folder and choose **"Open Git Bash here"**.

A terminal window opens.

### 2. Download FLAC Flow

In the Git Bash window, type exactly:

    git clone https://github.com/DavoDC/FLAC_Flow

Press Enter. This creates a `FLAC_Flow` folder containing everything.

### 3. Set up your config file

Open the `FLAC_Flow` folder in File Explorer. Go into the `config` subfolder.

Copy `config.example.json` and rename the copy to `config.json`.

Open `config.json` in a text editor (Notepad works, or use VS Code if you have it).

Edit the file to match your folders:

- `source_folders` - the folder(s) containing your FLAC files
- `destination_root` - where converted MP3s should go

**Path format:** use double backslashes inside the quotes, e.g:

    "C:\\Music\\FLAC\\MyAlbums"

VS Code makes this easy - paste a Windows path inside the quotes and it automatically doubles the backslashes for you.

**Scrub warning:** if `scrub_art_and_padding` is set to `true`, the program permanently removes album art and padding from your source FLAC files. Make sure you have a backup of your FLACs before using this option. The program will warn you and give you 5 seconds to abort (Ctrl+C) before it starts.

---

## Running the program

Double-click `scripts\run.bat`.

The first run downloads FFmpeg and metaflac automatically (about 120 MB total). This only happens once. After that, runs start straight away.

---

## Getting updates

When there is a new version, double-click `scripts\update.bat`.

That's it. Your `config.json` is never overwritten by updates.

---

## Troubleshooting

**The window closes immediately when I double-click run.bat**
- Python may not be installed, or "Add Python to PATH" was not ticked during install. Reinstall Python and tick that option.

**"No module named..." error**
- Same as above - Python PATH issue.

**Metaflac or FFmpeg download fails**
- Check your internet connection. The downloads are from ffmpeg.org and github.com. If they continue to fail, you can download them manually - see `dependencies\README.md` for instructions.

**Paths not found / config errors**
- Check that your paths in `config.json` use double backslashes and that the folders actually exist.

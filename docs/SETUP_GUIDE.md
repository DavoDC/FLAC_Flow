# FLAC Flow - Setup Guide

No accounts required at any step. Setup takes about 10 minutes and you never have to do it again.

---

## Step 1 - Install Git

Download: [git-scm.com/download/win](https://git-scm.com/download/win)

Run the installer, all defaults are fine.

Git is what lets you download FLAC Flow and get future updates instantly - no re-downloading zip files, no visiting websites. One command and you have the latest version.

---

## Step 2 - Install Python

Download: [python.org/downloads](https://www.python.org/downloads/)

Run the installer. On the first screen, tick **"Add Python to PATH"** before clicking Install.

Python is the language FLAC Flow is written in. Ticking "Add to PATH" means Windows can find it automatically.

---

## Step 3 - Download FLAC Flow

Open File Explorer and go to a folder where you want FLAC Flow to live, e.g. `C:\Tools\`.

Right-click in an empty area and choose **"Open Git Bash here"**. A terminal window opens.

Type this exactly and press Enter:

    git clone https://github.com/DavoDC/FLAC_Flow

This downloads everything into a `FLAC_Flow` folder. You only ever do this once.

---

## Step 4 - Configure your folders

Open the `FLAC_Flow` folder. Go into `config\`. Copy `config.example.json` and rename the copy to `config.json`.

Open `config.json` in a text editor and set your paths:

- `source_folders` - folder(s) containing your FLAC files (scanned recursively)
- `destination_root` - where converted MP3s will be saved

**Path tip:** paths inside JSON need double backslashes. If you have [VS Code](https://code.visualstudio.com/), just paste a Windows path and it fixes them automatically. Without VS Code, double every backslash manually:

    "C:\\Music\\FLAC\\MyAlbums"

**Options:**

| Option | What it does |
|--------|-------------|
| `scrub_art_and_padding` | Permanently removes embedded album art and padding from source FLACs before converting. Saves space. Make sure you have a backup before enabling this - the program warns you and asks you to press Y to confirm before it starts. |
| `convert_to_mp3` | Converts each FLAC to MP3 V0 (highest quality VBR). |

Your `config.json` is never touched by updates, so you only set this up once.

---

## Running the program

Double-click `scripts\run.bat`.

The first run automatically downloads FFmpeg and metaflac (~120 MB total) - no hunting for software, no manual installs. Every run after that starts immediately.

---

## Getting updates

When there is a new version, just double-click `scripts\update.bat` - no need to visit GitHub, re-download anything, or repeat any setup steps.

Git downloads only what changed, so updates are fast. Your config is never touched.

---

## Troubleshooting

**Window closes immediately on double-click**
Python is not installed or "Add Python to PATH" was not ticked. Reinstall Python and make sure to tick that option.

**"No module named..." error**
Same fix - Python PATH issue.

**FFmpeg or metaflac download fails**
Check your internet connection. If it keeps failing, see `dependencies\README.md` for manual install instructions.

**Config errors / paths not found**
Check that paths in `config.json` use double backslashes and that the folders actually exist on your machine.

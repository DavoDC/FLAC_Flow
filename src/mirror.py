from pathlib import Path


def mirror_path(file_path: Path, source_folder: Path, destination_root: Path) -> Path:
    """
    Compute the output MP3 path mirroring the source folder structure.

    The leaf folder name from source_folder is reproduced under destination_root.
    Nested subfolders within source_folder are preserved.

    Example:
        file_path        = C:/Music/FLAC/Artist/Album/Disc1/track01.flac
        source_folder    = C:/Music/FLAC/Artist/Album
        destination_root = C:/Music/MP3
        ->               = C:/Music/MP3/Album/Disc1/track01.mp3
    """
    relative = file_path.relative_to(source_folder)
    return (destination_root / source_folder.name / relative).with_suffix(".mp3")

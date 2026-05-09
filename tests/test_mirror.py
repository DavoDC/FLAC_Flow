from pathlib import Path

from mirror import mirror_path


def test_flat_folder_mirrors_correctly():
    source = Path("C:/Music/FLAC/Album")
    dest_root = Path("C:/Music/MP3")
    file_path = source / "track01.flac"
    result = mirror_path(file_path, source, dest_root)
    assert result == Path("C:/Music/MP3/Album/track01.mp3")


def test_nested_subfolder_mirrors_correctly():
    source = Path("C:/Music/FLAC/Album")
    dest_root = Path("C:/Music/MP3")
    file_path = source / "Disc1" / "track01.flac"
    result = mirror_path(file_path, source, dest_root)
    assert result == Path("C:/Music/MP3/Album/Disc1/track01.mp3")


def test_destination_path_constructed_correctly():
    source = Path("/music/flac/Artist/Album")
    dest_root = Path("/music/mp3")
    file_path = source / "track.flac"
    result = mirror_path(file_path, source, dest_root)
    assert result.suffix == ".mp3"
    assert result.parent == dest_root / "Album"


def test_leaf_folder_name_used_not_full_path():
    source = Path("C:/Deep/Nested/Path/Album")
    dest_root = Path("C:/Output")
    file_path = source / "track.flac"
    result = mirror_path(file_path, source, dest_root)
    assert result == Path("C:/Output/Album/track.mp3")

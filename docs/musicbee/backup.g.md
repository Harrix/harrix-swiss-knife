---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `backup.py`

## 🔧 Function `create_musicbee_backup`

```python
def create_musicbee_backup(library_dir: Path, backup_root: Path) -> Path
```

Copy playlists and the library file into a timestamped backup folder.

<details>
<summary>Code:</summary>

```python
def create_musicbee_backup(library_dir: Path, backup_root: Path) -> Path:
    stamp = datetime.now(UTC).astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    destination = backup_root / "MusicBee" / stamp
    destination.mkdir(parents=True, exist_ok=True)
    playlists_dir = library_dir / "Playlists"
    if playlists_dir.is_dir():
        shutil.copytree(playlists_dir, destination / "Playlists", dirs_exist_ok=True)
    for name in ("MusicBeeLibrary.mbl", "MusicBeeLibrary.bak", "MusicBeeLibrary.pfidx"):
        source = library_dir / name
        if source.is_file():
            shutil.copy2(source, destination / name)
    _export_m3u8(playlists_dir, destination / "exported")
    return destination
```

</details>

---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `process.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CheckPlan`](#%EF%B8%8F-class-checkplan)
  - [⚙️ Method `has_writes (property)`](#%EF%B8%8F-method-has_writes-property)
- [🏛️ Class `PlaylistChange`](#%EF%B8%8F-class-playlistchange)
  - [⚙️ Method `changed (property)`](#%EF%B8%8F-method-changed-property)
- [🔧 Function `apply_plan`](#-function-apply_plan)
- [🔧 Function `format_check_report`](#-function-format_check_report)
- [🔧 Function `is_musicbee_running`](#-function-is_musicbee_running)
- [🔧 Function `run_check`](#-function-run_check)

</details>

## 🏛️ Class `CheckPlan`

```python
class CheckPlan
```

In-memory result of a MusicBee check, ready to report or apply.

<details>
<summary>Code:</summary>

```python
class CheckPlan:

    settings: MusicBeeSettings
    backup_path: Path
    remaps: list[PathMatch] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    ambiguous: list[PathMatch] = field(default_factory=list)
    playlists: list[PlaylistChange] = field(default_factory=list)
    warnings: list[RuleWarning] = field(default_factory=list)
    library: MblLibrary | None = None
    library_changed: bool = False
    parsed_playlists: dict[str, MbpPlaylist] = field(default_factory=dict)
    unreadable_playlists: list[str] = field(default_factory=list)

    @property
    def has_writes(self) -> bool:
        """Whether Apply would write the library or any static playlist."""
        return self.library_changed or any(item.changed for item in self.playlists)
```

</details>

### ⚙️ Method `has_writes (property)`

```python
def has_writes(self) -> bool
```

Whether Apply would write the library or any static playlist.

<details>
<summary>Code:</summary>

```python
def has_writes(self) -> bool:
        return self.library_changed or any(item.changed for item in self.playlists)
```

</details>

## 🏛️ Class `PlaylistChange`

```python
class PlaylistChange
```

One static playlist that may be rewritten.

<details>
<summary>Code:</summary>

```python
class PlaylistChange:

    name: str
    path: Path
    original_tracks: list[str]
    new_tracks: list[str]

    @property
    def changed(self) -> bool:
        """Whether the track list differs after remaps and rules."""
        return [normalize_path_key(item) for item in self.original_tracks] != [
            normalize_path_key(item) for item in self.new_tracks
        ]
```

</details>

### ⚙️ Method `changed (property)`

```python
def changed(self) -> bool
```

Whether the track list differs after remaps and rules.

<details>
<summary>Code:</summary>

```python
def changed(self) -> bool:
        return [normalize_path_key(item) for item in self.original_tracks] != [
            normalize_path_key(item) for item in self.new_tracks
        ]
```

</details>

## 🔧 Function `apply_plan`

```python
def apply_plan(plan: CheckPlan) -> list[Path]
```

Write changed `.mbl` / `.mbp` files. Raises if MusicBee is running.

<details>
<summary>Code:</summary>

```python
def apply_plan(plan: CheckPlan) -> list[Path]:
    if is_musicbee_running():
        msg = "Close MusicBee before applying playlist or library changes"
        raise OSError(msg)
    written: list[Path] = []
    if plan.library is not None and plan.library_changed:
        write_bytes = write_mbl(plan.library)
        plan.library.path.write_bytes(write_bytes)
        written.append(plan.library.path)
        pfidx = plan.library.path.with_suffix(".pfidx")
        if pfidx.is_file():
            pfidx.unlink()
            written.append(pfidx)
    for change in plan.playlists:
        if not change.changed:
            continue
        parsed = plan.parsed_playlists[change.name]
        change.path.write_bytes(write_mbp(parsed, change.new_tracks))
        written.append(change.path)
    return written
```

</details>

## 🔧 Function `format_check_report`

```python
def format_check_report(plan: CheckPlan) -> str
```

Build the preview text shown before Apply.

<details>
<summary>Code:</summary>

```python
def format_check_report(plan: CheckPlan) -> str:
    lines = [
        f"Backup: {plan.backup_path}",
        f"Library: {plan.settings.library_dir}",
        f"Music: {plan.settings.music_root}",
        f"Stream: {plan.settings.stream_root}",
        "",
    ]
    if is_musicbee_running():
        lines.append("MusicBee is running. Close it before clicking Apply.")
        lines.append("")
    lines.append(f"Remapped paths: {len(plan.remaps)}")
    for item in plan.remaps:
        lines.append(f"  {item.original}")
        lines.append(f"    → {item.resolved}")
    lines.append("")
    lines.append(f"Missing (not remapped): {len(plan.missing)}")
    lines.extend(f"  {path}" for path in plan.missing)
    lines.append("")
    lines.append(f"Ambiguous (not remapped): {len(plan.ambiguous)}")
    for item in plan.ambiguous:
        lines.append(f"  {item.original}")
        lines.extend(f"    ? {candidate}" for candidate in item.candidates)
    if plan.unreadable_playlists:
        lines.append("")
        lines.append("Unreadable static playlists:")
        lines.extend(f"  {name}" for name in plan.unreadable_playlists)
    lines.append("")
    changed = [item for item in plan.playlists if item.changed]
    lines.append(f"Playlists to rewrite: {len(changed)}")
    lines.extend(f"  {item.name}: {len(item.original_tracks)} → {len(item.new_tracks)} tracks" for item in changed)
    if plan.library_changed:
        lines.append("Library file: path remaps will be written (play counts kept).")
    if plan.warnings:
        lines.append("")
        lines.append("Rule notes:")
        lines.extend(f"  {warning.message}" for warning in plan.warnings)
    if not plan.has_writes:
        lines.append("")
        lines.append("Nothing to apply.")
    else:
        lines.append("")
        lines.append("Click Apply to write the library and static playlists.")
        lines.append("Cancel closes without writing.")
        lines.append("Smart playlists (.xautopf) are not edited.")
        lines.append("Files under the music folder are not changed.")
    return "\n".join(lines)
```

</details>

## 🔧 Function `is_musicbee_running`

```python
def is_musicbee_running() -> bool
```

Return whether `MusicBee.exe` is running on Windows.

<details>
<summary>Code:</summary>

```python
def is_musicbee_running() -> bool:
    if sys.platform != "win32":
        return False
    tasklist = shutil.which("tasklist")
    if not tasklist:
        return False
    result = subprocess.run(
        [tasklist, "/FI", f"IMAGENAME eq {_MUSICBEE_PROCESS}", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    return "musicbee.exe" in (result.stdout or "").casefold()
```

</details>

## 🔧 Function `run_check`

```python
def run_check(settings: MusicBeeSettings, *, create_backup: bool = True) -> CheckPlan
```

Backup, index files, remap missing paths, and apply Stream rules in memory.

<details>
<summary>Code:</summary>

```python
def run_check(settings: MusicBeeSettings, *, create_backup: bool = True) -> CheckPlan:
    backup_path = (
        create_musicbee_backup(settings.library_dir, settings.backup_dir)
        if create_backup
        else settings.backup_dir / "MusicBee" / "preview"
    )
    index = index_audio_files(settings.music_root, settings.audio_extensions)
    playlists, unreadable = _load_static_playlists(settings.playlists_dir)
    library = _load_library(settings.library_file)
    matches = _collect_matches(library, playlists, index)
    remaps = [item for item in matches if item.status == "remap" and item.resolved]
    remap_map = {normalize_path_key(item.original): item.resolved for item in remaps if item.resolved}
    library_changed = _apply_library_remaps(library, remap_map)
    working = {name: _remap_tracks(playlist.tracks, remap_map) for name, playlist in playlists.items()}
    warnings = apply_rules(
        working,
        settings.rules,
        placeholders=settings.placeholders,
        file_index=index,
    )
    changes = [
        PlaylistChange(
            name=name,
            path=playlists[name].path,
            original_tracks=list(playlists[name].tracks),
            new_tracks=working[name],
        )
        for name in playlists
    ]
    return CheckPlan(
        settings=settings,
        backup_path=backup_path,
        remaps=remaps,
        missing=sorted({item.original for item in matches if item.status == "missing"}),
        ambiguous=[item for item in matches if item.status == "ambiguous"],
        playlists=changes,
        warnings=warnings,
        library=library,
        library_changed=library_changed,
        parsed_playlists=playlists,
        unreadable_playlists=unreadable,
    )
```

</details>

---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `beat_saber_backup_root`](#-function-beat_saber_backup_root)
- [🔧 Function `default_export_zip_path`](#-function-default_export_zip_path)
- [🔧 Function `pc_saves_dir`](#-function-pc_saves_dir)
- [🔧 Function `quest_remote_files_dir`](#-function-quest_remote_files_dir)

</details>

## 🔧 Function `beat_saber_backup_root`

```python
def beat_saber_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path
```

Return `{path_backups}/BeatSaber`, creating it when missing.

<details>
<summary>Code:</summary>

```python
def beat_saber_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    return _beat_saber_backup_root(config, config_path=config_path)
```

</details>

## 🔧 Function `default_export_zip_path`

```python
def default_export_zip_path(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path
```

Return a timestamped ZIP path under the Beat Saber backup root.

<details>
<summary>Code:</summary>

```python
def default_export_zip_path(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    stamp = datetime.now(UTC).astimezone().strftime("%Y%m%d-%H%M%S")
    return beat_saber_backup_root(config, config_path=config_path) / f"beat-saber-{stamp}.zip"
```

</details>

## 🔧 Function `pc_saves_dir`

```python
def pc_saves_dir() -> Path
```

Return ``%USERPROFILE%\AppData\LocalLow\Hyperbolic Magnetism\Beat Saber``.

<details>
<summary>Code:</summary>

```python
def pc_saves_dir() -> Path:
    return Path.home() / "AppData" / "LocalLow" / "Hyperbolic Magnetism" / "Beat Saber"
```

</details>

## 🔧 Function `quest_remote_files_dir`

```python
def quest_remote_files_dir() -> str
```

Return the Quest remote path for Beat Saber ``files`` (sdcard style).

<details>
<summary>Code:</summary>

```python
def quest_remote_files_dir() -> str:
    return f"/sdcard/{_QUEST_FILES_REL}"
```

</details>

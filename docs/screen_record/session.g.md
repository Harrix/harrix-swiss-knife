---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `session.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `record_region`](#-function-record_region)
- [🔧 Function `videos_folder`](#-function-videos_folder)

</details>

## 🔧 Function `record_region`

```python
def record_region(*, on_finished: Callable[[Path], None] | None = None) -> bool
```

Start the ShareX-like region screen recording flow.

Returns `False` when selection was cancelled or ffmpeg is missing.
When recording finishes successfully, `on_finished` receives the MP4 path.

<details>
<summary>Code:</summary>

```python
def record_region(*, on_finished: Callable[[Path], None] | None = None) -> bool:
    existing = _session_holder["session"]
    if existing is not None and existing.is_active:
        QMessageBox.information(None, "Screen record", "A recording session is already open.")
        return False

    root = get_project_root()
    if not is_ffmpeg_available(root):
        QMessageBox.warning(
            None,
            "Screen record",
            "ffmpeg.exe was not found in the project root.\nUse Development → Download optimize dependencies.",
        )
        return False

    rect = select_region(show_shutter_button=True)
    if rect is None or rect.isEmpty():
        return False

    session = _RecordSession(rect, on_finished=on_finished)
    _session_holder["session"] = session
    session.show()
    return True
```

</details>

## 🔧 Function `videos_folder`

```python
def videos_folder(project_root: Path) -> Path
```

Return `temp/videos` under `project_root`.

<details>
<summary>Code:</summary>

```python
def videos_folder(project_root: Path) -> Path:
    return project_root / "temp" / "videos"
```

</details>

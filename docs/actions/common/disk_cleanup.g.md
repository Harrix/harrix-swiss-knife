---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `disk_cleanup.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CleanupRunResult`](#%EF%B8%8F-class-cleanuprunresult)
- [🏛️ Class `CleanupTarget`](#%EF%B8%8F-class-cleanuptarget)
  - [⚙️ Method `choice_label`](#%EF%B8%8F-method-choice_label)
- [🔧 Function `discover_targets`](#-function-discover_targets)
- [🔧 Function `folder_size`](#-function-folder_size)
- [🔧 Function `format_cleanup_choice_sizes`](#-function-format_cleanup_choice_sizes)
- [🔧 Function `paths_size`](#-function-paths_size)
- [🔧 Function `run_cleanup`](#-function-run_cleanup)

</details>

## 🏛️ Class `CleanupRunResult`

```python
class CleanupRunResult
```

Outcome of cleaning selected targets.

<details>
<summary>Code:</summary>

```python
class CleanupRunResult:

    expected_bytes: int
    lines: tuple[str, ...]
    errors: tuple[str, ...]
```

</details>

## 🏛️ Class `CleanupTarget`

```python
class CleanupTarget
```

One reclaimable location offered in the cleanup dialog.

<details>
<summary>Code:</summary>

```python
class CleanupTarget:

    id: str
    title: str
    path_display: str
    size_bytes: int
    default_selected: bool
    cleaner: Callable[[], list[str]]

    def choice_label(self) -> str:
        """Return checkbox label with size, title, and path."""
        size = h.file.format_byte_size(self.size_bytes)
        return f"[{size}] {self.title} — {self.path_display}"
```

</details>

### ⚙️ Method `choice_label`

```python
def choice_label(self) -> str
```

Return checkbox label with size, title, and path.

<details>
<summary>Code:</summary>

```python
def choice_label(self) -> str:
        size = h.file.format_byte_size(self.size_bytes)
        return f"[{size}] {self.title} — {self.path_display}"
```

</details>

## 🔧 Function `discover_targets`

```python
def discover_targets(*, on_progress: ProgressCallback | None = None, on_found: Callable[[CleanupTarget], None] | None = None) -> list[CleanupTarget]
```

Scan known cleanup locations; return only those with size greater than zero.

Args:

- `on_progress` (`ProgressCallback | None`): Called with a log line before each measure.
- `on_found` (`Callable[[CleanupTarget], None] | None`): Called when a non-empty
  target is discovered (for live totals while scanning).

<details>
<summary>Code:</summary>

```python
def discover_targets(
    *,
    on_progress: ProgressCallback | None = None,
    on_found: Callable[[CleanupTarget], None] | None = None,
) -> list[CleanupTarget]:
    specs = _candidate_specs()
    found: list[CleanupTarget] = []
    for spec in specs:
        if on_progress is not None:
            on_progress(f"🔵 Measuring: {spec.title}")
        size = spec.size_fn()
        if size <= 0:
            continue
        target = CleanupTarget(
            id=spec.id,
            title=spec.title,
            path_display=spec.path_display,
            size_bytes=size,
            default_selected=spec.default_selected,
            cleaner=spec.cleaner,
        )
        found.append(target)
        if on_found is not None:
            on_found(target)
    return found
```

</details>

## 🔧 Function `folder_size`

```python
def folder_size(path: Path) -> int
```

Return total size of `path` (file or directory); skip inaccessible entries.

<details>
<summary>Code:</summary>

```python
def folder_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        with contextlib.suppress(OSError):
            return path.stat().st_size
        return 0

    total = 0
    for root, _dirs, files in os.walk(path, onerror=lambda _exc: None):
        for name in files:
            file_path = Path(root) / name
            with contextlib.suppress(OSError):
                total += file_path.stat().st_size
    return total
```

</details>

## 🔧 Function `format_cleanup_choice_sizes`

```python
def format_cleanup_choice_sizes(targets: list[CleanupTarget]) -> dict[str, int]
```

Map checkbox labels to byte sizes for the selection dialog footer.

<details>
<summary>Code:</summary>

```python
def format_cleanup_choice_sizes(targets: list[CleanupTarget]) -> dict[str, int]:
    return {target.choice_label(): target.size_bytes for target in targets}
```

</details>

## 🔧 Function `paths_size`

```python
def paths_size(paths: list[Path]) -> int
```

Sum sizes of existing paths (files or folders).

<details>
<summary>Code:</summary>

```python
def paths_size(paths: list[Path]) -> int:
    return sum(folder_size(path) for path in paths)
```

</details>

## 🔧 Function `run_cleanup`

```python
def run_cleanup(targets: list[CleanupTarget], *, on_progress: ProgressCallback | None = None) -> CleanupRunResult
```

Run cleaners for selected targets; collect log lines and errors.

<details>
<summary>Code:</summary>

```python
def run_cleanup(targets: list[CleanupTarget], *, on_progress: ProgressCallback | None = None) -> CleanupRunResult:
    lines: list[str] = []
    errors: list[str] = []
    expected = sum(target.size_bytes for target in targets)

    for target in targets:
        if on_progress is not None:
            on_progress(f"🔵 Cleaning: {target.title}")
        lines.append(f"Cleaning `{target.title}` ({h.file.format_byte_size(target.size_bytes)})…")
        try:
            cleaner_lines = target.cleaner()
            lines.extend(cleaner_lines)
            lines.append(f"✅ Cleaned `{target.title}`.")
        except OSError as exc:
            message = f"❌ Failed `{target.title}`: {exc}"
            lines.append(message)
            errors.append(message)

    return CleanupRunResult(expected_bytes=expected, lines=tuple(lines), errors=tuple(errors))
```

</details>

---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `repo_maintenance.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RepoMaintenanceWorker`](#%EF%B8%8F-class-repomaintenanceworker)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `run`](#%EF%B8%8F-method-run)
- [🔧 Function `beautify_and_optimize_icons`](#-function-beautify_and_optimize_icons)
- [🔧 Function `check_icon_repo`](#-function-check_icon_repo)
- [🔧 Function `is_family_prefixed_filename`](#-function-is_family_prefixed_filename)

</details>

## 🏛️ Class `RepoMaintenanceWorker`

```python
class RepoMaintenanceWorker(QObject)
```

Run icon-repo maintenance outside the GUI thread.

<details>
<summary>Code:</summary>

```python
class RepoMaintenanceWorker(QObject):

    progress = Signal(int, int, str)
    succeeded = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, repo_root: Path, kind: MaintenanceKind) -> None:
        """Store the repository path and the job kind."""
        super().__init__()
        self._repo_root = Path(repo_root)
        self._kind = kind

    @Slot()
    def run(self) -> None:
        """Execute the selected maintenance job."""
        try:
            if self._kind == "check":
                text = check_icon_repo(self._repo_root, on_progress=self._emit_progress)
            else:
                text = beautify_and_optimize_icons(self._repo_root, on_progress=self._emit_progress)
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            self.failed.emit(str(exc))
        else:
            self.succeeded.emit(text)
        finally:
            self.finished.emit()

    def _emit_progress(self, done: int, total: int, message: str) -> None:
        self.progress.emit(done, total, message)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, repo_root: Path, kind: MaintenanceKind) -> None
```

Store the repository path and the job kind.

<details>
<summary>Code:</summary>

```python
def __init__(self, repo_root: Path, kind: MaintenanceKind) -> None:
        super().__init__()
        self._repo_root = Path(repo_root)
        self._kind = kind
```

</details>

### ⚙️ Method `run`

```python
def run(self) -> None
```

Execute the selected maintenance job.

<details>
<summary>Code:</summary>

```python
def run(self) -> None:
        try:
            if self._kind == "check":
                text = check_icon_repo(self._repo_root, on_progress=self._emit_progress)
            else:
                text = beautify_and_optimize_icons(self._repo_root, on_progress=self._emit_progress)
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            self.failed.emit(str(exc))
        else:
            self.succeeded.emit(text)
        finally:
            self.finished.emit()
```

</details>

## 🔧 Function `beautify_and_optimize_icons`

```python
def beautify_and_optimize_icons(repo_root: Path, *, on_progress: ProgressCallback | None = None) -> str
```

Beautify Markdown notes under `icons/` and optimize SVG files in place.

<details>
<summary>Code:</summary>

```python
def beautify_and_optimize_icons(
    repo_root: Path,
    *,
    on_progress: ProgressCallback | None = None,
) -> str:
    icons_dir = _require_icons_dir(repo_root)
    lines: list[str] = ["🔵 Beautify Markdown"]
    beautify = OnBeautifyMd()
    beautify.beautify_markdown_common(
        str(icons_dir),
        is_include_summaries_and_combine=False,
        delete_generated_g_md=True,
    )
    lines.extend(beautify.result_lines)

    svgs = _iter_icon_svgs(icons_dir)
    total = max(1, len(svgs) + 1)
    _notify(on_progress, 1, total, "Optimizing SVG files…")
    lines.append("")
    lines.append("🔵 Optimize SVG files")
    stats = OptimizeSizeStats()
    errors: list[str] = []
    optimizer = h.svg_opt.SvgOptimizer()
    for index, svg in enumerate(svgs, start=1):
        _notify(on_progress, index + 1, total, f"Optimizing {svg.name}…")
        before = svg.stat().st_size
        try:
            optimizer.optimize_file(svg)
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"❌ {svg}: {exc}")
            continue
        stats.add(before, svg.stat().st_size)
    if svgs:
        lines.append(f"✅ Optimized {stats.count} SVG file(s).")
        lines.append(stats.format_summary())
    else:
        lines.append("🔵 No SVG files found.")
    lines.extend(errors)
    return "\n".join(lines).strip() + "\n"
```

</details>

## 🔧 Function `check_icon_repo`

```python
def check_icon_repo(repo_root: Path, *, on_progress: ProgressCallback | None = None) -> str
```

Check note filenames, category folders, and Markdown rules.

<details>
<summary>Code:</summary>

```python
def check_icon_repo(
    repo_root: Path,
    *,
    on_progress: ProgressCallback | None = None,
) -> str:
    icons_dir = _require_icons_dir(repo_root)
    note_dirs = iter_icon_note_dirs(icons_dir)
    structure_issues = _collect_top_level_issues(icons_dir)
    total = max(1, len(note_dirs) + 1)
    for done, note_dir in enumerate(note_dirs, start=1):
        _notify(on_progress, done, total, f"Checking {note_dir.name}…")
        structure_issues.extend(_check_note_dir(note_dir, icons_dir))

    _notify(on_progress, total, total, "Checking Markdown…")
    md_lines = _check_markdown_notes(icons_dir)
    lines = [
        "🔵 Check images",
        f"Notes: {len(note_dirs)}",
        "",
        "📁 Filenames, folders, and categories",
    ]
    if structure_issues:
        lines.extend(f"- {item}" for item in structure_issues)
        lines.append(f"🔢 Structure issues = {len(structure_issues)}")
    else:
        lines.append("✅ Filenames, folders, and categories match.")
    lines.append("")
    lines.append("🚧 Markdown check")
    lines.extend(md_lines)
    return "\n".join(lines).strip() + "\n"
```

</details>

## 🔧 Function `is_family_prefixed_filename`

```python
def is_family_prefixed_filename(name: str, family_id: str) -> bool
```

Return whether `name` is the family note or a `{family_id}_…` variant.

<details>
<summary>Code:</summary>

```python
def is_family_prefixed_filename(name: str, family_id: str) -> bool:
    stem = Path(name).stem
    return stem == family_id or stem.startswith(f"{family_id}_")
```

</details>

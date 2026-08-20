---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `uninstall.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `UninstallOptions`](#%EF%B8%8F-class-uninstalloptions)
- [🏛️ Class `UninstallResult`](#%EF%B8%8F-class-uninstallresult)
- [🔧 Function `default_preserve_dir`](#-function-default_preserve_dir)
- [🔧 Function `detect_hsk_path`](#-function-detect_hsk_path)
- [🔧 Function `list_paths_to_preserve`](#-function-list_paths_to_preserve)
- [🔧 Function `preserve_user_data`](#-function-preserve_user_data)
- [🔧 Function `run_uninstall`](#-function-run_uninstall)

</details>

## 🏛️ Class `UninstallOptions`

```python
class UninstallOptions
```

User choices for an uninstall run.

<details>
<summary>Code:</summary>

```python
class UninstallOptions:

    hsk_path: Path
    remove_sibling_repos: bool = True
```

</details>

## 🏛️ Class `UninstallResult`

```python
class UninstallResult
```

Outcome of [`run_uninstall`](#-function-run_uninstall).

<details>
<summary>Code:</summary>

```python
class UninstallResult:

    ok: bool
    hsk_path: Path | None
    preserved_dir: Path | None
    outcomes: OutcomeLog
    error: str | None = None
    elapsed_seconds: float = 0.0
    preserved_items: list[str] = field(default_factory=list)
```

</details>

## 🔧 Function `default_preserve_dir`

```python
def default_preserve_dir(hsk_path: Path) -> Path
```

Return the folder where databases and secrets are moved before deletion.

<details>
<summary>Code:</summary>

```python
def default_preserve_dir(hsk_path: Path) -> Path:
    parent = hsk_path.parent
    docs = Path.home() / "Documents" / _PRESERVE_DIR_NAME
    try:
        parent.mkdir(parents=True, exist_ok=True)
        probe = parent / ".hsk-uninstall-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError:
        return docs
    return parent / _PRESERVE_DIR_NAME
```

</details>

## 🔧 Function `detect_hsk_path`

```python
def detect_hsk_path(hint: Path | None = None) -> Path | None
```

Locate an installed `harrix-swiss-knife` checkout.

<details>
<summary>Code:</summary>

```python
def detect_hsk_path(hint: Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if hint is not None:
        candidates.append(hint)
    here = Path(__file__).resolve()
    # installer -> harrix_swiss_knife -> src -> repo root
    if len(here.parents) >= _REPO_ROOT_PARENT_DEPTH:
        candidates.append(here.parents[3])
    cwd = Path.cwd()
    candidates.extend((cwd, cwd / HSK_REPO_NAME, cwd.parent / HSK_REPO_NAME))
    for root in candidates:
        if _looks_like_hsk(root):
            return root.resolve()
    return None
```

</details>

## 🔧 Function `list_paths_to_preserve`

```python
def list_paths_to_preserve(hsk_path: Path) -> list[Path]
```

Return files/dirs under `hsk_path` that must survive uninstall.

<details>
<summary>Code:</summary>

```python
def list_paths_to_preserve(hsk_path: Path) -> list[Path]:
    root = hsk_path.resolve()
    found: list[Path] = []
    seen: set[str] = set()

    def _add(path: Path) -> None:
        try:
            resolved = path.resolve()
        except OSError:
            return
        key = str(resolved).lower()
        if key in seen:
            return
        if not resolved.exists():
            return
        try:
            resolved.relative_to(root)
        except ValueError:
            # Outside the project tree — leave in place, do not move.
            return
        seen.add(key)
        found.append(resolved)

    config_path = root / "config" / "config.json"
    data = _read_config(config_path)
    for key in _DB_CONFIG_KEYS:
        raw = data.get(key) if data else None
        if isinstance(raw, str) and raw.strip():
            _add(Path(raw))
            if key == "sqlite_fitness":
                _add(Path(raw).parent / "fitness_img")

    db_dir = root / "data" / "databases"
    if db_dir.is_dir():
        for path in db_dir.iterdir():
            if path.is_file() and path.suffix.lower() == _SQLITE_SUFFIX:
                _add(path)
        fitness_img = db_dir / "fitness_img"
        _add(fitness_img)

    _add(root / "api-keys")
    if config_path.is_file():
        _add(config_path)
    return found
```

</details>

## 🔧 Function `preserve_user_data`

```python
def preserve_user_data(hsk_path: Path, dest: Path, log: OutcomeLog) -> list[str]
```

Move databases, API keys, and fitness images out of the project tree.

<details>
<summary>Code:</summary>

```python
def preserve_user_data(hsk_path: Path, dest: Path, log: OutcomeLog) -> list[str]:
    items = list_paths_to_preserve(hsk_path)
    if not items:
        log.add("already", "No databases or api-keys found under the project to preserve")
        return []
    dest.mkdir(parents=True, exist_ok=True)
    preserved: list[str] = []
    root = hsk_path.resolve()
    for src in items:
        rel = src.relative_to(root)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            stamp = time.strftime("%Y%m%d-%H%M%S")
            target = target.with_name(f"{target.stem}-kept-{stamp}{target.suffix}")
        log.detail(f"Preserving {rel} -> {target}")
        shutil.move(str(src), str(target))
        preserved.append(str(target))
    readme = dest / "README.txt"
    readme.write_text(
        "Harrix Swiss Knife — preserved user data after uninstall.\n"
        "\n"
        "Databases, api-keys, and fitness images were moved here so the app folders\n"
        "could be removed. Reinstall and point config.json sqlite_* paths here, or\n"
        "copy files back into the new install's data/databases and api-keys folders.\n",
        encoding="utf-8",
    )
    log.add("installed", f"Preserved user data in {dest}")
    return preserved
```

</details>

## 🔧 Function `run_uninstall`

```python
def run_uninstall(options: UninstallOptions, log: OutcomeLog) -> UninstallResult
```

Remove the app install; keep databases and related user data.

<details>
<summary>Code:</summary>

```python
def run_uninstall(options: UninstallOptions, log: OutcomeLog) -> UninstallResult:
    started = time.perf_counter()
    hsk = options.hsk_path.resolve()
    if not _looks_like_hsk(hsk):
        return UninstallResult(
            ok=False,
            hsk_path=hsk,
            preserved_dir=None,
            outcomes=log,
            error=f"Not a Harrix Swiss Knife install: {hsk}",
            elapsed_seconds=time.perf_counter() - started,
        )

    try:
        log.step("Uninstall Harrix Swiss Knife")
        log.detail(f"Project: {hsk}")
        log.detail("Databases, api-keys, and fitness images are kept; Git/uv/VS Code/Python stay installed.")

        _stop_running_app(hsk, log)

        preserve_dir = default_preserve_dir(hsk)
        preserved = preserve_user_data(hsk, preserve_dir, log)

        log.step("Remove shortcuts")
        try:
            removed = remove_app_shortcuts()
            if removed:
                for path in removed:
                    log.add("installed", f"Removed shortcut {path}")
            else:
                log.add("already", "No desktop/startup/uninstall shortcuts found")
        except OSError as exc:
            log.add("failed", f"Shortcut removal failed: {exc}")

        log.step("Remove global hsk CLI (uv tool)")
        _uninstall_cli(log)

        log.step("Remove Apps & Features entry")
        unregister_uninstall(log)

        install_root = hsk.parent
        to_remove = [hsk]
        if options.remove_sibling_repos:
            for name in REPO_NAMES:
                if name == HSK_REPO_NAME:
                    continue
                sibling = install_root / name
                if sibling.is_dir():
                    to_remove.append(sibling.resolve())

        log.step("Remove install folders")
        for path in to_remove:
            log.detail(f"Deleting {path}")
            _rmtree_retry(path, log)
            if path.exists():
                log.add("failed", f"Could not fully delete {path}")
            else:
                log.add("installed", f"Removed {path.name}")

        log.step("Done")
        log.line("")
        log.line(f"Preserved data:  {preserve_dir if preserved else '(nothing under project)'}")
        for line in log.summary_lines(action_label="What was removed:"):
            log.line(line)
        return UninstallResult(
            ok=True,
            hsk_path=hsk,
            preserved_dir=preserve_dir if preserved else None,
            outcomes=log,
            elapsed_seconds=time.perf_counter() - started,
            preserved_items=preserved,
        )
    except Exception as exc:
        log.line(f"❌ ERROR: {exc}")
        return UninstallResult(
            ok=False,
            hsk_path=hsk,
            preserved_dir=None,
            outcomes=log,
            error=str(exc),
            elapsed_seconds=time.perf_counter() - started,
        )
```

</details>

---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `default_install_root_parent`](#-function-default_install_root_parent)
- [🔧 Function `detect_dev_checkout_parent`](#-function-detect_dev_checkout_parent)
- [🔧 Function `enable_long_paths`](#-function-enable_long_paths)
- [🔧 Function `is_under_program_files`](#-function-is_under_program_files)
- [🔧 Function `long_paths_enabled`](#-function-long_paths_enabled)
- [🔧 Function `normalize_install_root`](#-function-normalize_install_root)
- [🔧 Function `venv_path_headroom`](#-function-venv_path_headroom)

</details>

## 🔧 Function `default_install_root_parent`

```python
def default_install_root_parent() -> Path
```

Prefer existing GitHub folders, else create `C:\harrix-swiss-knife`.

Order:

1. `D:\GitHub`, `C:\GitHub`, `Documents\GitHub` when already present
2. Create `C:\harrix-swiss-knife` (admin installer)
3. Fall back to `%USERPROFILE%\harrix-swiss-knife`

<details>
<summary>Code:</summary>

```python
def default_install_root_parent() -> Path:
    for candidate in _preferred_parent_candidates():
        if candidate.is_dir():
            return candidate.resolve()
    try:
        _FALLBACK_CREATE_PARENT.mkdir(parents=True, exist_ok=True)
        return _FALLBACK_CREATE_PARENT.resolve()
    except OSError:
        bundle = Path.home() / "harrix-swiss-knife"
        bundle.mkdir(parents=True, exist_ok=True)
        return bundle.resolve()
```

</details>

## 🔧 Function `detect_dev_checkout_parent`

```python
def detect_dev_checkout_parent(project_hint: Path | None = None) -> Path | None
```

If running from a harrix-swiss-knife checkout, return its parent folder.

<details>
<summary>Code:</summary>

```python
def detect_dev_checkout_parent(project_hint: Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if project_hint is not None:
        candidates.append(project_hint)
    # installer package -> harrix_swiss_knife -> src -> repo root
    here = Path(__file__).resolve()
    candidates.append(here.parents[3] if len(here.parents) >= _REPO_ROOT_PARENT_DEPTH else here.parent)
    for root in candidates:
        pp = root / "pyproject.toml"
        if not pp.is_file():
            continue
        text = pp.read_text(encoding="utf-8", errors="replace")[:2000]
        if 'name = "harrix-swiss-knife"' in text or "name='harrix-swiss-knife'" in text:
            return root.parent.resolve()
    return None
```

</details>

## 🔧 Function `enable_long_paths`

```python
def enable_long_paths() -> bool
```

Turn on system-wide long-path support. Needs admin rights; returns whether it worked.

<details>
<summary>Code:</summary>

```python
def enable_long_paths() -> bool:
    if winreg is None:
        return False
    try:
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, _LONG_PATHS_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, _LONG_PATHS_VALUE, 0, winreg.REG_DWORD, 1)
    except OSError:
        return False
    return True
```

</details>

## 🔧 Function `is_under_program_files`

```python
def is_under_program_files(path: Path) -> bool
```

Return whether `path` is under Program Files (not recommended for this app).

<details>
<summary>Code:</summary>

```python
def is_under_program_files(path: Path) -> bool:
    program_files = (
        os.environ.get("PROGRAMFILES") or os.environ.get("ProgramFiles") or r"C:\Program Files"  # noqa: SIM112
    )
    return str(path.resolve()).lower().startswith(program_files.lower())
```

</details>

## 🔧 Function `long_paths_enabled`

```python
def long_paths_enabled() -> bool
```

Return whether Windows accepts paths longer than `MAX_WINDOWS_PATH`.

<details>
<summary>Code:</summary>

```python
def long_paths_enabled() -> bool:
    if winreg is None:
        return True
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _LONG_PATHS_KEY) as key:
            value, _ = winreg.QueryValueEx(key, _LONG_PATHS_VALUE)
    except OSError:
        return False
    try:
        return bool(int(value))
    except (TypeError, ValueError):
        return False
```

</details>

## 🔧 Function `normalize_install_root`

```python
def normalize_install_root(selected: Path) -> Path
```

Accept a parent for the three repos; do not nest under an extra `GitHub`.

Kept as-is when the leaf is `GitHub` or `harrix-swiss-knife` (including
`C:\harrix-swiss-knife` on the system drive). Otherwise append `GitHub` only
for generic drive roots such as `D:\` so sibling repos still share a folder.

<details>
<summary>Code:</summary>

```python
def normalize_install_root(selected: Path) -> Path:
    p = selected.resolve()
    leaf = p.name.lower()
    if leaf in {"github", "harrix-swiss-knife"}:
        p.mkdir(parents=True, exist_ok=True)
        return p
    # Bare drive root like `D:\` → `D:\GitHub`
    if len(p.parts) <= 1:
        gh = p / "GitHub"
        gh.mkdir(parents=True, exist_ok=True)
        return gh.resolve()
    # Any other explicit folder is used as the install parent as chosen.
    p.mkdir(parents=True, exist_ok=True)
    return p
```

</details>

## 🔧 Function `venv_path_headroom`

```python
def venv_path_headroom(install_root: Path) -> int
```

Characters left for files inside a repo `.venv` when installing into [`install_root`](wizard.g.md#%EF%B8%8F-method-install_root).

Compare the result with `DEEPEST_VENV_RELATIVE` to see whether `uv sync` can
write every packaged file without long-path support.

<details>
<summary>Code:</summary>

```python
def venv_path_headroom(install_root: Path) -> int:
    longest_repo = max(len(name) for name in REPO_NAMES)
    return MAX_WINDOWS_PATH - len(str(install_root).rstrip("\\/")) - 1 - longest_repo
```

</details>

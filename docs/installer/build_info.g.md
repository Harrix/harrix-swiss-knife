---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `build_info.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `collect_build_meta`](#-function-collect_build_meta)
- [🔧 Function `display_build_lines`](#-function-display_build_lines)
- [🔧 Function `git_short_hash`](#-function-git_short_hash)
- [🔧 Function `load_build_meta`](#-function-load_build_meta)
- [🔧 Function `read_pyproject_version`](#-function-read_pyproject_version)
- [🔧 Function `summarize_dependency_artifacts`](#-function-summarize_dependency_artifacts)
- [🔧 Function `write_build_meta`](#-function-write_build_meta)

</details>

## 🔧 Function `collect_build_meta`

```python
def collect_build_meta(project_root: Path) -> dict[str, str]
```

Collect version, Git hash, build timestamp, and key payload artifact sizes.

<details>
<summary>Code:</summary>

```python
def collect_build_meta(project_root: Path) -> dict[str, str]:
    meta = {
        "version": read_pyproject_version(project_root),
        "built_at": datetime.now(tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M"),
        "git": git_short_hash(project_root),
    }
    artifacts = summarize_dependency_artifacts(project_root / "install" / "dependencies")
    if artifacts:
        meta["artifacts"] = artifacts
    return meta
```

</details>

## 🔧 Function `display_build_lines`

```python
def display_build_lines(meta: dict[str, str] | None = None) -> tuple[str, str]
```

Return `(version_line, built_line)` for the welcome page.

<details>
<summary>Code:</summary>

```python
def display_build_lines(meta: dict[str, str] | None = None) -> tuple[str, str]:
    info = meta if meta is not None else load_build_meta()
    version = info.get("version") or "unknown"
    git = info.get("git") or ""
    built = info.get("built_at") or "unknown"
    version_line = f"Version {version}"
    if git:
        version_line = f"{version_line} ({git})"
    return version_line, f"Built {built}"
```

</details>

## 🔧 Function `git_short_hash`

```python
def git_short_hash(project_root: Path) -> str
```

Return `git rev-parse --short HEAD`, or empty if unavailable.

<details>
<summary>Code:</summary>

```python
def git_short_hash(project_root: Path) -> str:
    git_exe = shutil.which("git")
    if git_exe is None:
        return ""
    try:
        proc = subprocess.run(
            [git_exe, "-C", str(project_root), "rev-parse", "--short", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()
```

</details>

## 🔧 Function `load_build_meta`

```python
def load_build_meta() -> dict[str, str]
```

Load baked metadata from the EXE overlay, then local fallbacks.

<details>
<summary>Code:</summary>

```python
def load_build_meta() -> dict[str, str]:
    if is_frozen():
        raw = read_overlay_member(frozen_executable(), "build_meta.json")
        parsed = _parse_meta(raw)
        if parsed:
            return parsed
    for path in _local_meta_paths():
        if path.is_file():
            parsed = _parse_meta(path.read_bytes())
            if parsed:
                return parsed
    root = _project_root_guess()
    if root is not None:
        return collect_build_meta(root)
    return {"version": "unknown", "built_at": "unknown", "git": ""}
```

</details>

## 🔧 Function `read_pyproject_version`

```python
def read_pyproject_version(project_root: Path) -> str
```

Return `[project].version` from `pyproject.toml`.

<details>
<summary>Code:</summary>

```python
def read_pyproject_version(project_root: Path) -> str:
    path = project_root / "pyproject.toml"
    if not path.is_file():
        return "unknown"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return "unknown"
    version = data.get("project", {}).get("version")
    return str(version) if version else "unknown"
```

</details>

## 🔧 Function `summarize_dependency_artifacts`

```python
def summarize_dependency_artifacts(deps: Path) -> str
```

Return a short `name=size` list of key files under `dependencies/`.

<details>
<summary>Code:</summary>

```python
def summarize_dependency_artifacts(deps: Path) -> str:
    if not deps.is_dir():
        return ""
    names = (
        "Git-latest-64-bit.exe",
        "uv-x86_64-pc-windows-msvc.zip",
        "VSCodeSetup-x64-latest.exe",
        "ffmpeg.exe",
        "avifenc.exe",
        "avifdec.exe",
    )
    parts: list[str] = []
    for name in names:
        path = deps / name
        if path.is_file() and path.stat().st_size > 0:
            parts.append(f"{name}={_human_size(path.stat().st_size)}")
    ext_dir = deps / "vscode-extensions"
    if ext_dir.is_dir():
        vsixes = sorted(p for p in ext_dir.glob("*.vsix") if p.is_file() and p.stat().st_size > 0)
        parts.extend(f"vscode-extensions/{path.name}={_human_size(path.stat().st_size)}" for path in vsixes)
    for cache_name in ("uv-cache", "uv-python-cache", "repos"):
        cache = deps / cache_name
        if cache.is_dir() and any(cache.iterdir()):
            parts.append(f"{cache_name}/={'present'}")
    return "; ".join(parts)
```

</details>

## 🔧 Function `write_build_meta`

```python
def write_build_meta(path: Path, meta: dict[str, str]) -> None
```

Write `build_meta.json`.

<details>
<summary>Code:</summary>

```python
def write_build_meta(path: Path, meta: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
```

</details>

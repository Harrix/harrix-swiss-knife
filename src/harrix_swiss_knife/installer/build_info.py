"""Version and build date shown on the installer welcome page."""

from __future__ import annotations

import json
import shutil
import subprocess
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from harrix_swiss_knife.installer.payload import frozen_executable, is_frozen, read_overlay_member


def collect_build_meta(project_root: Path) -> dict[str, str]:
    """Collect version, Git hash, build timestamp, and key payload artifact sizes."""
    meta = {
        "version": read_pyproject_version(project_root),
        "built_at": datetime.now(tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M"),
        "git": git_short_hash(project_root),
    }
    artifacts = summarize_dependency_artifacts(project_root / "install" / "dependencies")
    if artifacts:
        meta["artifacts"] = artifacts
    return meta


def display_build_lines(meta: dict[str, str] | None = None) -> tuple[str, str]:
    """Return `(version_line, built_line)` for the welcome page."""
    info = meta if meta is not None else load_build_meta()
    version = info.get("version") or "unknown"
    git = info.get("git") or ""
    built = info.get("built_at") or "unknown"
    version_line = f"Version {version}"
    if git:
        version_line = f"{version_line} ({git})"
    return version_line, f"Built {built}"


def git_short_hash(project_root: Path) -> str:
    """Return `git rev-parse --short HEAD`, or empty if unavailable."""
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


def load_build_meta() -> dict[str, str]:
    """Load baked metadata from the EXE overlay, then local fallbacks."""
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


def read_pyproject_version(project_root: Path) -> str:
    """Return `[project].version` from `pyproject.toml`."""
    path = project_root / "pyproject.toml"
    if not path.is_file():
        return "unknown"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return "unknown"
    version = data.get("project", {}).get("version")
    return str(version) if version else "unknown"


def summarize_dependency_artifacts(deps: Path) -> str:
    """Return a short `name=size` list of key files under `dependencies/`."""
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


def _human_size(size: int) -> str:
    if size < _BYTES_PER_KIB:
        return f"{size}B"
    if size < _BYTES_PER_MIB:
        return f"{size // _BYTES_PER_KIB}KB"
    return f"{size // _BYTES_PER_MIB}MB"


def _local_meta_paths() -> list[Path]:
    return [Path(__file__).resolve().parent / "build_meta.json"]


def _parse_meta(raw: bytes | None) -> dict[str, str] | None:
    if not raw:
        return None
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return {str(k): str(v) for k, v in data.items() if v is not None}


def _project_root_guess() -> Path | None:
    here = Path(__file__).resolve()
    if len(here.parents) >= _REPO_ROOT_PARENT_DEPTH:
        root = here.parents[_REPO_ROOT_PARENT_DEPTH - 1]
        if (root / "pyproject.toml").is_file():
            return root
    return None


_BYTES_PER_KIB = 1024
_BYTES_PER_MIB = 1024 * 1024


_REPO_ROOT_PARENT_DEPTH = 4

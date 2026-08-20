"""Download and install the VS Code Python extension pack (ms-python.python + deps)."""

from __future__ import annotations

import gzip
import json
import os
import shutil
import subprocess
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.error import HTTPError, URLError

if TYPE_CHECKING:
    from harrix_swiss_knife.installer.log import OutcomeLog

LogFn = Callable[[str], None]

PYTHON_EXTENSION_ID = "ms-python.python"
VSCODE_EXTENSIONS_DIR_NAME = "vscode-extensions"

# Used when package.json cannot be read from the downloaded VSIX.
FALLBACK_PYTHON_EXTENSION_IDS: tuple[str, ...] = (
    "ms-python.vscode-pylance",
    "ms-python.debugpy",
    "ms-python.vscode-python-envs",
    "ms-python.python",
)


def find_editor_cli() -> Path | None:
    """Return `code.cmd` / `Code.exe` / Cursor CLI if present."""
    for name in ("code", "code.cmd", "cursor", "cursor.cmd"):
        found = shutil.which(name)
        if found:
            return Path(found)
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    pf = Path(os.environ.get("PROGRAMFILES") or os.environ.get("ProgramFiles") or r"C:\Program Files")  # noqa: SIM112
    candidates = [
        local / "Programs" / "Microsoft VS Code" / "bin" / "code.cmd",
        local / "Programs" / "Microsoft VS Code" / "Code.exe",
        pf / "Microsoft VS Code" / "bin" / "code.cmd",
        pf / "Microsoft VS Code" / "Code.exe",
        local / "Programs" / "cursor" / "resources" / "app" / "bin" / "cursor.cmd",
        local / "Programs" / "cursor" / "Cursor.exe",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def install_order_for_vsixes(deps: Path) -> list[Path]:
    """Return VSIX paths to install: dependencies first, then ms-python.python."""
    folder = vscode_extensions_dir(deps)
    if not folder.is_dir():
        return []
    main = vsix_path_for(deps, PYTHON_EXTENSION_ID)
    ordered: list[Path] = []
    seen: set[str] = set()
    if main.is_file() and main.stat().st_size > 0:
        for ext_id in read_extension_dependencies(main):
            path = vsix_path_for(deps, ext_id)
            key = str(path).lower()
            if path.is_file() and path.stat().st_size > 0 and key not in seen:
                seen.add(key)
                ordered.append(path)
    for path in sorted(folder.glob("*.vsix")):
        key = str(path).lower()
        if key in seen:
            continue
        if path.resolve() == main.resolve() if main.is_file() else False:
            continue
        if path.is_file() and path.stat().st_size > 0:
            seen.add(key)
            ordered.append(path)
    if main.is_file() and main.stat().st_size > 0:
        ordered.append(main)
    return ordered


def install_vscode_python_extension(
    *,
    deps: Path,
    log: OutcomeLog,
    allow_network: bool,
) -> None:
    """Install bundled Python VSIX files, or fall back to Marketplace online."""
    log.step("Install VS Code Python extension")
    editor = find_editor_cli()
    if editor is None:
        log.add("skipped", "Python extension skipped (VS Code / Cursor not found)")
        return

    vsixes = install_order_for_vsixes(deps)
    if vsixes:
        ok_all = True
        for vsix in vsixes:
            log.detail(f"Installing {vsix.name} via {editor.name}")
            if not _install_extension(editor, str(vsix), log):
                ok_all = False
        if ok_all:
            log.add("installed", "Python extension (VSIX bundle) installed")
        else:
            log.add("failed", "Python extension VSIX install had errors")
        return

    if not allow_network:
        log.add("failed", "Python extension VSIX missing from offline payload")
        return
    log.detail(f"No bundled VSIX; installing {PYTHON_EXTENSION_ID} from Marketplace")
    if _install_extension(editor, PYTHON_EXTENSION_ID, log):
        log.add("installed", f"Python extension installed ({PYTHON_EXTENSION_ID})")
    else:
        log.add("failed", "Python extension Marketplace install failed")


def marketplace_vsix_url(extension_id: str) -> str:
    """Return the public Marketplace VSIX download URL for `publisher.name`."""
    publisher, _, name = extension_id.partition(".")
    if not publisher or not name:
        msg = f"Invalid extension id: {extension_id}"
        raise ValueError(msg)
    return (
        f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/"
        f"{publisher}/vsextensions/{name}/latest/vspackage"
    )


def populate_vscode_python_extensions(
    project_root: Path,
    log: LogFn,
    *,
    download_url: Callable[..., bool],
    config: dict[str, Any] | None = None,
    force: bool = True,
) -> None:
    """Download ms-python.python and its VSIX dependencies into dependencies/."""
    deps = project_root / "install" / "dependencies"
    folder = vscode_extensions_dir(deps)
    folder.mkdir(parents=True, exist_ok=True)
    log("==> Download VS Code Python extension (ms-python.python) and dependencies")

    main = vsix_path_for(deps, PYTHON_EXTENSION_ID)
    try:
        if download_url(
            marketplace_vsix_url(PYTHON_EXTENSION_ID),
            main,
            config=config,
            project_root=project_root,
            force=force,
        ):
            _unwrap_marketplace_vsix(main)
            log(f"  OK: {main.name}")
        else:
            log(f"  Keep existing {main.name}")
    except (HTTPError, URLError, ValueError, OSError) as exc:
        log(f"  Skip {PYTHON_EXTENSION_ID}: {exc}")
        return

    if not main.is_file() or main.stat().st_size <= 0:
        log("  Skip dependency VSIX download (python VSIX missing)")
        return

    dep_ids = read_extension_dependencies(main)
    if not dep_ids:
        dep_ids = list(FALLBACK_PYTHON_EXTENSION_IDS[:-1])
        log("  Could not parse extensionDependencies; using fallback list")
    else:
        log(f"  Dependencies from package.json: {', '.join(dep_ids)}")

    for ext_id in dep_ids:
        if ext_id.lower() == PYTHON_EXTENSION_ID.lower():
            continue
        dest = vsix_path_for(deps, ext_id)
        try:
            if download_url(
                marketplace_vsix_url(ext_id),
                dest,
                config=config,
                project_root=project_root,
                force=force,
            ):
                _unwrap_marketplace_vsix(dest)
                log(f"  OK: {dest.name}")
            else:
                log(f"  Keep existing {dest.name}")
        except (HTTPError, URLError, ValueError, OSError) as exc:
            log(f"  Skip {ext_id}: {exc}")


def read_extension_dependencies(vsix: Path) -> list[str]:
    """Return `extensionDependencies` (+ pack) from a VSIX `package.json`."""
    try:
        with zipfile.ZipFile(vsix, "r") as zf:
            names = [n for n in zf.namelist() if n.replace("\\", "/").endswith("package.json")]
            # Prefer the top-level extension/package.json
            names.sort(key=lambda n: (0 if n.replace("\\", "/").startswith("extension/") else 1, len(n)))
            if not names:
                return []
            raw = zf.read(names[0])
    except (OSError, zipfile.BadZipFile):
        return []
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    deps: list[str] = []
    for key in ("extensionDependencies", "extensionPack"):
        value = data.get(key)
        if isinstance(value, list):
            deps.extend(str(item) for item in value if isinstance(item, str) and item.strip())
    # Deduplicate, keep order
    seen: set[str] = set()
    ordered: list[str] = []
    for item in deps:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def vscode_extensions_dir(deps: Path) -> Path:
    """Return `dependencies/vscode-extensions/`."""
    return deps / VSCODE_EXTENSIONS_DIR_NAME


def vsix_path_for(deps: Path, extension_id: str) -> Path:
    """Return the on-disk VSIX path for an extension ID."""
    return vscode_extensions_dir(deps) / f"{extension_id}.vsix"


def _install_extension(editor: Path, target: str, log: OutcomeLog) -> bool:
    creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    cmd = [str(editor), "--install-extension", target, "--force", "--wait"]
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creation,
            timeout=600,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        log.detail(f"install-extension failed: {exc}")
        return False
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    if out:
        log.detail(out[:1500])
    return proc.returncode == 0


def _unwrap_marketplace_vsix(path: Path) -> None:
    """Marketplace sometimes serves gzip-wrapped VSIX; unwrap in place."""
    if not path.is_file() or path.stat().st_size < _GZIP_MAGIC_LEN:
        return
    head = path.read_bytes()[:_GZIP_MAGIC_LEN]
    if head != b"\x1f\x8b":
        return
    raw = gzip.decompress(path.read_bytes())
    path.write_bytes(raw)


_GZIP_MAGIC_LEN = 2

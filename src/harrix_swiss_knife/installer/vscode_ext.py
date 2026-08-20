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


def clear_obsolete_markers(extension_ids: list[str], log: OutcomeLog) -> int:
    """Drop `.obsolete` uninstall markers so freshly installed VSIX files stay visible.

    VS Code / Cursor write `{publisher.name}-{version}: true` into `.obsolete` when an
    extension is uninstalled in the UI; a later `--install-extension` can leave the
    marker in place and the extension then shows up as disabled.

    """
    cleared = 0
    prefixes = tuple(f"{ext_id.lower()}-" for ext_id in extension_ids)
    for ext_root in editor_extension_dirs():
        obsolete_path = ext_root / ".obsolete"
        if not obsolete_path.is_file():
            continue
        try:
            data = json.loads(obsolete_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        stale = [key for key in data if str(key).lower().startswith(prefixes)]
        if not stale:
            continue
        for key in stale:
            data.pop(key, None)
        try:
            obsolete_path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        except OSError as exc:
            log.detail(f"Could not update {obsolete_path}: {exc}")
            continue
        cleared += len(stale)
        log.detail(f"Cleared {len(stale)} uninstall marker(s) in {obsolete_path}")
    return cleared


def editor_extension_dirs() -> list[Path]:
    """Return existing per-user extension folders of VS Code-family editors."""
    home = Path.home()
    candidates = (
        home / ".vscode" / "extensions",
        home / ".vscode-insiders" / "extensions",
        home / ".cursor" / "extensions",
        home / ".vscode-oss" / "extensions",
    )
    return [path for path in candidates if path.is_dir()]


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
        extension_ids = [vsix.stem for vsix in vsixes]
        clear_obsolete_markers(extension_ids, log)
        ok_all = True
        for vsix in vsixes:
            log.detail(f"Installing {vsix.name} via {editor.name}")
            if not _install_extension(editor, str(vsix), log):
                ok_all = False
        clear_obsolete_markers(extension_ids, log)
        verify_extensions_enabled(editor, extension_ids, log)
        if ok_all:
            log.add("installed", "Python extension (VSIX bundle) installed")
        else:
            log.add("failed", "Python extension VSIX install had errors")
        return

    if not allow_network:
        log.add("failed", "Python extension VSIX missing from offline payload")
        return
    log.detail(f"No bundled VSIX; installing {PYTHON_EXTENSION_ID} from Marketplace")
    clear_obsolete_markers([PYTHON_EXTENSION_ID], log)
    if _install_extension(editor, PYTHON_EXTENSION_ID, log):
        clear_obsolete_markers([PYTHON_EXTENSION_ID], log)
        verify_extensions_enabled(editor, [PYTHON_EXTENSION_ID], log)
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


def verify_extensions_enabled(editor: Path, extension_ids: list[str], log: OutcomeLog) -> list[str]:
    """Log which requested extensions the editor reports, and return the missing ones."""
    listed = _list_installed_extensions(editor, log)
    if listed is None:
        return []
    missing = [ext_id for ext_id in extension_ids if ext_id.lower() not in listed]
    if missing:
        log.add("failed", f"Editor does not list: {', '.join(missing)} (install or enable manually)")
    else:
        log.detail(f"Editor lists all requested extensions ({len(extension_ids)})")
    log.detail(
        "If Python still looks disabled, click Trust in the editor: an untrusted folder "
        "runs extensions in Restricted Mode."
    )
    return missing


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


def _list_installed_extensions(editor: Path, log: OutcomeLog) -> set[str] | None:
    """Return lowercase extension ids reported by `--list-extensions`, or `None` on failure."""
    creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        proc = subprocess.run(
            [str(editor), "--list-extensions"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creation,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        log.detail(f"list-extensions failed: {exc}")
        return None
    if proc.returncode != 0:
        log.detail(f"list-extensions exit {proc.returncode}")
        return None
    return {line.strip().lower() for line in (proc.stdout or "").splitlines() if line.strip()}


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

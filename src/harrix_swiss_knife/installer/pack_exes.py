"""Build PyInstaller stub and append online/offline payload overlays."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import zipfile
from collections.abc import Callable
from pathlib import Path  # noqa: TC003

from harrix_swiss_knife.installer.build_info import collect_build_meta
from harrix_swiss_knife.installer.constants import (
    OFFLINE_EXE_NAME,
    ONLINE_EXE_NAME,
    STUB_EXE_NAME,
    STUB_SPEC_VERSION,
)
from harrix_swiss_knife.installer.icon_assets import find_logo_svg, write_padded_ico
from harrix_swiss_knife.installer.payload import append_overlay_zip

LogFn = Callable[[str], None]

# Fast DEFLATE for most files; store huge uv caches uncompressed (zip time >> size).
_ZIP_COMPRESS_LEVEL = 1
_STORED_DEPENDENCY_DIRS = frozenset({"uv-cache", "uv-python-cache"})


def build_payload_zips(
    project_root: Path,
    log: LogFn,
    *,
    copy_deps_fn: Callable[..., None] | None = None,
    online_exclude_dirs: frozenset[str],
    omit_files: set[str],
) -> tuple[Path, Path]:
    """Create temporary online/offline zips containing only `dependencies/`.

    Zips directly from `install/dependencies` (no full tree copy). `copy_deps_fn`
    is kept for call-site compatibility and ignored.

    """
    del copy_deps_fn  # unused; kept so call sites need not change
    deps = project_root / "install" / "dependencies"
    if not deps.is_dir():
        msg = f"Not found: {deps}"
        raise FileNotFoundError(msg)

    install = project_root / "install"
    out_online = install / ".payload-online.zip"
    out_offline = install / ".payload-offline.zip"
    meta = collect_build_meta(project_root)
    meta_json = json.dumps(meta, indent=2, ensure_ascii=False) + "\n"

    log("==> Build payload zips (direct from dependencies/, compresslevel=1)")
    _zip_dependencies(
        deps,
        out_online,
        exclude_dirs=online_exclude_dirs,
        exclude_files=omit_files,
        build_meta_json=meta_json,
    )
    log(f"  Online payload: {out_online.name} ({out_online.stat().st_size // (1024 * 1024)} MB)")
    _zip_dependencies(
        deps,
        out_offline,
        exclude_dirs=frozenset(),
        exclude_files=omit_files,
        build_meta_json=meta_json,
    )
    log(f"  Offline payload: {out_offline.name} ({out_offline.stat().st_size // (1024 * 1024)} MB)")
    log(f"  Payload zips: {out_online.name}, {out_offline.name}")
    return out_online, out_offline


def ensure_installer_stub(project_root: Path, log: LogFn, *, force: bool = False) -> Path:
    """Freeze the GUI installer stub once (reused across online/offline packs)."""
    out = stub_exe_path(project_root)
    version_file = stub_dir(project_root) / "stub-version.txt"
    stale = (not version_file.is_file()) or version_file.read_text(encoding="utf-8").strip() != STUB_SPEC_VERSION
    if out.is_file() and not force and not stale:
        log(f"  Reusing installer stub: {out}")
        return out

    if shutil.which("pyinstaller") is None and not _module_available("PyInstaller"):
        msg = "PyInstaller is required. Install with: uv sync --group dev"
        raise RuntimeError(msg)

    work = stub_dir(project_root)
    work.mkdir(parents=True, exist_ok=True)
    dist = work / "dist"
    build = work / "build"
    dist.mkdir(exist_ok=True)
    build.mkdir(exist_ok=True)

    # Entry script that only imports the installer package (not the tray app).
    entry = work / "stub_main.py"
    entry.write_text(
        "from harrix_swiss_knife.installer.wizard import main\n\nif __name__ == '__main__':\n    main()\n",
        encoding="utf-8",
    )

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        # Windows prompts for UAC on launch, so the wizard never restarts itself.
        "--uac-admin",
        "--name",
        STUB_EXE_NAME.removesuffix(".exe"),
        "--distpath",
        str(dist),
        "--workpath",
        str(build),
        "--specpath",
        str(work),
        "--paths",
        str(project_root / "src"),
    ]
    icon = project_root / "src" / "harrix_swiss_knife" / "assets" / "app.ico"
    padded_ico = work / "app-padded.ico"
    if icon.is_file():
        try:
            write_padded_ico(padded_ico)
            icon_for_exe = padded_ico
        except Exception as exc:
            log(f"  Could not rebuild padded ICO ({exc}); using app.ico as-is")
            icon_for_exe = icon
        cmd.extend(["--icon", str(icon_for_exe)])
        cmd.extend(["--add-data", f"{icon}{os.pathsep}harrix_swiss_knife/assets"])
    logo = find_logo_svg() or (project_root / "src" / "harrix_swiss_knife" / "assets" / "logo.svg")
    if logo.is_file():
        cmd.extend(["--add-data", f"{logo}{os.pathsep}harrix_swiss_knife/assets"])
    cmd.extend(
        [
            "--collect-all",
            "PySide6",
            "--collect-data",
            "certifi",
            "--collect-submodules",
            "harrix_swiss_knife.installer",
            "--hidden-import",
            "harrix_swiss_knife.desktop_shortcut",
            "--hidden-import",
            "harrix_swiss_knife.integrations.http_download",
            "--hidden-import",
            "harrix_swiss_knife.integrations.http_transport",
            "--hidden-import",
            "clr",
            "--hidden-import",
            "pythonnet",
            "--exclude-module",
            "harrix_pylib",
            "--exclude-module",
            "harrix_pyssg",
            "--exclude-module",
            "harrix_swiss_knife.actions",
            "--exclude-module",
            "harrix_swiss_knife.apps",
            "--exclude-module",
            "harrix_swiss_knife.integrations.ai",
            "--exclude-module",
            "harrix_swiss_knife.integrations.bothub_client",
            str(entry),
        ]
    )
    log("==> Freeze installer stub (PyInstaller one-file)")
    log(f"  $ {' '.join(cmd)}")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src") + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        cmd,
        cwd=str(project_root),
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    if proc.stdout.strip():
        log(proc.stdout.strip()[-4000:])
    if proc.stderr.strip():
        log(proc.stderr.strip()[-4000:])
    if proc.returncode != 0 or not out.is_file():
        msg = f"PyInstaller failed (exit {proc.returncode}); stub missing at {out}"
        raise RuntimeError(msg)
    version_file.write_text(STUB_SPEC_VERSION, encoding="utf-8")
    log(f"✅ Stub ready: {out}")
    return out


def pack_installer_exes(
    project_root: Path,
    online_zip: Path,
    offline_zip: Path,
    log: LogFn,
    *,
    force_stub: bool = False,
) -> tuple[Path, Path]:
    """Append payload zips to the stub; write online/offline EXEs under `install/`."""
    stub = ensure_installer_stub(project_root, log, force=force_stub)
    install = project_root / "install"
    online_exe = install / ONLINE_EXE_NAME
    offline_exe = install / OFFLINE_EXE_NAME
    log(f"==> Pack installer EXEs\n  {online_exe}\n  {offline_exe}")
    append_overlay_zip(stub, online_zip, online_exe)
    log(f"✅ Created: {online_exe} ({online_exe.stat().st_size // (1024 * 1024)} MB)")
    append_overlay_zip(stub, offline_zip, offline_exe)
    log(f"✅ Created: {offline_exe} ({offline_exe.stat().st_size // (1024 * 1024)} MB)")
    return online_exe, offline_exe


def stub_dir(project_root: Path) -> Path:
    """Return the PyInstaller stub working directory."""
    return project_root / "install" / ".installer-stub"


def stub_exe_path(project_root: Path) -> Path:
    """Return the built stub executable path."""
    return stub_dir(project_root) / "dist" / STUB_EXE_NAME


def _module_available(name: str) -> bool:
    try:
        __import__(name)
    except ImportError:
        return False
    return True


def _zip_dependencies(
    deps: Path,
    zip_path: Path,
    *,
    exclude_dirs: frozenset[str],
    exclude_files: set[str],
    build_meta_json: str,
) -> None:
    """Write a payload zip from `deps` without staging a full copy."""
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=_ZIP_COMPRESS_LEVEL,
    ) as zf:
        zf.writestr("build_meta.json", build_meta_json)
        for child in sorted(deps.iterdir(), key=lambda p: p.name.lower()):
            if child.is_dir():
                if child.name in exclude_dirs:
                    continue
                store = child.name in _STORED_DEPENDENCY_DIRS
                for path in sorted(child.rglob("*")):
                    if not path.is_file():
                        continue
                    arcname = f"dependencies/{path.relative_to(deps).as_posix()}"
                    if store:
                        zf.write(path, arcname, compress_type=zipfile.ZIP_STORED)
                    else:
                        zf.write(path, arcname)
                continue
            if child.suffix.lower() == ".log":
                continue
            if child.name in exclude_files:
                continue
            zf.write(child, f"dependencies/{child.name}")


def _zip_tree(source_dir: Path, zip_path: Path) -> None:
    """Zip a directory tree (tests / helpers); uses fast compression."""
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=_ZIP_COMPRESS_LEVEL,
    ) as zf:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(source_dir).as_posix())

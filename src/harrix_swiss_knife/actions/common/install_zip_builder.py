"""Build online/offline GUI installer EXEs under `install/`.

Fills `install/dependencies/`, freezes a PySide6 installer stub, and appends
online/offline payload zips. Target PCs run `harrix-swiss-knife-online.exe` or
`harrix-swiss-knife-offline-for-personal-use.exe` (no bat/ps1 payload).

"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import harrix_pylib as h

from harrix_swiss_knife.actions.common.github_https import (
    github_api_headers,
    github_download_headers,
    validate_https_url,
)
from harrix_swiss_knife.installer.constants import OFFLINE_EXE_NAME, ONLINE_EXE_NAME
from harrix_swiss_knife.installer.pack_exes import build_payload_zips, pack_installer_exes
from harrix_swiss_knife.integrations.http_download import download_https_to_path
from harrix_swiss_knife.integrations.http_transport import https_ssl_context

GITHUB_UA = "Harrix-Swiss-Knife/1.0 (Python; install-zip-builder)"
DOWNLOAD_CHUNK = 256 * 1024
DOWNLOAD_TIMEOUT = 120
SIBLING_REPO_NAMES = ("harrix-pylib", "harrix-pyssg")
HSK_REPO_NAME = "harrix-swiss-knife"
ONLINE_EXCLUDE_DIRS = frozenset({"repos", "uv-cache", "uv-python-cache"})
# Back-compat aliases for older tests/docs imports
ONLINE_ZIP_NAME = ONLINE_EXE_NAME
OFFLINE_ZIP_NAME = OFFLINE_EXE_NAME
MEDIA_EXE_NAMES = ("ffmpeg.exe", "avifenc.exe", "avifdec.exe")
UV_WINDOWS_ZIP = "uv-x86_64-pc-windows-msvc.zip"
UV_WINDOWS_URL = f"https://github.com/astral-sh/uv/releases/latest/download/{UV_WINDOWS_ZIP}"
VSCODE_URL = "https://update.code.visualstudio.com/latest/win32-x64-user/stable"
VSCODE_EXE_NAME = "VSCodeSetup-x64-latest.exe"
GIT_EXE_NAME = "Git-latest-64-bit.exe"
LIBAVIF_ZIP_NAME = "windows-artifacts.zip"
FFMPEG_ZIP_NAME = "ffmpeg-master-latest-win64-gpl.zip"

LogFn = Callable[[str], None]


@dataclass(frozen=True)
class BuildSteps:
    """Selected builder steps (order is fixed by `run_pipeline`)."""

    wipe_dependencies: bool = True
    binaries: bool = True
    installers: bool = True
    repos: bool = True
    uv_cache: bool = True
    build_zips: bool = True  # builds installer EXEs (name kept for CLI/tests)
    open_install: bool = True
    clean_logs: bool = False

    def any_work(self) -> bool:
        """Return whether at least one productive step is selected."""
        return any(
            (
                self.wipe_dependencies,
                self.binaries,
                self.installers,
                self.repos,
                self.uv_cache,
                self.build_zips,
                self.clean_logs,
            )
        )

    @classmethod
    def from_labels(cls, labels: Sequence[str]) -> BuildSteps:
        """Map checkbox labels to steps."""
        selected = set(labels)
        return cls(
            wipe_dependencies=STEP_WIPE in selected,
            binaries=STEP_BINARIES in selected,
            installers=STEP_INSTALLERS in selected,
            repos=STEP_REPOS in selected,
            uv_cache=STEP_UV_CACHE in selected,
            build_zips=STEP_BUILD_EXES in selected,
            open_install=STEP_OPEN in selected,
            clean_logs=STEP_CLEAN_LOGS in selected,
        )


@dataclass
class PipelineResult:
    """Outcome of `run_pipeline`."""

    ok: bool
    lines: list[str]
    online_zip: Path | None = None
    offline_zip: Path | None = None

    @property
    def offline_exe(self) -> Path | None:
        """Alias for `offline_zip` (EXE path)."""
        return self.offline_zip

    @property
    def online_exe(self) -> Path | None:
        """Alias for `online_zip` (EXE path)."""
        return self.online_zip


def asset_download_url(
    release: dict[str, Any],
    *,
    asset_name: str | None = None,
    name_contains: Sequence[str] = (),
) -> str:
    """Return `browser_download_url` for a release asset."""
    assets = release.get("assets") or []
    if asset_name:
        for asset in assets:
            if asset.get("name") == asset_name:
                return str(asset["browser_download_url"])
        msg = f"Asset '{asset_name}' not found in release"
        raise ValueError(msg)
    for asset in assets:
        name = str(asset.get("name") or "")
        if all(part in name for part in name_contains):
            return str(asset["browser_download_url"])
    msg = f"No asset matching {tuple(name_contains)} found in release"
    raise ValueError(msg)


def build_install_exes(project_root: Path, log: LogFn) -> tuple[Path, Path]:
    """Create online and offline installer EXEs under `install/`."""
    deps = dependencies_dir(project_root)
    if not deps.is_dir():
        msg = f"Not found: {deps}"
        raise FileNotFoundError(msg)

    omit = redundant_media_zip_names(deps)
    if omit:
        log(f"  Omitting redundant media zips: {', '.join(sorted(omit))}")

    online_zip, offline_zip = build_payload_zips(
        project_root,
        log,
        online_exclude_dirs=ONLINE_EXCLUDE_DIRS,
        omit_files=omit,
    )
    try:
        return pack_installer_exes(project_root, online_zip, offline_zip, log)
    finally:
        online_zip.unlink(missing_ok=True)
        offline_zip.unlink(missing_ok=True)


def build_install_zips(project_root: Path, log: LogFn) -> tuple[Path, Path]:
    """Alias for `build_install_exes` (older name kept for tests)."""
    return build_install_exes(project_root, log)


def clean_install_logs(project_root: Path, log: LogFn) -> None:
    """Remove top-level `*.log` under `install/` and `install/dependencies/`."""
    removed = 0
    for root in (install_dir(project_root), dependencies_dir(project_root)):
        if not root.is_dir():
            continue
        for path in root.glob("*.log"):
            if path.is_file():
                path.unlink()
                removed += 1
                log(f"  Removed: {path}")
    log(f"✅ Removed {removed} log file(s).")


def cli_argv_for_steps(steps: BuildSteps) -> list[str]:
    """Return CLI flag list that reproduces `steps` (relative to all-on defaults)."""
    flags: list[str] = []
    if not steps.wipe_dependencies:
        flags.append("--no-wipe")
    if not steps.binaries:
        flags.append("--skip-binaries")
    if not steps.installers:
        flags.append("--skip-installers")
    if not steps.repos:
        flags.append("--skip-repos")
    if not steps.uv_cache:
        flags.append("--skip-uv-cache")
    if not steps.build_zips:
        flags.append("--no-exes")
        flags.append("--no-zips")  # back-compat
    if not steps.open_install:
        flags.append("--no-open")
    if steps.clean_logs:
        flags.append("--clean-logs")
    return flags


def commit_stage_dir(stage_dir: Path, final_dir: Path) -> None:
    """Replace `final_dir` with `stage_dir` (Windows-safe directory swap).

    `Path.replace` on Windows raises `[WinError 5] Access is denied` when the
    destination name still exists or was just deleted. Retry, then copy.

    """
    last_error: OSError | None = None
    for delay in (0.0, 0.25, 0.5, 1.0, 2.0):
        if delay:
            time.sleep(delay)
        if final_dir.exists():
            try:
                shutil.rmtree(final_dir)
            except OSError as exc:
                last_error = exc
                continue
        try:
            stage_dir.replace(final_dir)
        except OSError:
            try:
                if final_dir.exists():
                    shutil.rmtree(final_dir)
                shutil.copytree(stage_dir, final_dir)
                shutil.rmtree(stage_dir, ignore_errors=True)
            except OSError as exc:
                last_error = exc
                continue
        if final_dir.is_dir():
            return
        last_error = OSError(f"Swap produced no directory `{final_dir}`")
    msg = f"Failed to swap `{stage_dir}` -> `{final_dir}`: {last_error}"
    raise OSError(msg) from last_error


def default_tray_step_labels(project_root: Path) -> list[str]:
    """Return tray checkbox defaults: full rebuild when empty, quick rebuild when deps exist.

    When `install/dependencies` already has binaries, installers, and/or a uv cache,
    skip wipe and those heavy steps by default. Always leave repos + EXE pack + open on.
    CLI with no flags still uses the full `BuildSteps()` / `DEFAULT_STEP_LABELS` path.

    """
    deps = dependencies_dir(project_root)
    if not deps.is_dir():
        return list(DEFAULT_STEP_LABELS)

    has_binaries = any(_nonempty_file(deps / name) for name in MEDIA_EXE_NAMES)
    has_installers = any(_nonempty_file(deps / name) for name in (GIT_EXE_NAME, UV_WINDOWS_ZIP, VSCODE_EXE_NAME))
    uv_cache = deps / "uv-cache"
    has_uv_cache = uv_cache.is_dir() and any(uv_cache.iterdir())

    if not (has_binaries or has_installers or has_uv_cache):
        return list(DEFAULT_STEP_LABELS)

    selected: list[str] = []
    if not has_binaries:
        selected.append(STEP_BINARIES)
    if not has_installers:
        selected.append(STEP_INSTALLERS)
    selected.append(STEP_REPOS)
    if not has_uv_cache:
        selected.append(STEP_UV_CACHE)
    selected.extend((STEP_BUILD_EXES, STEP_OPEN))
    return selected


def dependencies_dir(project_root: Path) -> Path:
    """Return `install/dependencies/`."""
    return install_dir(project_root) / "dependencies"


def download_url(
    url: str,
    dest: Path,
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
    force: bool = True,
) -> bool:
    """Download HTTPS URL to `dest`. Return `False` if skipped (exists and not force)."""
    validate_https_url(url)
    if dest.is_file() and dest.stat().st_size > 0 and not force:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + f".tmp.{uuid.uuid4().hex}")
    try:
        download_https_to_path(
            url,
            tmp,
            headers=github_download_headers(
                url,
                config=config,
                project_root=project_root,
                user_agent=GITHUB_UA,
            ),
            timeout=DOWNLOAD_TIMEOUT,
            chunk_size=DOWNLOAD_CHUNK,
        )
        tmp.replace(dest)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
    return True


def extract_exe_from_zip(zip_path: Path, dest_dir: Path, exe_name: str, *, overwrite: bool = True) -> Path | None:
    """Extract a single EXE from a zip into `dest_dir` by basename match."""
    target = dest_dir / exe_name
    if target.is_file() and target.stat().st_size > 0 and not overwrite:
        return target
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if name.replace("\\", "/").rstrip("/").endswith(exe_name):
                with tempfile.TemporaryDirectory() as tmp:
                    tmp_path = Path(tmp)
                    zf.extract(name, tmp_path)
                    extracted = tmp_path / name
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(extracted, target)
                return target
    return None


def fetch_github_release_latest(
    owner: str,
    repo: str,
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Fetch latest GitHub release JSON."""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    validate_https_url(url)
    req = Request(
        url,
        headers=github_api_headers(config=config, project_root=project_root, user_agent=GITHUB_UA),
    )
    with urlopen(req, timeout=30, context=https_ssl_context()) as resp:  # noqa: S310
        return json.loads(resp.read().decode())


def install_dir(project_root: Path) -> Path:
    """Return `install/` under the project root."""
    return project_root / "install"


def open_install_folder(project_root: Path, log: LogFn) -> None:
    """Open `install/` in the system file manager."""
    path = install_dir(project_root)
    path.mkdir(parents=True, exist_ok=True)
    try:
        h.file.open_file_or_folder(path)
    except Exception:
        if sys.platform == "win32":
            os.startfile(str(path))  # noqa: S606
        else:
            raise
    log(f"Opened `{path}`")


def populate_binaries(
    project_root: Path,
    log: LogFn,
    *,
    config: dict[str, Any] | None = None,
    force: bool = True,
) -> None:
    """Copy or download media binaries into `install/dependencies/`."""
    deps = dependencies_dir(project_root)
    deps.mkdir(parents=True, exist_ok=True)

    log("==> Copy binaries from repo root (if present)")
    for exe_name in MEDIA_EXE_NAMES:
        src = project_root / exe_name
        dest = deps / exe_name
        if src.is_file():
            if force or not _nonempty_file(dest):
                shutil.copy2(src, dest)
                log(f"  Copied {exe_name}")
            else:
                log(f"  Keep existing {exe_name}")
        else:
            log(f"  Not found: {exe_name} (will rely on zip fallback)")

    log("==> Download fallback zip archives")
    try:
        release = fetch_github_release_latest("AOMediaCodec", "libavif", config=config, project_root=project_root)
        url = asset_download_url(release, asset_name=LIBAVIF_ZIP_NAME)
        dest = deps / LIBAVIF_ZIP_NAME
        if download_url(url, dest, config=config, project_root=project_root, force=force):
            log(f"  Downloaded {LIBAVIF_ZIP_NAME}")
        else:
            log(f"  Keep existing {LIBAVIF_ZIP_NAME}")
    except (HTTPError, URLError, ValueError, OSError) as exc:
        log(f"  Skip libavif zip: {exc}")

    try:
        release = fetch_github_release_latest("BtbN", "FFmpeg-Builds", config=config, project_root=project_root)
        try:
            url = asset_download_url(release, asset_name=FFMPEG_ZIP_NAME)
        except ValueError:
            url = asset_download_url(release, name_contains=("win64", "gpl", ".zip"))
        dest = deps / FFMPEG_ZIP_NAME
        if download_url(url, dest, config=config, project_root=project_root, force=force):
            log(f"  Downloaded {FFMPEG_ZIP_NAME}")
        else:
            log(f"  Keep existing {FFMPEG_ZIP_NAME}")
    except (HTTPError, URLError, ValueError, OSError) as exc:
        log(f"  Skip FFmpeg zip: {exc}")

    w_zip = deps / LIBAVIF_ZIP_NAME
    enc = deps / "avifenc.exe"
    dec = deps / "avifdec.exe"
    if w_zip.is_file():
        if _nonempty_file(enc) and _nonempty_file(dec):
            w_zip.unlink(missing_ok=True)
            log(f"  Removed redundant {LIBAVIF_ZIP_NAME}")
        else:
            log("==> Extract avifenc.exe / avifdec.exe")
            ok_enc = extract_exe_from_zip(w_zip, deps, "avifenc.exe", overwrite=force) is not None
            ok_dec = extract_exe_from_zip(w_zip, deps, "avifdec.exe", overwrite=force) is not None
            if ok_enc and ok_dec and _nonempty_file(enc) and _nonempty_file(dec):
                w_zip.unlink(missing_ok=True)
                log(f"  Removed {LIBAVIF_ZIP_NAME} after extract.")
            else:
                log(f"  Keeping {LIBAVIF_ZIP_NAME} (extract incomplete).")

    ff_zip = deps / FFMPEG_ZIP_NAME
    ff_exe = deps / "ffmpeg.exe"
    if ff_zip.is_file():
        if _nonempty_file(ff_exe):
            ff_zip.unlink(missing_ok=True)
            log(f"  Removed redundant {FFMPEG_ZIP_NAME}")
        else:
            log("==> Extract ffmpeg.exe")
            ok_ff = extract_exe_from_zip(ff_zip, deps, "ffmpeg.exe", overwrite=force) is not None
            if ok_ff and _nonempty_file(ff_exe):
                ff_zip.unlink(missing_ok=True)
                log(f"  Removed {FFMPEG_ZIP_NAME} after extract.")
            else:
                log(f"  Keeping {FFMPEG_ZIP_NAME} (extract failed).")


def populate_installers(
    project_root: Path,
    log: LogFn,
    *,
    config: dict[str, Any] | None = None,
    force: bool = True,
) -> None:
    """Download Git, uv, and VS Code installers into `install/dependencies/`."""
    deps = dependencies_dir(project_root)
    deps.mkdir(parents=True, exist_ok=True)

    log("==> Download Git for Windows installer")
    try:
        release = fetch_github_release_latest("git-for-windows", "git", config=config, project_root=project_root)
        url = asset_download_url(release, name_contains=("64-bit.exe",))
        dest = deps / GIT_EXE_NAME
        if download_url(url, dest, config=config, project_root=project_root, force=force):
            log(f"  OK: {GIT_EXE_NAME}")
        else:
            log(f"  Keep existing {GIT_EXE_NAME}")
    except (HTTPError, URLError, ValueError, OSError) as exc:
        log(f"  Skip Git: {exc}")

    log("==> Download uv windows zip")
    uv_dest = deps / UV_WINDOWS_ZIP
    try:
        if not download_url(UV_WINDOWS_URL, uv_dest, config=config, project_root=project_root, force=force):
            log(f"  Keep existing {UV_WINDOWS_ZIP}")
        else:
            log(f"  OK: {UV_WINDOWS_ZIP}")
    except (HTTPError, URLError, ValueError, OSError):
        try:
            release = fetch_github_release_latest("astral-sh", "uv", config=config, project_root=project_root)
            url = asset_download_url(release, asset_name=UV_WINDOWS_ZIP)
            if download_url(url, uv_dest, config=config, project_root=project_root, force=force):
                log(f"  OK: {UV_WINDOWS_ZIP} (API)")
            else:
                log(f"  Keep existing {UV_WINDOWS_ZIP}")
        except (HTTPError, URLError, ValueError, OSError) as exc:
            log(f"  Skip uv: {exc}")

    log("==> Download VS Code user installer")
    try:
        dest = deps / VSCODE_EXE_NAME
        if download_url(VSCODE_URL, dest, config=config, project_root=project_root, force=force):
            log(f"  OK: {VSCODE_EXE_NAME}")
        else:
            log(f"  Keep existing {VSCODE_EXE_NAME}")
    except (HTTPError, URLError, ValueError, OSError) as exc:
        log(f"  Skip VS Code: {exc}")

    from harrix_swiss_knife.installer.vscode_ext import populate_vscode_python_extensions  # noqa: PLC0415

    populate_vscode_python_extensions(
        project_root,
        log,
        download_url=download_url,
        config=config,
        force=force,
    )


def populate_uv_cache(
    project_root: Path,
    log: LogFn,
) -> None:
    """Warm `uv-python-cache` and `uv-cache` without touching the live `.venv`.

    Installs a throwaway CPython and project venvs under a temp directory, so the
    running tray app can keep its interpreter locked.

    """
    if shutil.which("uv") is None:
        msg = "uv is not on PATH"
        raise RuntimeError(msg)

    deps = dependencies_dir(project_root)
    deps.mkdir(parents=True, exist_ok=True)
    py_version = _python_version(project_root)
    py_cache = deps / "uv-python-cache"
    py_cache.mkdir(parents=True, exist_ok=True)

    log("==> Populate uv python cache (managed CPython, isolated install dir)")
    with tempfile.TemporaryDirectory(prefix="hsk-uv-warm-") as tmp_raw:
        tmp = Path(tmp_raw)
        python_install = tmp / "python-install"
        python_install.mkdir()
        env = uv_isolated_env(
            python_cache_dir=py_cache,
            python_install_dir=python_install,
        )
        log(f"  UV_PYTHON_CACHE_DIR={py_cache}")
        log(f"  UV_PYTHON_INSTALL_DIR={python_install}")
        code, _text = _run_uv(
            ["python", "install", py_version],
            cwd=project_root,
            env=env,
            log=log,
        )
        if code != 0:
            log(f"  uv python install exited with code {code} (continue; package cache still runs)")
        else:
            log(f"  OK: managed Python {py_version} cached in uv-python-cache")

        log("==> Populate uv cache (sibling repos, isolated venvs)")
        final_dir = deps / "uv-cache"
        stage_dir = deps / f"uv-cache.stage.{uuid.uuid4().hex}"
        if stage_dir.exists():
            shutil.rmtree(stage_dir)
        stage_dir.mkdir(parents=True)
        all_ok = True
        try:
            for name, path in sibling_repos(project_root):
                if not (path / "pyproject.toml").is_file():
                    log(f"  Skip {name}: pyproject.toml not found at {path}")
                    all_ok = False
                    continue
                venv_dir = tmp / "venvs" / name
                env = uv_isolated_env(
                    cache_dir=stage_dir,
                    python_cache_dir=py_cache,
                    python_install_dir=python_install,
                    project_environment=venv_dir,
                )
                log(f"  uv sync in {name} ({path})")
                log(f"    UV_PROJECT_ENVIRONMENT={venv_dir}")
                code, _text = _run_uv(
                    ["sync", "--python", py_version],
                    cwd=path,
                    env=env,
                    log=log,
                )
                if code != 0:
                    log(f"  {name}: uv sync exited with code {code}")
                    all_ok = False
                else:
                    log(f"  OK: {name}")

            if all_ok:
                log("  Swap uv cache (stage -> final)")
                commit_stage_dir(stage_dir, final_dir)
            else:
                msg = "uv cache incomplete; kept previous uv-cache/ if any"
                raise RuntimeError(msg)
        finally:
            if stage_dir.exists():
                shutil.rmtree(stage_dir, ignore_errors=True)


def redundant_media_zip_names(deps: Path) -> set[str]:
    """Names of fallback zips to omit when loose tools already exist."""
    names: set[str] = set()
    if not deps.is_dir():
        return names
    if (
        _nonempty_file(deps / "avifenc.exe")
        and _nonempty_file(deps / "avifdec.exe")
        and (deps / LIBAVIF_ZIP_NAME).is_file()
    ):
        names.add(LIBAVIF_ZIP_NAME)
    if _nonempty_file(deps / "ffmpeg.exe") and (deps / FFMPEG_ZIP_NAME).is_file():
        names.add(FFMPEG_ZIP_NAME)
    return names


def run_pipeline(
    project_root: Path,
    steps: BuildSteps,
    *,
    config: dict[str, Any] | None = None,
    log: LogFn | None = None,
) -> PipelineResult:
    """Run selected builder steps in order."""
    lines: list[str] = []

    def _log(message: str) -> None:
        lines.append(message)
        if log is not None:
            log(message)
        else:
            print(message)

    if not steps.any_work() and not steps.open_install:
        _log("❌ No steps selected.")
        return PipelineResult(ok=False, lines=lines)

    online_zip: Path | None = None
    offline_zip: Path | None = None
    try:
        if steps.wipe_dependencies:
            wipe_dependencies(project_root, _log)
        if steps.binaries:
            populate_binaries(project_root, _log, config=config, force=steps.wipe_dependencies)
        if steps.installers:
            populate_installers(project_root, _log, config=config, force=steps.wipe_dependencies)
        if steps.repos:
            snapshot_repos(project_root, _log)
        if steps.uv_cache:
            populate_uv_cache(project_root, _log)
        if steps.build_zips:
            online_zip, offline_zip = build_install_exes(project_root, _log)
        if steps.clean_logs:
            clean_install_logs(project_root, _log)
        if steps.open_install:
            open_install_folder(project_root, _log)
    except Exception as exc:
        _log(f"❌ {exc}")
        return PipelineResult(ok=False, lines=lines, online_zip=online_zip, offline_zip=offline_zip)

    _log("✅ Install EXE pipeline finished.")
    return PipelineResult(ok=True, lines=lines, online_zip=online_zip, offline_zip=offline_zip)


def sibling_repos(project_root: Path) -> list[tuple[str, Path]]:
    """Return `(name, path)` for pylib, pyssg, and this repo."""
    parent = project_root.parent
    items = [(name, parent / name) for name in SIBLING_REPO_NAMES]
    items.append((HSK_REPO_NAME, project_root))
    return items


def snapshot_repos(project_root: Path, log: LogFn) -> None:
    """Write `git archive HEAD` zips into `install/dependencies/repos/`."""
    if shutil.which("git") is None:
        msg = "git is not on PATH"
        raise RuntimeError(msg)

    deps = dependencies_dir(project_root)
    deps.mkdir(parents=True, exist_ok=True)
    final_dir = deps / "repos"
    stage_dir = deps / f"repos.stage.{uuid.uuid4().hex}"
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True)

    log("==> Snapshot sibling repos (git archive HEAD)")
    all_ok = True
    try:
        for name, path in sibling_repos(project_root):
            if not (path / ".git").exists():
                log(f"  Skip {name}: not a git repo at {path}")
                all_ok = False
                continue
            out = stage_dir / f"{name}.zip"
            log(f"  git archive {name} -> {out}")
            proc = subprocess.run(
                ["git", "archive", "--format=zip", f"--output={out}", "HEAD"],  # noqa: S607
                cwd=str(path),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                shell=False,
                creationflags=_no_window_creationflags(),
            )
            if proc.stdout.strip():
                log(proc.stdout.strip())
            if proc.stderr.strip():
                log(proc.stderr.strip())
            if proc.returncode != 0 or not _nonempty_file(out):
                log(f"  {name}: git archive failed (code {proc.returncode})")
                all_ok = False
            else:
                log(f"  OK: {name}")

        if all_ok:
            log("  Swap repos snapshot (stage -> final)")
            commit_stage_dir(stage_dir, final_dir)
        else:
            msg = "Repo snapshot incomplete; kept previous repos/ if any"
            raise RuntimeError(msg)
    finally:
        if stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)


def steps_from_cli_flags(
    *,
    no_wipe: bool = False,
    skip_binaries: bool = False,
    skip_installers: bool = False,
    skip_repos: bool = False,
    skip_uv_cache: bool = False,
    no_zips: bool = False,
    no_exes: bool = False,
    no_open: bool = False,
    clean_logs: bool = False,
) -> BuildSteps:
    """Build step selection from CLI skip flags (default: all on)."""
    return BuildSteps(
        wipe_dependencies=not no_wipe,
        binaries=not skip_binaries,
        installers=not skip_installers,
        repos=not skip_repos,
        uv_cache=not skip_uv_cache,
        build_zips=not (no_zips or no_exes),
        open_install=not no_open,
        clean_logs=clean_logs,
    )


def uv_isolated_env(
    *,
    cache_dir: Path | None = None,
    python_cache_dir: Path | None = None,
    python_install_dir: Path | None = None,
    project_environment: Path | None = None,
) -> dict[str, str]:
    """Env for uv that does not reuse the live tray `.venv` or its interpreter."""
    env = os.environ.copy()
    for key in ("VIRTUAL_ENV", "PYTHONHOME", "UV_PYTHON"):
        env.pop(key, None)
    if cache_dir is not None:
        env["UV_CACHE_DIR"] = str(cache_dir)
    if python_cache_dir is not None:
        env["UV_PYTHON_CACHE_DIR"] = str(python_cache_dir)
    if python_install_dir is not None:
        env["UV_PYTHON_INSTALL_DIR"] = str(python_install_dir)
    if project_environment is not None:
        env["UV_PROJECT_ENVIRONMENT"] = str(project_environment)
    return env


def wipe_dependencies(project_root: Path, log: LogFn) -> None:
    """Remove `install/dependencies` entirely."""
    deps = dependencies_dir(project_root)
    if not deps.exists():
        log(f"`{deps}` not present (nothing to wipe).")
        return
    log(f"Removing `{deps}`…")
    shutil.rmtree(deps)
    if deps.exists():
        msg = f"Failed to remove `{deps}`. Close programs using those files and retry."
        raise OSError(msg)
    log("✅ Dependencies folder removed.")


def _no_window_creationflags() -> int:
    """Hide console Windows for child processes on Windows."""
    if sys.platform != "win32":
        return 0
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0))


def _nonempty_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def _python_version(project_root: Path) -> str:
    version_file = project_root / ".python-version"
    if version_file.is_file():
        line = version_file.read_text(encoding="utf-8").splitlines()
        if line and line[0].strip():
            return line[0].strip()
    return "3.13"


def _run_uv(
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    log: LogFn,
) -> tuple[int, str]:
    uv = shutil.which("uv") or "uv"
    cmd = [uv, *args]
    log(f"  $ {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            shell=False,
            creationflags=_no_window_creationflags(),
        )
    except OSError as exc:
        return 1, str(exc)
    out = "\n".join(part for part in ((proc.stdout or "").strip(), (proc.stderr or "").strip()) if part)
    if out:
        log(out)
    return int(proc.returncode), out


STEP_WIPE = "Wipe install/dependencies first"
STEP_BINARIES = "Media binaries (ffmpeg, avifenc, avifdec)"
STEP_INSTALLERS = "Installers (Git, uv, VS Code)"
STEP_REPOS = "Repo snapshots (git archive of siblings)"
STEP_UV_CACHE = "uv cache (isolated; safe while tray is running)"
STEP_BUILD_EXES = "Build installer EXEs (online + offline)"
STEP_BUILD_ZIPS = STEP_BUILD_EXES  # back-compat alias for imports
STEP_OPEN = "Open install/ when finished"
STEP_CLEAN_LOGS = "Clean *.log under install/"

ALL_STEP_LABELS: tuple[str, ...] = (
    STEP_WIPE,
    STEP_BINARIES,
    STEP_INSTALLERS,
    STEP_REPOS,
    STEP_UV_CACHE,
    STEP_BUILD_EXES,
    STEP_OPEN,
    STEP_CLEAN_LOGS,
)

DEFAULT_STEP_LABELS: tuple[str, ...] = (
    STEP_WIPE,
    STEP_BINARIES,
    STEP_INSTALLERS,
    STEP_REPOS,
    STEP_UV_CACHE,
    STEP_BUILD_EXES,
    STEP_OPEN,
)

# Same as DEFAULT — used by the tray "Full rebuild" preset.
FULL_REBUILD_STEP_LABELS: tuple[str, ...] = DEFAULT_STEP_LABELS

# Fast tray preset: refresh repo snapshots and re-pack EXEs only.
QUICK_REBUILD_STEP_LABELS: tuple[str, ...] = (
    STEP_REPOS,
    STEP_BUILD_EXES,
    STEP_OPEN,
)

"""Build online/offline install zip bundles under `install/`.

Replaces the numbered bat/PowerShell builder pipeline. Target-PC payload scripts
(`install.bat`, `install-with-log.ps1`, `harrix-swiss-knife.ps1`) are copied into
the zips unchanged.

"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
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
from harrix_swiss_knife.integrations.http_download import download_https_to_path
from harrix_swiss_knife.integrations.http_transport import https_ssl_context

GITHUB_UA = "Harrix-Swiss-Knife/1.0 (Python; install-zip-builder)"
DOWNLOAD_CHUNK = 256 * 1024
DOWNLOAD_TIMEOUT = 120
SIBLING_REPO_NAMES = ("harrix-pylib", "harrix-pyssg")
HSK_REPO_NAME = "harrix-swiss-knife"
ONLINE_ZIP_NAME = "install-harrix-swiss-knife.zip"
OFFLINE_ZIP_NAME = "install-offline-harrix-swiss-knife.zip"
ONLINE_EXCLUDE_DIRS = frozenset({"repos", "uv-cache", "uv-python-cache"})
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
    build_zips: bool = True
    open_install: bool = True
    clean_logs: bool = False

    @classmethod
    def all_steps(cls) -> BuildSteps:
        """Return the full default pipeline (CLI default)."""
        return cls()

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
            build_zips=STEP_BUILD_ZIPS in selected,
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


def build_install_zips(project_root: Path, log: LogFn) -> tuple[Path, Path]:
    """Create online and offline install zip archives under `install/`."""
    root = install_dir(project_root)
    deps = dependencies_dir(project_root)
    if not deps.is_dir():
        msg = f"Not found: {deps}"
        raise FileNotFoundError(msg)

    required = ("harrix-swiss-knife.ps1", "install.bat", "install-with-log.ps1")
    for name in required:
        if not (root / name).is_file():
            msg = f"Not found: {root / name}"
            raise FileNotFoundError(msg)

    out_online = root / ONLINE_ZIP_NAME
    out_offline = root / OFFLINE_ZIP_NAME
    omit = redundant_media_zip_names(deps)
    log(f"Building:\n  {out_online}\n  {out_offline}")
    if omit:
        log(f"  Omitting redundant media zips: {', '.join(sorted(omit))}")

    stage_base = Path(tempfile.mkdtemp(prefix="hsk-install-zip-"))
    try:
        stage_online = stage_base / "online"
        stage_offline = stage_base / "offline"
        stage_online.mkdir()
        stage_offline.mkdir()

        for name in required:
            shutil.copy2(root / name, stage_online / name)
            shutil.copy2(root / name, stage_offline / name)

        _copy_deps(deps, stage_online / "dependencies", exclude_dirs=ONLINE_EXCLUDE_DIRS, exclude_files=omit)
        _zip_dir(stage_online, out_online)
        log(f"✅ Created: {out_online}")

        _copy_deps(deps, stage_offline / "dependencies", exclude_dirs=frozenset(), exclude_files=omit)
        _zip_dir(stage_offline, out_offline)
        log(f"✅ Created: {out_offline}")
    finally:
        shutil.rmtree(stage_base, ignore_errors=True)

    return out_online, out_offline


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
        flags.append("--no-zips")
    if not steps.open_install:
        flags.append("--no-open")
    if steps.clean_logs:
        flags.append("--clean-logs")
    return flags


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


def list_hsk_pids(project_root: Path) -> list[int]:
    """Return PIDs of Harrix Swiss Knife processes holding this repo's `.venv`."""
    if sys.platform != "win32":
        return []
    venv_scripts = str((project_root / ".venv" / "Scripts").resolve()).replace("'", "''")
    # Match tray: python(w) under .venv\\Scripts, or command line with main.py.
    script = (
        f"$venv = '{venv_scripts}'; "
        "$seen = @{}; "
        "foreach ($name in @('python','pythonw')) { "
        "  Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object { "
        "    try { $p = [string]$_.Path } catch { $p = '' }; "
        "    if ($p -and $venv -and ($p.Length -ge $venv.Length) -and "
        "($p.Substring(0, $venv.Length) -ieq $venv)) { "
        "      $seen[[int]$_.Id] = $true "
        "    } "
        "  } "
        "}; "
        "Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { "
        "  $_.Name -match '^(?i)pythonw?\\.exe$' -and $_.CommandLine -and "
        "  ($_.CommandLine -match 'harrix_swiss_knife[\\\\/]+main\\.py') "
        "} | ForEach-Object { $seen[[int]$_.ProcessId] = $true }; "
        "$seen.Keys"
    )
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],  # noqa: S607
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            shell=False,
        )
    except OSError:
        return []
    pids: set[int] = set()
    for raw_line in proc.stdout.splitlines():
        stripped = raw_line.strip()
        if stripped.isdigit():
            pids.add(int(stripped))
    return sorted(pids)


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
        download_url(url, deps / LIBAVIF_ZIP_NAME, config=config, project_root=project_root, force=force)
        log(f"  Downloaded {LIBAVIF_ZIP_NAME}")
    except (HTTPError, URLError, ValueError, OSError) as exc:
        log(f"  Skip libavif zip: {exc}")

    try:
        release = fetch_github_release_latest("BtbN", "FFmpeg-Builds", config=config, project_root=project_root)
        try:
            url = asset_download_url(release, asset_name=FFMPEG_ZIP_NAME)
        except ValueError:
            url = asset_download_url(release, name_contains=("win64", "gpl", ".zip"))
        download_url(url, deps / FFMPEG_ZIP_NAME, config=config, project_root=project_root, force=force)
        log(f"  Downloaded {FFMPEG_ZIP_NAME}")
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
        download_url(url, deps / GIT_EXE_NAME, config=config, project_root=project_root, force=force)
        log(f"  OK: {GIT_EXE_NAME}")
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
            download_url(url, uv_dest, config=config, project_root=project_root, force=force)
            log(f"  OK: {UV_WINDOWS_ZIP} (API)")
        except (HTTPError, URLError, ValueError, OSError) as exc:
            log(f"  Skip uv: {exc}")

    log("==> Download VS Code user installer")
    try:
        download_url(VSCODE_URL, deps / VSCODE_EXE_NAME, config=config, project_root=project_root, force=force)
        log(f"  OK: {VSCODE_EXE_NAME}")
    except (HTTPError, URLError, ValueError, OSError) as exc:
        log(f"  Skip VS Code: {exc}")


def populate_uv_cache(
    project_root: Path,
    log: LogFn,
    *,
    interactive: bool = True,
) -> None:
    """Warm `uv-python-cache` and `uv-cache` under `install/dependencies/`."""
    if shutil.which("uv") is None:
        msg = "uv is not on PATH"
        raise RuntimeError(msg)

    deps = dependencies_dir(project_root)
    deps.mkdir(parents=True, exist_ok=True)

    log("==> Populate uv python cache (managed CPython)")
    wait_until_hsk_closed(
        project_root,
        log,
        why="uv cannot replace Python files while the tray app holds them.",
        interactive=interactive,
    )
    py_cache = deps / "uv-python-cache"
    py_cache.mkdir(parents=True, exist_ok=True)
    py_version = "3.13"
    version_file = project_root / ".python-version"
    if version_file.is_file():
        line = version_file.read_text(encoding="utf-8").splitlines()
        if line and line[0].strip():
            py_version = line[0].strip()

    env = os.environ.copy()
    env["UV_PYTHON_CACHE_DIR"] = str(py_cache)
    log(f"  UV_PYTHON_CACHE_DIR={py_cache}")
    code = _uv_with_hsk_retry(
        project_root,
        ["python", "install", py_version],
        cwd=project_root,
        env=env,
        log=log,
        label="uv python install",
        interactive=interactive,
    )
    if code != 0:
        log(f"  uv python install exited with code {code} (continue; package cache still runs)")
    else:
        log(f"  OK: managed Python {py_version} cached in uv-python-cache")

    log("==> Populate uv cache (sibling repos)")
    final_dir = deps / "uv-cache"
    stage_dir = deps / f"uv-cache.stage.{uuid.uuid4().hex}"
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True)

    env = os.environ.copy()
    env["UV_CACHE_DIR"] = str(stage_dir)
    all_ok = True
    try:
        for name, path in sibling_repos(project_root):
            if not (path / "pyproject.toml").is_file():
                log(f"  Skip {name}: pyproject.toml not found at {path}")
                all_ok = False
                continue
            log(f"  uv sync in {name} ({path})")
            code = _uv_with_hsk_retry(
                project_root,
                ["sync", "--reinstall"],
                cwd=path,
                env=env,
                log=log,
                label=f"uv sync ({name})",
                interactive=interactive,
            )
            if code != 0:
                log(f"  {name}: uv sync exited with code {code}")
                all_ok = False
            else:
                log(f"  OK: {name}")

        if all_ok:
            log("  Swap uv cache (stage -> final)")
            if final_dir.exists():
                shutil.rmtree(final_dir)
            stage_dir.replace(final_dir)
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
    interactive: bool = True,
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
            populate_binaries(project_root, _log, config=config, force=True)
        if steps.installers:
            populate_installers(project_root, _log, config=config, force=True)
        if steps.repos:
            snapshot_repos(project_root, _log)
        if steps.uv_cache:
            populate_uv_cache(project_root, _log, interactive=interactive)
        if steps.build_zips:
            online_zip, offline_zip = build_install_zips(project_root, _log)
        if steps.clean_logs:
            clean_install_logs(project_root, _log)
        if steps.open_install:
            open_install_folder(project_root, _log)
    except Exception as exc:
        _log(f"❌ {exc}")
        return PipelineResult(ok=False, lines=lines, online_zip=online_zip, offline_zip=offline_zip)

    _log("✅ Install zip pipeline finished.")
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
            if final_dir.exists():
                shutil.rmtree(final_dir)
            stage_dir.replace(final_dir)
        else:
            msg = "Repo snapshot incomplete; kept previous repos/ if any"
            raise RuntimeError(msg)
    finally:
        if stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)


def spawn_pipeline_console(project_root: Path, steps: BuildSteps) -> subprocess.Popen[Any]:
    """Start the pipeline in a new console window (Windows); returns immediately."""
    if sys.platform != "win32":
        msg = "New console spawn is only supported on Windows."
        raise RuntimeError(msg)

    # Run via the same interpreter; -c avoids depending on hsk being on PATH.
    # New console lets the user Exit the tray while uv cache runs.
    code = (
        "from harrix_swiss_knife.actions.common.install_zip_builder import run_pipeline, steps_from_cli_flags; "
        "from harrix_swiss_knife.paths import get_project_root; "
        f"steps = steps_from_cli_flags("
        f"no_wipe={not steps.wipe_dependencies}, "
        f"skip_binaries={not steps.binaries}, "
        f"skip_installers={not steps.installers}, "
        f"skip_repos={not steps.repos}, "
        f"skip_uv_cache={not steps.uv_cache}, "
        f"no_zips={not steps.build_zips}, "
        f"no_open={not steps.open_install}, "
        f"clean_logs={steps.clean_logs}); "
        "result = run_pipeline(get_project_root(), steps, interactive=True); "
        "print(); "
        "input('Press Enter to close this window… '); "
        "raise SystemExit(0 if result.ok else 1)"
    )
    # Prefer console python.exe when the tray runs under pythonw.exe.
    python = Path(sys.executable)
    if python.name.lower() == "pythonw.exe":
        candidate = python.with_name("python.exe")
        if candidate.is_file():
            python = candidate
    creationflags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
    return subprocess.Popen(
        [str(python), "-c", code],
        cwd=str(project_root),
        creationflags=creationflags,
        shell=False,
    )


def steps_from_cli_flags(
    *,
    no_wipe: bool = False,
    skip_binaries: bool = False,
    skip_installers: bool = False,
    skip_repos: bool = False,
    skip_uv_cache: bool = False,
    no_zips: bool = False,
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
        build_zips=not no_zips,
        open_install=not no_open,
        clean_logs=clean_logs,
    )


def wait_until_hsk_closed(
    project_root: Path,
    log: LogFn,
    *,
    why: str,
    interactive: bool,
    exclude_pid: int | None = None,
) -> None:
    """Block until no HSK tray processes remain (interactive) or raise."""
    while True:
        pids = [pid for pid in list_hsk_pids(project_root) if pid != exclude_pid]
        # Current process may itself be the tray — exclude self
        self_pid = os.getpid()
        pids = [pid for pid in pids if pid != self_pid]
        if not pids:
            return
        log(f"⚠️ Harrix Swiss Knife is still running. {why}")
        log(f"  PIDs: {', '.join(str(p) for p in pids)}")
        if not interactive:
            msg = "Quit the tray app (Exit), then re-run this command."
            raise RuntimeError(msg)
        log("Quit from the tray icon (Exit), then press Enter to retry.")
        try:
            input()
        except EOFError as exc:
            msg = "Tray still running and stdin closed."
            raise RuntimeError(msg) from exc


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


def _copy_deps(
    src_deps: Path,
    dst_deps: Path,
    *,
    exclude_dirs: frozenset[str],
    exclude_files: set[str],
) -> None:
    dst_deps.mkdir(parents=True, exist_ok=True)
    for child in src_deps.iterdir():
        if child.is_dir():
            if child.name in exclude_dirs:
                continue
            shutil.copytree(child, dst_deps / child.name, dirs_exist_ok=True)
        else:
            if child.suffix.lower() == ".log":
                continue
            if child.name in exclude_files:
                continue
            shutil.copy2(child, dst_deps / child.name)


def _nonempty_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


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
        )
    except OSError as exc:
        return 1, str(exc)
    out = "\n".join(part for part in ((proc.stdout or "").strip(), (proc.stderr or "").strip()) if part)
    if out:
        log(out)
    return int(proc.returncode), out


def _uv_with_hsk_retry(
    project_root: Path,
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    log: LogFn,
    label: str,
    interactive: bool,
) -> int:
    while True:
        wait_until_hsk_closed(
            project_root,
            log,
            why=label,
            interactive=interactive,
        )
        code, text = _run_uv(args, cwd=cwd, env=env, log=log)
        if code == 0:
            return 0
        locked = "Access is denied" in text or "os error 5" in text.lower()
        if not locked or not interactive:
            return code
        log(f"  {label} failed (Access is denied). Close Harrix Swiss Knife if it is still open.")
        try:
            input("Press Enter to retry… ")
        except EOFError:
            return code


def _zip_dir(source_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(source_dir).as_posix())


STEP_WIPE = "Wipe install/dependencies first"
STEP_BINARIES = "Media binaries (ffmpeg, avifenc, avifdec)"
STEP_INSTALLERS = "Installers (Git, uv, VS Code)"
STEP_REPOS = "Repo snapshots (git archive of siblings)"
STEP_UV_CACHE = "uv cache (quit tray app if it holds .venv)"
STEP_BUILD_ZIPS = "Build zip archives"
STEP_OPEN = "Open install/ when finished"
STEP_CLEAN_LOGS = "Clean *.log under install/"

ALL_STEP_LABELS: tuple[str, ...] = (
    STEP_WIPE,
    STEP_BINARIES,
    STEP_INSTALLERS,
    STEP_REPOS,
    STEP_UV_CACHE,
    STEP_BUILD_ZIPS,
    STEP_OPEN,
    STEP_CLEAN_LOGS,
)

DEFAULT_STEP_LABELS: tuple[str, ...] = (
    STEP_WIPE,
    STEP_BINARIES,
    STEP_INSTALLERS,
    STEP_REPOS,
    STEP_UV_CACHE,
    STEP_BUILD_ZIPS,
    STEP_OPEN,
)

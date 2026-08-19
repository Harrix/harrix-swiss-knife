"""Install ffmpeg / avifenc / avifdec into the project root."""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.request import Request, urlopen

from harrix_swiss_knife.installer.constants import (
    FFMPEG_ZIP_NAME,
    GITHUB_UA,
    LIBAVIF_ZIP_NAME,
    MEDIA_EXE_NAMES,
)
from harrix_swiss_knife.installer.prereqs import find_local_dependency
from harrix_swiss_knife.integrations.http_download import download_https_to_path
from harrix_swiss_knife.integrations.http_transport import https_ssl_context

if TYPE_CHECKING:
    from harrix_swiss_knife.installer.log import OutcomeLog


def install_optimize_binaries(
    project_root: Path,
    *,
    deps: Path,
    skip_download: bool,
    log: OutcomeLog,
) -> None:
    """Copy or download ffmpeg / avifenc / avifdec into the project root."""
    log.step("Optimize dependencies (ffmpeg, avifenc, avifdec)")
    need = list(MEDIA_EXE_NAMES)
    if all((project_root / name).is_file() for name in need):
        log.add("already", "Optimize binaries already present")
        return

    for exe in MEDIA_EXE_NAMES:
        dest = project_root / exe
        src = deps / exe
        if not dest.is_file() and src.is_file():
            shutil.copy2(src, dest)
            log.add("installed", f"Copied {exe} from offline bundle")

    if all((project_root / name).is_file() for name in need):
        return

    if skip_download:
        missing = [n for n in need if not (project_root / n).is_file()]
        if missing:
            log.add("skipped", f"Optimize binaries incomplete; download skipped: {', '.join(missing)}")
        return

    with tempfile.TemporaryDirectory(prefix="hsk-bins-") as tmp:
        tmp_path = Path(tmp)
        if not all((project_root / n).is_file() for n in ("avifenc.exe", "avifdec.exe")):
            zip_lib = find_local_dependency(deps, LIBAVIF_ZIP_NAME) or find_local_dependency(deps, "libavif*.zip")
            if zip_lib is None:
                log.detail("Download libavif windows-artifacts…")
                release = _fetch_github_release_latest("AOMediaCodec", "libavif")
                url = _asset_download_url(release, asset_name=LIBAVIF_ZIP_NAME)
                zip_lib = tmp_path / "libavif.zip"
                download_https_to_path(url, zip_lib, headers=_github_headers(), timeout=180)
            for exe in ("avifenc.exe", "avifdec.exe"):
                if (project_root / exe).is_file():
                    continue
                path = _extract_exe_from_zip(zip_lib, project_root, exe)
                if path:
                    log.add("installed", f"Extracted {exe}")
                else:
                    log.add("skipped", f"{exe} not found in archive")
        if not (project_root / "ffmpeg.exe").is_file():
            zip_ff = find_local_dependency(deps, "ffmpeg*-win64*gpl*.zip") or find_local_dependency(
                deps, FFMPEG_ZIP_NAME
            )
            if zip_ff is None:
                log.detail("Download FFmpeg…")
                release = _fetch_github_release_latest("BtbN", "FFmpeg-Builds")
                try:
                    url = _asset_download_url(release, asset_name=FFMPEG_ZIP_NAME)
                except ValueError:
                    url = _asset_download_url(release, name_contains=("win64", "gpl"))
                zip_ff = tmp_path / "ffmpeg.zip"
                download_https_to_path(url, zip_ff, headers=_github_headers(), timeout=180)
            path = _extract_exe_from_zip(zip_ff, project_root, "ffmpeg.exe")
            if path:
                log.add("installed", "Extracted ffmpeg.exe")
            else:
                log.add("skipped", "ffmpeg.exe not found in archive")


def _asset_download_url(
    release: dict[str, Any],
    *,
    asset_name: str | None = None,
    name_contains: tuple[str, ...] = (),
) -> str:
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
    msg = f"No asset matching {name_contains} found in release"
    raise ValueError(msg)


def _extract_exe_from_zip(zip_path: Path, dest_dir: Path, exe_name: str) -> Path | None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if name.replace("\\", "/").rstrip("/").endswith(exe_name):
                with tempfile.TemporaryDirectory() as tmp:
                    zf.extract(name, tmp)
                    extracted = Path(tmp) / name
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    target = dest_dir / exe_name
                    shutil.copy2(extracted, target)
                    return target
    return None


def _fetch_github_release_latest(owner: str, repo: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    req = Request(url, headers=_github_headers(), method="GET")
    with urlopen(req, timeout=30, context=https_ssl_context()) as resp:  # noqa: S310
        return json.loads(resp.read().decode())


def _github_headers() -> dict[str, str]:
    return {"User-Agent": GITHUB_UA, "Accept": "application/vnd.github+json"}

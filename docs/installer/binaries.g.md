---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `binaries.py`

## 🔧 Function `install_optimize_binaries`

```python
def install_optimize_binaries(project_root: Path, *, deps: Path, skip_download: bool, log: OutcomeLog) -> None
```

Copy or download ffmpeg / avifenc / avifdec into the project root.

<details>
<summary>Code:</summary>

```python
def install_optimize_binaries(
    project_root: Path,
    *,
    deps: Path,
    skip_download: bool,
    log: OutcomeLog,
) -> None:
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
```

</details>

"""Appended zip overlay inside frozen installer EXEs."""

from __future__ import annotations

import os
import shutil
import struct
import sys
import tempfile
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import BinaryIO

from harrix_swiss_knife.installer.constants import OVERLAY_MAGIC, OVERLAY_TRAILER_SIZE

LogFn = Callable[[str], None]
ProgressFn = Callable[[int, int], None]

# `\\?\` lifts the 260-character MAX_PATH limit; uv-cache entries easily exceed it.
_LONG_PATH_PREFIX = "\\\\?\\"
_COPY_CHUNK = 1024 * 1024
_LOG_EVERY = 200
_NAME_PARTS_MAX = 3


class _OffsetView:
    """Seekable view of a byte range inside an already-open binary file."""

    def __init__(self, handle: BinaryIO, start: int, length: int) -> None:
        self._handle = handle
        self._start = start
        self._length = length
        self._handle.seek(start)

    def read(self, size: int = -1) -> bytes:
        pos = self.tell()
        if size is None or size < 0:
            size = self._length - pos
        size = max(0, min(size, self._length - pos))
        return self._handle.read(size)

    def readable(self) -> bool:
        return True

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            target = self._start + offset
        elif whence == 1:
            target = self._handle.tell() + offset
        else:
            target = self._start + self._length + offset
        target = min(max(target, self._start), self._start + self._length)
        self._handle.seek(target)
        return self.tell()

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self._handle.tell() - self._start


def append_overlay_zip(stub_exe: Path, zip_path: Path, out_exe: Path) -> None:
    """Copy stub and append zip bytes + length + magic."""
    zip_bytes = zip_path.read_bytes()
    out_exe.parent.mkdir(parents=True, exist_ok=True)
    with out_exe.open("wb") as out, stub_exe.open("rb") as stub:
        while True:
            chunk = stub.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
        out.write(zip_bytes)
        out.write(struct.pack("<Q", len(zip_bytes)))
        out.write(OVERLAY_MAGIC)


def create_work_dir() -> Path:
    r"""Create a short-path work folder so deep payload entries stay manageable.

    Deep `uv-cache` paths plus the long `%LOCALAPPDATA%\Temp` prefix overflow
    `MAX_PATH` for tools that do not opt into long paths, so prefer a short root.

    """
    if sys.platform == "win32":
        drive = os.environ.get("SYSTEMDRIVE", "C:")
        short_root = Path(f"{drive}\\") / "hsk-setup"
        try:
            short_root.mkdir(parents=True, exist_ok=True)
            return Path(tempfile.mkdtemp(prefix="", dir=str(short_root)))
        except OSError:
            pass
    return Path(tempfile.mkdtemp(prefix="hsk-install-"))


def extract_overlay(
    exe_path: Path,
    dest_dir: Path,
    *,
    log: LogFn | None = None,
    progress: ProgressFn | None = None,
) -> Path:
    """Extract appended zip into `dest_dir`. Return path to `dependencies/` (or dest if flat)."""
    bounds = read_overlay_bounds(exe_path)
    if bounds is None:
        msg = f"No HSK payload overlay in `{exe_path}`"
        raise RuntimeError(msg)
    start, length = bounds
    _make_dirs(dest_dir)
    tmp_zip = dest_dir / "_payload.zip"
    if log:
        log(f"Extracting payload ({length // _COPY_CHUNK} MB) from this EXE…")
    with exe_path.open("rb") as src, tmp_zip.open("wb") as dst:
        src.seek(start)
        remaining = length
        done = 0
        while remaining > 0:
            chunk = src.read(min(_COPY_CHUNK, remaining))
            if not chunk:
                break
            dst.write(chunk)
            remaining -= len(chunk)
            done += len(chunk)
            if progress:
                progress(done, length)
    with zipfile.ZipFile(tmp_zip, "r") as zf:
        infos = zf.infolist()
        total = max(len(infos), 1)
        for index, info in enumerate(infos, start=1):
            _extract_member(zf, info, dest_dir)
            if progress:
                progress(index, total)
            if log and (index % _LOG_EVERY == 0 or index == total):
                log(f"    Extracted {index}/{total} files: {_display_name(info.filename)}")
    tmp_zip.unlink(missing_ok=True)
    deps = dest_dir / "dependencies"
    if deps.is_dir():
        return deps
    # Flat overlay: dependencies contents at root of zip
    return dest_dir


def frozen_executable() -> Path:
    """Path to the running frozen EXE (or current interpreter when unpackaged)."""
    return Path(sys.executable).resolve()


def is_frozen() -> bool:
    """Return whether the installer is running as a frozen executable."""
    return bool(getattr(sys, "frozen", False))


def long_path(path: Path) -> str:
    """Return a filesystem path string that is not limited by Windows `MAX_PATH`."""
    absolute = str(Path(path).resolve())
    if sys.platform != "win32" or absolute.startswith(_LONG_PATH_PREFIX):
        return absolute
    if absolute.startswith("\\\\"):
        return _LONG_PATH_PREFIX + "UNC" + absolute[1:]
    return _LONG_PATH_PREFIX + absolute


def read_overlay_bounds(exe_path: Path) -> tuple[int, int] | None:
    """Return `(zip_start, zip_length)` or `None` if no overlay."""
    size = exe_path.stat().st_size
    if size < OVERLAY_TRAILER_SIZE:
        return None
    with exe_path.open("rb") as f:
        f.seek(size - OVERLAY_TRAILER_SIZE)
        trailer = f.read(OVERLAY_TRAILER_SIZE)
    length = struct.unpack_from("<Q", trailer, 0)[0]
    magic = trailer[8:]
    if magic != OVERLAY_MAGIC:
        return None
    if length <= 0 or length + OVERLAY_TRAILER_SIZE > size:
        return None
    return size - OVERLAY_TRAILER_SIZE - length, length


def read_overlay_member(exe_path: Path, member: str) -> bytes | None:
    """Read one file from the appended overlay zip without extracting the payload."""
    bounds = read_overlay_bounds(exe_path)
    if bounds is None:
        return None
    start, length = bounds
    with exe_path.open("rb") as src:
        view = _OffsetView(src, start, length)
        with zipfile.ZipFile(view, "r") as zf:
            try:
                info = zf.getinfo(member)
            except KeyError:
                return None
            return zf.read(info)


def _display_name(name: str) -> str:
    """Shorten a zip member name for one log line."""
    parts = [part for part in name.replace("\\", "/").split("/") if part]
    if len(parts) <= _NAME_PARTS_MAX:
        return "/".join(parts)
    return ".../" + "/".join(parts[-2:])


def _extract_member(zf: zipfile.ZipFile, info: zipfile.ZipInfo, dest_dir: Path) -> None:
    """Extract one member, tolerating paths longer than `MAX_PATH`."""
    parts = [part for part in info.filename.replace("\\", "/").split("/") if part not in {"", ".", ".."}]
    if not parts:
        return
    target = dest_dir.joinpath(*parts)
    if info.is_dir():
        _make_dirs(target)
        return
    _make_dirs(target.parent)
    with zf.open(info, "r") as src, open(long_path(target), "wb") as dst:  # noqa: PTH123
        shutil.copyfileobj(src, dst, _COPY_CHUNK)


def _make_dirs(path: Path) -> None:
    """Create a directory tree, tolerating paths longer than `MAX_PATH`."""
    Path(long_path(path)).mkdir(parents=True, exist_ok=True)

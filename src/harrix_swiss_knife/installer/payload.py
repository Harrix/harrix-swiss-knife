"""Appended zip overlay inside frozen installer EXEs."""

from __future__ import annotations

import struct
import sys
import zipfile
from collections.abc import Callable
from pathlib import Path

from harrix_swiss_knife.installer.constants import OVERLAY_MAGIC, OVERLAY_TRAILER_SIZE

LogFn = Callable[[str], None]
ProgressFn = Callable[[int, int], None]


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
    dest_dir.mkdir(parents=True, exist_ok=True)
    tmp_zip = dest_dir / "_payload.zip"
    if log:
        log(f"Extracting payload ({length // (1024 * 1024)} MB)…")
    with exe_path.open("rb") as src, tmp_zip.open("wb") as dst:
        src.seek(start)
        remaining = length
        done = 0
        chunk_size = 1024 * 1024
        while remaining > 0:
            chunk = src.read(min(chunk_size, remaining))
            if not chunk:
                break
            dst.write(chunk)
            remaining -= len(chunk)
            done += len(chunk)
            if progress:
                progress(done, length)
    with zipfile.ZipFile(tmp_zip, "r") as zf:
        members = zf.namelist()
        total = max(len(members), 1)
        for index, name in enumerate(members, start=1):
            zf.extract(name, dest_dir)
            if progress:
                progress(index, total)
            if log and index % 50 == 0:
                log(f"  Extracted {index}/{total} entries…")
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

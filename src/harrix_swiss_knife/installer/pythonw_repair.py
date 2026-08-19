"""Repair venv `pythonw.exe` GUI subsystem (uv #19226)."""

from __future__ import annotations

import shutil
import struct
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harrix_swiss_knife.installer.log import OutcomeLog

_GUI_SUBSYSTEM = 2
_PE_HEADER_MIN_SIZE = 64


def repair_pythonw_launcher(project_root: Path, log: OutcomeLog) -> None:
    """Replace venv `pythonw.exe` with the managed GUI launcher when needed."""
    log.step("Repair pythonw.exe launcher (uv #19226)")
    cfg = project_root / ".venv" / "pyvenv.cfg"
    target = project_root / ".venv" / "Scripts" / "pythonw.exe"
    home = _pyvenv_home(cfg)
    if not home:
        log.add("skipped", "pythonw.exe repair skipped (pyvenv.cfg home missing)")
        return
    source = Path(home) / "pythonw.exe"
    if not source.is_file():
        log.add("skipped", "pythonw.exe repair skipped (managed pythonw.exe missing)")
        return
    if _pe_subsystem(source) != _GUI_SUBSYSTEM:
        log.add("skipped", "pythonw.exe repair skipped (managed launcher is not GUI)")
        return
    if not target.is_file():
        log.add("skipped", "pythonw.exe repair skipped (venv pythonw.exe missing)")
        return
    if _pe_subsystem(target) == _GUI_SUBSYSTEM:
        log.add("skipped", "pythonw.exe repair skipped (already GUI launcher)")
        return
    broken = target.with_name("pythonw.exe.broken")
    for stale in (broken, Path(str(broken) + ".old")):
        stale.unlink(missing_ok=True)
    try:
        shutil.copy2(source, target)
    except OSError:
        try:
            target.rename(broken)
            shutil.copy2(source, target)
        except OSError as exc:
            if broken.is_file() and not target.exists():
                broken.rename(target)
            log.add("failed", f"pythonw.exe repair failed: {exc}")
            return
    if _pe_subsystem(target) != _GUI_SUBSYSTEM:
        log.add("failed", "pythonw.exe repair failed (launcher still not GUI)")
        return
    log.add("installed", "Repaired pythonw.exe launcher (uv #19226 workaround)")


def _pe_subsystem(path: Path) -> int | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < _PE_HEADER_MIN_SIZE:
        return None
    pe_offset = struct.unpack_from("<I", data, 60)[0]
    subsystem_offset = pe_offset + 92
    if subsystem_offset + 2 > len(data):
        return None
    return int(struct.unpack_from("<H", data, subsystem_offset)[0])


def _pyvenv_home(cfg: Path) -> str | None:
    if not cfg.is_file():
        return None
    for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("home"):
            _, _, value = line.partition("=")
            home = value.strip()
            if home:
                return home
    return None

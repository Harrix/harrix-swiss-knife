"""Repair broken console ``pythonw.exe`` launchers in uv-managed Windows venvs (uv #19226)."""

from __future__ import annotations

import contextlib
import shutil
from dataclasses import dataclass
from pathlib import Path

_PE_SUBSYSTEM_GUI = 2
_PE_DOS_STUB_MIN_SIZE = 64


@dataclass(frozen=True)
class FixPythonwResult:
    r"""Outcome of attempting to repair ``.venv\Scripts\pythonw.exe``."""

    status: str
    message: str
    details: tuple[str, ...] = ()


def fix_pythonw_launcher(project_root: Path) -> FixPythonwResult:
    """Replace a console ``pythonw.exe`` venv launcher with the real GUI executable.

    uv currently generates identical console trampolines for ``python.exe`` and
    ``pythonw.exe`` in managed-Python venvs (<https://github.com/astral-sh/uv/issues/19226>).
    The real ``pythonw.exe`` lives in the managed Python install referenced by
    ``home`` in ``.venv/pyvenv.cfg``.

    After ``uv sync``, uv may overwrite the launcher again; rerun this repair when needed.
    """
    venv_dir = project_root / ".venv"
    pyvenv_cfg = venv_dir / "pyvenv.cfg"
    pyw_target = venv_dir / "Scripts" / "pythonw.exe"
    details: list[str] = []

    home = read_pyvenv_home(pyvenv_cfg)
    if home is None:
        return FixPythonwResult(
            status="skipped",
            message=f"Could not read home from {pyvenv_cfg}",
        )

    pyw_source = home / "pythonw.exe"
    if not pyw_source.is_file():
        return FixPythonwResult(
            status="skipped",
            message=f"Managed pythonw.exe not found: {pyw_source}",
        )

    source_subsystem = read_pe_subsystem(pyw_source)
    if source_subsystem != _PE_SUBSYSTEM_GUI:
        return FixPythonwResult(
            status="skipped",
            message=f"Managed pythonw.exe is not a GUI launcher: {_format_launcher_info(pyw_source)}",
        )

    if not pyw_target.is_file():
        return FixPythonwResult(
            status="skipped",
            message=f"venv pythonw.exe not found: {pyw_target}",
        )

    details.append(f"Before: {_format_launcher_info(pyw_target)}")

    current_subsystem = read_pe_subsystem(pyw_target)
    if current_subsystem == _PE_SUBSYSTEM_GUI:
        return FixPythonwResult(
            status="already_ok",
            message="pythonw.exe already uses the GUI subsystem",
            details=tuple(details),
        )

    broken_path = pyw_target.parent / "pythonw.exe.broken"
    for stale in (broken_path, pyw_target.parent / "pythonw.exe.broken.old"):
        with contextlib.suppress(OSError):
            if stale.is_file():
                stale.unlink()

    try:
        shutil.copy2(pyw_source, pyw_target)
    except OSError:
        try:
            pyw_target.rename(broken_path)
        except OSError as exc:
            return FixPythonwResult(
                status="error",
                message=f"Could not replace pythonw.exe: {exc}",
                details=tuple(details),
            )
        try:
            shutil.copy2(pyw_source, pyw_target)
        except OSError as exc:
            if broken_path.is_file() and not pyw_target.is_file():
                with contextlib.suppress(OSError):
                    broken_path.rename(pyw_target)
            return FixPythonwResult(
                status="error",
                message=f"Could not copy managed pythonw.exe into venv: {exc}",
                details=tuple(details),
            )

    repaired_subsystem = read_pe_subsystem(pyw_target)
    details.append(f"After: {_format_launcher_info(pyw_target)}")
    if repaired_subsystem != _PE_SUBSYSTEM_GUI:
        return FixPythonwResult(
            status="error",
            message="pythonw.exe was copied but still does not use the GUI subsystem",
            details=tuple(details),
        )

    return FixPythonwResult(
        status="fixed",
        message="Replaced console pythonw.exe with managed GUI launcher",
        details=tuple(details),
    )


def read_pe_subsystem(path: Path) -> int | None:
    """Return the PE optional-header subsystem value, or ``None`` when unreadable."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < _PE_DOS_STUB_MIN_SIZE:
        return None
    pe_offset = int.from_bytes(data[60:64], "little")
    subsystem_offset = pe_offset + 92
    if subsystem_offset + 2 > len(data):
        return None
    return int.from_bytes(data[subsystem_offset : subsystem_offset + 2], "little")


def read_pyvenv_home(pyvenv_cfg: Path) -> Path | None:
    """Read the ``home = ...`` path from ``pyvenv.cfg``."""
    if not pyvenv_cfg.is_file():
        return None
    for line in pyvenv_cfg.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("home"):
            _, _, value = stripped.partition("=")
            home = value.strip()
            if home:
                return Path(home)
    return None


def _format_launcher_info(path: Path) -> str:
    subsystem = read_pe_subsystem(path)
    size = path.stat().st_size if path.is_file() else 0
    subsystem_label = "unknown" if subsystem is None else str(subsystem)
    return f"{path} ({size} bytes, subsystem={subsystem_label})"

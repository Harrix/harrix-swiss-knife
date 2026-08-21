"""Format human-readable install/uninstall finish reports."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.installer.build_info import display_build_lines, load_build_meta
from harrix_swiss_knife.toast_countdown_notification import format_elapsed_clock

if TYPE_CHECKING:
    from harrix_swiss_knife.installer.deploy import DeployResult
    from harrix_swiss_knife.installer.log import OutcomeLog
    from harrix_swiss_knife.installer.uninstall import UninstallResult


def format_elapsed_display(elapsed_seconds: float) -> str:
    """Format installer elapsed time like toast clocks (`MM:SS` / `HH:MM:SS`)."""
    return format_elapsed_clock(int(elapsed_seconds + 0.5))


def format_install_report(result: DeployResult) -> str:
    """Build the text shown on the installer Finished page."""
    lines: list[str] = ["Installation finished.", ""]
    version_line, built_line = display_build_lines(load_build_meta())
    lines.append(version_line)
    lines.append(built_line)
    meta = load_build_meta()
    artifacts = meta.get("artifacts") or ""
    if artifacts:
        lines.append("")
        lines.append("Bundled payload artifacts:")
        lines.extend(f"  - {part.strip()}" for part in artifacts.split("; ") if part.strip())
    if result.install_root is not None:
        lines.append("")
        lines.append(f"Install root: {result.install_root}")
    if result.hsk_path is not None:
        hsk = result.hsk_path
        pyw = hsk / ".venv" / "Scripts" / "pythonw.exe"
        launch = hsk / "launch_tray.py"
        uninstall = hsk / "launch_uninstall.py"
        lines.append(f'Run tray app: "{pyw}" "{launch}"')
        lines.append(f'Uninstall:    "{pyw}" "{uninstall}"')
        lines.append("CLI:          hsk md --help")
        install_log = hsk / "install.log"
        if install_log.is_file():
            lines.append(f"Install log:  {install_log}")
    lines.extend(_outcome_block(result.outcomes))
    if result.elapsed_seconds:
        lines.append("")
        lines.append(f"Elapsed: {format_elapsed_display(result.elapsed_seconds)}")
    return "\n".join(lines)


def format_uninstall_report(result: UninstallResult) -> str:
    """Build a short uninstall summary for the UI."""
    lines: list[str] = ["Uninstall finished.", ""]
    if result.preserved_dir is not None:
        lines.append(f"Preserved data: {result.preserved_dir}")
    elif result.hsk_path is not None:
        lines.append("Preserved data: (nothing under project)")
    lines.extend(_outcome_block(result.outcomes, action_label="What was removed:"))
    if result.elapsed_seconds:
        lines.append("")
        lines.append(f"Elapsed: {format_elapsed_display(result.elapsed_seconds)}")
    return "\n".join(lines)


def _outcome_block(log: OutcomeLog, *, action_label: str = "What was installed:") -> list[str]:
    return list(log.summary_lines(action_label=action_label))

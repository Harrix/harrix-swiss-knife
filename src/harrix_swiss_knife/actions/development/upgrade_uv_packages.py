"""Exit HSK and upgrade uv packages in Harrix projects via a detached .cmd."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import QApplication, QMessageBox

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.app_restart import restart_argv
from harrix_swiss_knife.single_instance import release_held_instance, restore_held_instance
from harrix_swiss_knife.uv_locate import find_uv_exe, refresh_path
from harrix_swiss_knife.uv_upgrade_bat import (
    PROJECT_NAMES,
    resolve_upgrade_projects,
    write_uv_upgrade_cmd,
)


class OnUpgradeUvPackages(ActionBase):
    """Upgrade uv and sync packages in the three Harrix projects after exit.

    Writes a temporary `.cmd`, starts it in a new console, releases the tray
    singleton, and quits so `.venv` files are not locked. The script waits for
    this PID, closes Cursor if it is running (it can lock uv-managed Python),
    runs `uv self update`, then per project `uv python upgrade` (from
    `.python-version` when present) and `uv sync --upgrade`, then relaunches
    with the same argv.

    """

    icon = "📦"
    title = "Upgrade packages (uv)"

    @ActionBase.handle_exceptions("upgrade uv packages")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Confirm, spawn the upgrade script, then quit the app."""
        if sys.platform != "win32":
            self.add_line("Upgrade packages (uv) is only available on Windows.")
            self.show_result()
            return

        refresh_path()
        uv = find_uv_exe()
        if uv is None:
            self.add_line(
                "❌ uv not found on PATH or in common install locations "
                "(checked %USERPROFILE%\\.local\\bin and WinGet links)."
            )
            self.show_result()
            return

        raw = self.config.get("paths_python_projects")
        if not isinstance(raw, list):
            self.add_line('❌ config "paths_python_projects" must be a list.')
            self.show_result()
            return
        projects = resolve_upgrade_projects(raw)
        if not projects:
            self.add_line(f'❌ None of {PROJECT_NAMES} found as existing dirs in "paths_python_projects".')
            self.show_result()
            return

        project_lines = "\n".join(f"  • {path}" for path in projects)
        answer = QMessageBox.question(
            None,
            "Upgrade packages (uv)",
            "The app will exit, then run:\n\n"
            "  uv self update\n"
            "  uv python upgrade\n"
            "  uv sync --upgrade\n\n"
            f"in:\n{project_lines}\n\n"
            "If Cursor is open, it will be closed first (save your work).\n"
            "When finished, the same app launch will start again.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.add_line("Upgrade cancelled.")
            self.show_result()
            return

        temp_dir = Path(tempfile.gettempdir())
        cmd_path = temp_dir / f"hsk-uv-upgrade-{os.getpid()}.cmd"
        log_path = temp_dir / "hsk-uv-upgrade.log"
        relaunch = restart_argv()
        write_uv_upgrade_cmd(
            cmd_path,
            wait_pid=os.getpid(),
            uv_exe=uv,
            project_dirs=projects,
            relaunch_argv=relaunch,
            log_path=log_path,
        )

        cmd_exe = os.environ.get("COMSPEC") or str(
            Path(os.environ.get("SYSTEMROOT", r"C:\Windows")) / "System32" / "cmd.exe"
        )
        # CREATE_NEW_CONSOLE and DETACHED_PROCESS are mutually exclusive (WinError 87).
        creation = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
        try:
            subprocess.Popen(
                [cmd_exe, "/c", str(cmd_path)],
                cwd=str(temp_dir),
                creationflags=creation,
                close_fds=True,
            )
        except OSError as exc:
            self.add_line(f"❌ Failed to start upgrade script: {exc}")
            self.show_result()
            return

        held = release_held_instance()
        self.add_line(f"Upgrade script started: {cmd_path}")
        self.add_line(f"Log: {log_path}")
        self.add_line("Exiting so .venv files can be updated…")
        app = QApplication.instance()
        if app is None:
            if held is not None:
                restore_held_instance(held)
            self.show_result()
            return
        app.quit()

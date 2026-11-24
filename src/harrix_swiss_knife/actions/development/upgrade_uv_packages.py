"""Exit HSK and upgrade uv packages in Harrix projects via a detached .cmd."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from PySide6.QtWidgets import QApplication, QMessageBox
from shiboken6 import isValid

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.development.run_maintenance_checklist import OnRunMaintenanceChecklist
from harrix_swiss_knife.app_restart import project_gui_relaunch_argv
from harrix_swiss_knife.cursor_backup.paths import cursor_running, find_cursor_exe
from harrix_swiss_knife.paths import get_project_root
from harrix_swiss_knife.single_instance import release_held_instance, restore_held_instance
from harrix_swiss_knife.uv_locate import find_uv_exe, refresh_path
from harrix_swiss_knife.uv_upgrade_bat import (
    PROJECT_NAMES,
    resolve_upgrade_projects,
    write_uv_upgrade_cmd,
)
from harrix_swiss_knife.uv_upgrade_resume import (
    clear_cursor_terminal_resume_flag,
    clear_uv_upgrade_resume,
    save_uv_upgrade_resume,
    write_cursor_terminal_resume_flag,
)


class OnUpgradeUvPackages(ActionBase):
    """Upgrade uv and sync packages in the three Harrix projects after exit.

    Writes a temporary `.cmd`, starts it in a new console, releases the tray
    singleton, and quits so `.venv` files are not locked. The script waits for
    this PID, closes Cursor if it is running (it can lock uv-managed Python),
    runs `uv self update`, then per project `uv python upgrade` (from
    `.python-version` when present) and `uv sync --upgrade`, commits changed
    `uv.lock` / `pyproject.toml` as Update packages, repairs
    `pythonw.exe` when needed, optionally reopens Cursor, then relaunches HSK
    with a GUI interpreter. If Cursor was open, it is reopened without admin and
    HSK starts from the Cursor folderOpen terminal task (dies with Cursor). When
    the upgrade was started from the maintenance checklist, the checklist is
    reopened and this step is marked Done.

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

        cursor_was_running = cursor_running()
        cursor_exe = find_cursor_exe() if cursor_was_running else None
        from_checklist, session_done = _maintenance_resume_snapshot()
        project_root = get_project_root()

        project_lines = "\n".join(f"  • {path}" for path in projects)
        restore_bits: list[str] = []
        if cursor_was_running:
            restore_bits.append(
                "If Cursor is open, it will be closed first (save your work), then reopened "
                "without Administrator. HSK starts again in Cursor's terminal "
                "(same as `python.exe …/main.py`), so closing Cursor quits HSK."
            )
            restore_bits.append("Cursor may ask once to allow automatic tasks for this folder — choose Allow.")
        else:
            restore_bits.append("When finished, Harrix Swiss Knife relaunches standalone via pythonw (tray).")
        if from_checklist:
            restore_bits.append("The maintenance checklist will reopen with this step marked Done.")
        answer = QMessageBox.question(
            None,
            "Upgrade packages (uv)",
            "The app will exit, then run:\n\n"
            "  uv self update\n"
            "  uv python upgrade\n"
            "  uv sync --upgrade\n"
            "  git commit (uv.lock / pyproject.toml) as Update packages\n\n"
            f"in:\n{project_lines}\n\n" + "\n".join(restore_bits) + "\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.add_line("Upgrade cancelled.")
            self.show_result()
            return

        if from_checklist:
            save_uv_upgrade_resume(
                reopen_maintenance_checklist=True,
                maintenance_session_done=session_done,
            )
        else:
            clear_uv_upgrade_resume()

        if cursor_was_running:
            write_cursor_terminal_resume_flag(project_root)
        else:
            clear_cursor_terminal_resume_flag(project_root)

        temp_dir = Path(tempfile.gettempdir())
        cmd_path = temp_dir / f"hsk-uv-upgrade-{os.getpid()}.cmd"
        log_path = temp_dir / "hsk-uv-upgrade.log"
        relaunch = project_gui_relaunch_argv(project_root)
        write_uv_upgrade_cmd(
            cmd_path,
            wait_pid=os.getpid(),
            uv_exe=uv,
            project_dirs=projects,
            relaunch_argv=relaunch,
            log_path=log_path,
            close_cursor=cursor_was_running,
            reopen_cursor=cursor_was_running,
            cursor_exe=cursor_exe,
            cursor_workspace=project_root if cursor_was_running else None,
            pythonw_fix_project=project_root,
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
        if cursor_was_running:
            self.add_line("Cursor will close for the upgrade, then reopen; HSK starts in Cursor's terminal.")
        if from_checklist:
            self.add_line("Maintenance checklist will reopen after relaunch.")
        self.add_line("Exiting so .venv files can be updated…")
        app = QApplication.instance()
        if app is None:
            if held is not None:
                restore_held_instance(held)
            self.show_result()
            return
        app.quit()


def _maintenance_resume_snapshot() -> tuple[bool, list[str]]:
    """Return whether the checklist is open and its session Done class names."""
    dialog = OnRunMaintenanceChecklist.checklist_dialog
    if dialog is None or not isValid(dialog) or not dialog.isVisible():
        return False, []
    return True, dialog.session_done_class_names()

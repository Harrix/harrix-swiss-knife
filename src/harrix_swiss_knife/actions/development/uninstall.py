"""Open the Harrix Swiss Knife uninstall wizard."""

from __future__ import annotations

import subprocess
import sys
from typing import Any

import harrix_pylib as h
from PySide6.QtWidgets import QApplication, QMessageBox

from harrix_swiss_knife.actions.common.base import ActionBase


class OnUninstall(ActionBase):
    """Open the uninstall wizard (keeps databases, api-keys, fitness images).

    Launches `launch_uninstall.py` with the project venv, then exits the tray app
    so files are not locked. Git, uv, VS Code, and Python are not removed.

    """

    icon = "🗑️"
    title = "Uninstall Harrix Swiss Knife…"

    @ActionBase.handle_exceptions("opening uninstall wizard")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Confirm, start uninstall UI in a separate process, then quit."""
        if sys.platform != "win32":
            self.add_line("Uninstall is only available on Windows.")
            self.show_result()
            return

        project_root = h.dev.get_project_root()
        launch_py = project_root / "launch_uninstall.py"
        pyw = project_root / ".venv" / "Scripts" / "pythonw.exe"
        if not launch_py.is_file():
            self.add_line(f"❌ launch_uninstall.py not found: {launch_py}")
            self.show_result()
            return
        if not pyw.is_file():
            self.add_line(f"❌ pythonw.exe not found: {pyw}")
            self.show_result()
            return

        answer = QMessageBox.question(
            None,
            "Uninstall Harrix Swiss Knife",
            "Open the uninstall wizard?\n\n"
            "Databases, api-keys, and fitness images will be kept.\n"
            "This tray app will exit so files can be removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.add_line("Uninstall cancelled.")
            self.show_result()
            return

        creation = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.Popen(
            [str(pyw), str(launch_py)],
            cwd=str(project_root),
            creationflags=creation,
        )
        self.add_line("Uninstall wizard started; exiting tray app.")
        app = QApplication.instance()
        if app is not None:
            app.quit()

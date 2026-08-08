"""Add Harrix Swiss Knife to Windows autostart (Startup folder)."""

from __future__ import annotations

import sys
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.desktop_shortcut import create_startup_shortcut
from harrix_swiss_knife.pythonw_launcher import fix_pythonw_launcher


class OnAddToAutostart(ActionBase):
    r"""Create or update a Startup-folder shortcut so the app launches at logon.

    Uses the same target, arguments, working directory, and icon as the desktop
    shortcut (`pythonw.exe`, `main.py`, `assets/app.ico` or legacy
    `img/icon.ico`). Before creating the shortcut, repairs
    `.venv\Scripts\pythonw.exe` when uv creates a console launcher. Windows
    only. Remove the shortcut from the Startup folder to disable autostart.

    """

    icon = "🚀"
    title = "Add to Windows autostart"

    @ActionBase.handle_exceptions("adding to Windows autostart")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Create Startup-folder shortcut for this project."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            self.show_result()
            return

        project_root = h.dev.get_project_root()
        pyw = project_root / ".venv" / "Scripts" / "pythonw.exe"
        main_py = project_root / "src" / "harrix_swiss_knife" / "main.py"

        if not pyw.is_file():
            self.add_line(f"❌ pythonw.exe not found: {pyw}")
            self.show_result()
            return
        if not main_py.is_file():
            self.add_line(f"❌ main.py not found: {main_py}")
            self.show_result()
            return

        repair = fix_pythonw_launcher(project_root)
        for line in repair.details:
            self.add_line(line)

        if repair.status == "fixed":
            self.add_line(f"✅ {repair.message}")
        elif repair.status == "already_ok":
            self.add_line(f"OK: {repair.message}")
        elif repair.status == "skipped":
            self.add_line(f"⚠️ {repair.message}")
        else:
            self.add_line(f"❌ {repair.message}")
            self.show_result()
            return

        try:
            lnk_path = create_startup_shortcut(project_root)
        except OSError as e:
            self.add_line(f"❌ {e}")
            self.show_result()
            return

        self.add_line(f"✅ Autostart shortcut created: {lnk_path}")
        self.show_toast("Added to Windows autostart")
        self.show_result()

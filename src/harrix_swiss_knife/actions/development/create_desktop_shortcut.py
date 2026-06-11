"""Actions for Python development and code management."""

from __future__ import annotations

import sys
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.desktop_shortcut import create_desktop_shortcut
from harrix_swiss_knife.pythonw_launcher import fix_pythonw_launcher


class OnCreateDesktopShortcut(ActionBase):
    r"""Create or update a desktop shortcut to launch Harrix Swiss Knife.

    Uses the same target, arguments, working directory, and icon as
    ``New-DesktopShortcut`` in ``install/harrix-swiss-knife.ps1`` (``pythonw.exe``,
    ``main.py``, ``img/icon.ico`` or ``assets/app.ico``). Before creating the
    shortcut, repairs ``.venv\Scripts\pythonw.exe`` when uv creates a console
    launcher (https://github.com/astral-sh/uv/issues/19226). After ``uv sync``,
    rerun this action if a console window appears on startup. Windows only.
    """

    icon = "🔗"
    title = "Create desktop shortcut"

    @ActionBase.handle_exceptions("creating desktop shortcut")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Create desktop shortcut for this project."""
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
            lnk_path = create_desktop_shortcut(project_root)
        except OSError as e:
            self.add_line(f"❌ {e}")
            self.show_result()
            return

        self.add_line(f"✅ Desktop shortcut created: {lnk_path}")
        self.show_toast("Desktop shortcut created")
        self.show_result()

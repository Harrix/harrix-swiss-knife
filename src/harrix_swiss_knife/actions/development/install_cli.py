"""Install global `hsk` CLI via uv tool."""

from __future__ import annotations

import shutil
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnInstallCli(ActionBase):
    r"""Install or reinstall the global `hsk` CLI (`uv tool install -e`).

    Puts `hsk` on PATH (typically `%USERPROFILE%\\.local\\bin`). Same step as
    `install/harrix-swiss-knife.ps1` after `uv sync`. Rerun after renaming CLI
    entry points in `pyproject.toml` or after pulling changes to CLI commands.
    """

    icon = "⌨️"
    title = "Install CLI (hsk on PATH)"
    cli_available = True
    cli_hint = "dev install-cli"

    @ActionBase.handle_exceptions("install CLI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Run `uv tool install -e` for this repository."""
        if shutil.which("uv") is None:
            self.add_line("❌ uv not found on PATH. Install uv first: https://docs.astral.sh/uv/")
            self.show_result()
            return

        project_root = h.dev.get_project_root()
        pyproject = project_root / "pyproject.toml"
        if not pyproject.is_file():
            self.add_line(f"❌ pyproject.toml not found: {pyproject}")
            self.show_result()
            return

        tool_list = h.dev.run_command("uv tool list")
        reinstall = "harrix-swiss-knife" in tool_list
        reinstall_flag = " --reinstall" if reinstall else ""
        quoted = f'"{project_root}"'
        cmd = f"uv tool install{reinstall_flag} -e {quoted}"
        self.add_line(f"$ {cmd}")
        result = h.dev.run_command(cmd)
        if result:
            self.add_line(result)

        hsk_on_path = shutil.which("hsk")
        if hsk_on_path:
            self.add_line(f"✅ `hsk` is on PATH: {hsk_on_path}")
            self.show_toast("CLI installed (hsk on PATH)")
        else:
            self.add_line(
                "⚠️ `hsk` was not found on PATH after install. "
                "Open a new terminal or ensure %USERPROFILE%\\.local\\bin is on PATH."
            )
            self.show_toast("CLI install finished (see output)")
        self.show_result()

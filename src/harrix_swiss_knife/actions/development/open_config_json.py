"""Open the application `config.json` in an editor."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.paths import get_config_path_str


class OnOpenConfigJson(ActionBase):
    """Open the application's configuration file.

    Opens `config.json` in the editor from `editor`. If that command or path is
    missing, tries `cursor`, `code` (VS Code), `code-insiders` in order, writes
    the first match back to `config.json` under `editor`, then opens the file.
    If none are available on Windows, uses Notepad and persists `editor` as
    `notepad`. On other platforms, opens the file with the default application when
    no editor is found.

    """

    icon = "⚙️"
    title = "Open `config.json`"

    @ActionBase.handle_exceptions("config file opening")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the application's configuration file."""
        lines = open_config_json_in_editor(
            config_path=self.config_path,
            preferred_editor=str(self.config.get("editor") or "").strip() or None,
        )
        for line in lines:
            self.add_line(line)
        if any(line.startswith("❌") for line in lines):
            self.show_result()


def open_config_json_in_editor(
    *,
    config_path: str | Path | None = None,
    preferred_editor: str | None = None,
) -> list[str]:
    """Open `config.json` in the configured editor and return status lines.

    Uses `preferred_editor` or the `editor` key from config. If that command or
    path is missing, tries `cursor`, `code`, `code-insiders` in order, writes the
    first match back to `config.json` under `editor`, then opens the file. On
    Windows, falls back to Notepad. On other platforms, opens with the default
    application when no editor is found.

    """
    lines: list[str] = []
    path_str = str(config_path) if config_path is not None else get_config_path_str()
    config_file = Path(path_str)
    if not config_file.is_absolute():
        config_file = (h.dev.get_project_root() / config_file).resolve()
    else:
        config_file = config_file.resolve()

    try:
        config = h.dev.config_load(path_str)
    except (FileNotFoundError, OSError, ValueError, TypeError):
        config = {}

    editor_raw = (preferred_editor if preferred_editor is not None else str(config.get("editor") or "")).strip()
    fallback_commands = ("cursor", "code", "code-insiders")

    chosen_key = editor_raw
    resolved: str | None = None

    if editor_raw:
        resolved = _resolve_editor_executable(editor_raw)

    if resolved is None:
        for name in fallback_commands:
            found = shutil.which(name)
            if found:
                chosen_key = name
                resolved = found
                break

    if resolved is None and sys.platform == "win32":
        found = shutil.which("notepad") or _windows_notepad_exe()
        if found:
            chosen_key = "notepad"
            resolved = found

    if resolved is not None and chosen_key != editor_raw:
        h.dev.config_update_value("editor", chosen_key, path_str)
        lines.append(f'Updated "editor" in config.json to: {chosen_key}')

    if resolved is not None:
        commands = f'"{resolved}" "{config_file}"'
        result = h.dev.run_command(commands, is_shell=True)
        if result:
            lines.append(result)
        lines.append(f"Opened: {config_file}")
        return lines

    if sys.platform == "win32":
        try:
            os.startfile(str(config_file))  # noqa: S606
        except OSError as e:
            lines.append(f"❌ Could not open config.json: {e}")
            return lines
        lines.append(f"Opened with default app: {config_file}")
        return lines
    if sys.platform == "darwin":
        result = h.dev.run_command(f'open "{config_file}"', is_shell=True)
        if result:
            lines.append(result)
        lines.append(f"Opened with default app: {config_file}")
        return lines

    result = h.dev.run_command(f'xdg-open "{config_file}"', is_shell=True)
    if result:
        lines.append(result)
    lines.append(f"Opened with default app: {config_file}")
    return lines


def _editor_token_looks_like_path(editor: str) -> bool:
    min_windows_drive_len = 2
    return "/" in editor or "\\" in editor or (len(editor) >= min_windows_drive_len and editor[1] == ":")


def _resolve_editor_executable(editor: str) -> str | None:
    """Return a filesystem path to `editor` if it can be launched, else `None`."""
    editor = editor.strip()
    if not editor:
        return None
    if _editor_token_looks_like_path(editor):
        try:
            candidate = Path(editor).expanduser().resolve()
        except OSError:
            return None
        return str(candidate) if candidate.is_file() else None
    return shutil.which(editor)


def _windows_notepad_exe() -> str | None:
    system_root = os.environ.get("SYSTEMROOT") or r"C:\Windows"
    notepad = Path(system_root) / "System32" / "notepad.exe"
    return str(notepad) if notepad.is_file() else None

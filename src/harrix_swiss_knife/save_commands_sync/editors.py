"""VS Code-family editor paths, process names, and Save Commands extension detection."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from harrix_swiss_knife.actions.vscode.install_harrix_notes_explorer_extension import (
    OnInstallHarrixNotesExplorerExtension,
)
from harrix_swiss_knife.browser_bookmarks.paths import is_process_running

if TYPE_CHECKING:
    from collections.abc import Iterable

EXTENSION_ID = "deepakgupta191199.save-commands"
EXTENSION_FOLDER_PREFIX = f"{EXTENSION_ID}-"

_Install = OnInstallHarrixNotesExplorerExtension

EDITOR_LABEL_VSCODE = _Install._EDITOR_LABEL_VSCODE  # noqa: SLF001
EDITOR_LABEL_INSIDERS = _Install._EDITOR_LABEL_INSIDERS  # noqa: SLF001
EDITOR_LABEL_CURSOR = _Install._EDITOR_LABEL_CURSOR  # noqa: SLF001
EDITOR_LABEL_VSCODIUM = _Install._EDITOR_LABEL_VSCODIUM  # noqa: SLF001
EDITOR_LABEL_WINDSURF = _Install._EDITOR_LABEL_WINDSURF  # noqa: SLF001
EDITOR_LABEL_ANTIGRAVITY = _Install._EDITOR_LABEL_ANTIGRAVITY  # noqa: SLF001
EDITOR_NOT_INSTALLED_SUFFIX = _Install._EDITOR_NOT_INSTALLED_SUFFIX  # noqa: SLF001
SUPPORTED_EDITOR_LABELS: tuple[str, ...] = _Install._SUPPORTED_WIN32_EDITOR_LABELS  # noqa: SLF001
CLI_EDITOR_TOKEN_TO_LABEL: dict[str, str] = dict(_Install._CLI_EDITOR_TOKEN_TO_LABEL)  # noqa: SLF001
CLI_EDITOR_CHOICES: tuple[str, ...] = _Install.CLI_EDITOR_CHOICES

_USER_DATA_DIR_NAMES: dict[str, str] = {
    EDITOR_LABEL_VSCODE: "Code",
    EDITOR_LABEL_INSIDERS: "Code - Insiders",
    EDITOR_LABEL_CURSOR: "Cursor",
    EDITOR_LABEL_VSCODIUM: "VSCodium",
    EDITOR_LABEL_WINDSURF: "Windsurf",
    EDITOR_LABEL_ANTIGRAVITY: "Antigravity",
}

_PROCESS_IMAGE_NAMES: dict[str, str] = {
    EDITOR_LABEL_VSCODE: "Code.exe",
    EDITOR_LABEL_INSIDERS: "Code - Insiders.exe",
    EDITOR_LABEL_CURSOR: "Cursor.exe",
    EDITOR_LABEL_VSCODIUM: "VSCodium.exe",
    EDITOR_LABEL_WINDSURF: "Windsurf.exe",
    EDITOR_LABEL_ANTIGRAVITY: "Antigravity.exe",
}


def canonical_editor_label(display: str) -> str:
    """Strip `(not installed)` from a checkbox label."""
    return _Install._canonical_editor_label(display)  # noqa: SLF001


def discover_editors() -> list[str]:
    """Return labels for editors that look installed or already have user data."""
    if sys.platform == "win32":
        found = list(_Install._discover_win32_editors())  # noqa: SLF001
        extra = [label for label in SUPPORTED_EDITOR_LABELS if label not in found and _editor_has_user_data(label)]
        return found + extra
    return [label for label in SUPPORTED_EDITOR_LABELS if _editor_has_user_data(label)]


def editor_choice_label(canonical: str, *, installed: bool) -> str:
    """Return dialog checkbox text for `canonical` editor name."""
    return _Install._editor_choice_label(canonical, installed=installed)  # noqa: SLF001


def extensions_root(label: str) -> Path | None:
    """Return the user `extensions` directory for `label`, or `None` if unknown."""
    pairs = _Install._dest_extension_roots([label])  # noqa: SLF001
    if not pairs:
        return None
    return pairs[0][1]


def resolve_editor_cli_token(token: str) -> str | None:
    """Map a CLI editor token (and aliases) to a canonical display label."""
    return _Install._resolve_editor_cli_token(token)  # noqa: SLF001


def roaming_app_data() -> Path:
    """Return the OS roaming/config directory that holds VS Code-family user data."""
    if sys.platform == "win32":
        roaming = os.environ.get("APPDATA")
        if roaming:
            return Path(roaming)
        return Path.home() / "AppData" / "Roaming"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return Path(xdg) if xdg else Path.home() / ".config"


def running_editor_names(labels: Iterable[str]) -> list[str]:
    """Return display names of selected editors whose process is running (Windows)."""
    names: list[str] = []
    for label in labels:
        image = _PROCESS_IMAGE_NAMES.get(label)
        if image and is_process_running(image):
            names.append(label)
    return names


def save_commands_extension_installed(label: str) -> bool:
    """Return whether the Save Commands extension folder exists for `label`."""
    root = extensions_root(label)
    if root is None or not root.is_dir():
        return False
    try:
        children = root.iterdir()
    except OSError:
        return False
    prefix = EXTENSION_FOLDER_PREFIX.casefold()
    return any(path.is_dir() and path.name.casefold().startswith(prefix) for path in children)


def state_vscdb_path(label: str) -> Path | None:
    """Return `User/globalStorage/state.vscdb` for `label`, or `None` if unknown."""
    folder = _USER_DATA_DIR_NAMES.get(label)
    if folder is None:
        return None
    return roaming_app_data() / folder / "User" / "globalStorage" / "state.vscdb"


def _editor_has_user_data(label: str) -> bool:
    db = state_vscdb_path(label)
    if db is not None and db.is_file():
        return True
    root = extensions_root(label)
    return root is not None and root.is_dir()

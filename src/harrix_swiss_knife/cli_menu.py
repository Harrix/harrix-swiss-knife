"""CLI-related menu helpers: suffix, copy command, tray context menu."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction, QClipboard, QGuiApplication, QMouseEvent
from PySide6.QtWidgets import QMenu, QWidget

CLI_EXECUTABLE = "harrix-swiss-knife-cli"
CLI_MENU_SUFFIX = " ꟲᴸᴵ"
CLI_TOOLTIP_DEFAULT = f"Available via {CLI_EXECUTABLE} (see --help)"
COPY_CLI_MENU_PREFIX = "Copy CLI command: "


class CliContextMenu(QMenu):
    """QMenu that offers Copy CLI command on right-click for CLI-enabled actions."""

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """On right-click over a CLI action, show the copy-command context menu."""
        if event.button() == Qt.MouseButton.RightButton:
            action = self.actionAt(event.pos())
            cmd = get_cli_copy_command(action)
            if cmd is not None:
                show_copy_cli_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    cli_copy_command=cmd,
                )
                event.accept()
                return
        super().mouseReleaseEvent(event)


def build_cli_copy_command(hint: str) -> str:
    """Build a full CLI invocation string for clipboard and tooltips."""
    stripped = hint.strip()
    if stripped:
        return f"{CLI_EXECUTABLE} {stripped}"
    return CLI_EXECUTABLE


def copy_cli_command_to_clipboard(command: str) -> None:
    """Copy a full CLI command string to the system clipboard."""
    copy_text_to_clipboard(command)


def copy_text_to_clipboard(text: str) -> None:
    """Copy text to the system clipboard."""
    clipboard = QGuiApplication.clipboard()
    if clipboard is not None:
        clipboard.setText(text, QClipboard.Mode.Clipboard)


def format_copy_cli_menu_label(cli_copy_command: str) -> str:
    """Build context menu item text: prefix, colon, and the command to copy."""
    return f"{COPY_CLI_MENU_PREFIX}{cli_copy_command}"


def get_cli_copy_command(action: QAction | None) -> str | None:
    """Return the CLI copy string stored on a menu action, if any."""
    if action is None:
        return None
    cmd = getattr(action, "cli_copy_command", None)
    if isinstance(cmd, str) and cmd:
        return cmd
    return None


def show_copy_cli_menu(*, parent: QWidget | None, global_pos: QPoint, cli_copy_command: str) -> None:
    """Show a small context menu to copy a CLI command to the clipboard."""
    menu = QMenu(parent)
    copy_action = menu.addAction(format_copy_cli_menu_label(cli_copy_command))
    copy_action.triggered.connect(lambda: copy_cli_command_to_clipboard(cli_copy_command))
    menu.exec_(global_pos)

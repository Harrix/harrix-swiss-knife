"""CLI-related menu helpers: suffix, copy command, tray context menu."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction, QClipboard, QGuiApplication, QMouseEvent

from harrix_swiss_knife.action_identity import (
    ActionIdentityParts,
    action_identity_parts,
    format_action_identity_text,
)
from harrix_swiss_knife.fluent.widgets.menus import FluentMenu
from harrix_swiss_knife.qt_lucide_icon import apply_leading_chrome_icons
from harrix_swiss_knife.qt_widget_identity_menu import add_widget_identity_actions

if TYPE_CHECKING:
    from collections.abc import Iterable

    from PySide6.QtWidgets import QMenu, QWidget

CLI_EXECUTABLE = "hsk"
CLI_MENU_SUFFIX = " ꟲᴸᴵ"
CLI_TOOLTIP_DEFAULT = f"Available via {CLI_EXECUTABLE} (see --help)"
COPY_ACTION_IDENTITY_MENU_LABEL = "📋 Copy action name, class, and path"
COPY_ACTION_NAME_MENU_PREFIX = "📋 Copy action name: "
COPY_ACTION_CLASS_MENU_PREFIX = "📋 Copy action class: "
COPY_ACTION_PATH_MENU_PREFIX = "📋 Copy action path: "
COPY_ACTION_NAME_PREVIEW_MAX_LEN = 40
COPY_CLI_MENU_PREFIX = "📋 Copy CLI command: "
OPEN_ALL_TRACKERS_MENU_LABEL = "Open all trackers"
# Tray top-level trackers that share the «Open all trackers» right-click menu.
TRACKER_LAUNCHER_CLASS_NAMES: frozenset[str] = frozenset(
    {
        "OnFinance",
        "OnFitness",
        "OnFood",
        "OnHabits",
    }
)
_ELLIPSIS = "…"


class CliContextMenu(FluentMenu):
    """Tray menu: middle-click copies identity; right-click on trackers opens all four."""

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle middle-click identity copy and right-click open-all for trackers."""
        action = self.actionAt(event.position().toPoint())
        if action is not None and not action.isSeparator() and action.menu() is None:
            if event.button() == Qt.MouseButton.MiddleButton:
                show_action_item_context_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    action=action,
                )
                event.accept()
                return
            if event.button() == Qt.MouseButton.RightButton and is_tracker_launcher_action(action):
                show_open_all_trackers_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    host_menu=self,
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


def format_copy_action_class_menu_label(class_name: str) -> str:
    """Build context menu item text: prefix, colon, and the class name to copy."""
    return f"{COPY_ACTION_CLASS_MENU_PREFIX}{class_name}"


def format_copy_action_name_menu_label(name: str) -> str:
    """Build context menu item text: prefix, colon, and a shortened name preview."""
    return f"{COPY_ACTION_NAME_MENU_PREFIX}{truncate_action_name_preview(name)}"


def format_copy_action_path_menu_label(path: str) -> str:
    """Build context menu item text: prefix, colon, and the path to copy."""
    return f"{COPY_ACTION_PATH_MENU_PREFIX}{path}"


def format_copy_cli_menu_label(cli_copy_command: str) -> str:
    """Build context menu item text: prefix, colon, and the command to copy."""
    return f"{COPY_CLI_MENU_PREFIX}{cli_copy_command}"


def get_action_identity_parts(action: QAction | None) -> ActionIdentityParts | None:
    """Return name/class/path parts stored on a menu action, if any."""
    if action is None:
        return None
    parts = getattr(action, "action_identity_parts", None)
    if isinstance(parts, ActionIdentityParts):
        return parts
    return None


def get_action_identity_text(action: QAction | None) -> str | None:
    """Return the name/class/path snippet stored on a menu action, if any."""
    if action is None:
        return None
    text = getattr(action, "action_identity_text", None)
    if isinstance(text, str) and text:
        return text
    parts = get_action_identity_parts(action)
    if parts is None:
        return None
    return f"{parts.name}\n{parts.class_name}\n{parts.path}"


def get_cli_copy_command(action: QAction | None) -> str | None:
    """Return the CLI copy string stored on a menu action, if any."""
    if action is None:
        return None
    cmd = getattr(action, "cli_copy_command", None)
    if isinstance(cmd, str) and cmd:
        return cmd
    return None


def is_tracker_launcher_action(action: QAction | None) -> bool:
    """Return whether `action` is one of the four tray tracker launchers."""
    parts = get_action_identity_parts(action)
    return parts is not None and parts.class_name in TRACKER_LAUNCHER_CLASS_NAMES


def iter_tracker_launcher_actions(menu: QMenu) -> Iterable[QAction]:
    """Yield Finance/Fitness/Food/Habits leaf actions from `menu` in menu order."""
    for action in menu.actions():
        if is_tracker_launcher_action(action):
            yield action


def show_action_class_context_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    action_cls: type,
    host_widget: QWidget | None = None,
) -> None:
    """Show copy name/class/path (and CLI when available) for an action class."""
    identity_parts = action_identity_parts(action_cls)
    identity_text = format_action_identity_text(action_cls)
    cli_copy_command: str | None = None
    if getattr(action_cls, "cli_available", False):
        cli_copy_command = build_cli_copy_command(str(getattr(action_cls, "cli_hint", "") or ""))
    show_action_identity_context_menu(
        parent=parent,
        global_pos=global_pos,
        identity_text=identity_text,
        identity_parts=identity_parts,
        cli_copy_command=cli_copy_command,
        host_widget=host_widget,
    )


def show_action_identity_context_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    identity_text: str | None = None,
    identity_parts: ActionIdentityParts | None = None,
    cli_copy_command: str | None = None,
    host_widget: QWidget | None = None,
) -> None:
    """Show a context menu to copy action identity fields and optional CLI command."""
    if identity_text is None and identity_parts is None and cli_copy_command is None and host_widget is None:
        return

    menu = FluentMenu("", parent)
    if identity_text is not None:
        copy_identity = menu.addAction(COPY_ACTION_IDENTITY_MENU_LABEL)
        copy_identity.triggered.connect(
            lambda *_args, text=identity_text: copy_text_to_clipboard(text),
        )
    if identity_parts is not None:
        copy_name = menu.addAction(format_copy_action_name_menu_label(identity_parts.name))
        copy_name.triggered.connect(
            lambda *_args, text=identity_parts.name: copy_text_to_clipboard(text),
        )
        copy_class = menu.addAction(format_copy_action_class_menu_label(identity_parts.class_name))
        copy_class.triggered.connect(
            lambda *_args, text=identity_parts.class_name: copy_text_to_clipboard(text),
        )
        copy_path = menu.addAction(format_copy_action_path_menu_label(identity_parts.path))
        copy_path.triggered.connect(
            lambda *_args, text=identity_parts.path: copy_text_to_clipboard(text),
        )
    if cli_copy_command is not None:
        if not menu.isEmpty():
            menu.addSeparator()
        copy_cli = menu.addAction(format_copy_cli_menu_label(cli_copy_command))
        copy_cli.triggered.connect(
            lambda *_args, cmd=cli_copy_command: copy_cli_command_to_clipboard(cmd),
        )
    if host_widget is not None:
        if not menu.isEmpty():
            menu.addSeparator()
        add_widget_identity_actions(menu, host_widget)
    apply_leading_chrome_icons(menu)
    menu.refresh_theme()
    menu.exec(global_pos)


def show_action_item_context_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    action: QAction,
    host_widget: QWidget | None = None,
) -> None:
    """Show a context menu to copy action identity and, when present, the CLI command."""
    show_action_identity_context_menu(
        parent=parent,
        global_pos=global_pos,
        identity_text=get_action_identity_text(action),
        identity_parts=get_action_identity_parts(action),
        cli_copy_command=get_cli_copy_command(action),
        host_widget=host_widget,
    )


def show_open_all_trackers_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    host_menu: QMenu,
) -> None:
    """Show a one-item menu that opens Finance, Fitness, Food, and Habits."""
    menu = FluentMenu("", parent)
    open_all = menu.addAction(OPEN_ALL_TRACKERS_MENU_LABEL)
    open_all.triggered.connect(lambda *_args, source=host_menu: trigger_all_tracker_launchers(source))
    apply_leading_chrome_icons(menu)
    menu.refresh_theme()
    menu.exec(global_pos)


def trigger_all_tracker_launchers(menu: QMenu) -> None:
    """Trigger every tracker launcher QAction found on `menu`."""
    for action in iter_tracker_launcher_actions(menu):
        action.trigger()


def truncate_action_name_preview(name: str, max_len: int = COPY_ACTION_NAME_PREVIEW_MAX_LEN) -> str:
    """Return `name` unchanged, or a prefix ending with `…` when it is too long."""
    if max_len <= 0:
        return _ELLIPSIS
    if len(name) <= max_len:
        return name
    return name[:max_len].rstrip() + _ELLIPSIS

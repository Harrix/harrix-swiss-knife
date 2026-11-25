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
from harrix_swiss_knife.action_title import strip_md_inline_code_markers
from harrix_swiss_knife.fluent.widgets.menus import FluentMenu
from harrix_swiss_knife.qt_lucide_icon import (
    apply_leading_chrome_icons,
    apply_lucide_action_icon,
    apply_menu_icon_size,
)
from harrix_swiss_knife.qt_widget_identity_menu import add_widget_identity_actions

if TYPE_CHECKING:
    from collections.abc import Iterable

    from PySide6.QtWidgets import QMenu, QWidget

CLI_EXECUTABLE = "hsk"
CLI_MENU_SUFFIX = " ꟲᴸᴵ"
CLI_TOOLTIP_DEFAULT = f"Available via {CLI_EXECUTABLE} (see --help)"
COPY_ACTION_IDENTITY_MENU_LABEL = "📋 Copy action name, class, and path"
COPY_MENU_TITLE_MENU_PREFIX = "📋 Copy menu title: "
COPY_ACTION_NAME_MENU_PREFIX = "📋 Copy action name: "
COPY_ACTION_CLASS_MENU_PREFIX = "📋 Copy action class: "
COPY_ACTION_PATH_MENU_PREFIX = "📋 Copy action path: "
COPY_ACTION_NAME_PREVIEW_MAX_LEN = 40
COPY_CLI_MENU_PREFIX = "📋 Copy CLI command: "
SHOW_ACTION_USAGE_STATS_MENU_LABEL = "Show in Action usage stats"
OPEN_ALL_TRACKERS_MENU_LABEL = "Open all trackers"
OPEN_ALL_TRACKERS_PRESENTATION_MENU_LABEL = "Open all trackers in presentation mode"
# Tray top-level trackers that share the «Open all trackers» right-click menu.
TRACKER_LAUNCHER_CLASS_NAMES: frozenset[str] = frozenset(
    {
        "OnFinance",
        "OnFitness",
        "OnFood",
        "OnHabits",
    }
)
_OPEN_ALL_TRACKERS_ICON = "layout-grid"
_OPEN_ALL_TRACKERS_PRESENTATION_ICON = "monitor-play"
_OPEN_IN_PRESENTATION_ICON = "presentation"
_SHOW_ACTION_USAGE_STATS_ICON = "chart-column"
_ELLIPSIS = "…"


class CliContextMenu(FluentMenu):
    """Tray menu: middle-click copies identity; right-click opens CLI / usage menu."""

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle middle-click identity copy and right-click tray action menu."""
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
            if event.button() == Qt.MouseButton.RightButton:
                # Do not fall through to QMenu — that would trigger the action.
                show_tray_action_context_menu(
                    parent=self,
                    global_pos=event.globalPosition().toPoint(),
                    action=action,
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


def format_copy_menu_title_menu_label(title: str) -> str:
    """Build context menu item text: prefix, colon, and a shortened menu-title preview."""
    return f"{COPY_MENU_TITLE_MENU_PREFIX}{truncate_action_name_preview(title)}"


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


def get_menu_item_title(action: QAction | None) -> str | None:
    """Return the visible tray/menu label without the CLI suffix marker."""
    if action is None:
        return None
    text = action.text().replace(CLI_MENU_SUFFIX, "").strip()
    return text or None


def is_tracker_launcher_action(action: QAction | None) -> bool:
    """Return whether `action` is one of the four tray tracker launchers."""
    parts = get_action_identity_parts(action)
    return parts is not None and parts.class_name in TRACKER_LAUNCHER_CLASS_NAMES


def iter_tracker_launcher_actions(menu: QMenu) -> Iterable[QAction]:
    """Yield Finance/Fitness/Food/Habits leaf actions from `menu` in menu order."""
    for action in menu.actions():
        if is_tracker_launcher_action(action):
            yield action


def menu_title_from_action_class(action_cls: type) -> str:
    """Return the UI title for `action_cls` (card label without CLI / bold markers)."""
    return strip_md_inline_code_markers(str(getattr(action_cls, "title", "") or "")).strip()


def show_action_class_context_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    action_cls: type,
    host_widget: QWidget | None = None,
    menu_title: str | None = None,
) -> None:
    """Show copy name/class/path (and CLI when available) for an action class."""
    identity_parts = action_identity_parts(action_cls)
    identity_text = format_action_identity_text(action_cls)
    cli_copy_command: str | None = None
    if getattr(action_cls, "cli_available", False):
        cli_copy_command = build_cli_copy_command(str(getattr(action_cls, "cli_hint", "") or ""))
    title = menu_title.strip() if isinstance(menu_title, str) and menu_title.strip() else None
    if title is None:
        title = menu_title_from_action_class(action_cls) or None
    show_action_identity_context_menu(
        parent=parent,
        global_pos=global_pos,
        menu_title=title,
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
    menu_title: str | None = None,
) -> None:
    """Show a context menu to copy action identity fields and optional CLI command."""
    if (
        menu_title is None
        and identity_text is None
        and identity_parts is None
        and cli_copy_command is None
        and host_widget is None
    ):
        return

    menu = FluentMenu("", parent)
    if menu_title is not None:
        copy_menu_title = menu.addAction(format_copy_menu_title_menu_label(menu_title))
        copy_menu_title.triggered.connect(
            lambda *_args, text=menu_title: copy_text_to_clipboard(text),
        )
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
        menu_title=get_menu_item_title(action),
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
    """Show open-all actions that launch Finance, Fitness, Food, and Habits."""
    show_tracker_launcher_context_menu(
        parent=parent,
        global_pos=global_pos,
        host_menu=host_menu,
        tracker_action=None,
    )


def show_tracker_launcher_context_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    host_menu: QMenu,
    tracker_action: QAction | None,
) -> None:
    """Show presentation-mode and open-all actions for tray tracker items."""
    menu = FluentMenu("", parent)
    _add_tracker_launcher_actions(menu, host_menu=host_menu, tracker_action=tracker_action)
    apply_menu_icon_size(menu)
    menu.refresh_theme()
    menu.exec(global_pos)


def show_tray_action_context_menu(
    *,
    parent: QWidget | None,
    global_pos: QPoint,
    action: QAction,
    host_menu: QMenu | None = None,
) -> None:
    """Show tray right-click menu: CLI copy (when set), usage stats, tracker extras."""
    menu = FluentMenu("", parent)
    has_items = False

    if host_menu is not None and is_tracker_launcher_action(action):
        _add_tracker_launcher_actions(menu, host_menu=host_menu, tracker_action=action)
        has_items = True

    cli_copy_command = get_cli_copy_command(action)
    if cli_copy_command is not None:
        if has_items:
            menu.addSeparator()
        copy_cli = menu.addAction(format_copy_cli_menu_label(cli_copy_command))
        copy_cli.triggered.connect(
            lambda *_args, cmd=cli_copy_command: copy_cli_command_to_clipboard(cmd),
        )
        has_items = True

    identity_parts = get_action_identity_parts(action)
    if identity_parts is not None:
        if has_items:
            menu.addSeparator()
        show_stats = menu.addAction(SHOW_ACTION_USAGE_STATS_MENU_LABEL)
        apply_lucide_action_icon(show_stats, _SHOW_ACTION_USAGE_STATS_ICON)
        show_stats.triggered.connect(
            lambda *_args, class_name=identity_parts.class_name: _open_action_usage_stats(
                select_class_name=class_name,
            ),
        )
        has_items = True

    if not has_items:
        return
    apply_leading_chrome_icons(menu)
    apply_menu_icon_size(menu)
    menu.refresh_theme()
    menu.exec(global_pos)


def trigger_all_tracker_launchers(menu: QMenu) -> None:
    """Trigger every tracker launcher QAction found on `menu`."""
    for action in iter_tracker_launcher_actions(menu):
        action.trigger()


def trigger_all_tracker_launchers_presentation_mode(menu: QMenu) -> None:
    """Open every tracker launcher from `menu` in presentation mode."""
    for action in iter_tracker_launcher_actions(menu):
        trigger_tracker_presentation_mode(action)


def trigger_tracker_presentation_mode(action: QAction) -> None:
    """Launch the tracker behind `action` in presentation mode."""
    instance = getattr(action, "_hsk_action_instance", None)
    if instance is None:
        action_cls = getattr(action, "_hsk_action_class", None)
        parent = action.parent()
        output_bus = getattr(parent, "output_bus", None) if parent is not None else None
        if callable(action_cls):
            instance = action_cls(parent=parent, output_bus=output_bus)
            setattr(action, "_hsk_action_instance", instance)  # noqa: B010
    if instance is not None and hasattr(instance, "execute"):
        instance.execute(presentation_mode=True)
        return
    action.trigger()


def truncate_action_name_preview(name: str, max_len: int = COPY_ACTION_NAME_PREVIEW_MAX_LEN) -> str:
    """Return `name` unchanged, or a prefix ending with `…` when it is too long."""
    if max_len <= 0:
        return _ELLIPSIS
    if len(name) <= max_len:
        return name
    return name[:max_len].rstrip() + _ELLIPSIS


def _add_tracker_launcher_actions(
    menu: FluentMenu,
    *,
    host_menu: QMenu,
    tracker_action: QAction | None,
) -> None:
    """Append presentation-mode and open-all tracker actions to `menu`."""
    from harrix_swiss_knife.apps.common.presentation_mode import (  # noqa: PLC0415
        OPEN_IN_PRESENTATION_MENU_LABEL,
    )

    if tracker_action is not None:
        open_presentation = menu.addAction(OPEN_IN_PRESENTATION_MENU_LABEL)
        apply_lucide_action_icon(open_presentation, _OPEN_IN_PRESENTATION_ICON)
        open_presentation.triggered.connect(
            lambda *_args, source=tracker_action: trigger_tracker_presentation_mode(source),
        )
        menu.addSeparator()
    open_all = menu.addAction(OPEN_ALL_TRACKERS_MENU_LABEL)
    apply_lucide_action_icon(open_all, _OPEN_ALL_TRACKERS_ICON)
    open_all.triggered.connect(lambda *_args, source=host_menu: trigger_all_tracker_launchers(source))
    open_all_presentation = menu.addAction(OPEN_ALL_TRACKERS_PRESENTATION_MENU_LABEL)
    apply_lucide_action_icon(open_all_presentation, _OPEN_ALL_TRACKERS_PRESENTATION_ICON)
    open_all_presentation.triggered.connect(
        lambda *_args, source=host_menu: trigger_all_tracker_launchers_presentation_mode(source),
    )


def _open_action_usage_stats(*, select_class_name: str | None = None) -> None:
    """Open Action usage stats from a context menu (lazy import)."""
    from harrix_swiss_knife.actions.development.show_action_usage_stats import (  # noqa: PLC0415
        open_action_usage_stats,
    )

    open_action_usage_stats(select_class_name=select_class_name)

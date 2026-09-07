"""Qt helper for Lucide stroke SVG icons.

UI chrome loads icons by Lucide ID (`save`, `trash`, …) from `assets/lucide/`.
`currentColor` is replaced with the application palette so icons follow the
theme. Action tray emojis and user-content emojis stay in `qt_emoji_icon`.

Browse names at https://lucide.dev/icons. Refresh SVGs with
`python src/harrix_swiss_knife/assets/sync_lucide_icons.py`.

"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import (
    QAction,
    QColor,
    QCursor,
    QGuiApplication,
    QIcon,
    QPainter,
    QPalette,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QDialogButtonBox,
    QMenu,
    QMenuBar,
    QPushButton,
    QToolButton,
    QWidget,
)

from harrix_swiss_knife.qt_emoji_icon import split_leading_emoji

logger = logging.getLogger(__name__)

DEFAULT_LUCIDE_BUTTON_ICON_SIZE = 18
DEFAULT_LUCIDE_MENU_ICON_SIZE = 18

OK_BUTTON_ICON = "circle-check"
CANCEL_BUTTON_ICON = "x"
SAVE_BUTTON_ICON = "save"
CLOSE_BUTTON_ICON = "x"
COPY_BUTTON_ICON = "clipboard-copy"
DELETE_BUTTON_ICON = "trash"
AI_BUTTON_ICON = "sparkles"
AI_BUTTON_ICON_COLOR = "#2e86b7"

_ICON_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_CACHE: dict[tuple[str, int, str, float], QIcon] = {}

# Leading emoji on chrome labels → Lucide id. Content/action emojis are not listed.
CHROME_EMOJI_TO_LUCIDE: dict[str, str] = {
    "✅": "circle-check",
    "✔️": "check",
    "✔": "check",
    "❌": "x",
    "✖️": "x",
    "✖": "x",
    "💾": "save",
    "📋": "clipboard-list",
    "🗑️": "trash",
    "🗑": "trash",
    "➕": "plus",  # noqa: RUF001
    "✏️": "pencil",
    "✏": "pencil",
    "🤖": "sparkles",
    "🔄": "refresh-cw",
    "📁": "folder",
    "📂": "folder-open",
    "📷": "camera",
    "▶️": "play",
    "▶": "play",
    "⏸️": "pause",
    "⏸": "pause",
    "⏹️": "square-stop",
    "⏹": "square-stop",
    "🔊": "volume-2",
    "🔇": "volume-x",
    "⏮️": "skip-back",
    "⏭️": "skip-forward",
    "✂️": "scissors",
    "✂": "scissors",
    "↩️": "undo-2",
    "🔍": "search",
    "🔎": "search",
    "⭐": "star",
    "🧮": "calculator",
    "☑️": "square-check",
    "⬜": "square",
    "📥": "download",
    "🎙️": "mic",
    "🎤": "mic",
    "📝": "notebook-pen",
    "📊": "chart-column",
    "💬": "message-square",
    "📅": "calendar",
    "📆": "calendar",
    "🗄": "archive",
    "🗄️": "archive",
    "🏃": "person-standing",
    "⚙️": "settings",
    "⚙": "settings",
    "🧹": "broom",
    "📤": "upload",
    "✨": "sparkles",
    "📄": "file",
    "🏋️": "dumbbell",
    "🕒": "clock",
    "⏱️": "timer",
    "⏺️": "circle-dot",
    "↺": "rotate-ccw",
    "↻": "rotate-cw",
    "➖": "minus",  # noqa: RUF001
    "🏷️": "tag",
    "🏷": "tag",
    "🍽️": "utensils",
    "🍽": "utensils",
    "⚖️": "scale",
    "⚖": "scale",
    "ℹ️": "info",  # noqa: RUF001
    "ℹ": "info",  # noqa: RUF001
    "📌": "pin",
    "🚧": "construction",
    "💎": "gem",
    "🎨": "palette",
    "🖼️": "expand",
    "🖼": "expand",
    "✍️": "square-pen",
    "✍": "square-pen",
    "🔀": "git-merge",
    "💱": "arrow-left-right",
    "💸": "trending-down",
    "💰": "wallet",
    "🏆": "trophy",
    "👟": "footprints",
    "🙈": "eye-off",
    "👀": "eye",
    "♻": "archive-restore",
    "♻️": "archive-restore",
    "🗂️": "folders",
    "🗂": "folders",
    "🔤": "a-large-small",
    "🌐": "languages",
    "🖥️": "monitor",
    "🖥": "monitor",
    "🚪": "log-out",
    "☰": "menu",
    "⋯": "ellipsis",
    "…": "ellipsis",
    "⋮": "ellipsis-vertical",
    "🔗": "link",
    "🪟": "app-window",
    "👁️": "eye",
    "👁": "eye",
    "📐": "ruler",
    "🖱️": "mouse-pointer-2",
    "🖱": "mouse-pointer-2",
    "➡️": "arrow-right",
    "💧": "pipette",
    "⬅️": "arrow-left",
    "←": "arrow-left",
    "→": "arrow-right",
    "🎯": "target",
    "🥤": "cup-soda",
    "📜": "scroll-text",
    "⚠️": "alert-triangle",
    "⚠": "alert-triangle",
}


def add_lucide_action(
    menu: QMenu,
    label: str,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
) -> QAction:
    """Add a menu action with a Lucide `QIcon` and plain `label` text."""
    action = menu.addAction(label)
    apply_lucide_action_icon(action, name, icon_size=icon_size)
    return action


def apply_leading_chrome_button_icon(
    button: QAbstractButton,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
) -> bool:
    """Move a leading chrome emoji from `button` text onto a Lucide `QIcon`.

    Returns `True` when a mapped emoji prefix was converted.

    """
    emoji, rest = split_leading_emoji(button.text())
    if not emoji:
        return False
    name = lucide_name_for_chrome_emoji(emoji)
    if name is None:
        logger.warning("No Lucide mapping for chrome emoji %r", emoji)
        return False
    if name == "clipboard-list" and rest.casefold().startswith("copy"):
        name = COPY_BUTTON_ICON
    color = AI_BUTTON_ICON_COLOR if _is_ai_chrome_emoji(emoji) else None
    apply_lucide_button_icon(button, name, icon_size=icon_size, color=color)
    button.setText(rest)
    return True


def apply_leading_chrome_buttons(
    root: QWidget,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
) -> None:
    """Convert leading chrome emoji prefixes on push and tool buttons under `root`."""
    for button in root.findChildren(QAbstractButton):
        if isinstance(button, (QPushButton, QToolButton)):
            apply_leading_chrome_button_icon(button, icon_size=icon_size)


def apply_leading_chrome_icon(
    action: QAction,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
) -> bool:
    """Move a leading chrome emoji from `action` text onto a Lucide `QIcon`.

    Returns `True` when a mapped emoji prefix was converted.

    """
    emoji, rest = split_leading_emoji(action.text())
    if not emoji:
        return False
    name = lucide_name_for_chrome_emoji(emoji)
    if name is None:
        logger.warning("No Lucide mapping for chrome emoji %r", emoji)
        return False
    if name == "clipboard-list" and rest.casefold().startswith("copy"):
        name = COPY_BUTTON_ICON
    color = AI_BUTTON_ICON_COLOR if _is_ai_chrome_emoji(emoji) else None
    apply_lucide_action_icon(action, name, icon_size=icon_size, color=color)
    action.setText(rest)
    return True


def apply_leading_chrome_icons(
    menu: QMenu | QMenuBar,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
) -> None:
    """Convert leading chrome emoji prefixes on `menu` actions into Lucide icons."""
    for action in menu.actions():
        if action.isSeparator():
            continue
        apply_leading_chrome_icon(action, icon_size=icon_size)
        submenu = action.menu()
        if isinstance(submenu, QMenu):
            apply_leading_chrome_icons(submenu, icon_size=icon_size)


def apply_lucide_action_icon(
    action: QAction,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
    color: QColor | str | None = None,
) -> None:
    """Set a Lucide icon on `action` without changing its text."""
    if name:
        action.setIcon(create_lucide_icon(name, icon_size, color=color))


def apply_lucide_button_icon(
    button: QAbstractButton,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
    color: QColor | str | None = None,
) -> None:
    """Set a Lucide icon on an existing button."""
    button.setIcon(create_lucide_icon(name, icon_size, color=color))
    button.setIconSize(QSize(icon_size, icon_size))


def apply_lucide_dialog_buttons(
    buttons: QDialogButtonBox,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
) -> None:
    """Set Lucide icons on standard `QDialogButtonBox` buttons when present."""
    for standard_button, name in (
        (QDialogButtonBox.StandardButton.Ok, OK_BUTTON_ICON),
        (QDialogButtonBox.StandardButton.Cancel, CANCEL_BUTTON_ICON),
        (QDialogButtonBox.StandardButton.Save, SAVE_BUTTON_ICON),
        (QDialogButtonBox.StandardButton.Close, CLOSE_BUTTON_ICON),
    ):
        button = buttons.button(standard_button)
        if button is not None:
            apply_lucide_button_icon(button, name, icon_size=icon_size)


def create_ai_lucide_icon(size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE) -> QIcon:
    """Create the shared AI chrome icon (`sparkles` in `#2e86b7`)."""
    return create_lucide_icon(AI_BUTTON_ICON, size, color=AI_BUTTON_ICON_COLOR)


def create_lucide_icon(
    name: str,
    size: int = 64,
    *,
    color: QColor | str | None = None,
    device_pixel_ratio: float | None = None,
) -> QIcon:
    """Create a square `QIcon` from a Lucide SVG ID.

    Unknown names log a warning and return an empty icon.

    """
    ratio = device_pixel_ratio if device_pixel_ratio is not None else _lucide_device_pixel_ratio()
    if ratio <= 0:
        ratio = 1.0
    paint_color = QColor(color) if color is not None else _lucide_palette_color()
    cache_key = (name, size, paint_color.name(QColor.NameFormat.HexArgb), ratio)
    cached = _CACHE.get(cache_key)
    if cached is not None:
        return cached

    svg_bytes = _lucide_svg_bytes(name, paint_color)
    if svg_bytes is None:
        return QIcon()

    physical = max(1, round(size * ratio))
    renderer = QSvgRenderer(QByteArray(svg_bytes))
    if not renderer.isValid():
        logger.warning("Lucide SVG for `%s` is invalid", name)
        return QIcon()

    pixmap = QPixmap(physical, physical)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    renderer.render(painter, QRectF(0.0, 0.0, float(physical), float(physical)))
    painter.end()
    pixmap.setDevicePixelRatio(ratio)

    icon = QIcon()
    icon.addPixmap(pixmap)
    _CACHE[cache_key] = icon
    return icon


def lucide_name_for_chrome_emoji(emoji: str) -> str | None:
    """Return the Lucide ID for a chrome emoji, or `None` when unmapped."""
    if emoji in CHROME_EMOJI_TO_LUCIDE:
        return CHROME_EMOJI_TO_LUCIDE[emoji]
    stripped = emoji.replace("\ufe0f", "").replace("\u200d", "")
    return CHROME_EMOJI_TO_LUCIDE.get(stripped)


def lucide_svg_path(name: str) -> Path | None:
    """Return the SVG path for `name`, or `None` when the ID is invalid or missing."""
    if not _ICON_NAME_RE.fullmatch(name):
        return None
    path = _lucide_dir() / f"{name}.svg"
    if not path.is_file():
        return None
    return path


def make_ai_lucide_push_button(
    label: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
    parent: QWidget | None = None,
) -> QPushButton:
    """Create a push button with the shared AI `sparkles` icon."""
    return make_lucide_push_button(
        label,
        AI_BUTTON_ICON,
        icon_size=icon_size,
        color=AI_BUTTON_ICON_COLOR,
        parent=parent,
    )


def make_lucide_push_button(
    label: str,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
    color: QColor | str | None = None,
    parent: QWidget | None = None,
) -> QPushButton:
    """Create a push button with a Lucide icon."""
    button = QPushButton(label, parent)
    apply_lucide_button_icon(button, name, icon_size=icon_size, color=color)
    return button


def set_action_text_with_lucide_icon(
    action: QAction,
    text: str,
    name: str | None = None,
    *,
    icon_size: int = DEFAULT_LUCIDE_MENU_ICON_SIZE,
) -> None:
    """Set action text and a Lucide icon.

    When `name` is omitted, a leading chrome emoji on `text` is mapped to Lucide
    and stripped from the visible label.

    """
    action.setText(text)
    if name:
        apply_lucide_action_icon(action, name, icon_size=icon_size)
        return
    apply_leading_chrome_icon(action, icon_size=icon_size)


def _is_ai_chrome_emoji(emoji: str) -> bool:
    """Return whether `emoji` is the robot chrome mark used for AI actions."""
    return emoji.replace("\ufe0f", "").replace("\u200d", "") == "🤖"


def _lucide_device_pixel_ratio() -> float:
    app = QGuiApplication.instance()
    if isinstance(app, QGuiApplication):
        screen = QGuiApplication.screenAt(QCursor.pos()) or app.primaryScreen()
        if screen is not None:
            ratio = screen.devicePixelRatio()
            if ratio > 0:
                return float(ratio)
    return 1.0


def _lucide_dir() -> Path:
    return Path(__file__).resolve().parent / "assets" / "lucide"


def _lucide_palette_color() -> QColor:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return QColor(app.palette().color(QPalette.ColorRole.WindowText))
    return QColor("#111827")


def _lucide_svg_bytes(name: str, color: QColor) -> bytes | None:
    path = lucide_svg_path(name)
    if path is None:
        logger.warning("Unknown Lucide icon `%s`", name)
        return None
    hex_color = color.name(QColor.NameFormat.HexRgb)
    text = path.read_text(encoding="utf-8").replace("currentColor", hex_color)
    return text.encode("utf-8")

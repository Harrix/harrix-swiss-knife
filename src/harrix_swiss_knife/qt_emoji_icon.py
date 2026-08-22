"""Qt helper for creating emoji icons without clipping.

Some emoji glyphs have a tight bounding box that is taller than it is wide.
If we scale naively by width (or pick a fixed point size), the glyph can be
visually clipped (often at the bottom). This helper sizes the font using the
glyph's tight bounding rect and centers the result without clipping.

"""

from __future__ import annotations

import unicodedata

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QAction, QFont, QFontMetricsF, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QDialogButtonBox, QMenu, QMenuBar, QPushButton, QWidget

DEFAULT_EMOJI_BUTTON_ICON_SIZE = 18
DEFAULT_EMOJI_MENU_ICON_SIZE = 18

OK_BUTTON_EMOJI = "✅"
CANCEL_BUTTON_EMOJI = "❌"
SAVE_BUTTON_EMOJI = "💾"
CLOSE_BUTTON_EMOJI = "❌"
COPY_BUTTON_EMOJI = "📋"
DELETE_BUTTON_EMOJI = "🗑️"

_EMOJI_CODE_RANGES = (
    (0x200D, 0x200D),
    (0x20E3, 0x20E3),
    (0x2100, 0x27BF),
    (0xFE00, 0xFE0F),
    (0x1F000, 0x1FAFF),
    (0x1F3FB, 0x1F3FF),
)


def add_emoji_action(
    menu: QMenu,
    label: str,
    emoji: str,
    *,
    icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE,
) -> QAction:
    """Add a menu action with `emoji` as a `QIcon` and `label` as the text."""
    action = menu.addAction(label)
    apply_emoji_action_icon(action, emoji, icon_size=icon_size)
    return action


def apply_emoji_action_icon(
    action: QAction,
    emoji: str,
    *,
    icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE,
) -> None:
    """Set `emoji` as the action icon without changing its text."""
    if emoji:
        action.setIcon(create_emoji_icon(emoji, icon_size))


def apply_emoji_dialog_buttons(
    buttons: QDialogButtonBox,
    *,
    icon_size: int = DEFAULT_EMOJI_BUTTON_ICON_SIZE,
) -> None:
    """Set emoji icons on standard QDialogButtonBox buttons when present."""
    for standard_button, emoji in (
        (QDialogButtonBox.StandardButton.Ok, OK_BUTTON_EMOJI),
        (QDialogButtonBox.StandardButton.Cancel, CANCEL_BUTTON_EMOJI),
        (QDialogButtonBox.StandardButton.Save, SAVE_BUTTON_EMOJI),
        (QDialogButtonBox.StandardButton.Close, CLOSE_BUTTON_EMOJI),
    ):
        button = buttons.button(standard_button)
        if button is not None:
            button.setIcon(create_emoji_icon(emoji, icon_size))


def apply_leading_emoji_icon(
    action: QAction,
    *,
    icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE,
) -> bool:
    """Move a leading emoji from `action` text onto its `QIcon`.

    Returns:

    - `bool`: `True` when an emoji prefix was converted.

    """
    emoji, rest = split_leading_emoji(action.text())
    if not emoji:
        return False
    apply_emoji_action_icon(action, emoji, icon_size=icon_size)
    action.setText(rest)
    return True


def apply_leading_emoji_icons(
    menu: QMenu | QMenuBar,
    *,
    icon_size: int = DEFAULT_EMOJI_MENU_ICON_SIZE,
) -> None:
    """Convert leading emoji prefixes on `menu` actions into `QIcon`s."""
    for action in menu.actions():
        if action.isSeparator():
            continue
        apply_leading_emoji_icon(action, icon_size=icon_size)
        submenu = action.menu()
        if isinstance(submenu, QMenu):
            apply_leading_emoji_icons(submenu, icon_size=icon_size)


def create_emoji_icon(emoji: str, size: int = 64) -> QIcon:
    """Create a square `QIcon` for an emoji, scaled to avoid clipping."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, on=True)
    paint_centered_emoji(painter, emoji, QRectF(0.0, 0.0, float(size), float(size)), fill=0.90)
    painter.end()

    return QIcon(pixmap)


def make_emoji_push_button(
    label: str,
    emoji: str,
    *,
    icon_size: int = DEFAULT_EMOJI_BUTTON_ICON_SIZE,
    parent: QWidget | None = None,
) -> QPushButton:
    """Create a push button with an emoji icon."""
    button = QPushButton(label, parent)
    button.setIcon(create_emoji_icon(emoji, icon_size))
    return button


def paint_centered_emoji(
    painter: QPainter,
    emoji: str,
    rect: QRectF,
    *,
    fill: float = 0.90,
) -> None:
    """Draw ``emoji`` centered in ``rect``, scaled to ``fill`` of the shorter side."""
    if not emoji:
        return
    painter.save()
    painter.setPen(Qt.GlobalColor.black)
    size = min(rect.width(), rect.height())
    target = size * fill
    base_font = QFont()
    base_font.setPointSizeF(max(1.0, size))
    bounds = QFontMetricsF(base_font).tightBoundingRect(emoji)
    rect_w = max(bounds.width(), 1.0)
    rect_h = max(bounds.height(), 1.0)
    scale = (target / rect_h) if rect_h > rect_w else (target / rect_w)
    font = QFont(base_font)
    font.setPointSizeF(max(1.0, base_font.pointSizeF() * scale))
    painter.setFont(font)
    fitted = QFontMetricsF(font).tightBoundingRect(emoji)
    x = rect.x() + (rect.width() - fitted.width()) / 2.0
    y = rect.y() + (rect.height() - fitted.height()) / 2.0
    painter.drawText(QPointF(x - fitted.left(), y - fitted.top()), emoji)
    painter.restore()


def split_leading_emoji(text: str) -> tuple[str, str]:
    """Split `emoji rest` menu text into `(emoji, rest)`.

    Returns `("", text)` when the first token is not an emoji.

    """
    raw = text.strip()
    if not raw:
        return "", text
    first, _sep, rest = raw.partition(" ")
    if _is_emoji_token(first):
        return first, rest
    return "", text


def _is_emoji_codepoint(code: int) -> bool:
    return any(start <= code <= end for start, end in _EMOJI_CODE_RANGES)


def _is_emoji_token(token: str) -> bool:
    if not token:
        return False
    has_symbol = False
    for char in token:
        category = unicodedata.category(char)
        if _is_emoji_codepoint(ord(char)) or category in {"So", "Sk"}:
            has_symbol = True
            continue
        if category in {"Mn", "Me"}:
            continue
        return False
    return has_symbol

"""Map finance category emoji (DB `categories.icon`) to Lucide for UI display.

The database and catalog keep emoji strings. Lists, filters, tables, and
dialogs show the matching Lucide `QIcon` instead of drawing the emoji glyph.

"""

from __future__ import annotations

from PySide6.QtGui import QIcon

from harrix_swiss_knife.fluent.tokens import ICON_SIZE
from harrix_swiss_knife.qt_emoji_icon import split_leading_emoji
from harrix_swiss_knife.qt_lucide_icon import create_lucide_icon, lucide_name_for_chrome_emoji

# Seed / preset emoji → Lucide id. Unknown custom emoji falls back below.
FINANCE_CATEGORY_EMOJI_TO_LUCIDE: dict[str, str] = {
    "🔌": "plug",
    "💄": "sparkles",
    "📖": "book-open",
    "☕": "coffee",
    "👶": "baby",
    "👕": "shirt",
    "📚": "graduation-cap",
    "🎬": "clapperboard",
    "🔄": "refresh-cw",
    "🍔": "utensils",
    "🛒": "shopping-cart",
    "🪑": "armchair",
    "🎁": "gift",
    "🏥": "hospital",
    "🏨": "hotel",
    "🏠": "house",
    "💻": "laptop",
    "⚖️": "scale",
    "❓": "circle-help",
    "👤": "user",
    "🐕": "dog",
    "💳": "credit-card",
    "🧾": "receipt",
    "🔧": "wrench",
    "⚽": "volleyball",
    "✏️": "pencil",
    "🎫": "ticket",
    "🧸": "toy-brick",
    "🚗": "car",
    "⚡": "zap",
    "🤝": "handshake",
    "↩️": "undo-2",
    "💼": "briefcase",
    "🎉": "party-popper",
    "🏛️": "landmark",
    "👥": "users",
    "💰": "wallet",
    "🛍️": "shopping-bag",
}

_FALLBACK_LUCIDE = "tags"
_CATEGORY_ICON_SIZE = ICON_SIZE


def category_display_label(name: str, *, income: bool = False, name_local: str = "") -> str:
    """Return category label text without the DB emoji glyph."""
    display = name.strip()
    if income:
        display = f"{display} (Income)"
    local = name_local.strip()
    if local:
        display = f"{display} ({local})"
    return display


def category_lucide_icon(emoji: str, size: int = _CATEGORY_ICON_SIZE) -> QIcon:
    """Return a Lucide `QIcon` for a category emoji, or empty when `emoji` is blank."""
    name = lucide_name_for_category_icon(emoji)
    if name is None:
        return QIcon()
    return create_lucide_icon(name, size)


def lucide_name_for_category_icon(emoji: str) -> str | None:
    """Return Lucide ID for a category emoji, or `None` when blank."""
    raw = emoji.strip()
    if not raw:
        return None
    # Variation selectors / ZWJ sequences: try exact, then stripped token.
    mapped = FINANCE_CATEGORY_EMOJI_TO_LUCIDE.get(raw)
    if mapped is None:
        key = raw.replace("\ufe0f", "")
        mapped = FINANCE_CATEGORY_EMOJI_TO_LUCIDE.get(key)
    if mapped is None:
        mapped = lucide_name_for_chrome_emoji(raw)
    return mapped or _FALLBACK_LUCIDE


def strip_category_display_value(category_value: str) -> str:
    """Strip a leading emoji and `(Income)` marker from a category display value."""
    _emoji, rest = split_leading_emoji(category_value)
    text = rest if _emoji else category_value
    return text.replace(" (Income)", "").strip()

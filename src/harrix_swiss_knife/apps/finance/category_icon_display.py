"""Map finance category emoji (DB `categories.icon`) to Lucide for UI display.

The database and catalog keep emoji strings in `icon`. Optional `icon_lucide`
stores an explicit Lucide ID chosen in the category dialog. When empty, UI
falls back to the emoji→Lucide map (or `tags` for unknown emoji).

Category icons always use a neutral dark stroke so they do not inherit
CodeStyle semantic colors (`sparkles` blue, `pencil` orange, …).

"""

from __future__ import annotations

from PySide6.QtGui import QIcon

from harrix_swiss_knife.fluent.tokens import ICON_SIZE
from harrix_swiss_knife.qt_emoji_icon import split_leading_emoji
from harrix_swiss_knife.qt_lucide_icon import (
    LUCIDE_COLOR_DARK,
    create_lucide_icon,
    lucide_name_for_chrome_emoji,
    lucide_svg_path,
)

# Seed / preset emoji → Lucide id. Unknown custom emoji falls back below.
FINANCE_CATEGORY_EMOJI_TO_LUCIDE: dict[str, str] = {
    "🔌": "plug",
    "💄": "spray-can",  # not `sparkles` — that is the AI chrome glyph
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

# Preset strip in the Lucide picker (finance-relevant ids).
FINANCE_CATEGORY_LUCIDE_PRESETS: tuple[str, ...] = tuple(
    dict.fromkeys([*sorted(FINANCE_CATEGORY_EMOJI_TO_LUCIDE.values()), "tags"])
)

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


def category_lucide_icon(
    emoji: str = "",
    size: int = _CATEGORY_ICON_SIZE,
    *,
    lucide_name: str = "",
) -> QIcon:
    """Return a neutral Lucide `QIcon` for a category.

    Prefers an explicit `lucide_name` override from `categories.icon_lucide`.
    Otherwise resolves from the DB emoji via `lucide_name_for_category_icon`.

    """
    name = resolve_category_lucide_name(emoji=emoji, lucide_name=lucide_name)
    if name is None:
        return QIcon()
    return create_lucide_icon(name, size, color=LUCIDE_COLOR_DARK)


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


def resolve_category_lucide_name(*, emoji: str = "", lucide_name: str = "") -> str | None:
    """Return the Lucide ID to paint for a category row."""
    override = lucide_name.strip()
    if override and lucide_svg_path(override) is not None:
        return override
    return lucide_name_for_category_icon(emoji)


def strip_category_display_value(category_value: str) -> str:
    """Strip a leading emoji and `(Income)` marker from a category display value."""
    _emoji, rest = split_leading_emoji(category_value)
    text = rest if _emoji else category_value
    return text.replace(" (Income)", "").strip()

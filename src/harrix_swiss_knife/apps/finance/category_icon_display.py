"""Map finance category emoji (DB `categories.icon`) to Lucide for UI display.

The database and catalog keep emoji strings in `icon`. Optional `icon_lucide`
stores an explicit Lucide ID chosen in the category dialog. When empty, UI
falls back to the emoji→Lucide map (or `tags` for unknown emoji).

Category icons use a stable chromatic stroke per Lucide ID (semantic colors for
seed icons, otherwise a hashed CodeStyle palette) so the picker and table stay
colorful without inheriting chrome action colors (`sparkles` blue, …).

"""

from __future__ import annotations

import hashlib

from PySide6.QtGui import QIcon

from harrix_swiss_knife.fluent.tokens import ICON_SIZE
from harrix_swiss_knife.qt_emoji_icon import split_leading_emoji
from harrix_swiss_knife.qt_lucide_icon import (
    LUCIDE_COLOR_BLUE,
    LUCIDE_COLOR_GREEN,
    LUCIDE_COLOR_GREEN_2,
    LUCIDE_COLOR_ORANGE,
    LUCIDE_COLOR_RED,
    LUCIDE_COLOR_TURQUOISE,
    create_lucide_icon,
    lucide_name_for_chrome_emoji,
    lucide_svg_path,
)

# Deeper gold / cyan than chrome `LUCIDE_COLOR_YELLOW` / `CYAN` so icons stay
# readable on day-band table fills without raising stroke weight.
_CATEGORY_GOLD = "#c49a2a"
_CATEGORY_CYAN = "#3d8fad"

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

# Semantic strokes for known category Lucide IDs (visible on light and dark chrome).
CATEGORY_LUCIDE_COLORS: dict[str, str] = {
    "utensils": LUCIDE_COLOR_ORANGE,
    "coffee": LUCIDE_COLOR_ORANGE,
    "shopping-cart": LUCIDE_COLOR_ORANGE,
    "shopping-bag": LUCIDE_COLOR_ORANGE,
    "car": LUCIDE_COLOR_BLUE,
    "plug": _CATEGORY_GOLD,
    "zap": _CATEGORY_GOLD,
    "house": LUCIDE_COLOR_TURQUOISE,
    "hotel": LUCIDE_COLOR_TURQUOISE,
    "armchair": LUCIDE_COLOR_TURQUOISE,
    "laptop": _CATEGORY_CYAN,
    "wrench": _CATEGORY_CYAN,
    "receipt": _CATEGORY_CYAN,
    "wallet": LUCIDE_COLOR_GREEN,
    "credit-card": LUCIDE_COLOR_GREEN,
    "landmark": LUCIDE_COLOR_GREEN,
    "briefcase": LUCIDE_COLOR_GREEN_2,
    "handshake": LUCIDE_COLOR_GREEN_2,
    "gift": _CATEGORY_GOLD,
    "party-popper": _CATEGORY_GOLD,
    "ticket": _CATEGORY_GOLD,
    "hospital": LUCIDE_COLOR_RED,
    "spray-can": LUCIDE_COLOR_RED,
    "scale": LUCIDE_COLOR_BLUE,
    "book-open": LUCIDE_COLOR_BLUE,
    "graduation-cap": LUCIDE_COLOR_BLUE,
    "clapperboard": _CATEGORY_CYAN,
    "volleyball": LUCIDE_COLOR_GREEN,
    "dog": LUCIDE_COLOR_ORANGE,
    "baby": LUCIDE_COLOR_ORANGE,
    "shirt": _CATEGORY_CYAN,
    "user": LUCIDE_COLOR_TURQUOISE,
    "users": LUCIDE_COLOR_TURQUOISE,
    "pencil": LUCIDE_COLOR_ORANGE,
    "toy-brick": _CATEGORY_GOLD,
    "refresh-cw": LUCIDE_COLOR_TURQUOISE,
    "undo-2": LUCIDE_COLOR_TURQUOISE,
    "circle-help": _CATEGORY_CYAN,
    "tags": _CATEGORY_CYAN,
}

_CATEGORY_COLOR_PALETTE: tuple[str, ...] = (
    LUCIDE_COLOR_BLUE,
    _CATEGORY_CYAN,
    LUCIDE_COLOR_TURQUOISE,
    LUCIDE_COLOR_GREEN,
    LUCIDE_COLOR_GREEN_2,
    LUCIDE_COLOR_ORANGE,
    _CATEGORY_GOLD,
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


def category_lucide_color(lucide_name: str) -> str:
    """Return a stable chromatic stroke for category Lucide ID `lucide_name`."""
    name = lucide_name.strip()
    if not name:
        return _CATEGORY_CYAN
    mapped = CATEGORY_LUCIDE_COLORS.get(name)
    if mapped is not None:
        return mapped
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return _CATEGORY_COLOR_PALETTE[digest[0] % len(_CATEGORY_COLOR_PALETTE)]


def category_lucide_icon(
    emoji: str = "",
    size: int = _CATEGORY_ICON_SIZE,
    *,
    lucide_name: str = "",
) -> QIcon:
    """Return a colored Lucide `QIcon` for a category.

    Prefers an explicit `lucide_name` override from `categories.icon_lucide`.
    Otherwise resolves from the DB emoji via `lucide_name_for_category_icon`.

    """
    name = resolve_category_lucide_name(emoji=emoji, lucide_name=lucide_name)
    if name is None:
        return QIcon()
    return create_lucide_icon(name, size, color=category_lucide_color(name))


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

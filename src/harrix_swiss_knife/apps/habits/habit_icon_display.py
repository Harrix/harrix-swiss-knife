"""Map habit emoji to Lucide IDs and paint colored habit icons.

The database keeps emoji in `habits.emoji`. Optional `icon_lucide` stores an
explicit Lucide ID from the habit editor. When `icon_lucide` is empty, UI shows
the emoji glyph (no auto-map at paint time). Schema ensure backfills empty
`icon_lucide` from `HABIT_EMOJI_TO_LUCIDE` when a mapping exists.

"""

from __future__ import annotations

import hashlib

from PySide6.QtGui import QIcon

from harrix_swiss_knife.fluent.tokens import ICON_SIZE
from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
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

_HABIT_GOLD = "#c49a2a"
_HABIT_CYAN = "#3d8fad"

# Habit emoji → Lucide id (presets + common custom habit glyphs for backfill).
HABIT_EMOJI_TO_LUCIDE: dict[str, str] = {
    "✅": "circle-check",
    "🏃": "person-standing",
    "🚶": "footprints",
    "🚴": "bike",
    "🏋️": "dumbbell",
    "🧘": "leaf",
    "🤸": "activity",
    "💧": "droplet",
    "🥗": "salad",
    "🍎": "apple",
    "☕": "coffee",
    "📚": "library",
    "✍️": "pencil",
    "🧠": "brain",
    "💤": "moon",
    "🌅": "sunrise",
    "🌙": "moon-star",
    "🧹": "broom",
    "🧺": "shopping-basket",
    "💊": "pill",
    "💉": "syringe",
    "🦷": "smile",
    "👃": "wind",
    "👄": "mouth",
    "👁️": "eye",
    "👁": "eye",
    "🧴": "bath",
    "🎧": "headphones",
    "🎸": "music",
    "🎨": "palette",
    "📷": "camera",
    "💻": "laptop",
    "📧": "mail",
    "📞": "phone",
    "💰": "wallet",
    "🛒": "shopping-cart",
    "🌱": "sprout",
    "🌳": "tree-deciduous",
    "🐶": "dog",
    "🐱": "cat",
    "❤️": "heart",
    "🔥": "flame",
    "⭐": "star",
    "🎯": "target",
    "📌": "pin",
    "🗓️": "calendar",
    "⏰": "clock",
    "📝": "notebook-pen",
    "📓": "notebook",
    "📖": "book-open",
    "📕": "book",
    "🧩": "puzzle",
    "🎮": "gamepad-2",
    "⚽": "volleyball",
    "🎾": "circle",
    "🏊": "waves",
    "🎂": "cake",
    "🧁": "cupcake",
    "🎉": "party-popper",
    "🗽": "landmark",
    "🌐": "globe",
    "🔤": "languages",
    "🇬🇧": "languages",
    "🇺🇸": "languages",
    "🔨": "hammer",
    "🔧": "wrench",
    "🛠️": "wrench",
    "🧰": "hammer",
    "🖨️": "printer",
    "💼": "briefcase",
    "🏢": "building-2",
    "💪": "dumbbell",
    "🤒": "thermometer",
    "🏥": "hospital",
    "😷": "shield-plus",
}

HABIT_LUCIDE_PRESETS: tuple[str, ...] = tuple(dict.fromkeys([*sorted(HABIT_EMOJI_TO_LUCIDE.values()), "circle-check"]))

HABIT_LUCIDE_COLORS: dict[str, str] = {
    "circle-check": LUCIDE_COLOR_GREEN,
    "person-standing": LUCIDE_COLOR_ORANGE,
    "footprints": LUCIDE_COLOR_ORANGE,
    "bike": LUCIDE_COLOR_BLUE,
    "dumbbell": LUCIDE_COLOR_RED,
    "leaf": LUCIDE_COLOR_GREEN,
    "droplet": LUCIDE_COLOR_BLUE,
    "salad": LUCIDE_COLOR_GREEN,
    "apple": LUCIDE_COLOR_RED,
    "coffee": LUCIDE_COLOR_ORANGE,
    "library": LUCIDE_COLOR_BLUE,
    "book-open": LUCIDE_COLOR_BLUE,
    "pencil": LUCIDE_COLOR_ORANGE,
    "notebook-pen": LUCIDE_COLOR_ORANGE,
    "brain": _HABIT_CYAN,
    "moon": LUCIDE_COLOR_TURQUOISE,
    "moon-star": LUCIDE_COLOR_TURQUOISE,
    "sunrise": _HABIT_GOLD,
    "broom": _HABIT_CYAN,
    "shopping-basket": LUCIDE_COLOR_ORANGE,
    "pill": LUCIDE_COLOR_RED,
    "syringe": LUCIDE_COLOR_RED,
    "smile": _HABIT_GOLD,
    "mouth": LUCIDE_COLOR_ORANGE,
    "eye": LUCIDE_COLOR_BLUE,
    "wind": LUCIDE_COLOR_TURQUOISE,
    "bath": LUCIDE_COLOR_TURQUOISE,
    "headphones": LUCIDE_COLOR_BLUE,
    "music": LUCIDE_COLOR_BLUE,
    "palette": LUCIDE_COLOR_ORANGE,
    "camera": _HABIT_CYAN,
    "laptop": _HABIT_CYAN,
    "mail": LUCIDE_COLOR_BLUE,
    "phone": LUCIDE_COLOR_GREEN_2,
    "wallet": LUCIDE_COLOR_GREEN,
    "shopping-cart": LUCIDE_COLOR_ORANGE,
    "sprout": LUCIDE_COLOR_GREEN,
    "tree-deciduous": LUCIDE_COLOR_GREEN_2,
    "dog": LUCIDE_COLOR_ORANGE,
    "cat": _HABIT_GOLD,
    "heart": LUCIDE_COLOR_RED,
    "flame": LUCIDE_COLOR_ORANGE,
    "star": _HABIT_GOLD,
    "target": LUCIDE_COLOR_RED,
    "pin": LUCIDE_COLOR_RED,
    "calendar": LUCIDE_COLOR_BLUE,
    "clock": _HABIT_CYAN,
    "puzzle": LUCIDE_COLOR_TURQUOISE,
    "gamepad-2": LUCIDE_COLOR_BLUE,
    "volleyball": LUCIDE_COLOR_GREEN,
    "circle": LUCIDE_COLOR_GREEN_2,
    "waves": LUCIDE_COLOR_BLUE,
    "activity": LUCIDE_COLOR_ORANGE,
    "cake": _HABIT_GOLD,
    "cupcake": _HABIT_GOLD,
    "party-popper": _HABIT_GOLD,
    "landmark": LUCIDE_COLOR_BLUE,
    "globe": LUCIDE_COLOR_BLUE,
    "languages": LUCIDE_COLOR_BLUE,
    "hammer": _HABIT_CYAN,
    "wrench": _HABIT_CYAN,
    "printer": _HABIT_CYAN,
    "briefcase": LUCIDE_COLOR_GREEN_2,
    "building-2": LUCIDE_COLOR_GREEN_2,
    "notebook": LUCIDE_COLOR_ORANGE,
    "book": LUCIDE_COLOR_BLUE,
    "thermometer": LUCIDE_COLOR_RED,
    "hospital": LUCIDE_COLOR_RED,
    "shield-plus": LUCIDE_COLOR_GREEN,
}

_HABIT_COLOR_PALETTE: tuple[str, ...] = (
    LUCIDE_COLOR_BLUE,
    _HABIT_CYAN,
    LUCIDE_COLOR_TURQUOISE,
    LUCIDE_COLOR_GREEN,
    LUCIDE_COLOR_GREEN_2,
    LUCIDE_COLOR_ORANGE,
    _HABIT_GOLD,
    LUCIDE_COLOR_RED,
)

_HABIT_ICON_SIZE = ICON_SIZE


def habit_display_icon(*, emoji: str = "", lucide_name: str = "", size: int = _HABIT_ICON_SIZE) -> QIcon:
    """Return Lucide icon when set, otherwise an emoji glyph icon."""
    lucide = resolve_habit_display_lucide(lucide_name=lucide_name)
    if lucide:
        return habit_lucide_icon(lucide, size)
    cleaned = emoji.strip()
    if cleaned:
        return create_emoji_icon(cleaned, size)
    return QIcon()


def habit_lucide_color(lucide_name: str) -> str:
    """Return a stable chromatic stroke for habit Lucide ID `lucide_name`."""
    name = lucide_name.strip()
    if not name:
        return _HABIT_CYAN
    mapped = HABIT_LUCIDE_COLORS.get(name)
    if mapped is not None:
        return mapped
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return _HABIT_COLOR_PALETTE[digest[0] % len(_HABIT_COLOR_PALETTE)]


def habit_lucide_icon(lucide_name: str = "", size: int = _HABIT_ICON_SIZE) -> QIcon:
    """Return a colored Lucide `QIcon` when `lucide_name` is a known SVG ID."""
    name = lucide_name.strip()
    if not name or lucide_svg_path(name) is None:
        return QIcon()
    return create_lucide_icon(name, size, color=habit_lucide_color(name))


def lucide_name_for_habit_emoji(emoji: str) -> str | None:
    """Return Lucide ID suggested for a habit emoji, or `None` when blank/unknown."""
    raw = emoji.strip()
    if not raw:
        return None
    mapped = HABIT_EMOJI_TO_LUCIDE.get(raw)
    if mapped is None:
        key = raw.replace("\ufe0f", "")
        mapped = HABIT_EMOJI_TO_LUCIDE.get(key)
    if mapped is None:
        mapped = lucide_name_for_chrome_emoji(raw)
    if mapped and lucide_svg_path(mapped) is not None:
        return mapped
    return None


def normalize_habit_lucide_name(lucide_name: str | None) -> str:
    """Return a trimmed Lucide ID when the SVG exists, otherwise empty."""
    name = (lucide_name or "").strip()
    if name and lucide_svg_path(name) is not None:
        return name
    return ""


def resolve_habit_display_lucide(*, lucide_name: str = "") -> str | None:
    """Return Lucide ID to paint, or `None` to fall back to emoji."""
    name = normalize_habit_lucide_name(lucide_name)
    return name or None

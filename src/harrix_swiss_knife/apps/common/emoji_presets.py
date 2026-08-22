"""Shared popular-emoji catalogs for picker grids."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

# Order is part of habit default assignment (`habit_id % len(...)`). Do not reorder.
POPULAR_EMOJI_PRESETS: tuple[str, ...] = (
    "✅",
    "🏃",
    "🚶",
    "🚴",
    "🏋️",
    "🧘",
    "💧",
    "🥗",
    "🍎",
    "☕",
    "📚",
    "✍️",
    "🧠",
    "💤",
    "🌅",
    "🌙",
    "🧹",
    "🧺",
    "💊",
    "🦷",
    "🧴",
    "🎧",
    "🎸",
    "🎨",
    "📷",
    "💻",
    "📧",
    "📞",
    "💰",
    "🛒",
    "🌱",
    "🌳",
    "🐶",
    "🐱",
    "❤️",
    "🔥",
    "⭐",
    "🎯",
    "📌",
    "🗓️",
    "⏰",
    "📝",
    "📖",
    "🧩",
    "🎮",
    "⚽",
    "🎾",
    "🏊",
)

FINANCE_CATEGORY_EMOJI_PRESETS: tuple[str, ...] = (
    "💰",
    "🍔",
    "☕",
    "🛒",
    "🚗",
    "🏠",
    "⚡",
    "💻",
    "👕",
    "🎁",
    "🏥",
    "🏨",
    "📚",
    "📖",
    "💄",
    "🔌",
    "🪑",
    "🎫",
    "🧸",
    "⚽",
    "✏️",
    "🔧",
    "💳",
    "🧾",
    "💼",
    "🛍️",
    "🎉",
    "🤝",
    "🏛️",
    "👥",
    "🐕",
    "👤",
    "❓",
    "↩️",
)


def unique_emojis(*groups: Iterable[str]) -> tuple[str, ...]:
    """Return emojis in first-seen order across `groups`."""
    seen: set[str] = set()
    result: list[str] = []
    for group in groups:
        for emoji in group:
            value = str(emoji).strip()
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
    return tuple(result)


FINANCE_EMOJI_PRESETS: tuple[str, ...] = unique_emojis(FINANCE_CATEGORY_EMOJI_PRESETS, POPULAR_EMOJI_PRESETS)

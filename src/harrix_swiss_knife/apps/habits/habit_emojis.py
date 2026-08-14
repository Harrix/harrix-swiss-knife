"""Preset emoji catalog for habits."""

from __future__ import annotations

HABIT_EMOJI_PRESETS: tuple[str, ...] = (
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


def default_habit_emoji(habit_id: int) -> str:
    """Return a stable preset emoji for a habit ID."""
    if not HABIT_EMOJI_PRESETS:
        return "✅"
    return HABIT_EMOJI_PRESETS[habit_id % len(HABIT_EMOJI_PRESETS)]


def normalize_habit_emoji(emoji: str | None, *, habit_id: int | None = None) -> str:
    """Return a cleaned emoji or a fallback when empty."""
    value = (emoji or "").strip()
    if value:
        return value
    if habit_id is not None:
        return default_habit_emoji(habit_id)
    return HABIT_EMOJI_PRESETS[0] if HABIT_EMOJI_PRESETS else "✅"

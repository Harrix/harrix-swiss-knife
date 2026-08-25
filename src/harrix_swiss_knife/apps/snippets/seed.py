"""Seed lists for the snippets database (`recover.sql`)."""

# ruff: noqa: RUF001

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.emoji_presets import FINANCE_CATEGORY_EMOJI_PRESETS, POPULAR_EMOJI_PRESETS
from harrix_swiss_knife.apps.snippets.constants import (
    SEED_CREATED_AT,
    ZONE_COLOR,
    ZONE_EMOJI,
    ZONE_PHRASE,
    ZONE_SYMBOL,
    ZONES,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from harrix_swiss_knife.apps.snippets.database_manager import DatabaseManager

SEED_PHRASES: tuple[str, ...] = (
    "➕ Add",
    "➕ Add annotations for",
    '➕ Add book "{TitleEnglish}" {AuthorEnglish}',
    "➕ Add CC BY 4.0 license",
    '☕ Add coffee note "{Title}" in {City}',
    "➕ Add empty line at end of file",
    '➕ Add event "{Title}"',
    '➕ Add featured image for article ""',
    "➕ Add MIT license",
    "➕ Add more information about",
    '➕ Add travel "{Title}"',
    '🎬 Add movie ""',
    '🎬 Add series "" (season )',
    "💤 Add dreams",
    '💭 Add quotes from ""',
    '📖 Add section "" in .md',
    "⚗️ Add test for",
    "⚗️ Test",
    "⚠️ Add TODO",
    "🚀 Build",
    "🚀 Build project",
    "🚀 Build version 0",
    "➕ Create",
    "➕ Create test.md",
    "🗑️ Delete",
    "🗑️ Delete extra spaces",
    "🗑️ Delete unnecessary files",
    "🗑️ Delete unnecessary imports",
    "🗑️ Delete unnecessary lines in code",
    "🗑️ Delete unnecessary sections",
    "🗑️ Remove",
    "📚 Docs",
    "📚 Docs. Add license in markdown format",
    "📚 Docs. Add range on copyright year",
    "📚 Docs. Fix",
    "📚 Docs. Modify README.md",
    "📚 Docs. Style. Correct docs",
    "📚 Docs. Add docstring",
    "📚 Docs. Add docstrings and annotations for",
    "📚 Docs. Update",
    "🧪 Experiment",
    "🐞 Fix",
    "🐞 Fix annotations",
    "🐞 Fix bug with ...",
    "🐞 Fix links",
    "🐞 Fix punctuation errors",
    "🐞 Fix ruff check issues",
    "🐞 Fix ty check issues",
    "🐞 Fix Cursor ai check issues",
    "🐞 Fix Harrix PyLib check issues",
    "🐞 Fix spelling mistakes",
    "🐞 Fix spelling and punctuation mistakes",
    "🐞 Fix style error",
    "🐞 Fix. Sentence must start with capital letter",
    "🔀 Merge",
    "🔧 Modify",
    "🔧 Modify some parts of code",
    "🔧 Modify. Comment out code",
    "📥 Modify. Download images",
    "🔧 Modify. Here is description of code modifications",
    "🖼️ Modify. Optimize images",
    "🔧 Modify. Transform GIF and MP4 to AVIF",
    "🔠 Modify. Translate",
    "🚚 Move",
    "🚚 Move files from folder '' to folder ''",
    "🚀 Publish",
    "🚀 Publish article",
    "♻️ Refactor",
    "♻️ Refactor code",
    "📶 Refactor. Ruff format, sort, make docs in PY files",
    "📶 Refactor. Sort classes, methods, functions",
    "📶 Refactor. Sort sections",
    "✒️ Rename",
    "✒️ Rename files",
    "🔄 Replace",
    "🔄 Replace hyphens with long dash",
    "🔙 Revert",
    '🔙 Revert "Experiment with definition lists"',
    "✨ Style",
    "✨ Style. Beautify code",
    "✨ Style. Beautify MD files",
    "✨ Style. Beautify MD and regenerate g.md",
    "✨ Style. Correct article",
    "✨ Style. Correct code",
    "✨ Style. Correct markdown file",
    "✨ Style. Fix ruff check issues",
    "✨ Style. Update docstrings to Markdown format",
    "⬆️ Update",
    "⬆️ Update files on new version",
    "📦 Update combined notes",
    "⬆️ Update packages",
    "⬆️ Update Prompts.md",
    "📜 Update TOC",
)

SEED_EMOJIS_BASE: tuple[str, ...] = (
    "⭐",
    "🔥",
    "💥",
    "👍",
    "🔗",
    "❤️",
    "🎵",
    "⚡",
    "🗺️",
    "🌏",
    "🌎",
    "🎓",
    "🎁",
    "💾",
    "📷",
    "🎥",
    "💻",
    "☎️",
    "📞",
    "🔍",
    "🔒",
    "🔓",
    "🔑",
    "📧",
    "✉️",
    "📦",
    "📁",
    "📂",
    "📅",
    "📆",
    "⏱️",
    "🔔",
    "📚",
    "📖",
    "🏆",
    "🇷🇺",
    "🇺🇸",
    "❌",
    "✅",
    "❓",
    "❗",
    "⛔",
    "🚫",
    "🔖",
    "🏷️",
    "✏️",
    "🔞",
    "📝",
    "⚠️",
    "💡",
    "👉🏻",
    "4️⃣2️⃣",
    "🐍",
)

# Buttons, menus, reports, and habit extras not already in the preset catalogs.
SEED_APP_UI_EMOJIS: tuple[str, ...] = (
    "📋",
    "🧮",
    "☑️",
    "⬜",
    "➖",
    "▶️",
    "🗄",
    "🔎",
    "💱",
    "🏦",
    "⚖️",
    "🛠️",
    "🤖",
    "⚙️",
    "📱",
    "🪟",
    "🗂️",
    "🔬",
    "⌨️",
    "📊",
    "📸",
    "🔤",
    "📑",
    "💎",
    "🌟",
    "📓",
    "🎙️",
    "✂️",
    "🌐",
    "ℹ️",
    "👉",
    "👈",
    "↔️",
    "🔝",
    "⬇️",
    "🏃🏻",
    "📄",
    "🖲️",
    "🚧",
    "❞",
    "👃",
    "🗽",
    "👄",
    "💉",
    "👀",
    "🎂",
)

SEED_SYMBOLS: tuple[tuple[str, str], ...] = (  # ignore: HP001
    ("—", "Век живи — век учись. | Тире"),  # ignore: HP001
    ("–", "2010–2012 | Короткое тире"),  # ignore: HP001
    ("−", "5−2=3 | Минус"),  # ignore: HP001
    ("-", "Кое-что, тел.: 123-45-67 | Обычный дефис"),  # ignore: HP001
    ("«»", "Петя сказал: «Скоро Новый год». | Кавычки-елочки"),  # ignore: HP001
    ("©", "Все права защищены © 2022. | Знак копирайта"),  # ignore: HP001
    ("×", "1920 × 768 px | Знак умножения"),  # ignore: HP001
    ("→", "`File` → `New file` | Стрелка"),  # ignore: HP001
    ("…", "Надо так много сказать… | Троеточие"),  # ignore: HP001
    ("°", "Температура была +31°. | Градус"),  # ignore: HP001
    ("🠕", "Рост на 10% 🠕 | Повышение"),  # ignore: HP001
    ("🠗", "Падение на 10% 🠗 | Понижение"),  # ignore: HP001
)

SEED_COLORS: tuple[tuple[str, str], ...] = (
    ("#ffffff", "transparent filled objects on white icons (with 10% transparency)"),
    ("#f4f4f4", "white color in icons"),
    ("#e9e9e9", "white color in icons № 2"),
    ("#dddddd", "white color in icons № 3"),
    ("#bbbbbb", "next after #dddddd"),
    ("#999999", "next after #bbbbbb"),
    ("#444444", "shadow (with 15% transparency)"),
    ("#607785", "light grey"),
    ("#7193ad", "light grey № 2"),
    ("#36434f", "gray color, as well as dark background"),
    ("#122a3a", "dark grey"),
    ("#121e28", "almost black"),
    ("#79b1d1", "cyan"),
    ("#2e86b7", "blue"),
    ("#038387", "turquoise"),
    ("#3aaf9d", "light turquoise"),
    ("#de2b26", "logo"),
    ("#cc584c", "red"),
    ("#f84d18", "red № 2"),
    ("#ad403b", "dark red"),
    ("#eec646", "yellow"),
    ("#ffdd7a", "light yellow"),
    ("#ffa000", "orange"),
    ("#df7148", "orange № 2"),
    ("#4caf50", "green"),
    ("#35965f", "green № 2"),
    ("#ffcc80", "skin"),
    ("#e3b877", "skin № 2"),
    ("#ddc4b0", "light beige"),
    ("#e0ac7e", "beige"),
    ("#a18267", "brown"),
    ("#66442b", "dark brown"),
)


def build_recover_sql() -> str:
    """Return `recover.sql` text for a fresh snippets database."""
    lines = [
        "CREATE TABLE items (",
        "  _id INTEGER PRIMARY KEY,",
        "  zone TEXT NOT NULL,",
        "  value TEXT NOT NULL,",
        "  hint TEXT NOT NULL DEFAULT '',",
        "  created_at TEXT NOT NULL,",
        "  last_used_at TEXT,",
        "  sort_index INTEGER NOT NULL DEFAULT 0",
        ");",
        "",
        "CREATE TABLE zone_sort (",
        "  zone TEXT PRIMARY KEY,",
        "  mode TEXT NOT NULL,",
        "  descending INTEGER NOT NULL DEFAULT 0",
        ");",
        "",
    ]
    lines.extend(f"INSERT INTO zone_sort (zone, mode, descending) VALUES ('{zone}', 'alpha', 0);" for zone in ZONES)
    lines.append("")
    lines.extend(_insert_item_sql(ZONE_PHRASE, phrase, "", index) + ";" for index, phrase in enumerate(SEED_PHRASES))
    lines.append("")
    lines.extend(_insert_item_sql(ZONE_EMOJI, emoji, "", index) + ";" for index, emoji in enumerate(seed_emojis()))
    lines.append("")
    lines.extend(
        _insert_item_sql(ZONE_SYMBOL, value, hint, index) + ";" for index, (value, hint) in enumerate(SEED_SYMBOLS)
    )
    lines.append("")
    lines.extend(
        _insert_item_sql(ZONE_COLOR, value, hint, index) + ";" for index, (value, hint) in enumerate(SEED_COLORS)
    )
    lines.append("")
    return "\n".join(lines)


def ensure_seed_emojis(manager: DatabaseManager) -> int:
    """Insert seed emojis that are missing from an existing snippets database."""
    existing = {item.value for item in manager.list_items(ZONE_EMOJI)}
    missing = [(emoji, "") for emoji in seed_emojis() if emoji not in existing]
    if not missing:
        return 0
    if not manager.add_items(ZONE_EMOJI, missing):
        return 0
    return len(missing)


def extract_phrase_emojis(phrases: Sequence[str]) -> list[str]:
    """Return leading emoji tokens from phrases, in first-seen order."""
    result: list[str] = []
    for phrase in phrases:
        token = phrase.split(" ", 1)[0]
        if token and not token.isascii() and token not in result:
            result.append(token)
    return result


def seed_emojis() -> list[str]:
    """Return seed emojis: catalogs, app UI icons, and phrase-only extras."""
    return unique_emojis(
        SEED_EMOJIS_BASE,
        extract_phrase_emojis(SEED_PHRASES),
        POPULAR_EMOJI_PRESETS,
        FINANCE_CATEGORY_EMOJI_PRESETS,
        SEED_APP_UI_EMOJIS,
    )


def unique_emojis(*groups: Sequence[str]) -> list[str]:
    """Return emojis from `groups` without duplicates, preserving order."""
    result: list[str] = []
    for group in groups:
        for emoji in group:
            if emoji and emoji not in result:
                result.append(emoji)
    return result


def _insert_item_sql(zone: str, value: str, hint: str, sort_index: int) -> str:
    return (
        "INSERT INTO items (zone, value, hint, created_at, last_used_at, sort_index) "
        f"VALUES ('{_sql_escape(zone)}', '{_sql_escape(value)}', '{_sql_escape(hint)}', "
        f"'{SEED_CREATED_AT}', NULL, {sort_index})"
    )


def _sql_escape(value: str) -> str:
    return value.replace("'", "''")

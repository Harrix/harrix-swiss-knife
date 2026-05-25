"""Parse BotHub response for bulk food_log name_en translation."""

from __future__ import annotations

_TSV_COLUMN_COUNT = 2


def parse_food_translate_response(text: str) -> dict[str, str]:
    """Parse TSV lines Name<TAB>EnglishName into a name-to-translation map.

    Args:

    - `text` (`str`): Raw BotHub response.

    Returns:

    - `dict[str, str]`: Russian name to English translation. Empty on parse failure.

    """
    translations: dict[str, str] = {}
    for line in _iter_data_lines(text):
        parts = line.split("\t")
        if len(parts) != _TSV_COLUMN_COUNT:
            continue
        name = parts[0].strip()
        name_en = parts[1].strip()
        if not name or not name_en:
            continue
        translations[name] = name_en
    return translations


def _iter_data_lines(text: str) -> list[str]:
    """Return non-empty lines, skipping markdown code fences."""
    lines: list[str] = []
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        lines.append(line)
    return lines

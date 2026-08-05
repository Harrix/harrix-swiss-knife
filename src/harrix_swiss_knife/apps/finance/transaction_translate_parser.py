"""Parse BotHub response for bulk transaction description translation."""

from __future__ import annotations

_TSV_COLUMN_COUNT = 2


def parse_transaction_translate_response(text: str) -> dict[str, str]:
    """Parse Description<TAB>English lines into a translation map."""
    translations: dict[str, str] = {}
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        parts = line.split("\t")
        if len(parts) != _TSV_COLUMN_COUNT:
            continue
        description = parts[0].strip()
        description_en = parts[1].strip()
        if description and description_en:
            translations[description] = description_en
    return translations

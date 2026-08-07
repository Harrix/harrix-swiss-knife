"""Parse BotHub response for bulk transaction description translation."""

from __future__ import annotations

_TSV_COLUMN_COUNT = 2


def align_translations_to_descriptions(
    descriptions: list[str],
    translations: dict[str, str],
) -> dict[str, str]:
    """Map parsed translations onto exact DB description strings (trim-tolerant).

    BotHub often returns trimmed description keys while the database still has
    leading/trailing spaces, so exact dict lookup would leave preview cells empty.

    """
    by_trim: dict[str, str] = {}
    for key, value in translations.items():
        trimmed_key = key.strip()
        trimmed_value = value.strip()
        if trimmed_key and trimmed_value:
            by_trim.setdefault(trimmed_key, trimmed_value)

    aligned: dict[str, str] = {}
    for description in descriptions:
        english = translations.get(description) or by_trim.get(description.strip(), "")
        english = english.strip()
        if description and english:
            aligned[description] = english
    return aligned


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

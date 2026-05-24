"""Parse BotHub response for food kcal lookup."""

from __future__ import annotations

from dataclasses import dataclass

_TSV_COLUMN_COUNT = 4


@dataclass(frozen=True)
class KcalLookupResult:
    """Parsed kcal lookup fields for the manual food entry form."""

    calories: float
    is_weight_mode: bool
    is_drink: bool
    weight_g: int


def parse_kcal_lookup_response(text: str) -> KcalLookupResult | None:
    """Parse a TSV line: Calories, Mode, Drink, Weight."""
    line = _first_data_line(text)
    if not line:
        return None

    parts = line.split("\t")
    if len(parts) != _TSV_COLUMN_COUNT:
        return None

    try:
        calories = float(parts[0].strip().replace(",", "."))
    except ValueError:
        return None

    mode = parts[1].strip().lower()
    if mode not in {"weight", "portion"}:
        return None

    drink_raw = parts[2].strip().lower()
    if drink_raw not in {"yes", "no"}:
        return None

    try:
        weight_g = int(float(parts[3].strip().replace(",", ".")))
    except ValueError:
        return None

    if calories < 0 or weight_g < 0:
        return None

    return KcalLookupResult(
        calories=calories,
        is_weight_mode=mode == "weight",
        is_drink=drink_raw == "yes",
        weight_g=max(0, weight_g),
    )


def _first_data_line(text: str) -> str:
    """Return first non-empty line, stripping markdown code fences."""
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        return line
    return ""

"""Parse BotHub response for portion weight lookup from calories mode."""

from __future__ import annotations

from dataclasses import dataclass

_TSV_COLUMN_COUNT = 2


@dataclass(frozen=True)
class PortionWeightResult:
    """Parsed fields for portion weight lookup from the manual food entry form."""

    is_drink: bool
    weight_g: int


def parse_portion_weight_response(text: str) -> PortionWeightResult | None:
    """Parse a TSV line: Drink, Weight."""
    line = _first_data_line(text)
    if not line:
        return None

    parts = line.split("\t")
    if len(parts) != _TSV_COLUMN_COUNT:
        return None

    drink_raw = parts[0].strip().lower()
    if drink_raw not in {"yes", "no"}:
        return None

    try:
        weight_g = int(float(parts[1].strip().replace(",", ".")))
    except ValueError:
        return None

    if weight_g < 0:
        return None

    return PortionWeightResult(is_drink=drink_raw == "yes", weight_g=weight_g)


def _first_data_line(text: str) -> str:
    """Return first non-empty line, stripping markdown code fences."""
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        return line
    return ""

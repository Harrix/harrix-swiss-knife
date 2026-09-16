"""Approximate day-level protein / fat / carb analysis helpers for Food."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.food.food_log_calories import calculate_food_log_calories

if TYPE_CHECKING:
    from collections.abc import Sequence

_PROMPT_KEY = "food_day_macros"
_TSV_COLUMN_COUNT = 4
_MIN_DATA_LINES = 2
_FLOAT_RE = re.compile(r"^-?\d+(?:[.,]\d+)?$")
_VERDICT_PREFIX = "VERDICT:"


@dataclass(frozen=True, slots=True)
class DayMacrosResult:
    """Parsed approximate macros and AI norms for one calendar day."""

    protein_g: float
    fat_g: float
    carb_g: float
    kcal: float
    norm_protein_g: float
    norm_fat_g: float
    norm_carb_g: float
    norm_kcal: float
    verdict: str
    notes: str


class DayMacrosStatus(StrEnum):
    """Whether a saved day analysis matches the current food log."""

    MISSING = "missing"
    OK = "ok"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class FoodDayLogLine:
    """One denormalized `food_log` row used for hashing and the AI menu."""

    name: str
    name_en: str
    weight: float | None
    portion_calories: float | None
    calories_per_100g: float | None
    is_drink: bool


@dataclass(frozen=True, slots=True)
class FoodDayMacrosAnalysis:
    """Persisted AI day analysis row."""

    date: str
    protein_g: float
    fat_g: float
    carb_g: float
    kcal: float
    norm_protein_g: float
    norm_fat_g: float
    norm_carb_g: float
    norm_kcal: float
    verdict: str
    notes: str
    input_hash: str
    analyzed_at: str
    prompt_key: str = _PROMPT_KEY


def day_macros_prompt_key() -> str:
    """Return the BotHub prompt key for day macros analysis."""
    return _PROMPT_KEY


def food_day_input_hash(lines: Sequence[FoodDayLogLine]) -> str:
    """Return a stable SHA-256 hex digest of the day's log lines.

    Args:

    - `lines` (`Sequence[FoodDayLogLine]`): Rows for one calendar date.

    Returns:

    - `str`: Hex digest. Empty day yields the digest of an empty payload.

    """
    payload = "\n".join(_canonical_line(line) for line in sorted(lines, key=_sort_key))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def format_day_menu_for_prompt(lines: Sequence[FoodDayLogLine], *, total_kcal: float) -> str:
    """Build a plain-text menu block for the day macros prompt.

    Args:

    - `lines` (`Sequence[FoodDayLogLine]`): Food log rows for the day.
    - `total_kcal` (`float`): Sum of row calories for the day.

    Returns:

    - `str`: Human-readable menu plus total kcal.

    """
    rows: list[str] = []
    for line in lines:
        kcal = calculate_food_log_calories(line.weight, line.calories_per_100g, line.portion_calories)
        name = line.name.strip() or "(unnamed)"
        name_en = line.name_en.strip()
        label = f"{name} / {name_en}" if name_en else name
        weight = f"{line.weight:g} g" if line.weight is not None else "— g"
        drink = "drink" if line.is_drink else "food"
        rows.append(f"- {label}: {weight}, {kcal:.1f} kcal ({drink})")
    body = "\n".join(rows) if rows else "(no food log rows)"
    return f"{body}\n\nTotal kcal (from log): {total_kcal:.1f}"


def parse_day_macros_response(text: str) -> DayMacrosResult | None:
    """Parse AI output: intake TSV, norms TSV, then VERDICT and notes.

    Args:

    - `text` (`str`): Raw BotHub response.

    Returns:

    - `DayMacrosResult | None`: Parsed values, or `None` when invalid.

    """
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    data_lines = [line for line in lines if line and not line.startswith("```")]
    if len(data_lines) < _MIN_DATA_LINES:
        return None
    intake = _parse_tsv_floats(data_lines[0])
    norms = _parse_tsv_floats(data_lines[1])
    if intake is None or norms is None:
        return None
    protein_g, fat_g, carb_g, kcal = intake
    norm_protein_g, norm_fat_g, norm_carb_g, norm_kcal = norms
    if min(protein_g, fat_g, carb_g, kcal, norm_protein_g, norm_fat_g, norm_carb_g, norm_kcal) < 0:
        return None
    verdict = ""
    notes_parts: list[str] = []
    for line in data_lines[2:]:
        if line.upper().startswith(_VERDICT_PREFIX):
            verdict = line[len(_VERDICT_PREFIX) :].strip()
            continue
        notes_parts.append(line)
    return DayMacrosResult(
        protein_g=protein_g,
        fat_g=fat_g,
        carb_g=carb_g,
        kcal=kcal,
        norm_protein_g=norm_protein_g,
        norm_fat_g=norm_fat_g,
        norm_carb_g=norm_carb_g,
        norm_kcal=norm_kcal,
        verdict=verdict,
        notes="\n".join(notes_parts).strip(),
    )


def percent_of_norm(value: float, norm: float) -> float | None:
    """Return `value` as a percent of `norm`, or `None` when `norm` is zero."""
    if norm <= 0:
        return None
    return (float(value) / float(norm)) * 100.0


def resolve_day_macros_status(
    analysis: FoodDayMacrosAnalysis | None,
    current_hash: str,
) -> DayMacrosStatus:
    """Compare a saved analysis with the current day hash.

    Args:

    - `analysis` (`FoodDayMacrosAnalysis | None`): Stored row, if any.
    - `current_hash` (`str`): Hash of the current food log for that date.

    Returns:

    - `DayMacrosStatus`: `missing`, `ok`, or `stale`.

    """
    if analysis is None:
        return DayMacrosStatus.MISSING
    if analysis.input_hash == current_hash:
        return DayMacrosStatus.OK
    return DayMacrosStatus.STALE


def _canonical_line(line: FoodDayLogLine) -> str:
    return "\t".join(
        [
            line.name.strip(),
            line.name_en.strip(),
            _num(line.weight),
            _num(line.portion_calories),
            _num(line.calories_per_100g),
            "1" if line.is_drink else "0",
        ]
    )


def _num(value: float | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.6f}".rstrip("0").rstrip(".")


def _parse_tsv_floats(line: str) -> tuple[float, float, float, float] | None:
    parts = line.split("\t")
    if len(parts) < _TSV_COLUMN_COUNT:
        return None
    values: list[float] = []
    for part in parts[:_TSV_COLUMN_COUNT]:
        raw = part.strip().replace(",", ".")
        if not _FLOAT_RE.match(raw):
            return None
        values.append(float(raw))
    return values[0], values[1], values[2], values[3]


def _sort_key(line: FoodDayLogLine) -> tuple[str, str, str, str, str, str]:
    return (
        line.name.casefold(),
        line.name_en.casefold(),
        _num(line.weight),
        _num(line.portion_calories),
        _num(line.calories_per_100g),
        "1" if line.is_drink else "0",
    )

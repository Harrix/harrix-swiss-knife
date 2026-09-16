"""Approximate day-level protein / fat / carb analysis helpers for Food."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Literal

from harrix_swiss_knife.apps.food.food_log_calories import calculate_food_log_calories

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_PROMPT_KEY = "food_day_macros"
_RANGE_PROMPT_KEY = "food_range_macros"
_TSV_COLUMN_COUNT = 4
_MIN_DATA_LINES = 2
_FLOAT_RE = re.compile(r"^-?\d+(?:[.,]\d+)?$")
_VERDICT_PREFIX = "VERDICT:"
_VERDICT_EN_PREFIX = "VERDICT_EN:"
_EN_SECTION = "EN:"
_LOCAL_SECTION = "LOCAL:"

# Share of AI day-norm treated as balanced / warning / bad.
_MACRO_OK_LOW = 75.0
_MACRO_OK_HIGH = 125.0
_MACRO_WARN_LOW = 60.0
_MACRO_WARN_HIGH = 150.0

MacroTone = Literal["good", "warn", "bad", "neutral"]


@dataclass(frozen=True, slots=True)
class CalorieThresholds:
    """Configured kcal bands from `food_calorie_thresholds`."""

    low: float = 1800.0
    medium_low: float = 2100.0
    medium_high: float = 2500.0


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
    verdict_en: str = ""
    notes_en: str = ""


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
    verdict_en: str = ""
    notes_en: str = ""


@dataclass(frozen=True, slots=True)
class FoodRangeMacrosAnalysis:
    """Persisted AI multi-day macros summary."""

    date_from: str
    date_to: str
    verdict: str
    notes: str
    verdict_en: str
    notes_en: str
    input_hash: str
    analyzed_at: str
    prompt_key: str = _RANGE_PROMPT_KEY


@dataclass(frozen=True, slots=True)
class RangeMacrosResult:
    """Parsed bilingual period-level macros advice."""

    verdict: str
    notes: str
    verdict_en: str
    notes_en: str


def calorie_band_rgb(kcal: float, thresholds: CalorieThresholds) -> tuple[int, int, int]:
    """Return pastel RGB for a daily kcal total vs configured bands.

    Bands match the kcal-per-day table and charts: low → green, medium-low →
    light yellow, medium-high → bisque, above medium-high → pink.

    """
    if kcal <= thresholds.low:
        return (144, 238, 144)
    if kcal <= thresholds.medium_low:
        return (255, 255, 224)
    if kcal <= thresholds.medium_high:
        return (255, 228, 196)
    return (255, 192, 203)


def calorie_thresholds_from_config(config: Mapping[str, Any] | None) -> CalorieThresholds:
    """Parse `food_calorie_thresholds` from app config with defaults."""
    raw = (config or {}).get("food_calorie_thresholds", {})
    if not isinstance(raw, dict):
        return CalorieThresholds()
    return CalorieThresholds(
        low=_as_positive_float(raw.get("low"), 1800.0),
        medium_low=_as_positive_float(raw.get("medium_low"), 2100.0),
        medium_high=_as_positive_float(raw.get("medium_high"), 2500.0),
    )


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


def food_range_input_hash(day_hashes: Sequence[tuple[str, str]]) -> str:
    """Hash of `(date, day_input_hash)` pairs for a multi-day summary."""
    payload = "\n".join(f"{day}\t{digest}" for day, digest in sorted(day_hashes))
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


def format_days_summary_for_range_prompt(analyses: Sequence[FoodDayMacrosAnalysis]) -> str:
    """Build a per-day macros block for the range-macros prompt."""
    lines = [
        (
            f"{row.date}: P {row.protein_g:.0f}/{row.norm_protein_g:.0f} g, "
            f"F {row.fat_g:.0f}/{row.norm_fat_g:.0f} g, "
            f"C {row.carb_g:.0f}/{row.norm_carb_g:.0f} g, "
            f"kcal {row.kcal:.0f}/{row.norm_kcal:.0f}"
        )
        for row in analyses
    ]
    return "\n".join(lines) if lines else "(no day analyses)"


def kcal_tone(kcal: float, thresholds: CalorieThresholds) -> MacroTone:
    """Map intake kcal onto configured low / medium / high bands."""
    if kcal <= thresholds.low:
        return "good"
    if kcal <= thresholds.medium_high:
        return "warn" if kcal > thresholds.medium_low else "good"
    return "bad"


def macro_tone(value: float, norm: float) -> MacroTone:
    """Map intake vs AI norm percent onto good / warn / bad."""
    pct = percent_of_norm(value, norm)
    if pct is None:
        return "neutral"
    if _MACRO_OK_LOW <= pct <= _MACRO_OK_HIGH:
        return "good"
    if _MACRO_WARN_LOW <= pct <= _MACRO_WARN_HIGH:
        return "warn"
    return "bad"


def parse_day_macros_response(text: str) -> DayMacrosResult | None:
    """Parse AI output: intake TSV, norms TSV, bilingual verdict/notes.

    Args:

    - `text` (`str`): Raw BotHub response.

    Returns:

    - `DayMacrosResult | None`: Parsed values, or `None` when invalid.

    """
    lines = _normalize_response_lines(text)
    tsv_indices: list[int] = []
    for index, line in enumerate(lines):
        if not line or line.startswith("```"):
            continue
        if _parse_tsv_floats(line) is None:
            continue
        tsv_indices.append(index)
        if len(tsv_indices) == _MIN_DATA_LINES:
            break
    if len(tsv_indices) < _MIN_DATA_LINES:
        return None
    intake = _parse_tsv_floats(lines[tsv_indices[0]])
    norms = _parse_tsv_floats(lines[tsv_indices[1]])
    if intake is None or norms is None:
        return None
    protein_g, fat_g, carb_g, kcal = intake
    norm_protein_g, norm_fat_g, norm_carb_g, norm_kcal = norms
    if min(protein_g, fat_g, carb_g, kcal, norm_protein_g, norm_fat_g, norm_carb_g, norm_kcal) < 0:
        return None
    tail = [line for line in lines[tsv_indices[1] + 1 :] if not line.startswith("```")]
    bilingual = _parse_bilingual_tail(tail)
    return DayMacrosResult(
        protein_g=protein_g,
        fat_g=fat_g,
        carb_g=carb_g,
        kcal=kcal,
        norm_protein_g=norm_protein_g,
        norm_fat_g=norm_fat_g,
        norm_carb_g=norm_carb_g,
        norm_kcal=norm_kcal,
        verdict=bilingual.verdict,
        notes=bilingual.notes,
        verdict_en=bilingual.verdict_en,
        notes_en=bilingual.notes_en,
    )


def parse_range_macros_response(text: str) -> RangeMacrosResult | None:
    """Parse bilingual period advice (no TSV lines)."""
    lines = _normalize_response_lines(text)
    data_lines = [line for line in lines if not line.startswith("```")]
    if not any(line for line in data_lines):
        return None
    bilingual = _parse_bilingual_tail(data_lines)
    if not (bilingual.verdict or bilingual.verdict_en or bilingual.notes or bilingual.notes_en):
        return None
    return bilingual


def percent_of_norm(value: float, norm: float) -> float | None:
    """Return `value` as a percent of `norm`, or `None` when `norm` is zero."""
    if norm <= 0:
        return None
    return (float(value) / float(norm)) * 100.0


def range_macros_prompt_key() -> str:
    """Return the BotHub prompt key for multi-day macros summary."""
    return _RANGE_PROMPT_KEY


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


def _as_positive_float(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


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


def _normalize_response_lines(text: str) -> list[str]:
    """Split response into lines; keep blank lines for Markdown paragraphs."""
    return [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]


def _num(value: float | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.6f}".rstrip("0").rstrip(".")


def _parse_bilingual_tail(lines: Sequence[str]) -> RangeMacrosResult:
    verdict = ""
    verdict_en = ""
    section: Literal["", "en", "local"] = ""
    en_parts: list[str] = []
    local_parts: list[str] = []
    legacy_notes: list[str] = []
    for line in lines:
        upper = line.upper()
        if upper.startswith(_VERDICT_EN_PREFIX):
            verdict_en = line[len(_VERDICT_EN_PREFIX) :].strip()
            continue
        if upper.startswith(_VERDICT_PREFIX) and not upper.startswith(_VERDICT_EN_PREFIX):
            verdict = line[len(_VERDICT_PREFIX) :].strip()
            continue
        if upper == _EN_SECTION or upper.startswith(f"{_EN_SECTION} "):
            section = "en"
            rest = line[len(_EN_SECTION) :].strip()
            if rest:
                en_parts.append(rest)
            continue
        if upper == _LOCAL_SECTION or upper.startswith(f"{_LOCAL_SECTION} "):
            section = "local"
            rest = line[len(_LOCAL_SECTION) :].strip()
            if rest:
                local_parts.append(rest)
            continue
        if section == "en":
            en_parts.append(line)
        elif section == "local":
            local_parts.append(line)
        else:
            legacy_notes.append(line)
    notes_en = "\n".join(en_parts).strip()
    notes = "\n".join(local_parts).strip()
    if not notes and not notes_en and legacy_notes:
        notes = "\n".join(legacy_notes).strip()
        notes_en = notes
    if not verdict_en and verdict:
        verdict_en = verdict
    if not verdict and verdict_en:
        verdict = verdict_en
    if not notes_en and notes:
        notes_en = notes
    if not notes and notes_en:
        notes = notes_en
    return RangeMacrosResult(verdict=verdict, notes=notes, verdict_en=verdict_en, notes_en=notes_en)


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

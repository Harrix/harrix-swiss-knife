"""Parse AI TSV rows and match them to the Fitness exercise catalog."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_EXERCISE_COL_NAME = 1
_EXERCISE_COL_UNIT = 2
_EXERCISE_COL_TYPE_REQUIRED = 3
_EXERCISE_COL_CALORIES = 4
_EXERCISE_COL_NAME_LOCAL = 5
_EXERCISE_MIN_COLS = _EXERCISE_COL_NAME + 1
_HEADER_PREFIXES = {"exercise"}
_TSV_TWO_COLUMNS = 2
_TYPE_COL_EXERCISE = 1
_TYPE_COL_NAME = 2
_TYPE_COL_MODIFIER = 3
_TYPE_COL_NAME_LOCAL = 4
_TYPE_MIN_COLS = _TYPE_COL_NAME + 1
_VALUE_RE = re.compile(r"^[+-]?\d+(?:[.,]\d+)?")


@dataclass(frozen=True)
class ExerciseCatalogEntry:
    """Exercise the model may map a spoken or typed name onto."""

    name: str
    name_local: str = ""
    type_required: bool = False
    unit: str = ""
    calories_per_unit: float = 0.0
    types: list[ExerciseTypeCatalog] = field(default_factory=list)


@dataclass(frozen=True)
class ExerciseTypeCatalog:
    """One type belonging to a catalog exercise."""

    name: str
    name_local: str = ""
    calories_modifier: float = 1.0


@dataclass(frozen=True)
class ParsedSetRow:
    """One process row from AI or the preview dialog."""

    exercise: str
    type_name: str
    value: str


def build_exercise_catalog(
    exercises: list[list],
    types: list[list],
) -> list[ExerciseCatalogEntry]:
    """Build catalog entries from `get_all_exercises` and `get_all_exercise_types` rows."""
    types_by_exercise: dict[str, list[ExerciseTypeCatalog]] = {}
    for row in types:
        if len(row) < _TYPE_MIN_COLS:
            continue
        exercise_name = str(row[_TYPE_COL_EXERCISE] or "").strip()
        type_name = str(row[_TYPE_COL_NAME] or "").strip()
        type_local = str(row[_TYPE_COL_NAME_LOCAL] or "").strip() if len(row) > _TYPE_COL_NAME_LOCAL else ""
        modifier = 1.0
        if len(row) > _TYPE_COL_MODIFIER and row[_TYPE_COL_MODIFIER] not in (None, ""):
            try:
                modifier = float(row[_TYPE_COL_MODIFIER])
            except (TypeError, ValueError):
                modifier = 1.0
        if not exercise_name or not type_name:
            continue
        types_by_exercise.setdefault(exercise_name, []).append(
            ExerciseTypeCatalog(name=type_name, name_local=type_local, calories_modifier=modifier)
        )

    catalog: list[ExerciseCatalogEntry] = []
    for row in exercises:
        if len(row) < _EXERCISE_MIN_COLS:
            continue
        name = str(row[_EXERCISE_COL_NAME] or "").strip()
        if not name:
            continue
        type_required = bool(row[_EXERCISE_COL_TYPE_REQUIRED]) if len(row) > _EXERCISE_COL_TYPE_REQUIRED else False
        name_local = str(row[_EXERCISE_COL_NAME_LOCAL] or "").strip() if len(row) > _EXERCISE_COL_NAME_LOCAL else ""
        unit = str(row[_EXERCISE_COL_UNIT] or "").strip() if len(row) > _EXERCISE_COL_UNIT else ""
        calories_per_unit = 0.0
        if len(row) > _EXERCISE_COL_CALORIES and row[_EXERCISE_COL_CALORIES] not in (None, ""):
            try:
                calories_per_unit = float(row[_EXERCISE_COL_CALORIES])
            except (TypeError, ValueError):
                calories_per_unit = 0.0
        catalog.append(
            ExerciseCatalogEntry(
                name=name,
                name_local=name_local,
                type_required=type_required,
                unit=unit,
                calories_per_unit=calories_per_unit,
                types=types_by_exercise.get(name, []),
            )
        )
    return catalog


def format_exercise_catalog(catalog: list[ExerciseCatalogEntry]) -> str:
    """Render the catalog for `{{EXERCISES}}` in BotHub prompts."""
    lines: list[str] = []
    for entry in catalog:
        label = entry.name
        if entry.name_local:
            label = f"{entry.name} ({entry.name_local})"
        required = "required" if entry.type_required else "optional"
        if entry.types:
            type_labels = []
            for item in entry.types:
                type_label = item.name
                if item.name_local:
                    type_label = f"{item.name} ({item.name_local})"
                type_labels.append(type_label)
            types_text = ", ".join(type_labels)
        else:
            types_text = "(none)"
        lines.append(f"{label} | type {required} | types: {types_text}")
    return "\n".join(lines)


def match_exercise(name: str, catalog: list[ExerciseCatalogEntry]) -> ExerciseCatalogEntry | None:
    """Return the catalog exercise matching English or local `name`."""
    needle = name.strip()
    if not needle:
        return None
    folded = needle.casefold()
    for entry in catalog:
        if entry.name.casefold() == folded:
            return entry
        if entry.name_local and entry.name_local.casefold() == folded:
            return entry
    return None


def match_type(name: str, entry: ExerciseCatalogEntry) -> str | None:
    """Return the official type name for `name`, or `None` if it does not match."""
    needle = name.strip()
    if not needle:
        return ""
    folded = needle.casefold()
    for item in entry.types:
        if item.name.casefold() == folded:
            return item.name
        if item.name_local and item.name_local.casefold() == folded:
            return item.name
    return None


def parse_sets_tsv(text: str) -> list[ParsedSetRow]:
    """Parse TSV lines `Exercise`, `Type`, `Value` (type may be empty).

    Args:

    - `text` (`str`): BotHub or preview-dialog table text.

    Returns:

    - `list[ParsedSetRow]`: Valid rows; malformed lines are skipped.

    """
    rows: list[ParsedSetRow] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        parts = [part.strip() for part in line.split("\t")]
        if len(parts) == 1:
            continue
        if _is_header_row(parts):
            continue
        if len(parts) == _TSV_TWO_COLUMNS:
            exercise, value_text = parts
            type_name = ""
        else:
            exercise, type_name, value_text = parts[0], parts[1], parts[2]
        value = _parse_value(value_text)
        if not exercise or value is None:
            continue
        rows.append(ParsedSetRow(exercise=exercise, type_name=type_name, value=value))
    return rows


def _is_header_row(parts: list[str]) -> bool:
    first = parts[0].casefold()
    return first in _HEADER_PREFIXES


def _parse_value(text: str) -> str | None:
    cleaned = text.strip().replace(",", ".")
    if not cleaned:
        return None
    try:
        number = float(cleaned)
    except ValueError:
        match = _VALUE_RE.match(cleaned)
        if match is None:
            return None
        number = float(match.group(0).replace(",", "."))
    if number < 0:
        return None
    if number == int(number):
        return str(int(number))
    return str(number)

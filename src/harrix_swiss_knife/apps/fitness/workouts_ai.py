"""Parse AI-generated workouts and format catalog / recent-set context."""

from __future__ import annotations

from dataclasses import dataclass

from harrix_swiss_knife.apps.fitness.sets_ai import (
    ExerciseCatalogEntry,
    ParsedSetRow,
    match_exercise,
    match_type,
    parse_sets_tsv,
)

_TITLE_PREFIXES = {"title"}
_RECENT_SET_COL_COUNT = 6
MIN_WORKOUT_DURATION_MIN = 1
MAX_WORKOUT_DURATION_MIN = 240
_SECONDS_PER_REP = 5
_REST_SECONDS_BETWEEN = 45
_MINUTE_UNITS = frozenset({"min", "minute", "minutes", "m"})
_SECOND_UNITS = frozenset({"sec", "second", "seconds", "s"})


@dataclass(frozen=True)
class ParsedWorkout:
    """Title plus set rows from a workout-generation response."""

    title: str
    rows: list[ParsedSetRow]


@dataclass(frozen=True)
class WorkoutItemDraft:
    """One workout item resolved against the exercise catalog."""

    exercise_id: int
    type_id: int
    exercise_name: str
    type_name: str
    target_value: str


@dataclass(frozen=True, slots=True)
class WorkoutGeneratePreferences:
    """Optional focus areas and free-text notes for workout generation."""

    dumbbells: bool = False
    cardio: bool = False
    stretching: bool = False
    yoga: bool = False
    strength: bool = False
    try_something_new: bool = False
    notes: str = ""


def apply_workout_preferences_to_title(title: str, preferences: WorkoutGeneratePreferences) -> str:
    """Append preference tags to `title` when they are not already mentioned."""
    base = title.strip()
    lowered = base.lower()
    parts: list[str] = []
    if preferences.dumbbells and "dumbbell" not in lowered:
        parts.append("Dumbbells")
    if preferences.cardio and "cardio" not in lowered:
        parts.append("Cardio")
    if preferences.stretching and "stretch" not in lowered:
        parts.append("Stretching")
    if preferences.yoga and "yoga" not in lowered:
        parts.append("Yoga")
    if preferences.strength and "strength" not in lowered:
        parts.append("Strength")
    if preferences.try_something_new and "new" not in lowered:
        parts.append("Something new")
    notes = preferences.notes.strip()
    if notes and notes.lower() not in lowered:
        parts.append(notes)
    if not parts:
        return base
    suffix = " · ".join(parts)
    if not base:
        return suffix
    return f"{base} — {suffix}"


def format_workout_preferences_for_prompt(
    preferences: WorkoutGeneratePreferences,
    *,
    catalog: list[ExerciseCatalogEntry] | None = None,
    recent_rows: list[list] | None = None,
) -> str:
    """Format athlete preferences for the workout-generation prompt."""
    lines: list[str] = []
    if preferences.dumbbells:
        lines.append("- Prefer dumbbell exercises where they fit the catalog.")
    if preferences.cardio:
        lines.append("- Include cardio exercises.")
    if preferences.stretching:
        lines.append("- Include stretching / mobility exercises.")
    if preferences.yoga:
        lines.append("- Include yoga-style exercises.")
    if preferences.strength:
        lines.append("- Emphasize strength / resistance exercises.")
    if preferences.try_something_new:
        lines.append(
            "- Include several catalog exercises that do NOT appear in recent sets. "
            "Prefer exercises the athlete has rarely or never logged."
        )
        unused = format_unused_exercise_names(catalog or [], recent_rows or [])
        if unused:
            lines.append(f"- Exercises not in recent sets (pick from these when possible): {unused}")
    notes = preferences.notes.strip()
    if notes:
        lines.append(f"- Additional notes: {notes}")
    if not lines:
        return "No specific preferences."
    return "\n".join(lines)


def format_unused_exercise_names(
    catalog: list[ExerciseCatalogEntry],
    recent_rows: list[list],
) -> str:
    """Return catalog exercise names absent from recent process rows."""
    recent_names = {
        str(row[1] or "").strip()
        for row in recent_rows
        if len(row) > 1 and str(row[1] or "").strip()
    }
    unused = [entry.name for entry in catalog if entry.name not in recent_names]
    return ", ".join(unused)


def format_workout_preferences_title_suffix(preferences: WorkoutGeneratePreferences) -> str:
    """Build a short English suffix for the workout title from preferences."""
    tags: list[str] = []
    if preferences.dumbbells:
        tags.append("Dumbbells")
    if preferences.cardio:
        tags.append("Cardio")
    if preferences.stretching:
        tags.append("Stretching")
    if preferences.yoga:
        tags.append("Yoga")
    if preferences.strength:
        tags.append("Strength")
    if preferences.try_something_new:
        tags.append("Something new")
    notes = preferences.notes.strip()
    if notes:
        tags.append(notes)
    return " · ".join(tags)


def estimate_workout_duration_min(items: list[tuple[str, str]]) -> int:
    """Estimate planned workout length from item values and units.

    Rep-based units use an approximate seconds-per-rep heuristic; minute and
    second units use the numeric value directly. Rest between exercises is
    included.

    """
    if not items:
        return MIN_WORKOUT_DURATION_MIN
    total_seconds = 0.0
    for index, (value_text, unit) in enumerate(items):
        total_seconds += _item_duration_seconds(value_text, unit)
        if index < len(items) - 1:
            total_seconds += _REST_SECONDS_BETWEEN
    minutes = round(total_seconds / 60)
    return max(MIN_WORKOUT_DURATION_MIN, min(minutes, MAX_WORKOUT_DURATION_MIN))


def format_recent_sets(rows: list[list]) -> str:
    """Render recent `process` rows for `{{RECENT_SETS}}`.

    Each row is `[id, exercise_name, type_name, value, unit, date]`.

    """
    if not rows:
        return "(none)"
    lines = ["Exercise\tType\tValue\tUnit\tDate"]
    for row in rows:
        if len(row) < _RECENT_SET_COL_COUNT:
            continue
        lines.append(f"{row[1] or ''}\t{row[2] or ''}\t{row[3] or ''}\t{row[4] or ''}\t{row[5] or ''}")
    return "\n".join(lines)


def format_workout_exercise_catalog(catalog: list[ExerciseCatalogEntry]) -> str:
    """Render catalog lines with unit, kcal/unit, and type calorie modifiers."""
    lines: list[str] = []
    for entry in catalog:
        label = entry.name
        if entry.name_local:
            label = f"{entry.name} ({entry.name_local})"
        unit = entry.unit or "times"
        required = "required" if entry.type_required else "optional"
        if entry.types:
            type_labels = []
            for item in entry.types:
                type_label = item.name
                if item.name_local:
                    type_label = f"{item.name} ({item.name_local})"
                type_labels.append(f"{type_label} x{item.calories_modifier:g}")
            types_text = ", ".join(type_labels)
        else:
            types_text = "(none)"
        lines.append(
            f"{label} | unit {unit} | {entry.calories_per_unit:g} kcal/unit | type {required} | types: {types_text}"
        )
    return "\n".join(lines)


def parse_workout_tsv(text: str) -> ParsedWorkout:
    r"""Parse `Title\t...` plus `Exercise\tType\tValue` rows.

    Args:

    - `text` (`str`): BotHub or preview-dialog table text.

    Returns:

    - `ParsedWorkout`: Title (may be empty) and parsed set rows.

    """
    title = ""
    body_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        parts = [part.strip() for part in line.split("\t")]
        if parts and parts[0].casefold() in _TITLE_PREFIXES:
            if len(parts) > 1:
                title = parts[1]
            continue
        body_lines.append(raw_line)
    return ParsedWorkout(title=title, rows=parse_sets_tsv("\n".join(body_lines)))


def recalculate_workout_duration(
    duration_min: int,
    *,
    remaining_count: int,
    previous_count: int,
) -> int:
    """Scale planned minutes after items are removed, clamped to 1-240.

    When no items remain, keep the previous duration so it can still be edited.

    """
    current = max(MIN_WORKOUT_DURATION_MIN, min(int(duration_min), MAX_WORKOUT_DURATION_MIN))
    if previous_count <= 0 or remaining_count <= 0:
        return current
    scaled = round(current * remaining_count / previous_count)
    return max(MIN_WORKOUT_DURATION_MIN, min(scaled, MAX_WORKOUT_DURATION_MIN))


def resolve_workout_item(
    row: ParsedSetRow,
    catalog: list[ExerciseCatalogEntry],
    exercise_ids: dict[str, int],
    type_ids: dict[tuple[str, str], int],
) -> tuple[WorkoutItemDraft | None, str | None]:
    """Match one parsed row to catalog IDs.

    Returns:

    - `tuple[WorkoutItemDraft | None, str | None]`: Draft or an error message.

    """
    entry = match_exercise(row.exercise, catalog)
    if entry is None:
        return None, f"{row.exercise}: exercise not found in catalog"
    type_name = match_type(row.type_name, entry)
    if type_name is None:
        return None, f"{entry.name}: type '{row.type_name}' not found"
    if entry.type_required and not type_name:
        return None, f"{entry.name}: exercise type is required"
    exercise_id = exercise_ids.get(entry.name)
    if exercise_id is None:
        return None, f"{entry.name}: exercise not found in database"
    type_id = -1
    if type_name:
        type_id = type_ids.get((entry.name, type_name), -1)
        if type_id < 0:
            return None, f"{entry.name}: type '{type_name}' not found"
    return (
        WorkoutItemDraft(
            exercise_id=exercise_id,
            type_id=type_id,
            exercise_name=entry.name,
            type_name=type_name,
            target_value=row.value,
        ),
        None,
    )


def _item_duration_seconds(value_text: str, unit: str) -> float:
    value = _parse_numeric_value(value_text)
    normalized = (unit or "times").strip().casefold()
    if normalized in _MINUTE_UNITS:
        return value * 60
    if normalized in _SECOND_UNITS:
        return value
    return value * _SECONDS_PER_REP


def _parse_numeric_value(value_text: str) -> float:
    try:
        return max(0.0, float(value_text.strip().replace(",", ".")))
    except (TypeError, ValueError):
        return 0.0

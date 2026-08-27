---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `workouts_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ParsedWorkout`](#%EF%B8%8F-class-parsedworkout)
- [🏛️ Class `WorkoutItemDraft`](#%EF%B8%8F-class-workoutitemdraft)
- [🔧 Function `format_recent_sets`](#-function-format_recent_sets)
- [🔧 Function `format_workout_exercise_catalog`](#-function-format_workout_exercise_catalog)
- [🔧 Function `parse_workout_tsv`](#-function-parse_workout_tsv)
- [🔧 Function `resolve_workout_item`](#-function-resolve_workout_item)

</details>

## 🏛️ Class `ParsedWorkout`

```python
class ParsedWorkout
```

Title plus set rows from a workout-generation response.

<details>
<summary>Code:</summary>

```python
class ParsedWorkout:

    title: str
    rows: list[ParsedSetRow]
```

</details>

## 🏛️ Class `WorkoutItemDraft`

```python
class WorkoutItemDraft
```

One workout item resolved against the exercise catalog.

<details>
<summary>Code:</summary>

```python
class WorkoutItemDraft:

    exercise_id: int
    type_id: int
    exercise_name: str
    type_name: str
    target_value: str
```

</details>

## 🔧 Function `format_recent_sets`

```python
def format_recent_sets(rows: list[list]) -> str
```

Render recent `process` rows for `{{RECENT_SETS}}`.

Each row is `[id, exercise_name, type_name, value, unit, date]`.

<details>
<summary>Code:</summary>

```python
def format_recent_sets(rows: list[list]) -> str:
    if not rows:
        return "(none)"
    lines = ["Exercise\tType\tValue\tUnit\tDate"]
    for row in rows:
        if len(row) < 6:
            continue
        lines.append(f"{row[1] or ''}\t{row[2] or ''}\t{row[3] or ''}\t{row[4] or ''}\t{row[5] or ''}")
    return "\n".join(lines)
```

</details>

## 🔧 Function `format_workout_exercise_catalog`

```python
def format_workout_exercise_catalog(catalog: list[ExerciseCatalogEntry]) -> str
```

Render catalog lines with unit, kcal/unit, and type calorie modifiers.

<details>
<summary>Code:</summary>

```python
def format_workout_exercise_catalog(catalog: list[ExerciseCatalogEntry]) -> str:
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
```

</details>

## 🔧 Function `parse_workout_tsv`

```python
def parse_workout_tsv(text: str) -> ParsedWorkout
```

Parse `Title\t...` plus `Exercise\tType\tValue` rows.

Args:

- `text` (`str`): BotHub or preview-dialog table text.

Returns:

- [`ParsedWorkout`](#%EF%B8%8F-class-parsedworkout): Title (may be empty) and parsed set rows.

<details>
<summary>Code:</summary>

````python
def parse_workout_tsv(text: str) -> ParsedWorkout:
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
````

</details>

## 🔧 Function `resolve_workout_item`

```python
def resolve_workout_item(row: ParsedSetRow, catalog: list[ExerciseCatalogEntry], exercise_ids: dict[str, int], type_ids: dict[tuple[str, str], int]) -> tuple[WorkoutItemDraft | None, str | None]
```

Match one parsed row to catalog IDs.

Returns:

- `tuple[WorkoutItemDraft | None, str | None]`: Draft or an error message.

<details>
<summary>Code:</summary>

```python
def resolve_workout_item(
    row: ParsedSetRow,
    catalog: list[ExerciseCatalogEntry],
    exercise_ids: dict[str, int],
    type_ids: dict[tuple[str, str], int],
) -> tuple[WorkoutItemDraft | None, str | None]:
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
```

</details>

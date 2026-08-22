---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sets_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExerciseCatalogEntry`](#%EF%B8%8F-class-exercisecatalogentry)
- [🏛️ Class `ExerciseTypeCatalog`](#%EF%B8%8F-class-exercisetypecatalog)
- [🏛️ Class `ParsedSetRow`](#%EF%B8%8F-class-parsedsetrow)
- [🔧 Function `build_exercise_catalog`](#-function-build_exercise_catalog)
- [🔧 Function `format_exercise_catalog`](#-function-format_exercise_catalog)
- [🔧 Function `match_exercise`](#-function-match_exercise)
- [🔧 Function `match_type`](#-function-match_type)
- [🔧 Function `parse_sets_tsv`](#-function-parse_sets_tsv)

</details>

## 🏛️ Class `ExerciseCatalogEntry`

```python
class ExerciseCatalogEntry
```

Exercise the model may map a spoken or typed name onto.

<details>
<summary>Code:</summary>

```python
class ExerciseCatalogEntry:

    name: str
    name_local: str = ""
    type_required: bool = False
    types: list[ExerciseTypeCatalog] = field(default_factory=list)
```

</details>

## 🏛️ Class `ExerciseTypeCatalog`

```python
class ExerciseTypeCatalog
```

One type belonging to a catalog exercise.

<details>
<summary>Code:</summary>

```python
class ExerciseTypeCatalog:

    name: str
    name_local: str = ""
```

</details>

## 🏛️ Class `ParsedSetRow`

```python
class ParsedSetRow
```

One process row from AI or the preview dialog.

<details>
<summary>Code:</summary>

```python
class ParsedSetRow:

    exercise: str
    type_name: str
    value: str
```

</details>

## 🔧 Function `build_exercise_catalog`

```python
def build_exercise_catalog(exercises: list[list], types: list[list]) -> list[ExerciseCatalogEntry]
```

Build catalog entries from [`get_all_exercises`](database_manager.g.md#%EF%B8%8F-method-get_all_exercises) and [`get_all_exercise_types`](database_manager.g.md#%EF%B8%8F-method-get_all_exercise_types) rows.

<details>
<summary>Code:</summary>

```python
def build_exercise_catalog(
    exercises: list[list],
    types: list[list],
) -> list[ExerciseCatalogEntry]:
    types_by_exercise: dict[str, list[ExerciseTypeCatalog]] = {}
    for row in types:
        if len(row) < _TYPE_MIN_COLS:
            continue
        exercise_name = str(row[_TYPE_COL_EXERCISE] or "").strip()
        type_name = str(row[_TYPE_COL_NAME] or "").strip()
        type_local = str(row[_TYPE_COL_NAME_LOCAL] or "").strip() if len(row) > _TYPE_COL_NAME_LOCAL else ""
        if not exercise_name or not type_name:
            continue
        types_by_exercise.setdefault(exercise_name, []).append(
            ExerciseTypeCatalog(name=type_name, name_local=type_local)
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
        catalog.append(
            ExerciseCatalogEntry(
                name=name,
                name_local=name_local,
                type_required=type_required,
                types=types_by_exercise.get(name, []),
            )
        )
    return catalog
```

</details>

## 🔧 Function `format_exercise_catalog`

```python
def format_exercise_catalog(catalog: list[ExerciseCatalogEntry]) -> str
```

Render the catalog for `{{EXERCISES}}` in BotHub prompts.

<details>
<summary>Code:</summary>

```python
def format_exercise_catalog(catalog: list[ExerciseCatalogEntry]) -> str:
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
```

</details>

## 🔧 Function `match_exercise`

```python
def match_exercise(name: str, catalog: list[ExerciseCatalogEntry]) -> ExerciseCatalogEntry | None
```

Return the catalog exercise matching English or local `name`.

<details>
<summary>Code:</summary>

```python
def match_exercise(name: str, catalog: list[ExerciseCatalogEntry]) -> ExerciseCatalogEntry | None:
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
```

</details>

## 🔧 Function `match_type`

```python
def match_type(name: str, entry: ExerciseCatalogEntry) -> str | None
```

Return the official type name for `name`, or `None` if it does not match.

<details>
<summary>Code:</summary>

```python
def match_type(name: str, entry: ExerciseCatalogEntry) -> str | None:
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
```

</details>

## 🔧 Function `parse_sets_tsv`

```python
def parse_sets_tsv(text: str) -> list[ParsedSetRow]
```

Parse TSV lines `Exercise`, `Type`, `Value` (type may be empty).

Args:

- `text` (`str`): BotHub or preview-dialog table text.

Returns:

- `list[ParsedSetRow]`: Valid rows; malformed lines are skipped.

<details>
<summary>Code:</summary>

````python
def parse_sets_tsv(text: str) -> list[ParsedSetRow]:
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
````

</details>

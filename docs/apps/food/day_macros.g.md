---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `day_macros.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DayMacrosResult`](#%EF%B8%8F-class-daymacrosresult)
- [🏛️ Class `DayMacrosStatus`](#%EF%B8%8F-class-daymacrosstatus)
- [🏛️ Class `FoodDayLogLine`](#%EF%B8%8F-class-fooddaylogline)
- [🏛️ Class `FoodDayMacrosAnalysis`](#%EF%B8%8F-class-fooddaymacrosanalysis)
- [🔧 Function `day_macros_prompt_key`](#-function-day_macros_prompt_key)
- [🔧 Function `food_day_input_hash`](#-function-food_day_input_hash)
- [🔧 Function `format_day_menu_for_prompt`](#-function-format_day_menu_for_prompt)
- [🔧 Function `parse_day_macros_response`](#-function-parse_day_macros_response)
- [🔧 Function `percent_of_norm`](#-function-percent_of_norm)
- [🔧 Function `resolve_day_macros_status`](#-function-resolve_day_macros_status)

</details>

## 🏛️ Class `DayMacrosResult`

```python
class DayMacrosResult
```

Parsed approximate macros and AI norms for one calendar day.

<details>
<summary>Code:</summary>

```python
class DayMacrosResult:

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
```

</details>

## 🏛️ Class `DayMacrosStatus`

```python
class DayMacrosStatus(StrEnum)
```

Whether a saved day analysis matches the current food log.

<details>
<summary>Code:</summary>

```python
class DayMacrosStatus(StrEnum):

    MISSING = "missing"
    OK = "ok"
    STALE = "stale"
```

</details>

## 🏛️ Class `FoodDayLogLine`

```python
class FoodDayLogLine
```

One denormalized `food_log` row used for hashing and the AI menu.

<details>
<summary>Code:</summary>

```python
class FoodDayLogLine:

    name: str
    name_en: str
    weight: float | None
    portion_calories: float | None
    calories_per_100g: float | None
    is_drink: bool
```

</details>

## 🏛️ Class `FoodDayMacrosAnalysis`

```python
class FoodDayMacrosAnalysis
```

Persisted AI day analysis row.

<details>
<summary>Code:</summary>

```python
class FoodDayMacrosAnalysis:

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
```

</details>

## 🔧 Function `day_macros_prompt_key`

```python
def day_macros_prompt_key() -> str
```

Return the BotHub prompt key for day macros analysis.

<details>
<summary>Code:</summary>

```python
def day_macros_prompt_key() -> str:
    return _PROMPT_KEY
```

</details>

## 🔧 Function `food_day_input_hash`

```python
def food_day_input_hash(lines: Sequence[FoodDayLogLine]) -> str
```

Return a stable SHA-256 hex digest of the day's log lines.

Args:

- `lines` (`Sequence[FoodDayLogLine]`): Rows for one calendar date.

Returns:

- `str`: Hex digest. Empty day yields the digest of an empty payload.

<details>
<summary>Code:</summary>

```python
def food_day_input_hash(lines: Sequence[FoodDayLogLine]) -> str:
    payload = "\n".join(_canonical_line(line) for line in sorted(lines, key=_sort_key))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

</details>

## 🔧 Function `format_day_menu_for_prompt`

```python
def format_day_menu_for_prompt(lines: Sequence[FoodDayLogLine], *, total_kcal: float) -> str
```

Build a plain-text menu block for the day macros prompt.

Args:

- `lines` (`Sequence[FoodDayLogLine]`): Food log rows for the day.
- `total_kcal` (`float`): Sum of row calories for the day.

Returns:

- `str`: Human-readable menu plus total kcal.

<details>
<summary>Code:</summary>

```python
def format_day_menu_for_prompt(lines: Sequence[FoodDayLogLine], *, total_kcal: float) -> str:
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
```

</details>

## 🔧 Function `parse_day_macros_response`

```python
def parse_day_macros_response(text: str) -> DayMacrosResult | None
```

Parse AI output: intake TSV, norms TSV, then VERDICT and notes.

Args:

- `text` (`str`): Raw BotHub response.

Returns:

- `DayMacrosResult | None`: Parsed values, or `None` when invalid.

<details>
<summary>Code:</summary>

````python
def parse_day_macros_response(text: str) -> DayMacrosResult | None:
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
````

</details>

## 🔧 Function `percent_of_norm`

```python
def percent_of_norm(value: float, norm: float) -> float | None
```

Return `value` as a percent of `norm`, or `None` when `norm` is zero.

<details>
<summary>Code:</summary>

```python
def percent_of_norm(value: float, norm: float) -> float | None:
    if norm <= 0:
        return None
    return (float(value) / float(norm)) * 100.0
```

</details>

## 🔧 Function `resolve_day_macros_status`

```python
def resolve_day_macros_status(analysis: FoodDayMacrosAnalysis | None, current_hash: str) -> DayMacrosStatus
```

Compare a saved analysis with the current day hash.

Args:

- `analysis` (`FoodDayMacrosAnalysis | None`): Stored row, if any.
- `current_hash` (`str`): Hash of the current food log for that date.

Returns:

- [`DayMacrosStatus`](#%EF%B8%8F-class-daymacrosstatus): `missing`, `ok`, or `stale`.

<details>
<summary>Code:</summary>

```python
def resolve_day_macros_status(
    analysis: FoodDayMacrosAnalysis | None,
    current_hash: str,
) -> DayMacrosStatus:
    if analysis is None:
        return DayMacrosStatus.MISSING
    if analysis.input_hash == current_hash:
        return DayMacrosStatus.OK
    return DayMacrosStatus.STALE
```

</details>

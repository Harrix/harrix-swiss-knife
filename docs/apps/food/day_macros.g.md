---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `day_macros.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CalorieThresholds`](#%EF%B8%8F-class-caloriethresholds)
- [🏛️ Class `DayMacrosResult`](#%EF%B8%8F-class-daymacrosresult)
- [🏛️ Class `DayMacrosStatus`](#%EF%B8%8F-class-daymacrosstatus)
- [🏛️ Class `FoodDayLogLine`](#%EF%B8%8F-class-fooddaylogline)
- [🏛️ Class `FoodDayMacrosAnalysis`](#%EF%B8%8F-class-fooddaymacrosanalysis)
- [🏛️ Class `FoodRangeMacrosAnalysis`](#%EF%B8%8F-class-foodrangemacrosanalysis)
- [🏛️ Class `RangeMacrosResult`](#%EF%B8%8F-class-rangemacrosresult)
- [🔧 Function `calorie_band_rgb`](#-function-calorie_band_rgb)
- [🔧 Function `calorie_thresholds_from_config`](#-function-calorie_thresholds_from_config)
- [🔧 Function `day_macros_prompt_key`](#-function-day_macros_prompt_key)
- [🔧 Function `fiber_tone`](#-function-fiber_tone)
- [🔧 Function `food_day_input_hash`](#-function-food_day_input_hash)
- [🔧 Function `food_range_input_hash`](#-function-food_range_input_hash)
- [🔧 Function `format_day_menu_for_prompt`](#-function-format_day_menu_for_prompt)
- [🔧 Function `format_days_summary_for_range_prompt`](#-function-format_days_summary_for_range_prompt)
- [🔧 Function `kcal_tone`](#-function-kcal_tone)
- [🔧 Function `macro_tone`](#-function-macro_tone)
- [🔧 Function `macro_tone_rgb`](#-function-macro_tone_rgb)
- [🔧 Function `parse_day_macros_response`](#-function-parse_day_macros_response)
- [🔧 Function `parse_range_macros_response`](#-function-parse_range_macros_response)
- [🔧 Function `percent_of_norm`](#-function-percent_of_norm)
- [🔧 Function `range_day_hash_token`](#-function-range_day_hash_token)
- [🔧 Function `range_macros_prompt_key`](#-function-range_macros_prompt_key)
- [🔧 Function `resolve_day_macros_status`](#-function-resolve_day_macros_status)

</details>

## 🏛️ Class `CalorieThresholds`

```python
class CalorieThresholds
```

Configured kcal bands from `food_calorie_thresholds`.

<details>
<summary>Code:</summary>

```python
class CalorieThresholds:

    low: float = 1800.0
    medium_low: float = 2100.0
    medium_high: float = 2500.0
```

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
    fiber_g: float
    kcal: float
    norm_protein_g: float
    norm_fat_g: float
    norm_carb_g: float
    norm_fiber_g: float
    norm_kcal: float
    verdict: str
    notes: str
    verdict_en: str = ""
    notes_en: str = ""
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
    verdict_en: str = ""
    notes_en: str = ""
    fiber_g: float | None = None
    norm_fiber_g: float | None = None
```

</details>

## 🏛️ Class `FoodRangeMacrosAnalysis`

```python
class FoodRangeMacrosAnalysis
```

Persisted AI multi-day macros summary.

<details>
<summary>Code:</summary>

```python
class FoodRangeMacrosAnalysis:

    date_from: str
    date_to: str
    verdict: str
    notes: str
    verdict_en: str
    notes_en: str
    input_hash: str
    analyzed_at: str
    prompt_key: str = _RANGE_PROMPT_KEY
```

</details>

## 🏛️ Class `RangeMacrosResult`

```python
class RangeMacrosResult
```

Parsed bilingual period-level macros advice.

<details>
<summary>Code:</summary>

```python
class RangeMacrosResult:

    verdict: str
    notes: str
    verdict_en: str
    notes_en: str
```

</details>

## 🔧 Function `calorie_band_rgb`

```python
def calorie_band_rgb(kcal: float, thresholds: CalorieThresholds) -> tuple[int, int, int]
```

Return pastel RGB for a daily kcal total vs configured bands.

Bands match the kcal-per-day table and charts: low → green, medium-low →
light yellow, medium-high → bisque, above medium-high → pink.

<details>
<summary>Code:</summary>

```python
def calorie_band_rgb(kcal: float, thresholds: CalorieThresholds) -> tuple[int, int, int]:
    if kcal <= thresholds.low:
        return (144, 238, 144)
    if kcal <= thresholds.medium_low:
        return (255, 255, 224)
    if kcal <= thresholds.medium_high:
        return (255, 228, 196)
    return (255, 192, 203)
```

</details>

## 🔧 Function `calorie_thresholds_from_config`

```python
def calorie_thresholds_from_config(config: Mapping[str, Any] | None) -> CalorieThresholds
```

Parse `food_calorie_thresholds` from app config with defaults.

<details>
<summary>Code:</summary>

```python
def calorie_thresholds_from_config(config: Mapping[str, Any] | None) -> CalorieThresholds:
    raw = (config or {}).get("food_calorie_thresholds", {})
    if not isinstance(raw, dict):
        return CalorieThresholds()
    return CalorieThresholds(
        low=_as_positive_float(raw.get("low"), 1800.0),
        medium_low=_as_positive_float(raw.get("medium_low"), 2100.0),
        medium_high=_as_positive_float(raw.get("medium_high"), 2500.0),
    )
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

## 🔧 Function `fiber_tone`

```python
def fiber_tone(value: float | None, norm: float | None) -> MacroTone
```

Map fiber intake against a minimum daily target.

Meeting or exceeding the norm is good. Only a shortfall is warn or bad.

<details>
<summary>Code:</summary>

```python
def fiber_tone(value: float | None, norm: float | None) -> MacroTone:
    pct = None if value is None else percent_of_norm(value, norm or 0.0)
    if pct is None:
        return "neutral"
    if pct >= _MACRO_OK_LOW:
        return "good"
    if pct >= _MACRO_WARN_LOW:
        return "warn"
    return "bad"
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

## 🔧 Function `food_range_input_hash`

```python
def food_range_input_hash(day_hashes: Sequence[tuple[str, str]]) -> str
```

Hash of `(date, day_input_hash)` pairs for a multi-day summary.

<details>
<summary>Code:</summary>

```python
def food_range_input_hash(day_hashes: Sequence[tuple[str, str]]) -> str:
    payload = "\n".join(f"{day}\t{digest}" for day, digest in sorted(day_hashes))
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
        kcal = calculate_food_log_calories(line.weight, line.calories_per_100g)
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

## 🔧 Function `format_days_summary_for_range_prompt`

```python
def format_days_summary_for_range_prompt(analyses: Sequence[FoodDayMacrosAnalysis]) -> str
```

Build a per-day macros block for the range-macros prompt.

<details>
<summary>Code:</summary>

```python
def format_days_summary_for_range_prompt(analyses: Sequence[FoodDayMacrosAnalysis]) -> str:
    lines = [
        (
            f"{row.date}: P {row.protein_g:.0f}/{row.norm_protein_g:.0f} g, "
            f"F {row.fat_g:.0f}/{row.norm_fat_g:.0f} g, "
            f"C {row.carb_g:.0f}/{row.norm_carb_g:.0f} g, "
            f"{_format_fiber_pair(row.fiber_g, row.norm_fiber_g)}, "
            f"kcal {row.kcal:.0f}/{row.norm_kcal:.0f}"
        )
        for row in analyses
    ]
    return "\n".join(lines) if lines else "(no day analyses)"
```

</details>

## 🔧 Function `kcal_tone`

```python
def kcal_tone(kcal: float, thresholds: CalorieThresholds) -> MacroTone
```

Map intake kcal onto configured low / medium / high bands.

<details>
<summary>Code:</summary>

```python
def kcal_tone(kcal: float, thresholds: CalorieThresholds) -> MacroTone:
    if kcal <= thresholds.low:
        return "good"
    if kcal <= thresholds.medium_high:
        return "warn" if kcal > thresholds.medium_low else "good"
    return "bad"
```

</details>

## 🔧 Function `macro_tone`

```python
def macro_tone(value: float, norm: float) -> MacroTone
```

Map intake vs AI norm percent onto good / warn / bad.

<details>
<summary>Code:</summary>

```python
def macro_tone(value: float, norm: float) -> MacroTone:
    pct = percent_of_norm(value, norm)
    if pct is None:
        return "neutral"
    if _MACRO_OK_LOW <= pct <= _MACRO_OK_HIGH:
        return "good"
    if _MACRO_WARN_LOW <= pct <= _MACRO_WARN_HIGH:
        return "warn"
    return "bad"
```

</details>

## 🔧 Function `macro_tone_rgb`

```python
def macro_tone_rgb(tone: MacroTone) -> tuple[int, int, int] | None
```

Return pastel RGB for a macros tone, or `None` for neutral/empty cells.

<details>
<summary>Code:</summary>

```python
def macro_tone_rgb(tone: MacroTone) -> tuple[int, int, int] | None:
    if tone == "good":
        return (144, 238, 144)
    if tone == "warn":
        return (255, 255, 224)
    if tone == "bad":
        return (255, 192, 203)
    return None
```

</details>

## 🔧 Function `parse_day_macros_response`

```python
def parse_day_macros_response(text: str) -> DayMacrosResult | None
```

Parse AI output: intake TSV, norms TSV, bilingual verdict/notes.

Args:

- `text` (`str`): Raw BotHub response.

Returns:

- `DayMacrosResult | None`: Parsed values, or `None` when invalid.

<details>
<summary>Code:</summary>

````python
def parse_day_macros_response(text: str) -> DayMacrosResult | None:
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
    protein_g, fat_g, carb_g, fiber_g, kcal = intake
    norm_protein_g, norm_fat_g, norm_carb_g, norm_fiber_g, norm_kcal = norms
    if (
        min(
            protein_g,
            fat_g,
            carb_g,
            fiber_g,
            kcal,
            norm_protein_g,
            norm_fat_g,
            norm_carb_g,
            norm_fiber_g,
            norm_kcal,
        )
        < 0
    ):
        return None
    tail = [line for line in lines[tsv_indices[1] + 1 :] if not line.startswith("```")]
    bilingual = _parse_bilingual_tail(tail)
    return DayMacrosResult(
        protein_g=protein_g,
        fat_g=fat_g,
        carb_g=carb_g,
        fiber_g=fiber_g,
        kcal=kcal,
        norm_protein_g=norm_protein_g,
        norm_fat_g=norm_fat_g,
        norm_carb_g=norm_carb_g,
        norm_fiber_g=norm_fiber_g,
        norm_kcal=norm_kcal,
        verdict=bilingual.verdict,
        notes=bilingual.notes,
        verdict_en=bilingual.verdict_en,
        notes_en=bilingual.notes_en,
    )
````

</details>

## 🔧 Function `parse_range_macros_response`

```python
def parse_range_macros_response(text: str) -> RangeMacrosResult | None
```

Parse bilingual period advice (no TSV lines).

<details>
<summary>Code:</summary>

````python
def parse_range_macros_response(text: str) -> RangeMacrosResult | None:
    lines = _normalize_response_lines(text)
    data_lines = [line for line in lines if not line.startswith("```")]
    if not any(line for line in data_lines):
        return None
    bilingual = _parse_bilingual_tail(data_lines)
    if not (bilingual.verdict or bilingual.verdict_en or bilingual.notes or bilingual.notes_en):
        return None
    return bilingual
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

## 🔧 Function `range_day_hash_token`

```python
def range_day_hash_token(food_hash: str, fiber_g: float | None, norm_fiber_g: float | None) -> str
```

Bind a day food-log hash to its fiber estimate.

Period cache uses this token, so a summary saved before fiber was estimated
becomes stale once fiber grams are stored.

<details>
<summary>Code:</summary>

```python
def range_day_hash_token(
    food_hash: str,
    fiber_g: float | None,
    norm_fiber_g: float | None,
) -> str:
    if fiber_g is None or norm_fiber_g is None:
        return f"{food_hash}|fiber-missing"
    return f"{food_hash}|{fiber_g:.1f}|{norm_fiber_g:.1f}"
```

</details>

## 🔧 Function `range_macros_prompt_key`

```python
def range_macros_prompt_key() -> str
```

Return the BotHub prompt key for multi-day macros summary.

<details>
<summary>Code:</summary>

```python
def range_macros_prompt_key() -> str:
    return _RANGE_PROMPT_KEY
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
    if analysis.input_hash != current_hash or analysis.fiber_g is None or analysis.norm_fiber_g is None:
        return DayMacrosStatus.STALE
    return DayMacrosStatus.OK
```

</details>

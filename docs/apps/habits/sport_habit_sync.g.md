---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sport_habit_sync.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_sport_checkins`](#-function-build_sport_checkins)
- [🔧 Function `find_sport_habit`](#-function-find_sport_habit)
- [🔧 Function `habit_names_match`](#-function-habit_names_match)
- [🔧 Function `iter_iso_dates`](#-function-iter_iso_dates)
- [🔧 Function `load_dates_with_non_steps_exercises`](#-function-load_dates_with_non_steps_exercises)
- [🔧 Function `local_today`](#-function-local_today)
- [🔧 Function `lookback_date_range`](#-function-lookback_date_range)
- [🔧 Function `resolve_fitness_db_path`](#-function-resolve_fitness_db_path)
- [🔧 Function `sync_sport_habit_from_fitness`](#-function-sync_sport_habit_from_fitness)

</details>

## 🔧 Function `build_sport_checkins`

```python
def build_sport_checkins(habit_id: int, date_from: str, date_to: str, sport_dates: set[str]) -> list[tuple[int, str, int]]
```

Build `(habit_id, date, 1|0)` rows for each day in the inclusive range.

<details>
<summary>Code:</summary>

```python
def build_sport_checkins(
    habit_id: int,
    date_from: str,
    date_to: str,
    sport_dates: set[str],
) -> list[tuple[int, str, int]]:
    return [(habit_id, day, 1 if day in sport_dates else 0) for day in iter_iso_dates(date_from, date_to)]
```

</details>

## 🔧 Function `find_sport_habit`

```python
def find_sport_habit(habits: Sequence[Sequence[Any]], sport_name: str) -> tuple[int, str] | None
```

Return `(habit_id, stored_name)` when a habit matches `sport_name` (case-insensitive).

<details>
<summary>Code:</summary>

```python
def find_sport_habit(habits: Sequence[Sequence[Any]], sport_name: str) -> tuple[int, str] | None:
    needle = sport_name.strip()
    if not needle:
        return None
    for row in habits:
        if len(row) <= _HABIT_NAME_INDEX or row[0] is None or row[_HABIT_NAME_INDEX] is None:
            continue
        name = str(row[_HABIT_NAME_INDEX])
        if habit_names_match(name, needle):
            return int(row[0]), name
    return None
```

</details>

## 🔧 Function `habit_names_match`

```python
def habit_names_match(left: str, right: str) -> bool
```

Return whether two habit names are equal ignoring case and surrounding space.

<details>
<summary>Code:</summary>

```python
def habit_names_match(left: str, right: str) -> bool:
    first = left.strip().casefold()
    second = right.strip().casefold()
    return bool(first) and first == second
```

</details>

## 🔧 Function `iter_iso_dates`

```python
def iter_iso_dates(date_from: str, date_to: str) -> list[str]
```

Return inclusive YYYY-MM-DD dates from `date_from` to `date_to`.

<details>
<summary>Code:</summary>

```python
def iter_iso_dates(date_from: str, date_to: str) -> list[str]:
    start = date.fromisoformat(date_from)
    end = date.fromisoformat(date_to)
    if end < start:
        return []
    span = (end - start).days
    return [(start + timedelta(days=offset)).isoformat() for offset in range(span + 1)]
```

</details>

## 🔧 Function `load_dates_with_non_steps_exercises`

```python
def load_dates_with_non_steps_exercises(fitness_db: Path, date_from: str, date_to: str) -> set[str] | None
```

Return dates that have at least one exercise other than Steps.

Returns `None` when the Fitness database cannot be read.

<details>
<summary>Code:</summary>

```python
def load_dates_with_non_steps_exercises(fitness_db: Path, date_from: str, date_to: str) -> set[str] | None:
    if not fitness_db.is_file():
        return None
    try:
        connection = sqlite3.connect(str(fitness_db))
        try:
            connection.execute("PRAGMA query_only = ON")
            rows = connection.execute(
                """
                SELECT DISTINCT p.date
                FROM process p
                JOIN exercises e ON p._id_exercises = e._id
                WHERE p.date BETWEEN ? AND ?
                  AND p.date IS NOT NULL
                  AND LOWER(e.name) != ?
                """,
                (date_from, date_to, STEPS_EXERCISE_NAME.casefold()),
            ).fetchall()
        finally:
            connection.close()
    except sqlite3.Error:
        return None
    return {str(row[0]) for row in rows if row and row[0]}
```

</details>

## 🔧 Function `local_today`

```python
def local_today() -> date
```

Return the local calendar date.

<details>
<summary>Code:</summary>

```python
def local_today() -> date:
    return datetime.now(UTC).astimezone().date()
```

</details>

## 🔧 Function `lookback_date_range`

```python
def lookback_date_range(today: date, days: int) -> tuple[str, str]
```

Return inclusive `(date_from, date_to)` for the last `days` days ending on `today`.

<details>
<summary>Code:</summary>

```python
def lookback_date_range(today: date, days: int) -> tuple[str, str]:
    span = max(1, int(days))
    start = today - timedelta(days=span - 1)
    return start.isoformat(), today.isoformat()
```

</details>

## 🔧 Function `resolve_fitness_db_path`

```python
def resolve_fitness_db_path(config: dict[str, Any]) -> Path | None
```

Return the Fitness SQLite path from config when the file exists.

<details>
<summary>Code:</summary>

```python
def resolve_fitness_db_path(config: dict[str, Any]) -> Path | None:
    raw = str(config.get("sqlite_fitness") or "").strip()
    if not raw:
        return None
    path = Path(raw)
    return path if path.is_file() else None
```

</details>

## 🔧 Function `sync_sport_habit_from_fitness`

```python
def sync_sport_habit_from_fitness(habits_db: DatabaseManager, config: dict[str, Any], *, today: date | None = None) -> int
```

Write sport-habit check-ins from Fitness and return how many days changed.

Days with any exercise other than Steps become done (`1`). Days with only
Steps, or with no Fitness records, become not done (`0`). Missing config,
habit, or Fitness database leaves habits unchanged.

<details>
<summary>Code:</summary>

```python
def sync_sport_habit_from_fitness(
    habits_db: DatabaseManager,
    config: dict[str, Any],
    *,
    today: date | None = None,
) -> int:
    sport_name = get_habits_sport_habit_name(config)
    if not sport_name:
        return 0
    found = find_sport_habit(habits_db.get_habits(include_archived=True), sport_name)
    if found is None:
        return 0
    habit_id, _stored_name = found
    fitness_path = resolve_fitness_db_path(config)
    if fitness_path is None:
        return 0
    date_from, date_to = lookback_date_range(today or local_today(), get_habits_sport_lookback_days(config))
    sport_dates = load_dates_with_non_steps_exercises(fitness_path, date_from, date_to)
    if sport_dates is None:
        return 0
    existing = habits_db.get_habit_values_between(habit_id, date_from, date_to)
    records: list[tuple[int, str, int]] = []
    for day in iter_iso_dates(date_from, date_to):
        wanted = 1 if day in sport_dates else 0
        if existing.get(day) != wanted:
            records.append((habit_id, day, wanted))
    if not records:
        return 0
    return habits_db.upsert_habit_checkins(records)
```

</details>

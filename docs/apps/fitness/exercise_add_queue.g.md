---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_add_queue.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PendingExerciseAdd`](#%EF%B8%8F-class-pendingexerciseadd)
  - [⚙️ Method `from_dialog_result (classmethod)`](#%EF%B8%8F-method-from_dialog_result-classmethod)
- [🔧 Function `find_queued_exercise_conflict`](#-function-find_queued_exercise_conflict)
- [🔧 Function `format_exercise_add_queue_toast`](#-function-format_exercise_add_queue_toast)

</details>

## 🏛️ Class `PendingExerciseAdd`

```python
class PendingExerciseAdd
```

One Add Exercise submission waiting to be committed.

<details>
<summary>Code:</summary>

```python
class PendingExerciseAdd:

    name: str
    unit: str
    is_type_required: bool
    calories_per_unit: float
    name_local: str
    is_favorite: bool
    media_path: str
    with_dumbbells: bool
    auto_fill: bool

    @classmethod
    def from_dialog_result(
        cls,
        result: tuple[str, str, bool, float, str, bool, str, bool],
    ) -> PendingExerciseAdd:
        """Build a queue item from `ExerciseAddDialog.get_result()`.

        Args:

        - `result` (`tuple[str, str, bool, float, str, bool, str, bool]`): Dialog payload.

        Returns:

        - `PendingExerciseAdd`: Normalized add job.

        """
        name, unit, is_type_required, calories_per_unit, name_local, is_favorite, media_path, with_dumbbells = result
        if with_dumbbells:
            is_type_required = True
        return cls(
            name=name.strip(),
            unit=unit.strip(),
            is_type_required=is_type_required,
            calories_per_unit=calories_per_unit,
            name_local=name_local.strip(),
            is_favorite=is_favorite,
            media_path=media_path.strip(),
            with_dumbbells=with_dumbbells,
            auto_fill=should_auto_fill_exercise_on_ok(name=name, name_local=name_local, media_path=media_path),
        )
```

</details>

### ⚙️ Method `from_dialog_result (classmethod)`

```python
def from_dialog_result(cls, result: tuple[str, str, bool, float, str, bool, str, bool]) -> PendingExerciseAdd
```

Build a queue item from `ExerciseAddDialog.get_result()`.

Args:

- `result` (`tuple[str, str, bool, float, str, bool, str, bool]`): Dialog payload.

Returns:

- [`PendingExerciseAdd`](#%EF%B8%8F-class-pendingexerciseadd): Normalized add job.

<details>
<summary>Code:</summary>

```python
def from_dialog_result(
        cls,
        result: tuple[str, str, bool, float, str, bool, str, bool],
    ) -> PendingExerciseAdd:
        name, unit, is_type_required, calories_per_unit, name_local, is_favorite, media_path, with_dumbbells = result
        if with_dumbbells:
            is_type_required = True
        return cls(
            name=name.strip(),
            unit=unit.strip(),
            is_type_required=is_type_required,
            calories_per_unit=calories_per_unit,
            name_local=name_local.strip(),
            is_favorite=is_favorite,
            media_path=media_path.strip(),
            with_dumbbells=with_dumbbells,
            auto_fill=should_auto_fill_exercise_on_ok(name=name, name_local=name_local, media_path=media_path),
        )
```

</details>

## 🔧 Function `find_queued_exercise_conflict`

```python
def find_queued_exercise_conflict(jobs: Sequence[PendingExerciseAdd], name: str, name_local: str) -> PendingExerciseAdd | None
```

Return the first queued job that already uses `name` or `name_local`.

Args:

- `jobs` (`Sequence[PendingExerciseAdd]`): Jobs not yet committed.
- `name` (`str`): English name to look up.
- `name_local` (`str`): Local name to look up.

Returns:

- `PendingExerciseAdd | None`: Conflicting job, or `None`.

<details>
<summary>Code:</summary>

```python
def find_queued_exercise_conflict(
    jobs: Sequence[PendingExerciseAdd],
    name: str,
    name_local: str,
) -> PendingExerciseAdd | None:
    name_folded = name.strip().casefold()
    local_folded = name_local.strip().casefold()
    for job in jobs:
        job_name = job.name.casefold()
        job_local = job.name_local.casefold()
        if name_folded and job_name and name_folded == job_name:
            return job
        if local_folded and job_local and local_folded == job_local:
            return job
    return None
```

</details>

## 🔧 Function `format_exercise_add_queue_toast`

```python
def format_exercise_add_queue_toast(count: int, *, stage: str = '') -> str
```

Build the shared add-queue toast label.

Args:

- [`count`](../../qt_flow_layout.g.md#%EF%B8%8F-method-count) (`int`): Exercises still in the queue.
- `stage` (`str`): Optional current step (`converting`, `filling`).

Returns:

- `str`: Compact status text.

<details>
<summary>Code:</summary>

```python
def format_exercise_add_queue_toast(count: int, *, stage: str = "") -> str:
    text = "Adding exercises…"
    if count > 0:
        text = f"{text} ({count})"
    if stage:
        return f"{text} · {stage}"
    return text
```

</details>

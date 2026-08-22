---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dumbbell_weight_types.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExerciseWeightSnapshot`](#%EF%B8%8F-class-exerciseweightsnapshot)
- [🏛️ Class `WeightTypeSpec`](#%EF%B8%8F-class-weighttypespec)
- [🔧 Function `exercises_needing_weight_sync`](#-function-exercises_needing_weight_sync)
- [🔧 Function `folded_type_name`](#-function-folded_type_name)
- [🔧 Function `is_template_exercise`](#-function-is_template_exercise)
- [🔧 Function `missing_weight_types`](#-function-missing_weight_types)
- [🔧 Function `shares_template_weight_types`](#-function-shares_template_weight_types)

</details>

## 🏛️ Class `ExerciseWeightSnapshot`

```python
class ExerciseWeightSnapshot
```

Exercise identity plus the type names it already has.

<details>
<summary>Code:</summary>

```python
class ExerciseWeightSnapshot:

    exercise_id: int
    name: str
    type_names: tuple[str, ...]
```

</details>

## 🏛️ Class `WeightTypeSpec`

```python
class WeightTypeSpec
```

One exercise type copied from the dumbbell-weight template.

<details>
<summary>Code:</summary>

```python
class WeightTypeSpec:

    name: str
    calories_modifier: float = 1.0
    name_local: str = ""
```

</details>

## 🔧 Function `exercises_needing_weight_sync`

```python
def exercises_needing_weight_sync(exercises: Iterable[ExerciseWeightSnapshot], template: Iterable[WeightTypeSpec], *, template_exercise_name: str = DUMBBELL_WEIGHT_TEMPLATE_EXERCISE) -> list[tuple[ExerciseWeightSnapshot, list[WeightTypeSpec]]]
```

Return exercises that already share a template weight and are missing some.

Args:

- `exercises` (`Iterable[ExerciseWeightSnapshot]`): All exercises except, typically, none filtered.
- `template` (`Iterable[WeightTypeSpec]`): Types from the template exercise.
- `template_exercise_name` (`str`): Template exercise name. Defaults to
  `DUMBBELL_WEIGHT_TEMPLATE_EXERCISE`.

Returns:

- `list[tuple[ExerciseWeightSnapshot, list[WeightTypeSpec]]]`: Targets and the types to add.

<details>
<summary>Code:</summary>

```python
def exercises_needing_weight_sync(
    exercises: Iterable[ExerciseWeightSnapshot],
    template: Iterable[WeightTypeSpec],
    *,
    template_exercise_name: str = DUMBBELL_WEIGHT_TEMPLATE_EXERCISE,
) -> list[tuple[ExerciseWeightSnapshot, list[WeightTypeSpec]]]:
    template_list = list(template)
    template_names = [spec.name for spec in template_list]
    result: list[tuple[ExerciseWeightSnapshot, list[WeightTypeSpec]]] = []
    for exercise in exercises:
        if is_template_exercise(exercise.name, template_exercise_name):
            continue
        if not shares_template_weight_types(exercise.type_names, template_names):
            continue
        missing = missing_weight_types(exercise.type_names, template_list)
        if missing:
            result.append((exercise, missing))
    return result
```

</details>

## 🔧 Function `folded_type_name`

```python
def folded_type_name(name: str) -> str
```

Return a case-folded type name for duplicate checks.

<details>
<summary>Code:</summary>

```python
def folded_type_name(name: str) -> str:
    return name.strip().casefold()
```

</details>

## 🔧 Function `is_template_exercise`

```python
def is_template_exercise(name: str, template_name: str = DUMBBELL_WEIGHT_TEMPLATE_EXERCISE) -> bool
```

Return whether `name` is the dumbbell-weight template exercise.

<details>
<summary>Code:</summary>

```python
def is_template_exercise(
    name: str,
    template_name: str = DUMBBELL_WEIGHT_TEMPLATE_EXERCISE,
) -> bool:
    return folded_type_name(name) == folded_type_name(template_name)
```

</details>

## 🔧 Function `missing_weight_types`

```python
def missing_weight_types(existing_names: Iterable[str], template: Iterable[WeightTypeSpec]) -> list[WeightTypeSpec]
```

Return template types that `existing_names` does not already have.

Args:

- `existing_names` (`Iterable[str]`): Type names already on the target exercise.
- `template` (`Iterable[WeightTypeSpec]`): Types from the template exercise.

Returns:

- `list[WeightTypeSpec]`: Template types that still need to be added.

<details>
<summary>Code:</summary>

```python
def missing_weight_types(
    existing_names: Iterable[str],
    template: Iterable[WeightTypeSpec],
) -> list[WeightTypeSpec]:
    have = {folded_type_name(name) for name in existing_names if str(name).strip()}
    missing: list[WeightTypeSpec] = []
    seen: set[str] = set()
    for spec in template:
        key = folded_type_name(spec.name)
        if not key or key in have or key in seen:
            continue
        seen.add(key)
        missing.append(spec)
    return missing
```

</details>

## 🔧 Function `shares_template_weight_types`

```python
def shares_template_weight_types(existing_names: Iterable[str], template_names: Iterable[str]) -> bool
```

Return whether the exercise already uses at least one template weight type.

Args:

- `existing_names` (`Iterable[str]`): Type names on the candidate exercise.
- `template_names` (`Iterable[str]`): Type names on the template exercise.

Returns:

- `bool`: `True` when the two sets share a type name.

<details>
<summary>Code:</summary>

```python
def shares_template_weight_types(
    existing_names: Iterable[str],
    template_names: Iterable[str],
) -> bool:
    have = {folded_type_name(name) for name in existing_names if str(name).strip()}
    wanted = {folded_type_name(name) for name in template_names if str(name).strip()}
    return bool(have & wanted)
```

</details>

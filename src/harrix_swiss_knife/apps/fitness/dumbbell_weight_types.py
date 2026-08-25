"""Copy dumbbell weight types from a template exercise onto others."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

DUMBBELL_WEIGHT_TEMPLATE_EXERCISE = "Dumbbell bicep curls standing"


@dataclass(frozen=True)
class ExerciseWeightSnapshot:
    """Exercise identity plus the type names it already has."""

    exercise_id: int
    name: str
    type_names: tuple[str, ...]


@dataclass(frozen=True)
class WeightTypeSpec:
    """One exercise type copied from the dumbbell-weight template."""

    name: str
    calories_modifier: float = 1.0
    name_local: str = ""


def exercises_needing_weight_sync(
    exercises: Iterable[ExerciseWeightSnapshot],
    template: Iterable[WeightTypeSpec],
    *,
    template_exercise_name: str = DUMBBELL_WEIGHT_TEMPLATE_EXERCISE,
) -> list[tuple[ExerciseWeightSnapshot, list[WeightTypeSpec]]]:
    """Return exercises that already share a template weight and are missing some.

    Args:

    - `exercises` (`Iterable[ExerciseWeightSnapshot]`): All exercises except, typically, none filtered.
    - `template` (`Iterable[WeightTypeSpec]`): Types from the template exercise.
    - `template_exercise_name` (`str`): Template exercise name. Defaults to
      `DUMBBELL_WEIGHT_TEMPLATE_EXERCISE`.

    Returns:

    - `list[tuple[ExerciseWeightSnapshot, list[WeightTypeSpec]]]`: Targets and the types to add.

    """
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


def folded_type_name(name: str) -> str:
    """Return a case-folded type name for duplicate checks."""
    return name.strip().casefold()


def is_dumbbell_exercise(
    name: str,
    type_names: Iterable[str],
    template_type_names: Iterable[str],
    *,
    template_exercise_name: str = DUMBBELL_WEIGHT_TEMPLATE_EXERCISE,
) -> bool:
    """Return whether the exercise is the template or already uses its weights.

    Args:

    - `name` (`str`): English exercise name.
    - `type_names` (`Iterable[str]`): Type names on the exercise.
    - `template_type_names` (`Iterable[str]`): Type names on the template exercise.
    - `template_exercise_name` (`str`): Template exercise name. Defaults to
      `DUMBBELL_WEIGHT_TEMPLATE_EXERCISE`.

    Returns:

    - `bool`: `True` when the exercise should show the dumbbell mark.

    """
    return is_template_exercise(name, template_exercise_name) or shares_template_weight_types(
        type_names,
        template_type_names,
    )


def is_template_exercise(
    name: str,
    template_name: str = DUMBBELL_WEIGHT_TEMPLATE_EXERCISE,
) -> bool:
    """Return whether `name` is the dumbbell-weight template exercise."""
    return folded_type_name(name) == folded_type_name(template_name)


def missing_weight_types(
    existing_names: Iterable[str],
    template: Iterable[WeightTypeSpec],
) -> list[WeightTypeSpec]:
    """Return template types that `existing_names` does not already have.

    Args:

    - `existing_names` (`Iterable[str]`): Type names already on the target exercise.
    - `template` (`Iterable[WeightTypeSpec]`): Types from the template exercise.

    Returns:

    - `list[WeightTypeSpec]`: Template types that still need to be added.

    """
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


def shares_template_weight_types(
    existing_names: Iterable[str],
    template_names: Iterable[str],
) -> bool:
    """Return whether the exercise already uses at least one template weight type.

    Args:

    - `existing_names` (`Iterable[str]`): Type names on the candidate exercise.
    - `template_names` (`Iterable[str]`): Type names on the template exercise.

    Returns:

    - `bool`: `True` when the two sets share a type name.

    """
    have = {folded_type_name(name) for name in existing_names if str(name).strip()}
    wanted = {folded_type_name(name) for name in template_names if str(name).strip()}
    return bool(have & wanted)

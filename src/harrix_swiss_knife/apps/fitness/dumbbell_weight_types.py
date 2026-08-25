"""Copy dumbbell weight types from a template exercise onto others."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

DUMBBELL_WEIGHT_TEMPLATE_EXERCISE = "Dumbbell bicep curls standing"


@dataclass(frozen=True)
class ExerciseWeightSnapshot:
    """Exercise identity plus the type names it already has."""

    exercise_id: int
    name: str
    type_names: tuple[str, ...]


@dataclass(frozen=True)
class WeightDraft:
    """One row in the dumbbell-weight editor."""

    original_name: str | None
    name: str
    calories_modifier: float = 1.0
    name_local: str = ""


@dataclass(frozen=True)
class WeightEditPlan:
    """Adds, renames, and deletes produced by the dumbbell-weight editor."""

    to_add: tuple[WeightTypeSpec, ...]
    to_delete: tuple[str, ...]
    to_rename: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class WeightTypeSpec:
    """One exercise type copied from the dumbbell-weight template."""

    name: str
    calories_modifier: float = 1.0
    name_local: str = ""


def blocked_weight_deletes(to_delete: Iterable[str], used_names: Iterable[str]) -> list[str]:
    """Return delete names that appear in any set record.

    Args:

    - `to_delete` (`Iterable[str]`): Weight names the user wants to remove.
    - `used_names` (`Iterable[str]`): Weight names that already have process rows.

    Returns:

    - `list[str]`: Names that must stay because they are used in sets.

    """
    used = {folded_type_name(name) for name in used_names if str(name).strip()}
    return [name for name in to_delete if folded_type_name(name) in used]


def build_weight_edit_plan(
    drafts: Sequence[WeightDraft],
    original_names: Sequence[str],
) -> WeightEditPlan | str:
    """Build add/rename/delete operations from the editor rows.

    Args:

    - `drafts` (`Sequence[WeightDraft]`): Current editor rows.
    - `original_names` (`Sequence[str]`): Template names before editing.

    Returns:

    - `WeightEditPlan | str`: The plan, or an error message.

    """
    names = [draft.name.strip() for draft in drafts]
    if any(not name for name in names):
        return "Weight name cannot be empty."
    folded = [folded_type_name(name) for name in names]
    if len(folded) != len(set(folded)):
        return "Weight names must be unique."

    to_add = tuple(
        WeightTypeSpec(draft.name.strip(), draft.calories_modifier, draft.name_local)
        for draft in drafts
        if draft.original_name is None
    )
    to_rename = tuple(
        (draft.original_name, draft.name.strip())
        for draft in drafts
        if draft.original_name is not None and folded_type_name(draft.original_name) != folded_type_name(draft.name)
    )
    kept = {folded_type_name(draft.original_name) for draft in drafts if draft.original_name}
    to_delete = tuple(name for name in original_names if folded_type_name(name) not in kept)
    return WeightEditPlan(to_add=to_add, to_delete=to_delete, to_rename=to_rename)


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

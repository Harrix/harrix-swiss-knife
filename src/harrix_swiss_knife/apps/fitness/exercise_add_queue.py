"""Queue helpers for adding fitness exercises without blocking the next dialog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.fitness.exercise_ai_fill import should_auto_fill_exercise_on_ok

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class PendingExerciseAdd:
    """One Add Exercise submission waiting to be committed."""

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


def find_queued_exercise_conflict(
    jobs: Sequence[PendingExerciseAdd],
    name: str,
    name_local: str,
) -> PendingExerciseAdd | None:
    """Return the first queued job that already uses `name` or `name_local`.

    Args:

    - `jobs` (`Sequence[PendingExerciseAdd]`): Jobs not yet committed.
    - `name` (`str`): English name to look up.
    - `name_local` (`str`): Local name to look up.

    Returns:

    - `PendingExerciseAdd | None`: Conflicting job, or `None`.

    """
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

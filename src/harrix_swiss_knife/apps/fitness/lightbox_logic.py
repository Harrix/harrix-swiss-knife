"""Pure helpers for the Fitness exercise lightbox stopwatch and form defaults."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

_MS_PER_SECOND = 1000
_SECONDS_PER_MINUTE = 60


class ExerciseStopwatch:
    """Countdown, then elapsed time, with an optional workout slot limit."""

    def __init__(
        self,
        *,
        countdown_seconds: int,
        limit_seconds: int | None,
        stop_at_limit: bool = False,
    ) -> None:
        """Build a stopwatch.

        Args:

        - `countdown_seconds` (`int`): Ready countdown before elapsed time starts.
        - `limit_seconds` (`int | None`): Target or slot length. `None` or `0`
          disables the overtime / finish threshold.
        - `stop_at_limit` (`bool`): When `True`, freeze the clock at the limit
          instead of continuing into overtime. Defaults to `False`.

        """
        self._countdown_ms = max(0, int(countdown_seconds)) * _MS_PER_SECOND
        if limit_seconds is None or int(limit_seconds) <= 0:
            self._limit_ms: int | None = None
        else:
            self._limit_ms = int(limit_seconds) * _MS_PER_SECOND
        self._stop_at_limit = bool(stop_at_limit) and self._limit_ms is not None
        self.reset()

    def advance(self, delta_ms: int) -> StopwatchSnapshot:
        """Advance the clock by `delta_ms` when running."""
        if self._running and delta_ms > 0:
            self._elapsed_ms += delta_ms
            if self._phase is StopwatchPhase.COUNTDOWN and self._elapsed_ms >= self._countdown_ms:
                overflow = self._elapsed_ms - self._countdown_ms
                self._phase = StopwatchPhase.RUNNING
                self._elapsed_ms = overflow
            if (
                self._stop_at_limit
                and self._limit_ms is not None
                and self._phase is StopwatchPhase.RUNNING
                and self._elapsed_ms >= self._limit_ms
            ):
                self._elapsed_ms = self._limit_ms
                self._running = False
        return self.snapshot()

    def apply_state(self, state: ExerciseStopwatchState) -> StopwatchSnapshot:
        """Restore a previously captured stopwatch state."""
        self._phase = state.phase
        self._elapsed_ms = max(0, int(state.elapsed_ms))
        self._running = bool(state.running) and state.phase is not StopwatchPhase.IDLE
        return self.snapshot()

    def capture_state(self) -> ExerciseStopwatchState:
        """Return the current phase and elapsed time for later resume."""
        return ExerciseStopwatchState(
            phase=self._phase,
            elapsed_ms=self._elapsed_ms,
            running=self._running,
        )

    def pause(self) -> StopwatchSnapshot:
        """Freeze the countdown or elapsed clock."""
        self._running = False
        return self.snapshot()

    def reset(self) -> StopwatchSnapshot:
        """Return to idle at zero without starting."""
        self._phase = StopwatchPhase.IDLE
        self._elapsed_ms = 0
        self._running = False
        return self.snapshot()

    def restart(self) -> StopwatchSnapshot:
        """Reset and start from the ready countdown."""
        self.reset()
        return self.start()

    def snapshot(self) -> StopwatchSnapshot:
        """Return the current display state without advancing."""
        if self._phase is StopwatchPhase.IDLE:
            return StopwatchSnapshot(
                phase=StopwatchPhase.IDLE,
                display_seconds=0,
                is_overtime=False,
                is_running=False,
                color=StopwatchColor.IDLE,
            )
        if self._phase is StopwatchPhase.COUNTDOWN:
            remaining_ms = max(0, self._countdown_ms - self._elapsed_ms)
            remaining = (remaining_ms + _MS_PER_SECOND - 1) // _MS_PER_SECOND
            return StopwatchSnapshot(
                phase=StopwatchPhase.COUNTDOWN,
                display_seconds=max(1, remaining) if remaining_ms > 0 else 0,
                is_overtime=False,
                is_running=self._running,
                color=StopwatchColor.COUNTDOWN,
            )
        overtime = self._limit_ms is not None and self._elapsed_ms >= self._limit_ms
        return StopwatchSnapshot(
            phase=StopwatchPhase.RUNNING,
            display_seconds=self._elapsed_ms // _MS_PER_SECOND,
            is_overtime=overtime,
            is_running=self._running,
            color=StopwatchColor.OVERTIME if overtime else StopwatchColor.RUNNING,
        )

    def start(self) -> StopwatchSnapshot:
        """Start from idle, or resume after pause."""
        if self._phase is StopwatchPhase.IDLE:
            self._elapsed_ms = 0
            self._phase = StopwatchPhase.RUNNING if self._countdown_ms <= 0 else StopwatchPhase.COUNTDOWN
        self._running = True
        return self.snapshot()


@dataclass(frozen=True, slots=True)
class ExerciseStopwatchState:
    """Persisted exercise-timer state so Continue can resume the lightbox clock."""

    phase: StopwatchPhase
    elapsed_ms: int
    running: bool


@dataclass(frozen=True, slots=True)
class FitnessLightboxConfirm:
    """Values submitted when the lightbox confirm button is pressed."""

    exercise_name: str
    type_name: str
    value: str
    workout_item_id: int | None


@dataclass(frozen=True, slots=True)
class FitnessLightboxDetails:
    """Type list, unit, and default value for the lightbox form."""

    unit: str
    types: list[str]
    selected_type: str
    value: int


class StopwatchColor(StrEnum):
    """Visual role for the stopwatch readout."""

    IDLE = "idle"
    COUNTDOWN = "countdown"
    RUNNING = "running"
    OVERTIME = "overtime"


class StopwatchPhase(StrEnum):
    """Lifecycle of the lightbox exercise timer."""

    IDLE = "idle"
    COUNTDOWN = "countdown"
    RUNNING = "running"


@dataclass(frozen=True, slots=True)
class StopwatchSnapshot:
    """Rendered stopwatch state after a tick or control press."""

    phase: StopwatchPhase
    display_seconds: int
    is_overtime: bool
    is_running: bool
    color: StopwatchColor


def allocated_exercise_seconds(duration_min: int, item_count: int) -> int:
    """Split workout duration evenly across items, in seconds.

    Args:

    - `duration_min` (`int`): Planned workout length in minutes.
    - `item_count` (`int`): Number of workout rows.

    Returns:

    - `int`: Seconds for one exercise, or `0` when there is no slot.

    """
    if item_count <= 0 or duration_min <= 0:
        return 0
    return max(1, round(int(duration_min) * _SECONDS_PER_MINUTE / int(item_count)))


def default_exercise_type(types: list[str], *, preferred: str, last_used: str) -> str:
    """Pick the type shown in the lightbox combo.

    Prefer the workout-plan type, then the last logged type, then the first
    catalog type.

    """
    names = [name for name in types if name]
    if preferred and preferred in names:
        return preferred
    if last_used and last_used in names:
        return last_used
    return names[0] if names else ""


def format_mm_ss(total_seconds: int) -> str:
    """Format elapsed or remaining seconds as `M:SS`."""
    total = max(0, int(total_seconds))
    minutes, seconds = divmod(total, _SECONDS_PER_MINUTE)
    return f"{minutes}:{seconds:02d}"


def is_seconds_exercise_unit(unit: str) -> bool:
    """Return whether `unit` stores duration as a number of seconds."""
    return normalize_exercise_unit(unit) in _SECOND_UNITS


def is_timed_exercise_unit(unit: str) -> bool:
    """Return whether `unit` measures hold/run duration (seconds or minutes)."""
    normalized = normalize_exercise_unit(unit)
    return normalized in _SECOND_UNITS or normalized in _MINUTE_UNITS


def minutes_seconds_to_total(minutes: int, seconds: int) -> int:
    """Combine minutes and seconds into a non-negative total in seconds."""
    return max(0, int(minutes)) * _SECONDS_PER_MINUTE + max(0, int(seconds))


def normalize_exercise_unit(unit: str) -> str:
    """Lowercase unit text and strip trailing punctuation (`sec.` → `sec`)."""
    return str(unit or "").strip().casefold().rstrip(".")


def split_total_seconds(total_seconds: int) -> tuple[int, int]:
    """Split a non-negative second count into `(minutes, seconds)`."""
    total = max(0, int(total_seconds))
    return divmod(total, _SECONDS_PER_MINUTE)


def parse_exercise_value(text: str) -> int:
    """Parse a logged or planned exercise value as a non-negative integer."""
    try:
        return max(0, int(float(str(text).strip() or 0)))
    except (TypeError, ValueError):
        return 0


def target_seconds_for_exercise(unit: str, value: int) -> int | None:
    """Return stopwatch target seconds when `unit` is timed; otherwise `None`.

    Args:

    - `unit` (`str`): Exercise unit from the catalog (`sec.`, `min`, …).
    - `value` (`int`): Planned or last logged quantity.

    Returns:

    - `int | None`: Seconds to stop at, or `None` for rep/weight units.

    """
    amount = max(0, int(value))
    if amount <= 0:
        return None
    normalized = normalize_exercise_unit(unit)
    if normalized in _SECOND_UNITS:
        return amount
    if normalized in _MINUTE_UNITS:
        return amount * _SECONDS_PER_MINUTE
    return None


_MINUTE_UNITS = frozenset({"min", "minute", "minutes", "m"})
_SECOND_UNITS = frozenset({"sec", "second", "seconds", "secs", "s"})

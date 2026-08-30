---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `lightbox_logic.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExerciseStopwatch`](#%EF%B8%8F-class-exercisestopwatch)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `advance`](#%EF%B8%8F-method-advance)
  - [⚙️ Method `apply_state`](#%EF%B8%8F-method-apply_state)
  - [⚙️ Method `capture_state`](#%EF%B8%8F-method-capture_state)
  - [⚙️ Method `pause`](#%EF%B8%8F-method-pause)
  - [⚙️ Method `reset`](#%EF%B8%8F-method-reset)
  - [⚙️ Method `restart`](#%EF%B8%8F-method-restart)
  - [⚙️ Method `snapshot`](#%EF%B8%8F-method-snapshot)
  - [⚙️ Method `start`](#%EF%B8%8F-method-start)
- [🏛️ Class `ExerciseStopwatchState`](#%EF%B8%8F-class-exercisestopwatchstate)
- [🏛️ Class `FitnessLightboxConfirm`](#%EF%B8%8F-class-fitnesslightboxconfirm)
- [🏛️ Class `FitnessLightboxDetails`](#%EF%B8%8F-class-fitnesslightboxdetails)
- [🏛️ Class `StopwatchColor`](#%EF%B8%8F-class-stopwatchcolor)
- [🏛️ Class `StopwatchPhase`](#%EF%B8%8F-class-stopwatchphase)
- [🏛️ Class `StopwatchSnapshot`](#%EF%B8%8F-class-stopwatchsnapshot)
- [🔧 Function `allocated_exercise_seconds`](#-function-allocated_exercise_seconds)
- [🔧 Function `default_exercise_type`](#-function-default_exercise_type)
- [🔧 Function `format_mm_ss`](#-function-format_mm_ss)
- [🔧 Function `is_seconds_exercise_unit`](#-function-is_seconds_exercise_unit)
- [🔧 Function `is_timed_exercise_unit`](#-function-is_timed_exercise_unit)
- [🔧 Function `minutes_seconds_to_total`](#-function-minutes_seconds_to_total)
- [🔧 Function `normalize_exercise_unit`](#-function-normalize_exercise_unit)
- [🔧 Function `parse_exercise_value`](#-function-parse_exercise_value)
- [🔧 Function `split_total_seconds`](#-function-split_total_seconds)
- [🔧 Function `target_seconds_for_exercise`](#-function-target_seconds_for_exercise)

</details>

## 🏛️ Class `ExerciseStopwatch`

```python
class ExerciseStopwatch
```

Countdown, then elapsed time, with an optional workout slot limit.

<details>
<summary>Code:</summary>

```python
class ExerciseStopwatch:

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, countdown_seconds: int, limit_seconds: int | None, stop_at_limit: bool = False) -> None
```

Build a stopwatch.

Args:

- `countdown_seconds` (`int`): Ready countdown before elapsed time starts.
- `limit_seconds` (`int | None`): Target or slot length. `None` or `0`
  disables the overtime / finish threshold.
- `stop_at_limit` (`bool`): When `True`, freeze the clock at the limit
  instead of continuing into overtime. Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        *,
        countdown_seconds: int,
        limit_seconds: int | None,
        stop_at_limit: bool = False,
    ) -> None:
        self._countdown_ms = max(0, int(countdown_seconds)) * _MS_PER_SECOND
        if limit_seconds is None or int(limit_seconds) <= 0:
            self._limit_ms: int | None = None
        else:
            self._limit_ms = int(limit_seconds) * _MS_PER_SECOND
        self._stop_at_limit = bool(stop_at_limit) and self._limit_ms is not None
        self.reset()
```

</details>

### ⚙️ Method `advance`

```python
def advance(self, delta_ms: int) -> StopwatchSnapshot
```

Advance the clock by `delta_ms` when running.

<details>
<summary>Code:</summary>

```python
def advance(self, delta_ms: int) -> StopwatchSnapshot:
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
```

</details>

### ⚙️ Method `apply_state`

```python
def apply_state(self, state: ExerciseStopwatchState) -> StopwatchSnapshot
```

Restore a previously captured stopwatch state.

<details>
<summary>Code:</summary>

```python
def apply_state(self, state: ExerciseStopwatchState) -> StopwatchSnapshot:
        self._phase = state.phase
        self._elapsed_ms = max(0, int(state.elapsed_ms))
        self._running = bool(state.running) and state.phase is not StopwatchPhase.IDLE
        return self.snapshot()
```

</details>

### ⚙️ Method `capture_state`

```python
def capture_state(self) -> ExerciseStopwatchState
```

Return the current phase and elapsed time for later resume.

<details>
<summary>Code:</summary>

```python
def capture_state(self) -> ExerciseStopwatchState:
        return ExerciseStopwatchState(
            phase=self._phase,
            elapsed_ms=self._elapsed_ms,
            running=self._running,
        )
```

</details>

### ⚙️ Method `pause`

```python
def pause(self) -> StopwatchSnapshot
```

Freeze the countdown or elapsed clock.

<details>
<summary>Code:</summary>

```python
def pause(self) -> StopwatchSnapshot:
        self._running = False
        return self.snapshot()
```

</details>

### ⚙️ Method `reset`

```python
def reset(self) -> StopwatchSnapshot
```

Return to idle at zero without starting.

<details>
<summary>Code:</summary>

```python
def reset(self) -> StopwatchSnapshot:
        self._phase = StopwatchPhase.IDLE
        self._elapsed_ms = 0
        self._running = False
        return self.snapshot()
```

</details>

### ⚙️ Method `restart`

```python
def restart(self) -> StopwatchSnapshot
```

Reset and start from the ready countdown.

<details>
<summary>Code:</summary>

```python
def restart(self) -> StopwatchSnapshot:
        self.reset()
        return self.start()
```

</details>

### ⚙️ Method `snapshot`

```python
def snapshot(self) -> StopwatchSnapshot
```

Return the current display state without advancing.

<details>
<summary>Code:</summary>

```python
def snapshot(self) -> StopwatchSnapshot:
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
```

</details>

### ⚙️ Method `start`

```python
def start(self) -> StopwatchSnapshot
```

Start from idle, or resume after pause.

<details>
<summary>Code:</summary>

```python
def start(self) -> StopwatchSnapshot:
        if self._phase is StopwatchPhase.IDLE:
            self._elapsed_ms = 0
            self._phase = StopwatchPhase.RUNNING if self._countdown_ms <= 0 else StopwatchPhase.COUNTDOWN
        self._running = True
        return self.snapshot()
```

</details>

## 🏛️ Class `ExerciseStopwatchState`

```python
class ExerciseStopwatchState
```

Persisted exercise-timer state so Continue can resume the lightbox clock.

<details>
<summary>Code:</summary>

```python
class ExerciseStopwatchState:

    phase: StopwatchPhase
    elapsed_ms: int
    running: bool
```

</details>

## 🏛️ Class `FitnessLightboxConfirm`

```python
class FitnessLightboxConfirm
```

Values submitted when the lightbox confirm button is pressed.

<details>
<summary>Code:</summary>

```python
class FitnessLightboxConfirm:

    exercise_name: str
    type_name: str
    value: str
    workout_item_id: int | None
```

</details>

## 🏛️ Class `FitnessLightboxDetails`

```python
class FitnessLightboxDetails
```

Type list, unit, and default value for the lightbox form.

<details>
<summary>Code:</summary>

```python
class FitnessLightboxDetails:

    unit: str
    types: list[str]
    selected_type: str
    value: int
```

</details>

## 🏛️ Class `StopwatchColor`

```python
class StopwatchColor(StrEnum)
```

Visual role for the stopwatch readout.

<details>
<summary>Code:</summary>

```python
class StopwatchColor(StrEnum):

    IDLE = "idle"
    COUNTDOWN = "countdown"
    RUNNING = "running"
    OVERTIME = "overtime"
```

</details>

## 🏛️ Class `StopwatchPhase`

```python
class StopwatchPhase(StrEnum)
```

Lifecycle of the lightbox exercise timer.

<details>
<summary>Code:</summary>

```python
class StopwatchPhase(StrEnum):

    IDLE = "idle"
    COUNTDOWN = "countdown"
    RUNNING = "running"
```

</details>

## 🏛️ Class `StopwatchSnapshot`

```python
class StopwatchSnapshot
```

Rendered stopwatch state after a tick or control press.

<details>
<summary>Code:</summary>

```python
class StopwatchSnapshot:

    phase: StopwatchPhase
    display_seconds: int
    is_overtime: bool
    is_running: bool
    color: StopwatchColor
```

</details>

## 🔧 Function `allocated_exercise_seconds`

```python
def allocated_exercise_seconds(duration_min: int, item_count: int) -> int
```

Split workout duration evenly across items, in seconds.

Args:

- [`duration_min`](workout_generate_dialog.g.md#%EF%B8%8F-method-duration_min) (`int`): Planned workout length in minutes.
- `item_count` (`int`): Number of workout rows.

Returns:

- `int`: Seconds for one exercise, or `0` when there is no slot.

<details>
<summary>Code:</summary>

```python
def allocated_exercise_seconds(duration_min: int, item_count: int) -> int:
    if item_count <= 0 or duration_min <= 0:
        return 0
    return max(1, round(int(duration_min) * _SECONDS_PER_MINUTE / int(item_count)))
```

</details>

## 🔧 Function `default_exercise_type`

```python
def default_exercise_type(types: list[str], *, preferred: str, last_used: str) -> str
```

Pick the type shown in the lightbox combo.

Prefer the workout-plan type, then the last logged type, then the first
catalog type.

<details>
<summary>Code:</summary>

```python
def default_exercise_type(types: list[str], *, preferred: str, last_used: str) -> str:
    names = [name for name in types if name]
    if preferred and preferred in names:
        return preferred
    if last_used and last_used in names:
        return last_used
    return names[0] if names else ""
```

</details>

## 🔧 Function `format_mm_ss`

```python
def format_mm_ss(total_seconds: int) -> str
```

Format elapsed or remaining seconds as `M:SS`.

<details>
<summary>Code:</summary>

```python
def format_mm_ss(total_seconds: int) -> str:
    total = max(0, int(total_seconds))
    minutes, seconds = divmod(total, _SECONDS_PER_MINUTE)
    return f"{minutes}:{seconds:02d}"
```

</details>

## 🔧 Function `is_seconds_exercise_unit`

```python
def is_seconds_exercise_unit(unit: str) -> bool
```

Return whether `unit` stores duration as a number of seconds.

<details>
<summary>Code:</summary>

```python
def is_seconds_exercise_unit(unit: str) -> bool:
    return normalize_exercise_unit(unit) in _SECOND_UNITS
```

</details>

## 🔧 Function `is_timed_exercise_unit`

```python
def is_timed_exercise_unit(unit: str) -> bool
```

Return whether `unit` measures hold/run duration (seconds or minutes).

<details>
<summary>Code:</summary>

```python
def is_timed_exercise_unit(unit: str) -> bool:
    normalized = normalize_exercise_unit(unit)
    return normalized in _SECOND_UNITS or normalized in _MINUTE_UNITS
```

</details>

## 🔧 Function `minutes_seconds_to_total`

```python
def minutes_seconds_to_total(minutes: int, seconds: int) -> int
```

Combine minutes and seconds into a non-negative total in seconds.

<details>
<summary>Code:</summary>

```python
def minutes_seconds_to_total(minutes: int, seconds: int) -> int:
    return max(0, int(minutes)) * _SECONDS_PER_MINUTE + max(0, int(seconds))
```

</details>

## 🔧 Function `normalize_exercise_unit`

```python
def normalize_exercise_unit(unit: str) -> str
```

Lowercase unit text and strip trailing punctuation (`sec.` → `sec`).

<details>
<summary>Code:</summary>

```python
def normalize_exercise_unit(unit: str) -> str:
    return str(unit or "").strip().casefold().rstrip(".")
```

</details>

## 🔧 Function `parse_exercise_value`

```python
def parse_exercise_value(text: str) -> int
```

Parse a logged or planned exercise value as a non-negative integer.

<details>
<summary>Code:</summary>

```python
def parse_exercise_value(text: str) -> int:
    try:
        return max(0, int(float(str(text).strip() or 0)))
    except (TypeError, ValueError):
        return 0
```

</details>

## 🔧 Function `split_total_seconds`

```python
def split_total_seconds(total_seconds: int) -> tuple[int, int]
```

Split a non-negative second count into `(minutes, seconds)`.

<details>
<summary>Code:</summary>

```python
def split_total_seconds(total_seconds: int) -> tuple[int, int]:
    total = max(0, int(total_seconds))
    return divmod(total, _SECONDS_PER_MINUTE)
```

</details>

## 🔧 Function `target_seconds_for_exercise`

```python
def target_seconds_for_exercise(unit: str, value: int) -> int | None
```

Return stopwatch target seconds when `unit` is timed; otherwise `None`.

Args:

- `unit` (`str`): Exercise unit from the catalog (`sec.`, `min`, …).
- `value` (`int`): Planned or last logged quantity.

Returns:

- `int | None`: Seconds to stop at, or `None` for rep/weight units.

<details>
<summary>Code:</summary>

```python
def target_seconds_for_exercise(unit: str, value: int) -> int | None:
    amount = max(0, int(value))
    if amount <= 0:
        return None
    normalized = normalize_exercise_unit(unit)
    if normalized in _SECOND_UNITS:
        return amount
    if normalized in _MINUTE_UNITS:
        return amount * _SECONDS_PER_MINUTE
    return None
```

</details>

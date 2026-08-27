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
  - [⚙️ Method `pause`](#%EF%B8%8F-method-pause)
  - [⚙️ Method `reset`](#%EF%B8%8F-method-reset)
  - [⚙️ Method `restart`](#%EF%B8%8F-method-restart)
  - [⚙️ Method `snapshot`](#%EF%B8%8F-method-snapshot)
  - [⚙️ Method `start`](#%EF%B8%8F-method-start)
- [🏛️ Class `FitnessLightboxConfirm`](#%EF%B8%8F-class-fitnesslightboxconfirm)
- [🏛️ Class `FitnessLightboxDetails`](#%EF%B8%8F-class-fitnesslightboxdetails)
- [🏛️ Class `StopwatchColor`](#%EF%B8%8F-class-stopwatchcolor)
- [🏛️ Class `StopwatchPhase`](#%EF%B8%8F-class-stopwatchphase)
- [🏛️ Class `StopwatchSnapshot`](#%EF%B8%8F-class-stopwatchsnapshot)
- [🔧 Function `allocated_exercise_seconds`](#-function-allocated_exercise_seconds)
- [🔧 Function `default_exercise_type`](#-function-default_exercise_type)
- [🔧 Function `format_mm_ss`](#-function-format_mm_ss)
- [🔧 Function `parse_exercise_value`](#-function-parse_exercise_value)

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

    def __init__(self, *, countdown_seconds: int, limit_seconds: int | None) -> None:
        """Build a stopwatch.

        Args:

        - `countdown_seconds` (`int`): Ready countdown before elapsed time starts.
        - `limit_seconds` (`int | None`): Workout slot length. `None` or `0`
          disables the overtime alert.

        """
        self._countdown_ms = max(0, int(countdown_seconds)) * _MS_PER_SECOND
        if limit_seconds is None or int(limit_seconds) <= 0:
            self._limit_ms: int | None = None
        else:
            self._limit_ms = int(limit_seconds) * _MS_PER_SECOND
        self.reset()

    def advance(self, delta_ms: int) -> StopwatchSnapshot:
        """Advance the clock by `delta_ms` when running."""
        if self._running and delta_ms > 0:
            self._elapsed_ms += delta_ms
            if self._phase is StopwatchPhase.COUNTDOWN and self._elapsed_ms >= self._countdown_ms:
                overflow = self._elapsed_ms - self._countdown_ms
                self._phase = StopwatchPhase.RUNNING
                self._elapsed_ms = overflow
        return self.snapshot()

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
def __init__(self, *, countdown_seconds: int, limit_seconds: int | None) -> None
```

Build a stopwatch.

Args:

- `countdown_seconds` (`int`): Ready countdown before elapsed time starts.
- `limit_seconds` (`int | None`): Workout slot length. `None` or `0`
  disables the overtime alert.

<details>
<summary>Code:</summary>

```python
def __init__(self, *, countdown_seconds: int, limit_seconds: int | None) -> None:
        self._countdown_ms = max(0, int(countdown_seconds)) * _MS_PER_SECOND
        if limit_seconds is None or int(limit_seconds) <= 0:
            self._limit_ms: int | None = None
        else:
            self._limit_ms = int(limit_seconds) * _MS_PER_SECOND
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
        return self.snapshot()
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

---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habits_ticktick_sync.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_habits_ticktick_sync`](#-function-apply_habits_ticktick_sync)
- [🔧 Function `build_habits_ticktick_sync_preview`](#-function-build_habits_ticktick_sync_preview)
- [🔧 Function `format_habits_ticktick_sync_preview`](#-function-format_habits_ticktick_sync_preview)
- [🔧 Function `format_habits_ticktick_sync_result`](#-function-format_habits_ticktick_sync_result)

</details>

## 🔧 Function `apply_habits_ticktick_sync`

```python
def apply_habits_ticktick_sync(db_manager: DatabaseManager, report: dict[str, Any], client: TickTickHabitsClient, *, progress: Callable[[int, int, str], None] | None = None) -> dict[str, Any]
```

Apply a sync preview plan to HSK SQLite and TickTick Open API.

Args:

- `db_manager` (`DatabaseManager`): Open habits database.
- `report` (`dict[str, Any]`): Plan from [`build_habits_ticktick_sync_preview`](#-function-build_habits_ticktick_sync_preview).
- `client` ([`TickTickHabitsClient`](ticktick_api.g.md#%EF%B8%8F-class-ticktickhabitsclient)): Authenticated TickTick API client.
- `progress` (`Callable | None`): Optional `(current, total, message)` callback.

Returns:

- `dict[str, Any]`: Applied counts and error messages.

<details>
<summary>Code:</summary>

```python
def apply_habits_ticktick_sync(
    db_manager: DatabaseManager,
    report: dict[str, Any],
    client: TickTickHabitsClient,
    *,
    progress: Callable[[int, int, str], None] | None = None,
) -> dict[str, Any]:
    steps = _count_apply_steps(report)
    current = 0
    applied = {
        "created_in_ticktick": 0,
        "created_in_hsk": 0,
        "to_ticktick_done": 0,
        "to_hsk_done": 0,
        "gap_not_done_to_hsk": 0,
    }
    errors: list[str] = []

    def _tick(message: str) -> None:
        nonlocal current
        current += 1
        if progress is not None:
            progress(current, max(steps, 1), message)

    for item in report.get("matched") or []:
        name = str(item.get("name") or "")
        hsk_id = item.get("hsk_id")
        tt_id = str(item.get("ticktick_id") or "")
        if hsk_id is None or not tt_id:
            errors.append(f"{name}: missing habit id")
            continue
        habit_id = int(hsk_id)
        for day in item.get("to_hsk_done_dates") or []:
            _tick(f"{name}: HSK Done {day}")
            if db_manager.set_habit_checkin(habit_id, str(day), 1):
                applied["to_hsk_done"] += 1
            else:
                errors.append(f"{name}: failed HSK Done {day}")
        for day in item.get("gap_not_done_to_hsk_dates") or []:
            _tick(f"{name}: HSK Not done {day}")
            if db_manager.set_habit_checkin(habit_id, str(day), 0):
                applied["gap_not_done_to_hsk"] += 1
            else:
                errors.append(f"{name}: failed HSK Not done {day}")
        for day in item.get("to_ticktick_done_dates") or []:
            _tick(f"{name}: TickTick Done {day}")
            try:
                client.checkin_done(tt_id, iso_to_ticktick_stamp(str(day)))
                applied["to_ticktick_done"] += 1
            except (OSError, ValueError, RuntimeError) as exc:
                errors.append(f"{name}: TickTick Done {day}: {exc}")

    for item in report.get("only_hsk") or []:
        name = str(item.get("name") or "").strip()
        _tick(f"Create in TickTick: {name}")
        try:
            created = client.create_boolean_habit(name)
            tt_id = str(created.get("id") or "")
            if not tt_id:
                errors.append(f"{name}: TickTick create returned no id")
                continue
            applied["created_in_ticktick"] += 1
        except (OSError, ValueError, RuntimeError) as exc:
            errors.append(f"{name}: create in TickTick: {exc}")
            continue
        for day in item.get("done_dates") or []:
            _tick(f"{name}: TickTick Done {day}")
            try:
                client.checkin_done(tt_id, iso_to_ticktick_stamp(str(day)))
                applied["to_ticktick_done"] += 1
            except (OSError, ValueError, RuntimeError) as exc:
                errors.append(f"{name}: TickTick Done {day}: {exc}")

    for item in report.get("only_ticktick") or []:
        name = str(item.get("name") or "").strip()
        _tick(f"Create in HSK: {name}")
        if not db_manager.add_habit(name, is_bool=True):
            errors.append(f"{name}: failed to create habit in HSK")
            continue
        habit_id = _latest_habit_id_by_name(db_manager, name)
        if habit_id is None:
            errors.append(f"{name}: created in HSK but id not found")
            continue
        applied["created_in_hsk"] += 1
        for day in item.get("done_dates") or []:
            _tick(f"{name}: HSK Done {day}")
            if db_manager.set_habit_checkin(habit_id, str(day), 1):
                applied["to_hsk_done"] += 1
            else:
                errors.append(f"{name}: failed HSK Done {day}")
        for day in item.get("gap_not_done_dates") or []:
            _tick(f"{name}: HSK Not done {day}")
            if db_manager.set_habit_checkin(habit_id, str(day), 0):
                applied["gap_not_done_to_hsk"] += 1
            else:
                errors.append(f"{name}: failed HSK Not done {day}")

    return {
        "applied": applied,
        "errors": errors[:_ERROR_LIMIT],
        "error_count": len(errors),
        "steps": steps,
    }
```

</details>

## 🔧 Function `build_habits_ticktick_sync_preview`

```python
def build_habits_ticktick_sync_preview(hsk_payload: dict[str, Any], ticktick_payload: dict[str, Any], *, today: date | None = None) -> dict[str, Any]
```

Compare HSK and TickTick habits and return a transfer plan without writing.

Matching uses exact habit name after `strip` (case-sensitive). Done on either
side wins. Numeric HSK values `> 0` are never overwritten with `1`. Empty
days after per-habit `last_done` stay No record.

Args:

- `hsk_payload` (`dict[str, Any]`): Export from [`export_hsk_habits_json`](habits_backup.g.md#-function-export_hsk_habits_json).
- `ticktick_payload` (`dict[str, Any]`): Export from [`export_ticktick_habits_json`](ticktick_habits.g.md#-function-export_ticktick_habits_json).
- `today` (`date | None`): Upper bound for gap fill. Defaults to local today.

Returns:

- `dict[str, Any]`: JSON-serializable sync preview report.

<details>
<summary>Code:</summary>

```python
def build_habits_ticktick_sync_preview(
    hsk_payload: dict[str, Any],
    ticktick_payload: dict[str, Any],
    *,
    today: date | None = None,
) -> dict[str, Any]:
    as_of = today or datetime.now(UTC).astimezone().date()
    hsk_by_name, hsk_dupes = _index_habits(hsk_payload.get("habits") or [], source="hsk")
    tt_by_name, tt_dupes = _index_habits(ticktick_payload.get("habits") or [], source="ticktick")

    name_conflicts: list[dict[str, Any]] = [*hsk_dupes, *tt_dupes]
    conflicted_names = {str(item["name"]) for item in name_conflicts}

    matched_names = sorted((set(hsk_by_name) & set(tt_by_name)) - conflicted_names)
    only_hsk_names = sorted((set(hsk_by_name) - set(tt_by_name)) - conflicted_names)
    only_tt_names = sorted((set(tt_by_name) - set(hsk_by_name)) - conflicted_names)

    matched: list[dict[str, Any]] = []
    totals = {
        "to_ticktick_done": 0,
        "to_hsk_done": 0,
        "gap_not_done_to_hsk": 0,
        "protected_numeric": 0,
        "hsk_not_done_after_last_done": 0,
    }
    for name in matched_names:
        detail = _preview_matched_habit(hsk_by_name[name], tt_by_name[name], as_of=as_of)
        matched.append(detail)
        for key in totals:
            totals[key] += int(detail["counts"][key])

    create_in_ticktick: list[dict[str, Any]] = []
    for name in only_hsk_names:
        detail = _preview_create_in_ticktick(hsk_by_name[name], as_of=as_of)
        create_in_ticktick.append(detail)
        totals["to_ticktick_done"] += int(detail["done_dates_count"])

    create_in_hsk: list[dict[str, Any]] = []
    for name in only_tt_names:
        detail = _preview_create_in_hsk(tt_by_name[name], as_of=as_of)
        create_in_hsk.append(detail)
        totals["to_hsk_done"] += int(detail["done_dates_count"])
        totals["gap_not_done_to_hsk"] += int(detail["gap_not_done_count"])

    return {
        "today": as_of.isoformat(),
        "hsk_database": hsk_payload.get("database"),
        "ticktick_database": ticktick_payload.get("database"),
        "habit_counts": {
            "hsk": len(hsk_payload.get("habits") or []),
            "ticktick": len(ticktick_payload.get("habits") or []),
            "matched": len(matched_names),
            "only_hsk": len(only_hsk_names),
            "only_ticktick": len(only_tt_names),
            "name_conflicts": len(name_conflicts),
        },
        "transfer_totals": totals,
        "matched": matched,
        "only_hsk": create_in_ticktick,
        "only_ticktick": create_in_hsk,
        "name_conflicts": name_conflicts,
    }
```

</details>

## 🔧 Function `format_habits_ticktick_sync_preview`

```python
def format_habits_ticktick_sync_preview(report: dict[str, Any], *, title: str | None = None) -> str
```

Return a short human-readable summary of a sync preview report.

Args:

- `report` (`dict[str, Any]`): Output of [`build_habits_ticktick_sync_preview`](#-function-build_habits_ticktick_sync_preview).
- `title` (`str | None`): Header line. Defaults to dry-run title.

Returns:

- `str`: Multi-line summary for a dialog.

<details>
<summary>Code:</summary>

```python
def format_habits_ticktick_sync_preview(report: dict[str, Any], *, title: str | None = None) -> str:
    counts = report["habit_counts"]
    totals = report["transfer_totals"]
    lines = [
        title or "TickTick sync preview (dry-run, no writes)",
        f"Today: {report['today']}",
        "",
        "Habits:",
        f"  HSK total: {counts['hsk']}",
        f"  TickTick total: {counts['ticktick']}",
        f"  Matched by name: {counts['matched']}",
        f"  Only in HSK (would create in TickTick): {counts['only_hsk']}",
        f"  Only in TickTick (would create in HSK): {counts['only_ticktick']}",
        f"  Name conflicts: {counts['name_conflicts']}",
        "",
        "Values that would transfer:",
        f"  → TickTick Done: {totals['to_ticktick_done']}",
        f"  → HSK Done (write 1): {totals['to_hsk_done']}",
        f"  → HSK Not done gap fill (write 0): {totals['gap_not_done_to_hsk']}",
        f"  Protected numeric (HSK > 0 kept): {totals['protected_numeric']}",
        f"  HSK Not done after last Done (left as-is): {totals['hsk_not_done_after_last_done']}",
    ]
    if report["name_conflicts"]:
        lines.append("")
        lines.append("Name conflicts:")
        lines.extend(
            f"  - {item['source']}: {item['name']} ({item['count']} habits)" for item in report["name_conflicts"]
        )
    if report["only_hsk"]:
        lines.append("")
        lines.append("Only in HSK:")
        preview = report["only_hsk"][:_SUMMARY_LIST_LIMIT]
        lines.extend(f"  - {item['name']}: {item['done_dates_count']} Done → TickTick" for item in preview)
        leftover = len(report["only_hsk"]) - _SUMMARY_LIST_LIMIT
        if leftover > 0:
            lines.append(f"  … and {leftover} more")
    if report["only_ticktick"]:
        lines.append("")
        lines.append("Only in TickTick:")
        preview = report["only_ticktick"][:_SUMMARY_LIST_LIMIT]
        lines.extend(
            f"  - {item['name']}: {item['done_dates_count']} Done + {item['gap_not_done_count']} gap 0 → HSK"
            for item in preview
        )
        leftover = len(report["only_ticktick"]) - _SUMMARY_LIST_LIMIT
        if leftover > 0:
            lines.append(f"  … and {leftover} more")
    return "\n".join(lines)
```

</details>

## 🔧 Function `format_habits_ticktick_sync_result`

```python
def format_habits_ticktick_sync_result(result: dict[str, Any]) -> str
```

Format apply-sync result for a dialog.

<details>
<summary>Code:</summary>

```python
def format_habits_ticktick_sync_result(result: dict[str, Any]) -> str:
    applied = result.get("applied") or {}
    created_tt = int(applied.get("created_in_ticktick", 0))
    created_hsk = int(applied.get("created_in_hsk", 0))
    to_tt_done = int(applied.get("to_ticktick_done", 0))
    to_hsk_done = int(applied.get("to_hsk_done", 0))
    to_hsk_zero = int(applied.get("gap_not_done_to_hsk", 0))
    hsk_values_changed = to_hsk_done + to_hsk_zero
    tt_values_changed = to_tt_done
    lines = [
        "TickTick sync finished",
        "",
        "HSK ← from TickTick:",
        f"  Habits created: {created_hsk}",
        f"  Values changed: {hsk_values_changed}",
        f"    Done (wrote 1): {to_hsk_done}",
        f"    Not done (wrote 0): {to_hsk_zero}",
        "",
        "TickTick ← from HSK:",
        f"  Habits created: {created_tt}",
        f"  Values transferred (Done): {tt_values_changed}",
        "",
        f"Total values changed: {hsk_values_changed + tt_values_changed}",
        f"Errors: {result.get('error_count', 0)}",
    ]
    errors = result.get("errors") or []
    if errors:
        lines.append("")
        lines.append("First errors:")
        lines.extend(f"  - {err}" for err in errors)
    return "\n".join(lines)
```

</details>

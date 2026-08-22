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
- [🔧 Function `earliest_iso_dates`](#-function-earliest_iso_dates)
- [🔧 Function `format_habits_ticktick_sync_preview`](#-function-format_habits_ticktick_sync_preview)
- [🔧 Function `format_habits_ticktick_sync_result`](#-function-format_habits_ticktick_sync_result)
- [🔧 Function `from_stamp_for_api_export`](#-function-from_stamp_for_api_export)
- [🔧 Function `load_ticktick_sync_payload`](#-function-load_ticktick_sync_payload)

</details>

## 🔧 Function `apply_habits_ticktick_sync`

```python
def apply_habits_ticktick_sync(db_manager: DatabaseManager, report: dict[str, Any], client: TickTickHabitsClient | None, *, progress: Callable[[int, int, str], None] | None = None) -> dict[str, Any]
```

Apply a sync preview plan to HSK SQLite and TickTick Open API.

Args:

- `db_manager` (`DatabaseManager`): Open habits database.
- `report` (`dict[str, Any]`): Plan from [`build_habits_ticktick_sync_preview`](#-function-build_habits_ticktick_sync_preview).
- `client` (`TickTickHabitsClient | None`): Authenticated TickTick API client.
  Required only when the plan writes to TickTick.
- `progress` (`Callable | None`): Optional `(current, total, message)` callback.

Returns:

- `dict[str, Any]`: Applied counts and error messages.

<details>
<summary>Code:</summary>

```python
def apply_habits_ticktick_sync(
    db_manager: DatabaseManager,
    report: dict[str, Any],
    client: TickTickHabitsClient | None,
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
    hsk_writes: list[tuple[int, str, int]] = []

    def _tick(message: str) -> None:
        nonlocal current
        current += 1
        if progress is not None:
            progress(current, max(steps, 1), message)

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
        hsk_writes.extend((habit_id, str(day), 1) for day in item.get("done_dates") or [])
        hsk_writes.extend((habit_id, str(day), 0) for day in item.get("gap_not_done_dates") or [])

    for item in report.get("matched") or []:
        name = str(item.get("name") or "")
        hsk_id = item.get("hsk_id")
        if hsk_id is None:
            errors.append(f"{name}: missing HSK habit id")
            continue
        habit_id = int(hsk_id)
        hsk_writes.extend((habit_id, str(day), 1) for day in item.get("to_hsk_done_dates") or [])
        hsk_writes.extend((habit_id, str(day), 0) for day in item.get("gap_not_done_to_hsk_dates") or [])

    if hsk_writes:
        done_count = sum(1 for _habit_id, _day, value in hsk_writes if value >= _DONE_MIN)
        zero_count = len(hsk_writes) - done_count
        _tick(f"Writing {len(hsk_writes)} HSK values")
        try:
            db_manager.upsert_habit_checkins(hsk_writes)
            applied["to_hsk_done"] += done_count
            applied["gap_not_done_to_hsk"] += zero_count
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"HSK batch write failed: {exc}")

    for item in report.get("matched") or []:
        name = str(item.get("name") or "")
        tt_id = str(item.get("ticktick_id") or "")
        if not tt_id:
            errors.append(f"{name}: missing TickTick habit id")
            continue
        for day in item.get("to_ticktick_done_dates") or []:
            _tick(f"{name}: TickTick Done {day}")
            if client is None:
                errors.append(f"{name}: TickTick Done {day}: API client is not available")
                continue
            try:
                client.checkin_done(tt_id, iso_to_ticktick_stamp(str(day)))
                applied["to_ticktick_done"] += 1
            except (OSError, ValueError, RuntimeError) as exc:
                errors.append(f"{name}: TickTick Done {day}: {exc}")

    for item in report.get("only_hsk") or []:
        name = str(item.get("name") or "").strip()
        _tick(f"Create in TickTick: {name}")
        if client is None:
            errors.append(f"{name}: create in TickTick: API client is not available")
            continue
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
    date_range = earliest_iso_dates(hsk_payload, ticktick_payload)
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
        "ticktick_source": _ticktick_source_label(ticktick_payload),
        "date_range": date_range,
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

## 🔧 Function `earliest_iso_dates`

```python
def earliest_iso_dates(hsk_payload: dict[str, Any], ticktick_payload: dict[str, Any] | None = None) -> dict[str, str | None]
```

Return the earliest check-in ISO dates from HSK and TickTick payloads.

Args:

- `hsk_payload` (`dict[str, Any]`): Export from [`export_hsk_habits_json`](habits_backup.g.md#-function-export_hsk_habits_json).
- `ticktick_payload` (`dict[str, Any] | None`): Export from TickTick local
  SQLite or Open API.

Returns:

- `dict[str, str | None]`: `hsk_earliest`, `ticktick_earliest`, and `from`
  (`min` of the two when both exist).

<details>
<summary>Code:</summary>

```python
def earliest_iso_dates(
    hsk_payload: dict[str, Any],
    ticktick_payload: dict[str, Any] | None = None,
) -> dict[str, str | None]:
    hsk_earliest = _earliest_iso_from_hsk(hsk_payload)
    tt_earliest = _earliest_iso_from_ticktick(ticktick_payload)
    candidates = [day for day in (hsk_earliest, tt_earliest) if day]
    return {
        "hsk_earliest": hsk_earliest,
        "ticktick_earliest": tt_earliest,
        "from": min(candidates) if candidates else None,
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
    date_range = report.get("date_range") or {}
    lines = [
        title or "TickTick sync preview (dry-run, no writes)",
        f"Today: {report['today']}",
    ]
    source = str(report.get("ticktick_source") or "").strip()
    if source:
        lines.append(f"TickTick source: {source}")
    hsk_earliest = date_range.get("hsk_earliest")
    tt_earliest = date_range.get("ticktick_earliest")
    if hsk_earliest or tt_earliest:
        lines.extend(
            [
                f"  Earliest HSK: {hsk_earliest or '—'}",
                f"  Earliest TickTick: {tt_earliest or '—'}",
            ]
        )
    lines.extend(
        [
            "",
            "Habits:",
        ]
    )
    lines.extend(
        [
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
    )
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

## 🔧 Function `from_stamp_for_api_export`

```python
def from_stamp_for_api_export(hsk_payload: dict[str, Any], ticktick_payload: dict[str, Any] | None = None) -> int
```

Return TickTick `YYYYMMDD` lower bound from the earliest known dates.

Args:

- `hsk_payload` (`dict[str, Any]`): HSK export used when local TickTick
  history is unavailable.
- `ticktick_payload` (`dict[str, Any] | None`): Optional TickTick export
  already loaded (for example a partial local snapshot).

Returns:

- `int`: `min(HSK earliest, TickTick earliest)`, or `FALLBACK_FROM_STAMP`.

<details>
<summary>Code:</summary>

```python
def from_stamp_for_api_export(
    hsk_payload: dict[str, Any],
    ticktick_payload: dict[str, Any] | None = None,
) -> int:
    range_from = earliest_iso_dates(hsk_payload, ticktick_payload).get("from")
    if range_from is None:
        return FALLBACK_FROM_STAMP
    return iso_to_ticktick_stamp(range_from)
```

</details>

## 🔧 Function `load_ticktick_sync_payload`

```python
def load_ticktick_sync_payload(*, hsk_payload: dict[str, Any], to_stamp: int, client: TickTickHabitsClient | None = None, ticktick_db_path: Path | None = None) -> dict[str, Any]
```

Load TickTick habits from local desktop SQLite, or Open API as fallback.

Local `TickTick.db` has the full check-in history, including pre-2020 years.
The Open API is used only when that file is missing or unreadable.

Args:

- `hsk_payload` (`dict[str, Any]`): HSK export used to compute the API
  `from` stamp when falling back.
- `to_stamp` (`int`): Inclusive API upper bound (`YYYYMMDD`).
- `client` (`TickTickHabitsClient | None`): Required for the API fallback.
- `ticktick_db_path` (`Path | None`): TickTick SQLite file. Defaults to the
  desktop AppData path.

Returns:

- `dict[str, Any]`: Payload shaped like [`export_ticktick_habits_json`](ticktick_habits.g.md#-function-export_ticktick_habits_json).

Raises:

- `FileNotFoundError`: Local database is missing and no API client is given.
- `OSError`: Local database cannot be read and no API client is given.
- `ValueError`: Local database is invalid and no API client is given.

<details>
<summary>Code:</summary>

```python
def load_ticktick_sync_payload(
    *,
    hsk_payload: dict[str, Any],
    to_stamp: int,
    client: TickTickHabitsClient | None = None,
    ticktick_db_path: Path | None = None,
) -> dict[str, Any]:
    try:
        payload = export_ticktick_habits_json(ticktick_db_path)
    except (FileNotFoundError, OSError, ValueError):
        if client is None:
            raise
        from_stamp = from_stamp_for_api_export(hsk_payload)
        payload = client.export_habits_payload(to_stamp=to_stamp, from_stamp=from_stamp)
        payload["source"] = "open-api"
        return payload
    payload["source"] = "local-sqlite"
    return payload
```

</details>

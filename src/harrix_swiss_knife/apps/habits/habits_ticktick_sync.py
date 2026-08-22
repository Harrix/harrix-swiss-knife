"""Habit sync between HSK and TickTick (preview plan and apply)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.habits.ticktick_api import (
    FALLBACK_FROM_STAMP,
    iso_to_ticktick_stamp,
    ticktick_habit_icon_is_missing,
)
from harrix_swiss_knife.apps.habits.ticktick_habits import export_ticktick_habits_json

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from harrix_swiss_knife.apps.habits.database_manager import DatabaseManager
    from harrix_swiss_knife.apps.habits.ticktick_api import TickTickHabitsClient

_DONE_MIN = 1
_SUMMARY_LIST_LIMIT = 20
_ERROR_LIMIT = 30


def apply_habits_ticktick_sync(
    db_manager: DatabaseManager,
    report: dict[str, Any],
    client: TickTickHabitsClient | None,
    *,
    progress: Callable[[int, int, str], None] | None = None,
) -> dict[str, Any]:
    """Apply a sync preview plan to HSK SQLite and TickTick Open API.

    Args:

    - `db_manager` (`DatabaseManager`): Open habits database.
    - `report` (`dict[str, Any]`): Plan from `build_habits_ticktick_sync_preview`.
    - `client` (`TickTickHabitsClient | None`): Authenticated TickTick API client.
      Required only when the plan writes to TickTick.
    - `progress` (`Callable | None`): Optional `(current, total, message)` callback.

    Returns:

    - `dict[str, Any]`: Applied counts and error messages.

    """
    steps = _count_apply_steps(report)
    current = 0
    applied = {
        "created_in_ticktick": 0,
        "created_in_hsk": 0,
        "to_ticktick_done": 0,
        "to_hsk_done": 0,
        "gap_not_done_to_hsk": 0,
        "fixed_icons": 0,
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

    for item in report.get("missing_icons") or []:
        name = str(item.get("name") or "").strip()
        tt_id = str(item.get("ticktick_id") or "").strip()
        _tick(f"Set TickTick icon: {name}")
        if client is None:
            errors.append(f"{name}: set TickTick icon: API client is not available")
            continue
        if not tt_id:
            errors.append(f"{name}: missing TickTick habit id for icon")
            continue
        try:
            client.ensure_habit_icon(tt_id)
            applied["fixed_icons"] += 1
        except (OSError, ValueError, RuntimeError) as exc:
            errors.append(f"{name}: set TickTick icon: {exc}")

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


def build_habits_ticktick_sync_preview(
    hsk_payload: dict[str, Any],
    ticktick_payload: dict[str, Any],
    *,
    today: date | None = None,
) -> dict[str, Any]:
    """Compare HSK and TickTick habits and return a transfer plan without writing.

    Matching uses exact habit name after `strip` (case-sensitive). Done on either
    side wins. Numeric HSK values `> 0` are never overwritten with `1`. Empty
    days after per-habit `last_done` stay No record.

    Args:

    - `hsk_payload` (`dict[str, Any]`): Export from `export_hsk_habits_json`.
    - `ticktick_payload` (`dict[str, Any]`): Export from `export_ticktick_habits_json`.
    - `today` (`date | None`): Upper bound for gap fill. Defaults to local today.

    Returns:

    - `dict[str, Any]`: JSON-serializable sync preview report.

    """
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
        "missing_icons": _missing_ticktick_icons(ticktick_payload),
        "name_conflicts": name_conflicts,
    }


def earliest_iso_dates(
    hsk_payload: dict[str, Any],
    ticktick_payload: dict[str, Any] | None = None,
) -> dict[str, str | None]:
    """Return the earliest check-in ISO dates from HSK and TickTick payloads.

    Args:

    - `hsk_payload` (`dict[str, Any]`): Export from `export_hsk_habits_json`.
    - `ticktick_payload` (`dict[str, Any] | None`): Export from TickTick local
      SQLite or Open API.

    Returns:

    - `dict[str, str | None]`: `hsk_earliest`, `ticktick_earliest`, and `from`
      (`min` of the two when both exist).

    """
    hsk_earliest = _earliest_iso_from_hsk(hsk_payload)
    tt_earliest = _earliest_iso_from_ticktick(ticktick_payload)
    candidates = [day for day in (hsk_earliest, tt_earliest) if day]
    return {
        "hsk_earliest": hsk_earliest,
        "ticktick_earliest": tt_earliest,
        "from": min(candidates) if candidates else None,
    }


def format_habits_ticktick_sync_preview(report: dict[str, Any], *, title: str | None = None) -> str:
    """Return a short human-readable summary of a sync preview report.

    Args:

    - `report` (`dict[str, Any]`): Output of `build_habits_ticktick_sync_preview`.
    - `title` (`str | None`): Header line. Defaults to dry-run title.

    Returns:

    - `str`: Multi-line summary for a dialog.

    """
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
            f"  TickTick habits missing icon: {len(report.get('missing_icons') or [])}",
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
    if report.get("missing_icons"):
        lines.append("")
        lines.append("TickTick habits missing icon (set default reading icon):")
        preview = report["missing_icons"][:_SUMMARY_LIST_LIMIT]
        lines.extend(f"  - {item['name']}" for item in preview)
        leftover = len(report["missing_icons"]) - _SUMMARY_LIST_LIMIT
        if leftover > 0:
            lines.append(f"  … and {leftover} more")
    return "\n".join(lines)


def format_habits_ticktick_sync_result(result: dict[str, Any]) -> str:
    """Format apply-sync result for a dialog."""
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
        f"  Default icons set: {int(applied.get('fixed_icons', 0))}",
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


def from_stamp_for_api_export(
    hsk_payload: dict[str, Any],
    ticktick_payload: dict[str, Any] | None = None,
) -> int:
    """Return TickTick `YYYYMMDD` lower bound from the earliest known dates.

    Args:

    - `hsk_payload` (`dict[str, Any]`): HSK export used when local TickTick
      history is unavailable.
    - `ticktick_payload` (`dict[str, Any] | None`): Optional TickTick export
      already loaded (for example a partial local snapshot).

    Returns:

    - `int`: `min(HSK earliest, TickTick earliest)`, or `FALLBACK_FROM_STAMP`.

    """
    range_from = earliest_iso_dates(hsk_payload, ticktick_payload).get("from")
    if range_from is None:
        return FALLBACK_FROM_STAMP
    return iso_to_ticktick_stamp(range_from)


def load_ticktick_sync_payload(
    *,
    hsk_payload: dict[str, Any],
    to_stamp: int,
    client: TickTickHabitsClient | None = None,
    ticktick_db_path: Path | None = None,
) -> dict[str, Any]:
    """Load TickTick habits from Open API and local desktop SQLite.

    Desktop `TickTick.db` is an incomplete cache: the app UI can show cloud
    history that is missing from SQLite. Open API check-ins use
    `min(HSK earliest, local earliest)` as the lower bound. Dates from both
    sources are unioned when both are available.

    Args:

    - `hsk_payload` (`dict[str, Any]`): HSK export used to compute the API
      `from` stamp.
    - `to_stamp` (`int`): Inclusive API upper bound (`YYYYMMDD`).
    - `client` (`TickTickHabitsClient | None`): Open API client. Required for
      cloud history.
    - `ticktick_db_path` (`Path | None`): TickTick SQLite file. Defaults to the
      desktop AppData path.

    Returns:

    - `dict[str, Any]`: Payload shaped like `export_ticktick_habits_json`.

    Raises:

    - `FileNotFoundError`: Local database is missing and no API client is given.
    - `OSError`: Local database cannot be read and no API client is given.
    - `ValueError`: Local database is invalid and no API client is given.

    """
    local_payload: dict[str, Any] | None = None
    local_error: Exception | None = None
    try:
        local_payload = export_ticktick_habits_json(ticktick_db_path)
        local_payload["source"] = "local-sqlite"
    except (FileNotFoundError, OSError, ValueError) as exc:
        local_error = exc

    if client is None:
        if local_payload is not None:
            return local_payload
        if local_error is not None:
            raise local_error
        msg = "TickTick data not available"
        raise FileNotFoundError(msg)

    from_stamp = from_stamp_for_api_export(hsk_payload, local_payload)
    api_payload = client.export_habits_payload(to_stamp=to_stamp, from_stamp=from_stamp)
    api_payload["source"] = "open-api"
    if local_payload is None:
        return api_payload
    return merge_ticktick_sync_payloads(local_payload, api_payload)


def merge_ticktick_sync_payloads(*payloads: dict[str, Any]) -> dict[str, Any]:
    """Union TickTick habit dates from local SQLite and Open API by name.

    Args:

    - `payloads` (`dict[str, Any]`): One or more TickTick habit exports.

    Returns:

    - `dict[str, Any]`: Combined payload. Open API habit ids win when present.

    """
    habits_by_name: dict[str, dict[str, Any]] = {}
    sources: list[str] = []
    databases: list[str] = []
    for payload in payloads:
        source = str(payload.get("source") or "").strip()
        if source and source not in sources:
            sources.append(source)
        database = str(payload.get("database") or "").strip()
        if database and database not in databases:
            databases.append(database)
        prefer_ids = source == "open-api" or database == "ticktick-open-api"
        for habit in payload.get("habits") or []:
            name = str(habit.get("name") or "").strip()
            if not name:
                continue
            incoming_dates = {str(day) for day in (habit.get("dates") or []) if day}
            current = habits_by_name.get(name)
            if current is None:
                merged = dict(habit)
                merged["name"] = name
                merged["dates"] = sorted(incoming_dates)
                merged["date_count"] = len(merged["dates"])
                habits_by_name[name] = merged
                continue
            dates = set(current.get("dates") or []) | incoming_dates
            current["dates"] = sorted(dates)
            current["date_count"] = len(dates)
            if prefer_ids and habit.get("id"):
                current["id"] = habit.get("id")
            if "icon_res" in habit:
                current["icon_res"] = habit.get("icon_res")
            current_total = int(current.get("total_check_ins") or 0)
            incoming_total = int(habit.get("total_check_ins") or 0)
            current["total_check_ins"] = max(current_total, incoming_total)
    return {
        "database": " + ".join(databases),
        "source": "+".join(sources),
        "habit_count": len(habits_by_name),
        "habits": list(habits_by_name.values()),
    }


def _consider_iso(day: object, earliest: str | None) -> str | None:
    text = str(day or "").strip()
    if _parse_iso(text) is None:
        return earliest
    if earliest is None or text < earliest:
        return text
    return earliest


def _count_apply_steps(report: dict[str, Any]) -> int:
    total = len(report.get("only_ticktick") or [])
    hsk_writes = 0
    for item in report.get("matched") or []:
        hsk_writes += len(item.get("to_hsk_done_dates") or [])
        hsk_writes += len(item.get("gap_not_done_to_hsk_dates") or [])
        total += len(item.get("to_ticktick_done_dates") or [])
    for item in report.get("only_ticktick") or []:
        hsk_writes += len(item.get("done_dates") or [])
        hsk_writes += len(item.get("gap_not_done_dates") or [])
    if hsk_writes:
        total += 1
    for item in report.get("only_hsk") or []:
        total += 1 + len(item.get("done_dates") or [])
    total += len(report.get("missing_icons") or [])
    return total


def _dates_between(start: date, end: date) -> list[date]:
    """Inclusive calendar days from `start` to `end`."""
    if end < start:
        return []
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def _earliest_iso_from_hsk(payload: dict[str, Any]) -> str | None:
    earliest: str | None = None
    for habit in payload.get("habits") or []:
        values = habit.get("values")
        if isinstance(values, dict):
            for day in values:
                earliest = _consider_iso(day, earliest)
        for day in habit.get("dates") or []:
            earliest = _consider_iso(day, earliest)
    return earliest


def _earliest_iso_from_ticktick(payload: dict[str, Any] | None) -> str | None:
    if payload is None:
        return None
    earliest: str | None = None
    for habit in payload.get("habits") or []:
        for day in habit.get("dates") or []:
            earliest = _consider_iso(day, earliest)
    return earliest


def _hsk_done_dates(values: dict[str, int]) -> set[str]:
    return {day for day, value in values.items() if value >= _DONE_MIN}


def _index_habits(
    habits: list[dict[str, Any]],
    *,
    source: str,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Map unique stripped names to habits; collect duplicate-name conflicts."""
    buckets: dict[str, list[dict[str, Any]]] = {}
    for habit in habits:
        name = str(habit.get("name") or "").strip()
        if not name:
            continue
        buckets.setdefault(name, []).append(habit)

    unique: dict[str, dict[str, Any]] = {}
    conflicts: list[dict[str, Any]] = []
    for name, group in buckets.items():
        if len(group) == 1:
            unique[name] = group[0]
        else:
            conflicts.append({"source": source, "name": name, "count": len(group)})
    return unique, conflicts


def _latest_habit_id_by_name(db_manager: DatabaseManager, name: str) -> int | None:
    rows = db_manager.get_rows(
        "SELECT _id FROM habits WHERE name = :name ORDER BY _id DESC LIMIT 1",
        {"name": name},
    )
    if not rows or rows[0][0] is None:
        return None
    return int(rows[0][0])


def _missing_ticktick_icons(ticktick_payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return TickTick habits whose `icon_res` is present but empty."""
    missing: list[dict[str, Any]] = []
    for habit in ticktick_payload.get("habits") or []:
        if "icon_res" not in habit:
            continue
        habit_id = str(habit.get("id") or "").strip()
        if not habit_id or not ticktick_habit_icon_is_missing(habit.get("icon_res")):
            continue
        missing.append(
            {
                "name": str(habit.get("name") or "").strip(),
                "ticktick_id": habit_id,
            }
        )
    return missing


def _parse_iso(day: str) -> date | None:
    try:
        return date.fromisoformat(day)
    except ValueError:
        return None


def _preview_create_in_hsk(tt_habit: dict[str, Any], *, as_of: date) -> dict[str, Any]:
    """Plan creating an HSK habit from TickTick Done dates plus gap zeros."""
    as_of_iso = as_of.isoformat()
    done_dates = sorted({str(day) for day in (tt_habit.get("dates") or []) if day and str(day) <= as_of_iso})
    last_done = done_dates[-1] if done_dates else None
    gap_days: list[str] = []
    if last_done is not None:
        first = _parse_iso(done_dates[0])
        last = _parse_iso(last_done)
        if first is not None and last is not None:
            for day in _dates_between(first, last):
                iso = day.isoformat()
                if iso not in done_dates:
                    gap_days.append(iso)
    return {
        "name": str(tt_habit.get("name") or "").strip(),
        "ticktick_id": tt_habit.get("id"),
        "action": "create_in_hsk",
        "done_dates": done_dates,
        "done_dates_count": len(done_dates),
        "gap_not_done_dates": gap_days,
        "gap_not_done_count": len(gap_days),
        "last_done": last_done,
    }


def _preview_create_in_ticktick(hsk_habit: dict[str, Any], *, as_of: date) -> dict[str, Any]:
    """Plan creating a TickTick habit from HSK Done dates."""
    as_of_iso = as_of.isoformat()
    values = {str(k): int(v) for k, v in (hsk_habit.get("values") or {}).items() if str(k) <= as_of_iso}
    done_dates = sorted(_hsk_done_dates(values))
    return {
        "name": str(hsk_habit.get("name") or "").strip(),
        "hsk_id": hsk_habit.get("id"),
        "action": "create_in_ticktick",
        "done_dates": done_dates,
        "done_dates_count": len(done_dates),
        "is_bool": hsk_habit.get("is_bool"),
    }


def _preview_matched_habit(
    hsk_habit: dict[str, Any],
    tt_habit: dict[str, Any],
    *,
    as_of: date,
) -> dict[str, Any]:
    """Plan day-level transfers for one matched habit name."""
    as_of_iso = as_of.isoformat()
    values = {str(k): int(v) for k, v in (hsk_habit.get("values") or {}).items() if str(k) <= as_of_iso}
    hsk_done = _hsk_done_dates(values)
    tt_done = {str(day) for day in (tt_habit.get("dates") or []) if day and str(day) <= as_of_iso}
    all_done = hsk_done | tt_done
    last_done = max(all_done) if all_done else None

    to_ticktick: list[str] = []
    to_hsk_done: list[str] = []
    gap_not_done: list[str] = []
    protected_numeric: list[str] = []
    hsk_not_done_after: list[str] = []

    recorded = set(values) | tt_done
    if last_done is not None and recorded:
        first_day = _parse_iso(min(recorded))
        last_day = _parse_iso(last_done)
        if first_day is not None and last_day is not None:
            for day in _dates_between(first_day, last_day):
                iso = day.isoformat()
                hsk_value = values.get(iso)
                tt_is_done = iso in tt_done
                hsk_is_done = hsk_value is not None and hsk_value >= _DONE_MIN
                if hsk_is_done and not tt_is_done:
                    to_ticktick.append(iso)
                elif tt_is_done and (hsk_value is None or hsk_value == 0):
                    to_hsk_done.append(iso)
                elif tt_is_done and hsk_value is not None and hsk_value > _DONE_MIN:
                    protected_numeric.append(iso)
                elif hsk_value is None and not tt_is_done:
                    gap_not_done.append(iso)

        for day in _dates_between(last_day + timedelta(days=1), as_of) if last_day else []:
            iso = day.isoformat()
            hsk_value = values.get(iso)
            tt_is_done = iso in tt_done
            if hsk_value == 0 and not tt_is_done:
                hsk_not_done_after.append(iso)

    return {
        "name": str(hsk_habit.get("name") or "").strip(),
        "hsk_id": hsk_habit.get("id"),
        "ticktick_id": tt_habit.get("id"),
        "is_bool": hsk_habit.get("is_bool"),
        "last_done": last_done,
        "counts": {
            "to_ticktick_done": len(to_ticktick),
            "to_hsk_done": len(to_hsk_done),
            "gap_not_done_to_hsk": len(gap_not_done),
            "protected_numeric": len(protected_numeric),
            "hsk_not_done_after_last_done": len(hsk_not_done_after),
        },
        "to_ticktick_done_dates": to_ticktick,
        "to_hsk_done_dates": to_hsk_done,
        "gap_not_done_to_hsk_dates": gap_not_done,
        "protected_numeric_dates": protected_numeric,
        "hsk_not_done_after_last_done_dates": hsk_not_done_after,
    }


def _ticktick_source_label(payload: dict[str, Any]) -> str:
    source = str(payload.get("source") or "").strip()
    if "open-api" in source and "local-sqlite" in source:
        return "TickTick Open API + local SQLite"
    if source == "open-api":
        return "TickTick Open API"
    if source == "local-sqlite":
        return "local TickTick SQLite"
    database = str(payload.get("database") or "").strip()
    if "ticktick-open-api" in database and "TickTick.db" in database:
        return "TickTick Open API + local SQLite"
    if database == "ticktick-open-api":
        return "TickTick Open API"
    if database:
        return "local TickTick SQLite"
    return ""

"""Dry-run habit sync preview between HSK and TickTick (no writes)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any

_DONE_MIN = 1
_SUMMARY_LIST_LIMIT = 20


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


def format_habits_ticktick_sync_preview(report: dict[str, Any]) -> str:
    """Return a short human-readable summary of a sync preview report.

    Args:

    - `report` (`dict[str, Any]`): Output of `build_habits_ticktick_sync_preview`.

    Returns:

    - `str`: Multi-line summary for a dialog.

    """
    counts = report["habit_counts"]
    totals = report["transfer_totals"]
    lines = [
        "TickTick sync preview (dry-run, no writes)",
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

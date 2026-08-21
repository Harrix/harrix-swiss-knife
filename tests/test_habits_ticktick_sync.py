"""Tests for HSK ↔ TickTick habit sync dry-run preview."""

from __future__ import annotations

from datetime import date

from harrix_swiss_knife.apps.habits.habits_ticktick_sync import (
    build_habits_ticktick_sync_preview,
    format_habits_ticktick_sync_preview,
)


def _hsk_habit(
    *,
    habit_id: int,
    name: str,
    values: dict[str, int],
    is_bool: bool = True,
) -> dict:
    return {
        "id": habit_id,
        "name": name,
        "emoji": "",
        "is_bool": is_bool,
        "archived": False,
        "values": values,
        "dates": sorted(values),
        "date_count": len(values),
    }


def _tt_habit(*, habit_id: str, name: str, dates: list[str]) -> dict:
    return {
        "id": habit_id,
        "name": name,
        "type": "Boolean",
        "archived": False,
        "archived_time": None,
        "created_time": None,
        "total_check_ins": len(dates),
        "dates": dates,
        "date_count": len(dates),
    }


def test_match_by_exact_name_and_done_wins_zero() -> None:
    """Matched names transfer Done; HSK 0 loses to TickTick Done."""
    report = build_habits_ticktick_sync_preview(
        {
            "database": "hsk.db",
            "habits": [
                _hsk_habit(
                    habit_id=1,
                    name=" English ",
                    values={"2026-08-01": 1, "2026-08-02": 0},
                )
            ],
        },
        {
            "database": "tt.db",
            "habits": [_tt_habit(habit_id="t1", name="English", dates=["2026-08-02", "2026-08-03"])],
        },
        today=date(2026, 8, 5),
    )
    assert report["habit_counts"]["matched"] == 1
    matched = report["matched"][0]
    assert matched["name"] == "English"
    assert matched["to_ticktick_done_dates"] == ["2026-08-01"]
    assert matched["to_hsk_done_dates"] == ["2026-08-02", "2026-08-03"]
    assert report["transfer_totals"]["to_ticktick_done"] == 1
    assert report["transfer_totals"]["to_hsk_done"] == 2


def test_numeric_value_not_overwritten() -> None:
    """HSK value 100 stays protected when TickTick is Done."""
    report = build_habits_ticktick_sync_preview(
        {
            "habits": [
                _hsk_habit(
                    habit_id=2,
                    name="Pages",
                    values={"2026-08-01": 100},
                    is_bool=False,
                )
            ]
        },
        {"habits": [_tt_habit(habit_id="t2", name="Pages", dates=["2026-08-01"])]},
        today=date(2026, 8, 2),
    )
    matched = report["matched"][0]
    assert matched["protected_numeric_dates"] == ["2026-08-01"]
    assert matched["to_hsk_done_dates"] == []
    assert report["transfer_totals"]["protected_numeric"] == 1


def test_gap_fill_only_until_last_done() -> None:
    """Empty days before last Done become Not done; after stay No record."""
    report = build_habits_ticktick_sync_preview(
        {
            "habits": [
                _hsk_habit(
                    habit_id=3,
                    name="Walk",
                    values={"2026-08-01": 1, "2026-08-04": 0},
                )
            ]
        },
        {"habits": [_tt_habit(habit_id="t3", name="Walk", dates=["2026-08-03"])]},
        today=date(2026, 8, 5),
    )
    matched = report["matched"][0]
    assert matched["last_done"] == "2026-08-03"
    # 2026-08-02 empty before last_done → gap 0
    assert matched["gap_not_done_to_hsk_dates"] == ["2026-08-02"]
    # 2026-08-04 is HSK 0 after last_done → noted, not gap
    assert matched["hsk_not_done_after_last_done_dates"] == ["2026-08-04"]
    # 2026-08-05 empty after last_done → No record (not listed)
    assert "2026-08-05" not in matched["gap_not_done_to_hsk_dates"]
    assert matched["to_ticktick_done_dates"] == ["2026-08-01"]
    assert matched["to_hsk_done_dates"] == ["2026-08-03"]


def test_only_one_side_counts_as_create_and_transfer() -> None:
    """Habits present on one side plan create + all Done transfers."""
    report = build_habits_ticktick_sync_preview(
        {
            "habits": [
                _hsk_habit(habit_id=4, name="SoloHSK", values={"2026-08-01": 1, "2026-08-02": 0}),
            ]
        },
        {
            "habits": [
                _tt_habit(habit_id="t4", name="SoloTT", dates=["2026-08-01", "2026-08-03"]),
            ]
        },
        today=date(2026, 8, 3),
    )
    assert report["habit_counts"]["only_hsk"] == 1
    assert report["habit_counts"]["only_ticktick"] == 1
    assert report["only_hsk"][0]["done_dates"] == ["2026-08-01"]
    assert report["only_ticktick"][0]["done_dates_count"] == 2
    assert report["only_ticktick"][0]["gap_not_done_count"] == 1  # Aug 2
    assert report["transfer_totals"]["to_ticktick_done"] == 1
    assert report["transfer_totals"]["to_hsk_done"] == 2
    assert report["transfer_totals"]["gap_not_done_to_hsk"] == 1


def test_duplicate_names_are_conflicts() -> None:
    """Two habits with the same name in one system are not matched."""
    report = build_habits_ticktick_sync_preview(
        {
            "habits": [
                _hsk_habit(habit_id=1, name="English", values={"2026-08-01": 1}),
                _hsk_habit(habit_id=2, name="English", values={"2026-08-02": 1}),
            ]
        },
        {"habits": [_tt_habit(habit_id="t1", name="English", dates=["2026-08-01"])]},
        today=date(2026, 8, 2),
    )
    assert report["habit_counts"]["matched"] == 0
    assert report["habit_counts"]["name_conflicts"] == 1
    assert report["name_conflicts"][0]["source"] == "hsk"
    assert report["name_conflicts"][0]["count"] == 2


def test_format_preview_mentions_dry_run() -> None:
    report = build_habits_ticktick_sync_preview({"habits": []}, {"habits": []}, today=date(2026, 8, 1))
    text = format_habits_ticktick_sync_preview(report)
    assert "dry-run" in text
    assert "Matched by name: 0" in text

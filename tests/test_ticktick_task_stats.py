"""Tests for local TickTick DB reading and completion stats aggregation."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path

import pytest

from harrix_swiss_knife.actions.common.ticktick_local_db import (
    TickTickCompletion,
    TickTickDbError,
    copy_ticktick_db,
    default_ticktick_db_path,
    load_completions,
    load_projects,
    open_ticktick_db,
    parse_ticktick_datetime,
)
from harrix_swiss_knife.actions.common.ticktick_task_stats import (
    aggregate_completions,
    available_years,
    current_streak_days,
    filter_completions_for_period,
    format_period_summary,
    longest_streak_days,
    resolve_period,
)
from harrix_swiss_knife.apps.common.calendar_heatmap import date_at_heatmap_point


def _create_fixture_db(path: Path) -> Path:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE ProjectModel (
            id TEXT,
            name TEXT,
            kind TEXT,
            closed INTEGER,
            delete_status INTEGER,
            sortOrder INTEGER
        );
        CREATE TABLE TaskModel (
            id TEXT,
            title TEXT,
            completedTime TEXT,
            projectId TEXT,
            status INTEGER,
            deleted INTEGER
        );
        INSERT INTO ProjectModel VALUES
            ('p1', 'Inbox', 'TASK', 0, 0, 1),
            ('p2', 'Work', 'TASK', 0, 0, 2),
            ('gone', 'Deleted list', 'TASK', 0, 1, 3);
        INSERT INTO TaskModel VALUES
            ('t1', 'Alpha', '2024-01-01 10:00:00', 'p1', 2, 0),
            ('t2', 'Beta', '2024-01-02 11:00:00', 'p1', 2, 0),
            ('t3', 'Gamma', '2024-01-02 12:00:00', 'p2', 2, 0),
            ('t4', 'Delta', '2024-01-03 09:00:00', 'p2', 2, 0),
            ('t5', 'Gone', '2024-01-04 09:00:00', 'p1', 2, 1),
            ('t6', 'Bad stamp', 'not-a-date', 'p1', 2, 0),
            ('t7', 'Old', '2023-12-31 23:00:00', 'p1', 2, 0);
        """,
    )
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def ticktick_db(tmp_path: Path) -> Path:
    """Minimal TickTick-like SQLite fixture."""
    return _create_fixture_db(tmp_path / "TickTick.db")


def test_default_ticktick_db_path_uses_appdata(tmp_path: Path) -> None:
    r"""Default path is `%APPDATA%\Tick_Tick\TickTick.db`."""
    assert default_ticktick_db_path(appdata=tmp_path) == tmp_path / "Tick_Tick" / "TickTick.db"


def test_copy_ticktick_db_requires_existing_file(tmp_path: Path) -> None:
    """Missing live DB raises a clear error."""
    with pytest.raises(TickTickDbError, match="not found"):
        copy_ticktick_db(tmp_path / "missing.db")


def test_copy_and_load_projects_completions(ticktick_db: Path, tmp_path: Path) -> None:
    """WAL-safe copy loads projects and non-deleted completions."""
    copied = copy_ticktick_db(ticktick_db, dest_dir=tmp_path / "copy")
    with open_ticktick_db(copied) as conn:
        projects = load_projects(conn)
        completions = load_completions(conn)
        work_only = load_completions(conn, project_id="p2")

    assert [project.id for project in projects] == ["p1", "p2"]
    assert [item.title for item in completions] == ["Old", "Alpha", "Beta", "Gamma", "Delta"]
    assert [item.title for item in work_only] == ["Gamma", "Delta"]


def test_parse_ticktick_datetime_formats() -> None:
    """Common TickTick timestamp formats parse to naive datetimes."""
    assert parse_ticktick_datetime("2024-01-02 11:00:00") == datetime(2024, 1, 2, 11, 0, 0)  # noqa: DTZ001
    assert parse_ticktick_datetime("2024-01-02") == datetime(2024, 1, 2)  # noqa: DTZ001
    assert parse_ticktick_datetime("") is None
    assert parse_ticktick_datetime("bogus") is None


def _sample_completions() -> list[TickTickCompletion]:
    return [
        TickTickCompletion("1", "A", datetime(2024, 1, 1, 10, 0, 0), "p1", "Inbox", 2),  # noqa: DTZ001
        TickTickCompletion("2", "B", datetime(2024, 1, 2, 11, 0, 0), "p1", "Inbox", 2),  # noqa: DTZ001
        TickTickCompletion("3", "C", datetime(2024, 1, 2, 12, 0, 0), "p2", "Work", 2),  # noqa: DTZ001
        TickTickCompletion("4", "D", datetime(2024, 1, 3, 9, 0, 0), "p2", "Work", 2),  # noqa: DTZ001
        TickTickCompletion("5", "E", datetime(2024, 1, 5, 9, 0, 0), "p1", "Inbox", 2),  # noqa: DTZ001
    ]


def test_resolve_period_year_and_rolling() -> None:
    """Year windows clamp the current year to today; None means last 365 days."""
    today = date(2024, 6, 15)
    assert resolve_period(year=2023, today=today) == (date(2023, 1, 1), date(2023, 12, 31))
    assert resolve_period(year=2024, today=today) == (date(2024, 1, 1), date(2024, 6, 15))
    start, end = resolve_period(year=None, today=today)
    assert end == today
    assert start == date(2023, 6, 16)


def test_aggregate_completions_counts_streaks_and_filter() -> None:
    """Aggregation fills counts, streaks, busiest day, and project filtering."""
    completions = _sample_completions()
    stats = aggregate_completions(
        completions,
        date(2024, 1, 1),
        date(2024, 1, 5),
        today=date(2024, 1, 5),
    )
    assert stats.total_completions == 5
    assert stats.active_days == 4
    assert stats.counts_by_day[date(2024, 1, 2)] == 2
    assert stats.busiest_day == date(2024, 1, 2)
    assert stats.busiest_count == 2
    assert stats.current_streak == 1
    assert stats.longest_streak == 3
    assert "Completions: 5" in format_period_summary(stats)

    work = aggregate_completions(
        completions,
        date(2024, 1, 1),
        date(2024, 1, 5),
        project_id="p2",
        today=date(2024, 1, 5),
    )
    assert work.total_completions == 2
    assert [
        item.title
        for item in filter_completions_for_period(
            completions,
            date(2024, 1, 1),
            date(2024, 1, 5),
            project_id="p2",
        )
    ] == ["C", "D"]


def test_streak_helpers() -> None:
    """Current streak allows a missed today; longest scans the window."""
    counts = {
        date(2024, 1, 1): 1,
        date(2024, 1, 2): 2,
        date(2024, 1, 3): 1,
        date(2024, 1, 5): 1,
    }
    assert current_streak_days(counts, date(2024, 1, 5)) == 1
    assert current_streak_days(counts, date(2024, 1, 6)) == 1
    assert current_streak_days(counts, date(2024, 1, 7)) == 0
    assert longest_streak_days(counts, date(2024, 1, 1), date(2024, 1, 5)) == 3


def test_available_years_caps_at_today() -> None:
    """Future years are ignored when listing filter years."""
    completions = [
        TickTickCompletion("1", "A", datetime(2020, 1, 1), "p", "P", 2),  # noqa: DTZ001
        TickTickCompletion("2", "B", datetime(2030, 1, 1), "p", "P", 2),  # noqa: DTZ001
    ]
    assert available_years(completions, today_year=2026) == [2020]


def test_date_at_heatmap_point_picks_nearest_cell() -> None:
    """Click mapping returns the nearest day within the distance threshold."""
    positions = {
        date(2024, 1, 1): (0.0, 0.0),
        date(2024, 1, 2): (1.0, 0.0),
    }
    assert date_at_heatmap_point(positions, 0.2, 0.2) == date(2024, 1, 1)
    assert date_at_heatmap_point(positions, 1.2, 0.2) == date(2024, 1, 2)
    assert date_at_heatmap_point(positions, 10.0, 10.0) is None

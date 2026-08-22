"""Tests for applying HSK ↔ TickTick sync plans."""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Self
from unittest.mock import MagicMock

from harrix_swiss_knife.apps.habits.habits_ticktick_sync import (
    apply_habits_ticktick_sync,
    build_habits_ticktick_sync_preview,
    format_habits_ticktick_sync_result,
)
from harrix_swiss_knife.apps.habits.ticktick_api import (
    DEFAULT_HABIT_COLOR,
    DEFAULT_HABIT_ICON_RES,
    TickTickHabitsClient,
    iso_to_ticktick_stamp,
    resolve_ticktick_api_token,
    ticktick_habit_icon_is_missing,
)
from tests.test_habits_ticktick_sync import _hsk_habit, _tt_habit


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


class _CapturingOpener:
    def __init__(self, bodies: list[bytes] | None = None) -> None:
        self.bodies = bodies if bodies is not None else [b'{"id":"h1"}']
        self.requests: list[Any] = []
        self._index = 0

    def open(self, request: Any, timeout: int = 120) -> _FakeResponse:  # noqa: ARG002
        self.requests.append(request)
        body = self.bodies[min(self._index, len(self.bodies) - 1)]
        self._index += 1
        return _FakeResponse(body)


def test_iso_to_ticktick_stamp() -> None:
    assert iso_to_ticktick_stamp("2026-08-21") == 20260821


def test_resolve_ticktick_api_token_from_file(tmp_path: Any) -> None:
    keys = tmp_path / "api-keys"
    keys.mkdir()
    (keys / "ticktick-api-key.txt").write_text("tp_test_token_value_here_xx\n", encoding="utf-8")
    assert resolve_ticktick_api_token(config={}, project_root=tmp_path) == "tp_test_token_value_here_xx"


def test_resolve_ticktick_api_token_apy_fallback(tmp_path: Any) -> None:
    keys = tmp_path / "api-keys"
    keys.mkdir()
    (keys / "ticktick-apy-key.txt").write_text("tp_legacy_name_token_xxxxx\n", encoding="utf-8")
    assert resolve_ticktick_api_token(config={}, project_root=tmp_path) == "tp_legacy_name_token_xxxxx"


def test_apply_sync_writes_hsk_and_calls_ticktick() -> None:
    report = build_habits_ticktick_sync_preview(
        {
            "habits": [
                _hsk_habit(
                    habit_id=1,
                    name="English",
                    values={"2026-08-01": 1, "2026-08-02": 0},
                )
            ]
        },
        {"habits": [_tt_habit(habit_id="t1", name="English", dates=["2026-08-02", "2026-08-03"])]},
        today=date(2026, 8, 5),
    )
    db = MagicMock()
    db.upsert_habit_checkins.return_value = 3
    client = MagicMock()

    result = apply_habits_ticktick_sync(db, report, client)

    assert result["error_count"] == 0
    assert result["applied"]["to_hsk_done"] == 2
    assert result["applied"]["to_ticktick_done"] == 1
    client.checkin_done.assert_called()
    client.ensure_habit_icon.assert_not_called()
    db.upsert_habit_checkins.assert_called_once()


def test_apply_sync_creates_missing_habits() -> None:
    report = build_habits_ticktick_sync_preview(
        {"habits": [_hsk_habit(habit_id=4, name="SoloHSK", values={"2026-08-01": 1})]},
        {"habits": [_tt_habit(habit_id="t4", name="SoloTT", dates=["2026-08-01"])]},
        today=date(2026, 8, 1),
    )
    db = MagicMock()
    db.add_habit.return_value = True
    db.get_rows.return_value = [[99]]
    db.upsert_habit_checkins.return_value = 1
    client = MagicMock()
    client.create_boolean_habit.return_value = {"id": "new-tt"}

    result = apply_habits_ticktick_sync(db, report, client)

    assert result["applied"]["created_in_ticktick"] == 1
    assert result["applied"]["created_in_hsk"] == 1
    client.create_boolean_habit.assert_called_once_with("SoloHSK")
    client.ensure_habit_icon.assert_not_called()
    db.add_habit.assert_called_once()
    client.checkin_done.assert_called()


def test_apply_sync_sets_missing_ticktick_icons() -> None:
    report = build_habits_ticktick_sync_preview(
        {"habits": [_hsk_habit(habit_id=1, name="English", values={})]},
        {"habits": [_tt_habit(habit_id="t1", name="English", dates=[], icon_res="")]},
        today=date(2026, 8, 1),
    )
    db = MagicMock()
    client = MagicMock()

    result = apply_habits_ticktick_sync(db, report, client)

    assert result["error_count"] == 0
    assert result["applied"]["fixed_icons"] == 1
    client.ensure_habit_icon.assert_called_once_with("t1")


def test_create_boolean_habit_sends_default_icon() -> None:
    opener = _CapturingOpener()
    client = TickTickHabitsClient("tp_token", opener=opener)
    created = client.create_boolean_habit("Read")
    assert created["id"] == "h1"
    body = json.loads(opener.requests[0].data.decode("utf-8"))
    assert body["iconRes"] == DEFAULT_HABIT_ICON_RES
    assert body["color"] == DEFAULT_HABIT_COLOR
    assert opener.requests[0].full_url.endswith("/habit")


def test_ensure_habit_icon_posts_default_icon() -> None:
    opener = _CapturingOpener(bodies=[b""])
    client = TickTickHabitsClient("tp_token", opener=opener)
    client.ensure_habit_icon("abc")
    body = json.loads(opener.requests[0].data.decode("utf-8"))
    assert body == {"iconRes": DEFAULT_HABIT_ICON_RES, "color": DEFAULT_HABIT_COLOR}
    assert opener.requests[0].full_url.endswith("/habit/abc")


def test_export_habits_payload_includes_icon_res() -> None:
    opener = _CapturingOpener(
        bodies=[
            b'[{"id":"h1","name":"Read","iconRes":"","status":0}]',
            b"[]",
        ]
    )
    client = TickTickHabitsClient("tp_token", opener=opener)
    payload = client.export_habits_payload(to_stamp=20260822)
    assert payload["habits"][0]["icon_res"] == ""


def test_ticktick_habit_icon_is_missing() -> None:
    assert ticktick_habit_icon_is_missing("")
    assert ticktick_habit_icon_is_missing("  ")
    assert ticktick_habit_icon_is_missing(None)
    assert not ticktick_habit_icon_is_missing("habit_reading")


def test_format_sync_result_shows_per_side_counts() -> None:
    text = format_habits_ticktick_sync_result(
        {
            "applied": {
                "created_in_ticktick": 1,
                "created_in_hsk": 2,
                "to_ticktick_done": 10,
                "to_hsk_done": 7,
                "gap_not_done_to_hsk": 3,
                "fixed_icons": 4,
            },
            "error_count": 0,
            "errors": [],
        }
    )
    assert "HSK ← from TickTick:" in text
    assert "Values changed: 10" in text
    assert "Done (wrote 1): 7" in text
    assert "Not done (wrote 0): 3" in text
    assert "TickTick ← from HSK:" in text
    assert "Values transferred (Done): 10" in text
    assert "Habits created: 1" in text
    assert "Habits created: 2" in text
    assert "Default icons set: 4" in text
    assert "Total values changed: 20" in text

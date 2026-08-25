"""Tests for fitness exercise AI fill response parsing."""

from __future__ import annotations

from harrix_swiss_knife.apps.fitness.exercise_ai_fill import media_filename_hint, parse_exercise_fill_response


def test_media_filename_hint_uses_basename() -> None:
    """Only the filename is sent to AI, not the full path."""
    assert media_filename_hint(r"D:\videos\High knees with clap.mp4") == "High knees with clap.mp4"
    assert media_filename_hint("/data/videos/push-ups.avif") == "push-ups.avif"
    assert media_filename_hint("   ") == ""
    assert media_filename_hint("") == ""


def test_parse_exercise_fill_response_valid() -> None:
    local_name = "\u041e\u0442\u0436\u0438\u043c\u0430\u043d\u0438\u044f"  # Отжимания
    result = parse_exercise_fill_response(f"Push-ups\t{local_name}\ttimes\t0.4")
    assert result is not None
    assert result.name == "Push-ups"
    assert result.name_local == local_name
    assert result.unit == "times"
    assert result.calories_per_unit == 0.4


def test_parse_exercise_fill_response_skips_fences_and_commas() -> None:
    local_name = "\u0411\u0435\u0433"  # Бег
    text = f"```text\nRunning\t{local_name}\tkm\t70,5\n```"
    result = parse_exercise_fill_response(text)
    assert result is not None
    assert result.name == "Running"
    assert result.name_local == local_name
    assert result.unit == "km"
    assert result.calories_per_unit == 70.5


def test_parse_exercise_fill_response_rejects_invalid() -> None:
    assert parse_exercise_fill_response("") is None
    assert parse_exercise_fill_response("only\ttwo") is None
    assert parse_exercise_fill_response("Name\tLocal\ttimes\tabc") is None
    assert parse_exercise_fill_response("\tLocal\ttimes\t1") is None

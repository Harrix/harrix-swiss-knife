"""Tests for Fitness catalog name checks and exercise AVIF rename."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey, AvifManager
from harrix_swiss_knife.apps.fitness.database_manager import catalog_name_taken


def test_catalog_name_taken_is_case_insensitive_and_can_exclude_id() -> None:
    """Duplicate names match ignoring case; the current row can be ignored."""
    rows = [[1, "Push-ups"], [2, "Squats"]]
    assert catalog_name_taken(rows, "push-ups")
    assert catalog_name_taken(rows, "  SQUATS  ")
    assert not catalog_name_taken(rows, "Plank")
    assert not catalog_name_taken(rows, "push-ups", exclude_id=1)
    assert catalog_name_taken(rows, "push-ups", exclude_id=2)


def test_rename_exercise_avif_renames_file_and_retargets_slot(tmp_path: Path) -> None:
    """Renaming an exercise also renames `{name}.avif` next to the database."""
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    source = img_dir / "Push-ups.avif"
    source.write_bytes(b"avif")
    manager = AvifManager(img_dir)
    manager.avif_data[AvifLabelKey.MAIN] = {
        "frames": [],
        "current_frame": 0,
        "timer": None,
        "exercise": "Push-ups",
    }

    assert manager.rename_exercise_avif("Push-ups", "Pike push-ups")
    assert not source.exists()
    assert (img_dir / "Pike push-ups.avif").is_file()
    assert manager.get_exercise_avif_path("Pike push-ups") is not None
    assert manager.get_current_exercise("main") == "Pike push-ups"


def test_rename_exercise_avif_skips_missing_and_same_name(tmp_path: Path) -> None:
    """No file and an unchanged name are not treated as a rename."""
    manager = AvifManager(tmp_path / "fitness_img")
    (tmp_path / "fitness_img").mkdir()
    assert not manager.rename_exercise_avif("Missing", "Other")
    (tmp_path / "fitness_img" / "Walk.avif").write_bytes(b"x")
    assert not manager.rename_exercise_avif("Walk", "Walk")

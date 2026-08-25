"""Tests for Fitness catalog name checks and exercise AVIF rename."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey, AvifManager
from harrix_swiss_knife.apps.fitness.database_manager import catalog_matching_row, catalog_name_taken


def test_catalog_name_taken_is_case_insensitive_and_can_exclude_id() -> None:
    """Duplicate names match ignoring case; the current row can be ignored."""
    rows = [[1, "Push-ups"], [2, "Squats"]]
    assert catalog_name_taken(rows, "push-ups")
    assert catalog_name_taken(rows, "  SQUATS  ")
    assert not catalog_name_taken(rows, "Plank")
    assert not catalog_name_taken(rows, "push-ups", exclude_id=1)
    assert catalog_name_taken(rows, "push-ups", exclude_id=2)


def test_catalog_matching_row_returns_english_and_local() -> None:
    rows = [[1, "Push-ups", "Отжимания"], [2, "Squats", "Приседания"]]
    match = catalog_matching_row(rows, "отжимания", name_index=2)
    assert match == [1, "Push-ups", "Отжимания"]
    assert catalog_matching_row(rows, "Push-ups", name_index=1) == [1, "Push-ups", "Отжимания"]
    assert catalog_matching_row(rows, "отжимания", name_index=2, exclude_id=1) is None


def test_catalog_name_taken_ignores_empty_local_names() -> None:
    """Blank local names are not treated as taken."""
    rows = [[1, "Отжимания"], [2, ""], [3, None]]
    assert catalog_name_taken(rows, "отжимания")
    assert not catalog_name_taken(rows, "")
    assert not catalog_name_taken(rows, "   ")


def test_rename_exercise_avif_renames_file_and_retargets_slot(tmp_path: Path) -> None:
    """Renaming an exercise also renames `{name}.avif` next to the database."""
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    source = img_dir / "Push-ups.avif"
    source.write_bytes(b"avif")
    high_source = img_dir / "high" / "Push-ups.avif"
    high_source.parent.mkdir()
    high_source.write_bytes(b"avif-high")
    manager = AvifManager(img_dir)
    manager.avif_data[AvifLabelKey.MAIN] = {
        "frames": [],
        "current_frame": 0,
        "timer": None,
        "exercise": "Push-ups",
    }

    assert manager.rename_exercise_avif("Push-ups", "Pike push-ups")
    assert not source.exists()
    assert not high_source.exists()
    assert (img_dir / "Pike push-ups.avif").is_file()
    assert (img_dir / "high" / "Pike push-ups.avif").read_bytes() == b"avif-high"
    assert manager.get_exercise_avif_path("Pike push-ups") is not None
    assert manager.get_exercise_avif_path("Pike push-ups", high=True) is not None
    assert manager.get_current_exercise("main") == "Pike push-ups"


def test_delete_exercise_avif_removes_small_and_high(tmp_path: Path) -> None:
    """Deleting an exercise removes both the UI AVIF and `high/` copy."""
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    (img_dir / "Walk.avif").write_bytes(b"small")
    high_dir = img_dir / "high"
    high_dir.mkdir()
    (high_dir / "Walk.avif").write_bytes(b"large")
    manager = AvifManager(img_dir)
    assert manager.delete_exercise_avif("Walk")
    assert not (img_dir / "Walk.avif").exists()
    assert not (high_dir / "Walk.avif").exists()
    assert not manager.delete_exercise_avif("Walk")


def test_lightbox_avif_path_prefers_high_resolution(tmp_path: Path) -> None:
    """Lightbox uses `fitness_img/high/{name}.avif` when that file exists."""
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    small = img_dir / "Walk.avif"
    small.write_bytes(b"small")
    high = img_dir / "high" / "Walk.avif"
    high.parent.mkdir()
    high.write_bytes(b"large")
    manager = AvifManager(img_dir)
    assert manager.get_exercise_avif_path("Walk") == small
    assert manager.get_exercise_lightbox_avif_path("Walk") == high
    assert manager.get_exercise_hover_avif_path("Walk") == small
    high.unlink()
    assert manager.get_exercise_lightbox_avif_path("Walk") == small
    assert manager.get_exercise_hover_avif_path("Walk") == small


def test_rename_exercise_avif_skips_missing_and_same_name(tmp_path: Path) -> None:
    """No file and an unchanged name are not treated as a rename."""
    manager = AvifManager(tmp_path / "fitness_img")
    (tmp_path / "fitness_img").mkdir()
    assert not manager.rename_exercise_avif("Missing", "Other")
    (tmp_path / "fitness_img" / "Walk.avif").write_bytes(b"x")
    assert not manager.rename_exercise_avif("Walk", "Walk")

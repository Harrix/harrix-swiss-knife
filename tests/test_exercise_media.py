"""Tests for dual small/high exercise AVIF conversion."""

from __future__ import annotations

from pathlib import Path

import pytest

from harrix_swiss_knife.apps.common.apps_config import (
    DEFAULT_FITNESS_IMAGE_HIGH_MAX_SIZE,
    DEFAULT_FITNESS_IMAGE_MAX_SIZE,
    DEFAULT_FITNESS_IMAGE_MIN_MAX_SIZE,
    get_apps_fitness_image_high_max_size,
    get_apps_fitness_image_max_size,
    get_apps_fitness_image_min_max_size,
)
from harrix_swiss_knife.apps.common.exercise_media import (
    FITNESS_IMG_HIGH_DIR,
    FITNESS_IMG_MIN_DIR,
    rebuild_min_thumbnails_from_small,
    rebuild_small_avifs_from_high,
    save_exercise_avif,
)


def test_fitness_image_high_max_size_defaults_and_clamps() -> None:
    """High size defaults to 1920 and is never smaller than the UI size."""
    assert get_apps_fitness_image_max_size({}) == DEFAULT_FITNESS_IMAGE_MAX_SIZE
    assert get_apps_fitness_image_high_max_size({}) == DEFAULT_FITNESS_IMAGE_HIGH_MAX_SIZE
    assert get_apps_fitness_image_high_max_size({"apps": {"fitness_image_high_max_size": 800}}) == 800
    assert (
        get_apps_fitness_image_high_max_size(
            {"apps": {"fitness_image_max_size": 500, "fitness_image_high_max_size": 200}},
        )
        == 500
    )
    assert get_apps_fitness_image_high_max_size({"apps": {"fitness_image_high_max_size": "x"}}) == (
        DEFAULT_FITNESS_IMAGE_HIGH_MAX_SIZE
    )


def test_fitness_image_min_max_size_defaults() -> None:
    assert get_apps_fitness_image_min_max_size({}) == DEFAULT_FITNESS_IMAGE_MIN_MAX_SIZE
    assert get_apps_fitness_image_min_max_size({"apps": {"fitness_image_min_max_size": 128}}) == 128
    assert get_apps_fitness_image_min_max_size({"apps": {"fitness_image_min_max_size": 0}}) == 1


def test_save_exercise_avif_writes_small_and_high(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Saving media writes `{name}.avif` and `high/{name}.avif`, replacing both."""
    source = tmp_path / "source.png"
    source.write_bytes(b"src")
    avif_dir = tmp_path / "fitness_img"
    avif_dir.mkdir()
    (avif_dir / "Walk.avif").write_bytes(b"old-small")
    high_dir = avif_dir / FITNESS_IMG_HIGH_DIR
    high_dir.mkdir()
    (high_dir / "Walk.avif").write_bytes(b"old-high")

    def fake_convert(source_path: Path, target: Path, *, project_root: Path, max_size: int | None) -> Path:
        del source_path, project_root
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.unlink()
        target.write_bytes(f"new-{max_size}".encode())
        return target

    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._convert_source_to_avif",
        fake_convert,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._avif_file_is_animated",
        lambda _path: False,
    )

    written = save_exercise_avif(source, "Walk", avif_dir, max_size=330, high_max_size=1920)
    assert written == avif_dir / "Walk.avif"
    assert written.read_bytes() == b"new-330"
    assert (high_dir / "Walk.avif").read_bytes() == b"new-1920"


def test_save_exercise_avif_writes_min_webp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "source.png"
    source.write_bytes(b"src")
    avif_dir = tmp_path / "fitness_img"

    def fake_convert(source_path: Path, target: Path, *, project_root: Path, max_size: int | None) -> Path:
        del source_path, project_root
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f"new-{max_size}".encode())
        return target

    def fake_min(source: Path, target: Path, *, max_size: int) -> Path:
        del source
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f"min-{max_size}".encode())
        return target

    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._convert_source_to_avif",
        fake_convert,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._avif_file_is_animated",
        lambda _path: False,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._write_min_webp_thumbnail",
        fake_min,
    )

    save_exercise_avif(source, "Walk", avif_dir, max_size=330, high_max_size=1920, min_max_size=96)
    assert (avif_dir / FITNESS_IMG_MIN_DIR / "Walk.webp").read_bytes() == b"min-96"


def test_rebuild_min_thumbnails_from_small(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    avif_dir = tmp_path / "fitness_img"
    avif_dir.mkdir()
    (avif_dir / "Walk.avif").write_bytes(b"small")

    def fake_min(source: Path, target: Path, *, max_size: int) -> Path:
        assert source.name == "Walk.avif"
        assert max_size == 96
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"webp")
        return target

    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._write_min_webp_thumbnail",
        fake_min,
    )
    result = rebuild_min_thumbnails_from_small(avif_dir, min_max_size=96)
    assert result.rebuilt == ("Walk",)
    assert (avif_dir / FITNESS_IMG_MIN_DIR / "Walk.webp").read_bytes() == b"webp"


def test_save_exercise_avif_keeps_old_files_when_high_convert_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed high-resolution convert leaves the previous pair unchanged."""
    source = tmp_path / "source.png"
    source.write_bytes(b"src")
    avif_dir = tmp_path / "fitness_img"
    small_target = avif_dir / "Walk.avif"
    small_target.parent.mkdir(parents=True)
    small_target.write_bytes(b"old-small")
    high_target = avif_dir / FITNESS_IMG_HIGH_DIR / "Walk.avif"
    high_target.parent.mkdir(parents=True)
    high_target.write_bytes(b"stale-high")

    def fake_convert(source_path: Path, target: Path, *, project_root: Path, max_size: int | None) -> Path:
        del source_path, project_root, target
        if max_size == 1920:
            msg = "high convert failed"
            raise RuntimeError(msg)
        msg = "small convert should not run"
        raise AssertionError(msg)

    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._convert_source_to_avif",
        fake_convert,
    )

    with pytest.raises(RuntimeError, match="high convert failed"):
        save_exercise_avif(source, "Walk", avif_dir, max_size=330, high_max_size=1920)
    assert small_target.read_bytes() == b"old-small"
    assert high_target.read_bytes() == b"stale-high"


def test_save_exercise_avif_shrinks_animated_high_to_small(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An animated high file is resized to the UI AVIF instead of a still."""
    source = tmp_path / "source.gif"
    source.write_bytes(b"src")
    avif_dir = tmp_path / "fitness_img"

    def fake_convert(source_path: Path, target: Path, *, project_root: Path, max_size: int | None) -> Path:
        del source_path, project_root
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f"high-{max_size}".encode())
        return target

    def fake_write_small(
        high_path: Path,
        target: Path,
        *,
        project_root: Path,
        max_size: int | None,
    ) -> Path:
        del project_root
        assert high_path.read_bytes() == b"high-1920"
        assert max_size == 330
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"small-from-high")
        return target

    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._convert_source_to_avif",
        fake_convert,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._avif_file_is_animated",
        lambda _path: True,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._write_small_from_animated_avif",
        fake_write_small,
    )

    written = save_exercise_avif(source, "Walk", avif_dir, max_size=330, high_max_size=1920)
    assert written.read_bytes() == b"small-from-high"
    assert (avif_dir / FITNESS_IMG_HIGH_DIR / "Walk.avif").read_bytes() == b"high-1920"


def test_rebuild_small_avifs_from_high_rewrites_animated_high(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Still UI files are rebuilt from animated high-resolution originals."""
    avif_dir = tmp_path / "fitness_img"
    high_dir = avif_dir / FITNESS_IMG_HIGH_DIR
    high_dir.mkdir(parents=True)
    (high_dir / "Walk.avif").write_bytes(b"high-anim")
    (high_dir / "Sit.avif").write_bytes(b"high-still")
    (avif_dir / "Walk.avif").write_bytes(b"old-still")

    def fake_animated(path: Path) -> bool:
        return path.name == "Walk.avif" and FITNESS_IMG_HIGH_DIR in path.parts

    def fake_write_small(
        high_path: Path,
        target: Path,
        *,
        project_root: Path,
        max_size: int | None,
    ) -> Path:
        del project_root
        assert high_path.name == "Walk.avif"
        assert max_size == 330
        target.write_bytes(b"rebuilt-small")
        return target

    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._avif_file_is_animated",
        fake_animated,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._write_small_from_animated_avif",
        fake_write_small,
    )

    result = rebuild_small_avifs_from_high(avif_dir, max_size=330, project_root=tmp_path)
    assert result.rebuilt == ("Walk",)
    assert result.skipped == ("Sit",)
    assert result.failed == ()
    assert (avif_dir / "Walk.avif").read_bytes() == b"rebuilt-small"

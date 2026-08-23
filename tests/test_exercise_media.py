"""Tests for dual small/high exercise AVIF conversion."""

from __future__ import annotations

from pathlib import Path

import pytest

from harrix_swiss_knife.apps.common.apps_config import (
    DEFAULT_FITNESS_IMAGE_HIGH_MAX_SIZE,
    DEFAULT_FITNESS_IMAGE_MAX_SIZE,
    get_apps_fitness_image_high_max_size,
    get_apps_fitness_image_max_size,
)
from harrix_swiss_knife.apps.common.exercise_media import FITNESS_IMG_HIGH_DIR, save_exercise_avif


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

    written = save_exercise_avif(source, "Walk", avif_dir, max_size=330, high_max_size=1920)
    assert written == avif_dir / "Walk.avif"
    assert written.read_bytes() == b"new-330"
    assert (high_dir / "Walk.avif").read_bytes() == b"new-1920"


def test_save_exercise_avif_removes_stale_high_when_high_convert_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed high-resolution convert must not leave the previous large file."""
    source = tmp_path / "source.png"
    source.write_bytes(b"src")
    avif_dir = tmp_path / "fitness_img"
    high_target = avif_dir / FITNESS_IMG_HIGH_DIR / "Walk.avif"
    high_target.parent.mkdir(parents=True)
    high_target.write_bytes(b"stale-high")

    def fake_convert(source_path: Path, target: Path, *, project_root: Path, max_size: int | None) -> Path:
        del source_path, project_root
        if max_size == 1920:
            msg = "high convert failed"
            raise RuntimeError(msg)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"new-small")
        return target

    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.exercise_media._convert_source_to_avif",
        fake_convert,
    )

    with pytest.raises(RuntimeError, match="high convert failed"):
        save_exercise_avif(source, "Walk", avif_dir, max_size=330, high_max_size=1920)
    assert (avif_dir / "Walk.avif").read_bytes() == b"new-small"
    assert not high_target.exists()

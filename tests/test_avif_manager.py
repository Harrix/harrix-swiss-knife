"""Tests for AvifManager path selection and non-lightbox load behavior."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pillow_avif  # noqa: F401
from PIL import Image
from PySide6.QtWidgets import QApplication, QLabel

from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey, AvifManager
from harrix_swiss_knife.apps.common.exercise_media import FITNESS_IMG_HIGH_DIR

if TYPE_CHECKING:
    import pytest


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _write_test_avif(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 48), (120, 80, 40)).save(path, format="AVIF")


def test_load_exercise_avif_main_and_hover_never_open_high(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MAIN and LIST_HOVER resolve only the small UI AVIF, never fitness_img/high/."""
    assert _qapp() is not None
    img_dir = tmp_path / "fitness_img"
    _write_test_avif(img_dir / "Walk.avif")
    _write_test_avif(img_dir / FITNESS_IMG_HIGH_DIR / "Walk.avif")

    high_flags: list[bool] = []
    lightbox_names: list[str] = []
    original_get = AvifManager.get_exercise_avif_path
    original_lightbox = AvifManager.get_exercise_lightbox_avif_path

    def spy_get(self: AvifManager, exercise_name: str, *, high: bool = False) -> Path | None:
        high_flags.append(high)
        return original_get(self, exercise_name, high=high)

    def spy_lightbox(self: AvifManager, exercise_name: str) -> Path | None:
        lightbox_names.append(exercise_name)
        return original_lightbox(self, exercise_name)

    monkeypatch.setattr(AvifManager, "get_exercise_avif_path", spy_get)
    monkeypatch.setattr(AvifManager, "get_exercise_lightbox_avif_path", spy_lightbox)

    manager = AvifManager(img_dir)
    label = QLabel()
    label.resize(120, 120)

    high_flags.clear()
    lightbox_names.clear()
    manager.load_exercise_avif("Walk", label, AvifLabelKey.MAIN)
    assert high_flags == [False]
    assert lightbox_names == []
    manager.stop_animation(AvifLabelKey.MAIN)

    high_flags.clear()
    lightbox_names.clear()
    manager.load_exercise_avif("Walk", label, AvifLabelKey.LIST_HOVER)
    assert high_flags == [False]
    assert lightbox_names == []
    manager.stop_animation(AvifLabelKey.LIST_HOVER)


def test_load_exercise_avif_list_hover_uses_async_animation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """List hover shows the first frame now and decodes the rest in a worker."""
    assert _qapp() is not None
    img_dir = tmp_path / "fitness_img"
    _write_test_avif(img_dir / "Walk.avif")

    called: list[str] = []

    def spy_async(
        _self: AvifManager,
        avif_path: Path,
        label_widget: QLabel,
        data: dict,
        key: AvifLabelKey,
        exercise_name: str,
    ) -> None:
        called.append("async")
        assert key is AvifLabelKey.LIST_HOVER
        assert exercise_name == "Walk"
        assert avif_path.name == "Walk.avif"
        assert label_widget is not None
        assert isinstance(data, dict)

    monkeypatch.setattr(AvifManager, "_load_avif_first_frame_then_async", spy_async)

    manager = AvifManager(img_dir)
    label = QLabel()
    label.resize(120, 120)
    manager.load_exercise_avif("Walk", label, AvifLabelKey.LIST_HOVER)
    assert called == ["async"]
    manager.stop_animation(AvifLabelKey.LIST_HOVER)


def test_load_exercise_avif_lightbox_prefers_high(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LIGHTBOX uses get_exercise_lightbox_avif_path (high when present)."""
    assert _qapp() is not None
    img_dir = tmp_path / "fitness_img"
    _write_test_avif(img_dir / "Walk.avif")
    _write_test_avif(img_dir / FITNESS_IMG_HIGH_DIR / "Walk.avif")

    high_flags: list[bool] = []
    lightbox_names: list[str] = []
    original_get = AvifManager.get_exercise_avif_path
    original_lightbox = AvifManager.get_exercise_lightbox_avif_path

    def spy_get(self: AvifManager, exercise_name: str, *, high: bool = False) -> Path | None:
        high_flags.append(high)
        return original_get(self, exercise_name, high=high)

    def spy_lightbox(self: AvifManager, exercise_name: str) -> Path | None:
        lightbox_names.append(exercise_name)
        return original_lightbox(self, exercise_name)

    monkeypatch.setattr(AvifManager, "get_exercise_avif_path", spy_get)
    monkeypatch.setattr(AvifManager, "get_exercise_lightbox_avif_path", spy_lightbox)

    manager = AvifManager(img_dir)
    label = QLabel()
    label.resize(200, 200)
    manager.load_exercise_avif("Walk", label, AvifLabelKey.LIGHTBOX)

    assert lightbox_names == ["Walk"]
    assert True in high_flags
    assert manager.get_exercise_lightbox_avif_path("Walk") == img_dir / FITNESS_IMG_HIGH_DIR / "Walk.avif"
    manager.stop_animation(AvifLabelKey.LIGHTBOX)

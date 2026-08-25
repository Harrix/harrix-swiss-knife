"""Tests for AvifManager path selection and non-lightbox load behavior."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pillow_avif  # noqa: F401
from PIL import Image
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel

from harrix_swiss_knife.apps.common import avif_manager as avif_manager_mod
from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey, AvifManager, animation_interval_ms
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


def test_animation_interval_ms() -> None:
    assert animation_interval_ms(100, 1.0) == 100
    assert animation_interval_ms(100, 2.0) == 50
    assert animation_interval_ms(100, 0.5) == 200
    assert animation_interval_ms(100, 0) == 1000
    assert animation_interval_ms(0, 1.0) == 100


def test_set_animation_speed_changes_lightbox_timer_only(tmp_path: Path) -> None:
    assert _qapp() is not None
    manager = AvifManager(tmp_path)
    lightbox_timer = QTimer()
    lightbox_timer.start(100)
    main_timer = QTimer()
    main_timer.start(100)
    manager.avif_data[AvifLabelKey.LIGHTBOX]["timer"] = lightbox_timer
    manager.avif_data[AvifLabelKey.LIGHTBOX]["duration_ms"] = 100
    manager.avif_data[AvifLabelKey.LIGHTBOX]["frames"] = [object(), object()]
    manager.avif_data[AvifLabelKey.MAIN]["timer"] = main_timer
    manager.avif_data[AvifLabelKey.MAIN]["duration_ms"] = 100
    manager.avif_data[AvifLabelKey.MAIN]["frames"] = [object(), object()]

    manager.set_animation_speed(AvifLabelKey.LIGHTBOX, 2.0)

    assert lightbox_timer.interval() == 50
    assert main_timer.interval() == 100
    assert manager.is_animation_active(AvifLabelKey.LIGHTBOX)
    manager.set_animation_speed(AvifLabelKey.LIGHTBOX, 0.5)
    assert lightbox_timer.interval() == 200
    lightbox_timer.stop()
    main_timer.stop()


def test_load_exercise_avif_preserves_lightbox_speed(tmp_path: Path) -> None:
    assert _qapp() is not None
    img_dir = tmp_path / "fitness_img"
    _write_test_avif(img_dir / "Walk.avif")
    manager = AvifManager(img_dir)
    manager.avif_data[AvifLabelKey.LIGHTBOX]["speed"] = 2.0
    label = QLabel()
    label.resize(120, 120)
    manager.load_exercise_avif("Walk", label, AvifLabelKey.LIGHTBOX)
    assert manager.avif_data[AvifLabelKey.LIGHTBOX]["speed"] == 2.0
    manager.stop_animation(AvifLabelKey.LIGHTBOX)


def test_load_exercise_avif_main_never_opens_high(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MAIN resolves only the small UI AVIF, never fitness_img/high/."""
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
    manager.load_exercise_avif("Walk", label, AvifLabelKey.MAIN)
    assert high_flags == [False]
    assert lightbox_names == []
    manager.stop_animation(AvifLabelKey.MAIN)


def test_hover_uses_small_when_high_is_also_still(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LIST_HOVER keeps the small file when neither AVIF is animated."""
    assert _qapp() is not None
    img_dir = tmp_path / "fitness_img"
    small = img_dir / "Walk.avif"
    high = img_dir / FITNESS_IMG_HIGH_DIR / "Walk.avif"
    _write_test_avif(small)
    _write_test_avif(high)

    loaded: list[Path] = []

    def spy_async(
        _self: AvifManager,
        avif_path: Path,
        _label_widget: QLabel,
        _data: dict,
        _key: AvifLabelKey,
        _exercise_name: str,
    ) -> None:
        loaded.append(avif_path)

    monkeypatch.setattr(AvifManager, "_load_avif_first_frame_then_async", spy_async)

    manager = AvifManager(img_dir)
    label = QLabel()
    label.resize(120, 120)
    manager.load_exercise_avif("Walk", label, AvifLabelKey.LIST_HOVER)
    assert loaded == [small]
    manager.stop_animation(AvifLabelKey.LIST_HOVER)


def test_hover_uses_high_when_small_is_still_and_high_is_animated(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LIST_HOVER falls back to high when the small UI file is a still."""
    assert _qapp() is not None
    img_dir = tmp_path / "fitness_img"
    small = img_dir / "Walk.avif"
    high = img_dir / FITNESS_IMG_HIGH_DIR / "Walk.avif"
    _write_test_avif(small)
    _write_test_avif(high)

    def fake_animated(path: Path) -> bool:
        return FITNESS_IMG_HIGH_DIR in path.parts

    loaded: list[Path] = []

    def spy_async(
        _self: AvifManager,
        avif_path: Path,
        _label_widget: QLabel,
        _data: dict,
        _key: AvifLabelKey,
        _exercise_name: str,
    ) -> None:
        loaded.append(avif_path)

    monkeypatch.setattr(avif_manager_mod, "_avif_is_animated", fake_animated)
    monkeypatch.setattr(AvifManager, "_load_avif_first_frame_then_async", spy_async)

    manager = AvifManager(img_dir)
    assert manager.get_exercise_hover_avif_path("Walk") == high
    label = QLabel()
    label.resize(120, 120)
    manager.load_exercise_avif("Walk", label, AvifLabelKey.LIST_HOVER)
    assert loaded == [high]
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

"""Tests for the shared app-window lightbox and exercise AVIF overlay."""

from __future__ import annotations

from pathlib import Path

import pillow_avif  # noqa: F401
import pytest
from PIL import Image
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QWidget

from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey, AvifManager
from harrix_swiss_knife.apps.common.widgets.app_window_lightbox import AppWindowLightboxDialog
from harrix_swiss_knife.apps.common.widgets.exercise_avif_lightbox import ExerciseAvifLightboxDialog
from harrix_swiss_knife.apps.icons.lightbox import IconLightboxDialog


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _write_test_avif(path: Path) -> None:
    Image.new("RGB", (64, 48), (120, 80, 40)).save(path, format="AVIF")


def test_icon_lightbox_uses_shared_app_window_chrome() -> None:
    assert issubclass(IconLightboxDialog, AppWindowLightboxDialog)


def test_exercise_avif_lightbox_fits_owner_and_navigates(tmp_path: Path, qapp: QApplication) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Push-ups.avif")
    _write_test_avif(img_dir / "Squats.avif")
    manager = AvifManager(img_dir)
    owner = QWidget()
    owner.resize(640, 480)
    owner.show()
    qapp.processEvents()

    dialog = ExerciseAvifLightboxDialog(
        ["Push-ups", "Squats"],
        avif_manager=manager,
        current_index=0,
        parent=owner,
    )
    assert dialog.parent() is owner
    assert dialog.size() == owner.size()
    assert dialog.current_index == 0

    dialog.show_next()
    assert dialog.current_index == 1
    dialog.show_previous()
    assert dialog.current_index == 0

    dialog.close()
    owner.close()


def test_exercise_avif_lightbox_has_no_speed_slider_by_default(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Walk.avif")
    manager = AvifManager(img_dir)
    dialog = ExerciseAvifLightboxDialog(["Walk"], avif_manager=manager)
    assert dialog._speed_bar is None
    dialog.close()


def test_exercise_avif_lightbox_hides_speed_slider_for_still(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Walk.avif")
    manager = AvifManager(img_dir)
    dialog = ExerciseAvifLightboxDialog(["Walk"], avif_manager=manager, show_speed_slider=True)
    assert dialog._speed_bar is not None
    assert dialog._speed_bar.isHidden()
    dialog.close()


def test_exercise_avif_lightbox_speed_slider_changes_interval(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Walk.avif")
    manager = AvifManager(img_dir)
    dialog = ExerciseAvifLightboxDialog(["Walk"], avif_manager=manager, show_speed_slider=True)
    timer = QTimer()
    timer.start(100)
    manager.avif_data[AvifLabelKey.LIGHTBOX]["timer"] = timer
    manager.avif_data[AvifLabelKey.LIGHTBOX]["duration_ms"] = 100
    manager.avif_data[AvifLabelKey.LIGHTBOX]["frames"] = [object(), object()]
    dialog._sync_speed_controls()
    assert dialog._speed_bar is not None
    assert dialog._speed_slider is not None
    assert not dialog._speed_bar.isHidden()
    dialog._speed_slider.setValue(200)
    assert timer.interval() == 50
    timer.stop()
    dialog.close()


def test_exercise_avif_lightbox_speed_field_enter_does_not_close(tmp_path: Path, qapp: QApplication) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Walk.avif")
    manager = AvifManager(img_dir)
    dialog = ExerciseAvifLightboxDialog(["Walk"], avif_manager=manager, show_speed_slider=True)
    dialog.show()
    qapp.processEvents()
    dialog._begin_speed_edit()
    assert dialog._speed_edit is not None
    assert dialog._speed_ok_button is not None
    assert not dialog._speed_ok_button.isHidden()
    dialog._speed_edit.setText("0.25")
    QTest.keyClick(dialog._speed_edit, Qt.Key.Key_Return)
    qapp.processEvents()
    assert dialog.isVisible()
    assert dialog._speed == 0.25
    dialog._begin_speed_edit()
    dialog._speed_edit.setText("1.5")
    QTest.mouseClick(dialog._speed_ok_button, Qt.MouseButton.LeftButton)
    qapp.processEvents()
    assert dialog.isVisible()
    assert dialog._speed == 1.5
    dialog.close()


def test_icon_lightbox_has_no_animation_speed_slider(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    svg = tmp_path / "icon.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"></svg>', encoding="utf-8")
    dialog = IconLightboxDialog([svg])
    assert getattr(dialog, "_speed_bar", None) is None
    dialog.close()


def test_exercise_avif_lightbox_double_click_closes(tmp_path: Path, qapp: QApplication) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Walk.avif")
    manager = AvifManager(img_dir)
    dialog = ExerciseAvifLightboxDialog(["Walk"], avif_manager=manager)
    dialog.show()
    qapp.processEvents()
    QTest.mouseDClick(dialog._label, Qt.MouseButton.LeftButton)
    qapp.processEvents()
    assert dialog.result() == QDialog.DialogCode.Accepted
    dialog.close()


def test_exercise_avif_lightbox_backdrop_toggle_shows_opposite_color(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Walk.avif")
    manager = AvifManager(img_dir)
    dialog = ExerciseAvifLightboxDialog(["Walk"], avif_manager=manager)
    assert not hasattr(dialog, "_backdrop_button")
    assert dialog._backdrop_color == "white"
    assert dialog._backdrop_toggle_action.text() == "Switch to black backdrop"
    dialog._toggle_backdrop_color()
    assert dialog._backdrop_color == "black"
    assert dialog._backdrop_toggle_action.text() == "Switch to white backdrop"
    dialog.close()


def test_stop_animation_clears_lightbox_slot(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    manager = AvifManager(tmp_path)
    timer = QTimer()
    timer.start(1000)
    manager.avif_data[AvifLabelKey.LIGHTBOX]["timer"] = timer
    manager.avif_data[AvifLabelKey.LIGHTBOX]["exercise"] = "Squats"
    manager.avif_data[AvifLabelKey.LIGHTBOX]["frames"] = [object()]

    manager.stop_animation("lightbox")

    assert not timer.isActive()
    assert manager.avif_data[AvifLabelKey.LIGHTBOX]["timer"] is None
    assert manager.avif_data[AvifLabelKey.LIGHTBOX]["frames"] == []
    assert manager.get_current_exercise(AvifLabelKey.LIGHTBOX) is None
    assert AvifLabelKey.LIGHTBOX in manager.avif_data

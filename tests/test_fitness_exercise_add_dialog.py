"""Tests for Add Exercise local-name check and duplicate warning."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.fitness import exercise_add_dialog as add_dialog_mod
from harrix_swiss_knife.apps.fitness.exercise_add_dialog import ExerciseAddDialog, contains_cyrillic


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_add_dialog_hides_check_button_without_finder(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog()
    assert dialog._local_check_button is None
    dialog.close()


def test_contains_cyrillic() -> None:
    assert contains_cyrillic("Приседания")
    assert contains_cyrillic("Push-ups и присед")
    assert not contains_cyrillic("Push-ups")
    assert not contains_cyrillic("")


def test_exercise_add_dialog_moves_cyrillic_name_to_local(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog()
    dialog._name_edit.setText("Приседания")
    assert dialog._name_edit.text() == ""
    assert dialog._name_local_edit.text() == "Приседания"
    dialog.close()


def test_exercise_add_dialog_keeps_english_name(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog()
    dialog._name_edit.setText("Push-ups")
    assert dialog._name_edit.text() == "Push-ups"
    assert dialog._name_local_edit.text() == ""
    dialog.close()


def test_exercise_add_dialog_does_not_overwrite_existing_local(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog()
    dialog._name_local_edit.setText("Отжимания")
    dialog._name_edit.setText("Приседания")
    assert dialog._name_edit.text() == "Приседания"
    assert dialog._name_local_edit.text() == "Отжимания"
    dialog.close()


def test_exercise_add_dialog_does_not_move_cyrillic_name_when_editing(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog(
        initial={"name": "Приседания", "name_local": "Local name"},
    )
    assert dialog._name_edit.text() == "Приседания"
    assert dialog._name_local_edit.text() == "Local name"
    dialog.close()


def test_check_local_name_marks_unique(qapp: QApplication) -> None:
    assert qapp is not None
    looked_up: list[tuple[str, str]] = []

    def find_duplicate(name: str, name_local: str) -> tuple[str, str] | None:
        looked_up.append((name, name_local))
        return None

    dialog = ExerciseAddDialog(find_duplicate=find_duplicate)
    assert dialog._local_check_button is not None
    dialog._name_local_edit.setText("Отжимания")
    dialog._on_check_local_name()
    assert looked_up == [("", "Отжимания")]
    assert dialog._local_check_passed
    dialog._name_local_edit.setText("Отжимания 2")
    assert not dialog._local_check_passed
    dialog.close()


def test_check_local_name_shows_duplicate(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    assert qapp is not None
    shown: list[tuple[str, str]] = []

    def fake_show(_parent: object, *, name: str, name_local: str, **_kwargs: object) -> None:
        shown.append((name, name_local))

    monkeypatch.setattr(add_dialog_mod, "show_exercise_already_exists", fake_show)

    def find_duplicate(_name: str, _name_local: str) -> tuple[str, str] | None:
        return ("Push-ups", "Отжимания")

    dialog = ExerciseAddDialog(find_duplicate=find_duplicate)
    dialog._name_local_edit.setText("Отжимания")
    dialog._on_check_local_name()
    assert shown == [("Push-ups", "Отжимания")]
    assert not dialog._local_check_passed
    dialog.close()


def test_accept_blocks_duplicate_english_or_local(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    assert qapp is not None
    shown: list[tuple[str, str]] = []

    def fake_show(_parent: object, *, name: str, name_local: str, **_kwargs: object) -> None:
        shown.append((name, name_local))

    monkeypatch.setattr(add_dialog_mod, "show_exercise_already_exists", fake_show)

    def find_duplicate(name: str, name_local: str) -> tuple[str, str] | None:
        if name == "Push-ups" or name_local == "Отжимания":
            return ("Push-ups", "Отжимания")
        return None

    dialog = ExerciseAddDialog(find_duplicate=find_duplicate)
    dialog._name_edit.setText("Push-ups")
    dialog._name_local_edit.setText("Новое")
    dialog._finish_accept()
    assert shown == [("Push-ups", "Отжимания")]
    assert dialog.get_result() is None
    dialog.close()


def test_exercise_add_dialog_accepts_local_and_media_without_english(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    assert qapp is not None
    media_path = tmp_path / "squat.mp4"
    media_path.write_bytes(b"fake")
    dialog = ExerciseAddDialog()
    dialog._name_local_edit.setText("Приседания")
    dialog._media_drop.set_file_path(str(media_path))
    dialog._finish_accept()
    result = dialog.get_result()
    assert result is not None
    assert result[0] == ""
    assert result[4] == "Приседания"
    assert result[6] == str(media_path)
    dialog.close()

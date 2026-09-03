"""Tests for Add Exercise local-name check and duplicate warning."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QCheckBox, QPushButton

from harrix_swiss_knife.apps.fitness import exercise_add_dialog as add_dialog_mod
from harrix_swiss_knife.apps.fitness.exercise_add_dialog import ExerciseAddDialog, contains_cyrillic
from harrix_swiss_knife.apps.fitness.exercise_type_add_dialog import ExerciseTypeAddDialog
from harrix_swiss_knife.apps.fitness.workout_preview_dialog import WorkoutPreviewDialog


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


def test_edit_exercise_dialog_has_no_favorite_checkbox(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog(initial={"name": "Push-ups", "name_local": "Отжимания"})
    labels = [box.text() for box in dialog.findChildren(QCheckBox)]
    assert "Favorite" not in labels
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


def _paste_local_name(dialog: ExerciseAddDialog, text: str) -> None:
    clipboard = QApplication.clipboard()
    assert clipboard is not None
    clipboard.setText(text)
    dialog._name_local_edit.paste()
    QApplication.processEvents()


def test_paste_local_name_checks_unique(qapp: QApplication) -> None:
    assert qapp is not None
    looked_up: list[tuple[str, str]] = []

    def find_duplicate(name: str, name_local: str) -> tuple[str, str] | None:
        looked_up.append((name, name_local))
        return None

    dialog = ExerciseAddDialog(find_duplicate=find_duplicate)
    _paste_local_name(dialog, "Отжимания")
    assert looked_up == [("", "Отжимания")]
    assert dialog._local_check_passed
    dialog.close()


def test_paste_local_name_shows_duplicate(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    assert qapp is not None
    shown: list[tuple[str, str]] = []

    def fake_show(_parent: object, *, name: str, name_local: str, **_kwargs: object) -> None:
        shown.append((name, name_local))

    monkeypatch.setattr(add_dialog_mod, "show_exercise_already_exists", fake_show)

    def find_duplicate(_name: str, _name_local: str) -> tuple[str, str] | None:
        return ("Push-ups", "Отжимания")

    dialog = ExerciseAddDialog(find_duplicate=find_duplicate)
    _paste_local_name(dialog, "Отжимания")
    assert shown == [("Push-ups", "Отжимания")]
    assert not dialog._local_check_passed
    dialog.close()


def test_typing_local_name_does_not_auto_check(qapp: QApplication) -> None:
    assert qapp is not None
    looked_up: list[tuple[str, str]] = []

    def find_duplicate(name: str, name_local: str) -> tuple[str, str] | None:
        looked_up.append((name, name_local))
        return None

    dialog = ExerciseAddDialog(find_duplicate=find_duplicate)
    dialog._name_local_edit.setText("Отжимания")
    assert looked_up == []
    assert not dialog._local_check_passed
    dialog.close()


def test_cyrillic_name_move_checks_local(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    assert qapp is not None
    shown: list[tuple[str, str]] = []

    def fake_show(_parent: object, *, name: str, name_local: str, **_kwargs: object) -> None:
        shown.append((name, name_local))

    monkeypatch.setattr(add_dialog_mod, "show_exercise_already_exists", fake_show)

    def find_duplicate(_name: str, _name_local: str) -> tuple[str, str] | None:
        return ("Squats", "Приседания")

    dialog = ExerciseAddDialog(find_duplicate=find_duplicate)
    dialog._name_edit.setText("Приседания")
    assert dialog._name_local_edit.text() == "Приседания"
    assert shown == [("Squats", "Приседания")]
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
    assert not dialog.add_another()
    dialog.close()


def _dialog_button_texts(dialog: ExerciseAddDialog) -> list[str]:
    return [button.text() for button in dialog.findChildren(QPushButton)]


def test_add_dialog_has_ok_and_add_another_button(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog()
    assert "OK and Add Another" in _dialog_button_texts(dialog)
    dialog.close()


def test_edit_dialog_has_no_ok_and_add_another_button(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog(initial={"name": "Push-ups", "name_local": "Отжимания"})
    assert "OK and Add Another" not in _dialog_button_texts(dialog)
    dialog.close()


def test_ok_does_not_request_another_exercise(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog()
    dialog._name_edit.setText("Push-ups")
    dialog._on_accept()
    assert dialog.get_result() is not None
    assert not dialog.add_another()
    dialog.close()


def test_exercise_add_dialog_capitalizes_names(qapp: QApplication) -> None:
    """OK capitalizes English and local exercise names."""
    assert qapp is not None
    dialog = ExerciseAddDialog()
    dialog._name_edit.setText("push-ups")
    dialog._name_local_edit.setText("отжимания")
    dialog._finish_accept()
    result = dialog.get_result()
    assert result is not None
    assert result[0] == "Push-ups"
    assert result[4] == "Отжимания"
    dialog.close()


def test_exercise_type_add_dialog_capitalizes_names(qapp: QApplication) -> None:
    """Add Exercise Type capitalizes Type and Local."""
    assert qapp is not None
    dialog = ExerciseTypeAddDialog(exercises=["Push-ups"], selected_exercise="Push-ups")
    dialog._type_edit.setText("wide")
    dialog._name_local_edit.setText("широкие")
    dialog._on_accept()
    assert dialog.get_result() == ("Push-ups", "Wide", 1.0, "Широкие")
    dialog.close()


def test_workout_preview_dialog_capitalizes_title(qapp: QApplication) -> None:
    """Workout Name is capitalized when reading the title."""
    assert qapp is not None
    dialog = WorkoutPreviewDialog("morning run", [])
    assert dialog.title_text() == "Morning run"
    dialog.line_title.setText("evening walk")
    assert dialog.title_text() == "Evening walk"
    dialog.close()


def test_ok_and_add_another_requests_another_exercise(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = ExerciseAddDialog()
    dialog._name_edit.setText("Push-ups")
    dialog._on_accept_and_add_another()
    assert dialog.get_result() is not None
    assert dialog.add_another()
    dialog.close()

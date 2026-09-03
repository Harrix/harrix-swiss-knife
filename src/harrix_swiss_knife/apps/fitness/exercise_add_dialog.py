"""Dialog for adding or editing a fitness exercise."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.exercise_media import (
    EXERCISE_MEDIA_EXTENSIONS,
    MEDIA_FILE_FILTER,
    is_exercise_media_path,
)
from harrix_swiss_knife.apps.common.text_case import capitalize_first_letter
from harrix_swiss_knife.apps.common.widgets.file_drop_widget import FileDropWidget
from harrix_swiss_knife.apps.fitness.exercise_ai_fill import (
    request_exercise_fill,
    should_auto_fill_exercise_on_ok,
)
from harrix_swiss_knife.apps.fitness.exercise_duplicate_dialog import show_exercise_already_exists
from harrix_swiss_knife.integrations.bothub import BothubRequestState
from harrix_swiss_knife.qt_emoji_icon import (
    apply_emoji_dialog_buttons,
    create_emoji_icon,
    make_emoji_push_button,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from harrix_swiss_knife.apps.common.avif_manager import AvifManager

_CHECK_EMOJI = "🔎"
_CHECK_OK_EMOJI = "✅"


class ExerciseAddDialog(QDialog):
    """Modal dialog to enter a new exercise or edit an existing one."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
        initial: dict[str, Any] | None = None,
        avif_manager: AvifManager | None = None,
        find_duplicate: Callable[[str, str], tuple[str, str] | None] | None = None,
    ) -> None:
        """Initialize the add/edit exercise dialog.

        Args:

        - `initial` (`dict[str, Any] | None`): Existing exercise fields for edit mode
          (`name`, `unit`, `is_type_required`, `calories_per_unit`, `name_local`).
          Dumbbells is shown only when adding.
        - `avif_manager` (`AvifManager | None`): Loader for the duplicate-name preview.
        - `find_duplicate` (`Callable[[str, str], tuple[str, str] | None] | None`):
          Lookup `(name, name_local)` of an existing exercise.

        """
        super().__init__(parent)
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self._initial = initial or {}
        self._editing = bool(self._initial)
        self._avif_manager = avif_manager
        self._find_duplicate = find_duplicate
        self._local_check_passed = False
        self._result: tuple[str, str, bool, float, str, bool, str, bool] | None = None
        self._add_another = False
        self._moving_cyrillic_name = False

        self.setWindowTitle("Edit Exercise" if self._editing else "Add New Exercise")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        form_group = QGroupBox("Exercise", self)
        form_layout = QVBoxLayout(form_group)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name:", form_group))
        self._name_edit = QLineEdit(form_group)
        self._name_edit.setPlaceholderText("English name")
        self._name_edit.textChanged.connect(self._on_name_changed)
        name_row.addWidget(self._name_edit, 1)
        form_layout.addLayout(name_row)

        name_local_row = QHBoxLayout()
        name_local_row.addWidget(QLabel("Local:", form_group))
        self._name_local_edit = _LocalNameEdit(form_group)
        self._name_local_edit.setPlaceholderText("Local name")
        self._name_local_edit.textChanged.connect(self._on_local_name_changed)
        self._name_local_edit.pasted.connect(self._on_local_name_pasted)
        name_local_row.addWidget(self._name_local_edit, 1)
        self._local_check_button: QPushButton | None = None
        if find_duplicate is not None:
            self._local_check_button = make_emoji_push_button("Check", _CHECK_EMOJI, parent=form_group)
            self._local_check_button.setToolTip("Check whether this local name is already used")
            self._local_check_button.clicked.connect(self._on_check_local_name)
            name_local_row.addWidget(self._local_check_button)
        form_layout.addLayout(name_local_row)

        unit_row = QHBoxLayout()
        unit_row.addWidget(QLabel("Unit:", form_group))
        self._unit_edit = QLineEdit(form_group)
        self._unit_edit.setPlaceholderText("times, kg, m…")
        unit_row.addWidget(self._unit_edit, 1)
        form_layout.addLayout(unit_row)

        calories_row = QHBoxLayout()
        calories_row.addWidget(QLabel("Calories per unit:", form_group))
        self._calories_spin = QDoubleSpinBox(form_group)
        self._calories_spin.setDecimals(1)
        self._calories_spin.setMinimum(0.0)
        self._calories_spin.setMaximum(999.9)
        self._calories_spin.setValue(0.0)
        calories_row.addWidget(self._calories_spin, 1)
        form_layout.addLayout(calories_row)

        self._type_required_check = QCheckBox("Type is required", form_group)
        self._type_required_check.toggled.connect(self._on_type_required_toggled)
        form_layout.addWidget(self._type_required_check)

        self._dumbbells_check: QCheckBox | None = None
        if not self._editing:
            self._dumbbells_check = QCheckBox("Dumbbells", form_group)
            self._dumbbells_check.setToolTip(
                "Add all template dumbbell weight types and mark this exercise with 🏋️",
            )
            self._dumbbells_check.toggled.connect(self._on_dumbbells_toggled)
            form_layout.addWidget(self._dumbbells_check)

        media_hint = (
            "Optional: drag and drop new video/image to replace media"
            if self._editing
            else "Drag and drop video/image (mp4, avif, gif, png, jpeg…)"
        )
        self._media_drop = FileDropWidget(
            form_group,
            name_filter=MEDIA_FILE_FILTER,
            allowed_extensions=EXERCISE_MEDIA_EXTENSIONS,
            hint_text=media_hint,
            dialog_title="Select exercise media",
            path_filter=is_exercise_media_path,
        )
        form_layout.addWidget(self._media_drop)

        layout.addWidget(form_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        self._fill_button = make_emoji_push_button("Fill with AI", "🤖")
        self._fill_button.setToolTip(
            "Fill English/local names, unit, and calories from the entered name or media filename",
        )
        self._fill_button.clicked.connect(self._on_fill_clicked)
        buttons.addButton(self._fill_button, QDialogButtonBox.ButtonRole.ActionRole)
        if not self._editing:
            add_another_button = make_emoji_push_button("OK and Add Another", "➕")  # noqa: RUF001
            add_another_button.setToolTip("Save this exercise and open Add New Exercise again")
            add_another_button.clicked.connect(self._on_accept_and_add_another)
            buttons.addButton(add_another_button, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate_initial()
        self._name_edit.setFocus()

    def add_another(self) -> bool:
        """Return whether the user asked to open another Add dialog after save."""
        return self._add_another

    def get_result(self) -> tuple[str, str, bool, float, str, bool, str, bool] | None:
        """Return `(name, unit, is_type_required, calories, name_local, is_favorite, media_path, with_dumbbells)`."""
        return self._result

    def _check_local_name(self, *, warn_if_empty: bool) -> None:
        """Look up the current local name and mark Check or show the duplicate dialog.

        Args:

        - `warn_if_empty` (`bool`): Show a validation warning when Local is blank.

        """
        if self._find_duplicate is None:
            return
        local_name = capitalize_first_letter(self._name_local_edit.text())
        if not local_name:
            if warn_if_empty:
                message_box.warning(self, "Validation Error", "Enter local name")
            return
        found = self._find_duplicate("", local_name)
        if found is None:
            self._set_local_check_passed(passed=True)
            return
        existing_name, existing_local = found
        show_exercise_already_exists(
            self,
            name=existing_name,
            name_local=existing_local,
            avif_manager=self._avif_manager,
        )
        self._set_local_check_passed(passed=False)

    def _finish_accept(self) -> None:
        name = capitalize_first_letter(self._name_edit.text())
        name_local = capitalize_first_letter(self._name_local_edit.text())
        media_path = self._media_drop.get_file_path()
        can_auto_fill = not self._editing and should_auto_fill_exercise_on_ok(
            name=name,
            name_local=name_local,
            media_path=media_path,
        )
        if not name and not can_auto_fill:
            message = (
                "Enter exercise name"
                if self._editing
                else "Enter English name, or add both local name and media so OK can fill the rest with AI"
            )
            message_box.warning(self, "Validation Error", message)
            return
        if self._show_duplicate_if_needed(name, name_local):
            return
        with_dumbbells = self._dumbbells_check.isChecked() if self._dumbbells_check is not None else False
        self._result = (
            name,
            self._unit_edit.text().strip(),
            with_dumbbells or self._type_required_check.isChecked(),
            self._calories_spin.value(),
            name_local,
            False,
            media_path,
            with_dumbbells,
        )
        self.accept()

    def _move_cyrillic_name_to_local(self, *, check_local: bool = True) -> None:
        """Move a Cyrillic English-name value into Local.

        Args:

        - `check_local` (`bool`): Run the local-name duplicate check after the move.
          Defaults to `True`. Set `False` on OK so accept can show one warning.

        """
        if self._editing or self._moving_cyrillic_name:
            return
        name = self._name_edit.text()
        if not contains_cyrillic(name) or self._name_local_edit.text().strip():
            return
        self._moving_cyrillic_name = True
        try:
            self._name_local_edit.setText(name.strip())
            self._name_edit.clear()
            self._name_local_edit.setFocus()
            self._name_local_edit.setCursorPosition(len(self._name_local_edit.text()))
        finally:
            self._moving_cyrillic_name = False
        if check_local:
            self._check_local_name(warn_if_empty=False)

    def _on_accept(self) -> None:
        self._add_another = False
        self._move_cyrillic_name_to_local(check_local=False)
        self._finish_accept()

    def _on_accept_and_add_another(self) -> None:
        self._add_another = True
        self._move_cyrillic_name_to_local(check_local=False)
        self._finish_accept()

    def _on_check_local_name(self) -> None:
        self._check_local_name(warn_if_empty=True)

    def _on_dumbbells_toggled(self) -> None:
        if self._dumbbells_check is not None and self._dumbbells_check.isChecked():
            self._type_required_check.setChecked(True)

    def _on_fill_clicked(self) -> None:
        request_exercise_fill(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            name_edit=self._name_edit,
            name_local_edit=self._name_local_edit,
            unit_edit=self._unit_edit,
            calories_spin=self._calories_spin,
            fill_button=self._fill_button,
            media_path=self._media_drop.get_file_path(),
        )

    def _on_local_name_changed(self, _text: str = "") -> None:
        if self._local_check_passed:
            self._set_local_check_passed(passed=False)

    def _on_local_name_pasted(self) -> None:
        self._check_local_name(warn_if_empty=False)

    def _on_name_changed(self, _text: str = "") -> None:
        self._move_cyrillic_name_to_local()

    def _on_type_required_toggled(self) -> None:
        if (
            self._dumbbells_check is not None
            and self._dumbbells_check.isChecked()
            and not self._type_required_check.isChecked()
        ):
            self._type_required_check.setChecked(True)

    def _populate_initial(self) -> None:
        if not self._initial:
            return
        self._name_edit.setText(str(self._initial.get("name") or ""))
        self._name_local_edit.setText(str(self._initial.get("name_local") or ""))
        self._unit_edit.setText(str(self._initial.get("unit") or ""))
        try:
            self._calories_spin.setValue(float(self._initial.get("calories_per_unit") or 0.0))
        except (TypeError, ValueError):
            self._calories_spin.setValue(0.0)
        self._type_required_check.setChecked(bool(self._initial.get("is_type_required")))

    def _set_local_check_passed(self, *, passed: bool) -> None:
        self._local_check_passed = passed
        if self._local_check_button is None:
            return
        emoji = _CHECK_OK_EMOJI if passed else _CHECK_EMOJI
        self._local_check_button.setIcon(create_emoji_icon(emoji))
        self._local_check_button.setToolTip(
            "Local name is available" if passed else "Check whether this local name is already used",
        )

    def _show_duplicate_if_needed(self, name: str, name_local: str) -> bool:
        """Show the existing-exercise warning when `name` or `name_local` is taken.

        Args:

        - `name` (`str`): English name to check.
        - `name_local` (`str`): Local name to check.

        Returns:

        - `bool`: `True` when a duplicate was shown and accept should stop.

        """
        if self._find_duplicate is None:
            return False
        found = self._find_duplicate(name, name_local)
        if found is None:
            return False
        existing_name, existing_local = found
        show_exercise_already_exists(
            self,
            name=existing_name,
            name_local=existing_local,
            avif_manager=self._avif_manager,
        )
        return True


class _LocalNameEdit(QLineEdit):
    """Local-name field that reports clipboard paste for an immediate duplicate check."""

    pasted = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the local-name field.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.

        """
        super().__init__(parent)
        self._paste_emit_queued = False

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Insert keys and emit `pasted` after a paste shortcut.

        Args:

        - `event` (`QKeyEvent`): The key event.

        """
        is_paste = event.matches(QKeySequence.StandardKey.Paste)
        super().keyPressEvent(event)
        if is_paste:
            self._queue_pasted()

    def paste(self) -> None:
        """Paste clipboard text and emit `pasted` when the field is not blank."""
        super().paste()
        self._queue_pasted()

    def _emit_pasted(self) -> None:
        self._paste_emit_queued = False
        if self.text().strip():
            self.pasted.emit()

    def _queue_pasted(self) -> None:
        if self._paste_emit_queued or not self.text().strip():
            return
        self._paste_emit_queued = True
        QTimer.singleShot(0, self._emit_pasted)


def contains_cyrillic(text: str) -> bool:
    """Return `True` if `text` includes at least one Cyrillic letter."""
    return any("\u0400" <= character <= "\u04ff" for character in text)

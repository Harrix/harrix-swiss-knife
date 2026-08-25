"""Warning dialog for an exercise name that already exists."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent

    from harrix_swiss_knife.apps.common.avif_manager import AvifManager

_PREVIEW_EDGE = 240


class ExerciseAlreadyExistsDialog(QDialog):
    """Show a duplicate-exercise warning with both names and an AVIF preview."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        name: str,
        name_local: str,
        avif_manager: AvifManager | None = None,
    ) -> None:
        """Build the warning dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `name` (`str`): English name of the existing exercise.
        - `name_local` (`str`): Local name of the existing exercise.
        - `avif_manager` (`AvifManager | None`): Loader for the exercise animation.

        """
        super().__init__(parent)
        self._avif_manager = avif_manager
        self._name = name.strip()
        local = name_local.strip() or "—"

        self.setWindowTitle("Exercise already exists")
        qt_modality.set_owner_window_modal(self)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        warning = QLabel("An exercise with this name already exists.", self)
        warning.setWordWrap(True)
        layout.addWidget(warning)

        self._preview = QLabel(self)
        self._preview.setFixedSize(_PREVIEW_EDGE, _PREVIEW_EDGE)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setStyleSheet("background: #f4f4f4; border-radius: 8px;")
        layout.addWidget(self._preview, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(QLabel(f"English: {self._name or '—'}", self))
        layout.addWidget(QLabel(f"Local: {local}", self))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

        self._load_preview()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop the preview animation when the dialog is closed."""
        self._stop_preview()
        super().closeEvent(event)

    def done(self, result: int) -> None:
        """Stop the preview animation when `exec` finishes."""
        self._stop_preview()
        super().done(result)

    def _load_preview(self) -> None:
        manager = self._avif_manager
        if manager is None or not self._name:
            self._preview.setText("No media")
            return
        if manager.get_exercise_hover_avif_path(self._name) is None:
            self._preview.setText("No media")
            return
        manager.load_exercise_avif(self._name, self._preview, AvifLabelKey.DIALOG_PREVIEW)

    def _stop_preview(self) -> None:
        if self._avif_manager is not None:
            self._avif_manager.stop_animation(AvifLabelKey.DIALOG_PREVIEW)


def show_exercise_already_exists(
    parent: QWidget | None,
    *,
    name: str,
    name_local: str,
    avif_manager: AvifManager | None = None,
) -> None:
    """Show the duplicate-exercise warning with both names and animation.

    Args:

    - `parent` (`QWidget | None`): Parent widget.
    - `name` (`str`): English name of the existing exercise.
    - `name_local` (`str`): Local name of the existing exercise.
    - `avif_manager` (`AvifManager | None`): Loader for the exercise animation.

    """
    dialog = ExerciseAlreadyExistsDialog(
        parent,
        name=name,
        name_local=name_local,
        avif_manager=avif_manager,
    )
    dialog.exec()

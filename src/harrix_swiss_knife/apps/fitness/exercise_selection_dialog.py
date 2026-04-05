"""Modal dialog for picking an exercise from AVIF previews."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, QSize, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QCloseEvent, QIcon

    from harrix_swiss_knife.apps.common.avif_manager import AvifManager


class ExerciseSelectionDialog(QDialog):
    """Modal dialog for selecting an exercise via AVIF previews."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        exercises: list[str],
        icon_provider: Callable[[str], QIcon | None],
        preview_size: QSize,
        current_selection: str | None,
        avif_manager: AvifManager | None = None,
    ) -> None:
        """Initialize the ExerciseSelectionDialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `exercises` (`list[str]`): List of exercise names to display.
        - `icon_provider` (`Callable[[str], QIcon | None]`): Returns an icon for a given exercise name.
        - `preview_size` (`QSize`): Size for icon previews.
        - `current_selection` (`str | None`): Currently selected exercise, if any.
        - `avif_manager` (`AvifManager | None`): AVIF manager for loading animations. Defaults to `None`.

        """
        super().__init__(parent)
        self.setWindowTitle("Select Exercise")
        self.setModal(True)
        self.selected_exercise: str | None = current_selection
        self._icon_provider = icon_provider
        self._avif_manager = avif_manager
        self._preview_size = preview_size
        self._current_hovered_item: QListWidgetItem | None = None
        self._animation_label: QLabel | None = None

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setMovement(QListWidget.Movement.Static)
        self.list_widget.setSpacing(16)
        self.list_widget.setIconSize(preview_size)
        self.list_widget.setWordWrap(True)
        self.list_widget.setUniformItemSizes(False)
        self.list_widget.setMouseTracking(True)
        layout.addWidget(self.list_widget)

        for exercise in exercises:
            item = QListWidgetItem(exercise, self.list_widget)
            item.setData(Qt.ItemDataRole.UserRole, exercise)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)

            icon = self._icon_provider(exercise)
            if icon is not None and not icon.isNull():
                item.setIcon(icon)

            if current_selection and exercise == current_selection:
                self.list_widget.setCurrentItem(item)

        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.itemEntered.connect(self._on_item_entered)
        self.list_widget.installEventFilter(self)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle dialog close event - stop animation."""
        self._stop_animation()
        super().closeEvent(event)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle mouse leave on the list so hover previews stop."""
        if obj == self.list_widget and event.type() == QEvent.Type.Leave:
            self._stop_animation()
            return False

        return super().eventFilter(obj, event)

    def reject(self) -> None:
        """Handle dialog rejection - stop animation."""
        self._stop_animation()
        super().reject()

    def _on_accept(self) -> None:
        if self.list_widget.currentItem() is None and self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
        self._on_selection_changed()

        if self.selected_exercise:
            self.accept()
        else:
            self.reject()

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        self.selected_exercise = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def _on_item_entered(self, item: QListWidgetItem) -> None:
        """Start AVIF animation when the pointer enters a row."""
        if not self._avif_manager:
            return

        exercise_name = item.data(Qt.ItemDataRole.UserRole)
        if not exercise_name:
            return

        if self._current_hovered_item is not None and self._current_hovered_item != item:
            self._stop_animation()

        self._current_hovered_item = item

        item_rect = self.list_widget.visualItemRect(item)
        item_pos = self.list_widget.mapToGlobal(item_rect.topLeft())

        if self._animation_label is None:
            self._animation_label = QLabel(self.list_widget)
            self._animation_label.setScaledContents(False)
            self._animation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._animation_label.setStyleSheet("background-color: transparent;")

        list_pos = self.list_widget.mapFromGlobal(item_pos)
        self._animation_label.setGeometry(
            list_pos.x(),
            list_pos.y(),
            self._preview_size.width(),
            self._preview_size.height(),
        )

        self._avif_manager.load_exercise_avif(exercise_name, self._animation_label, "dialog_preview")

        self._animation_label.show()

    def _on_selection_changed(self) -> None:
        item = self.list_widget.currentItem()
        self.selected_exercise = item.data(Qt.ItemDataRole.UserRole) if item else None

    def _stop_animation(self) -> None:
        """Stop AVIF animation and hide the overlay label."""
        if self._animation_label and self._animation_label.isVisible():
            if self._avif_manager:
                data = self._avif_manager.avif_data.get("dialog_preview")
                if data:
                    timer = data.get("timer")
                    if timer is not None:
                        timer.stop()
                        data["timer"] = None
                    data["frames"] = []
                    data["current_frame"] = 0

            self._animation_label.hide()
            self._current_hovered_item = None

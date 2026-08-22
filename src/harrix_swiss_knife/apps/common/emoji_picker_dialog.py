"""Shared dialog and row for choosing an emoji from a popular grid."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common.emoji_presets import POPULAR_EMOJI_PRESETS
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons

if TYPE_CHECKING:
    from collections.abc import Sequence

_GRID_COLUMNS = 8
_PREVIEW_STYLE = "QLabel { font-size: 28px; border: 1px solid #D1D5DB; border-radius: 8px; background: #F9FAFB; }"
_CELL_STYLE = """
    QPushButton {
        font-size: 20px;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        background: #FFFFFF;
    }
    QPushButton:hover { background: #EFF6FF; border-color: #93C5FD; }
"""


class EmojiChoiceRow(QWidget):
    """Preview button plus Choose that opens `EmojiPickerDialog`."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        current_emoji: str = "",
        presets: Sequence[str] | None = None,
        allow_empty: bool = False,
    ) -> None:
        """Create a compact emoji chooser row.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `current_emoji` (`str`): Initial emoji. Defaults to `""`.
        - `presets` (`Sequence[str] | None`): Grid emojis. Defaults to popular presets.
        - `allow_empty` (`bool`): Allow clearing the emoji. Defaults to `False`.

        """
        super().__init__(parent)
        self._presets = tuple(presets) if presets is not None else POPULAR_EMOJI_PRESETS
        self._allow_empty = allow_empty
        self._emoji = current_emoji.strip()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._preview = QPushButton(self._emoji)
        self._preview.setFixedSize(44, 44)
        self._preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self._preview.setStyleSheet("QPushButton { font-size: 22px; }")
        self._preview.setToolTip("Choose emoji")
        self._preview.clicked.connect(self._choose_emoji)

        choose_button = QPushButton("Choose…")
        choose_button.clicked.connect(self._choose_emoji)

        layout.addWidget(self._preview)
        layout.addWidget(choose_button)
        layout.addStretch(1)

    def emoji(self) -> str:
        """Return the current emoji, possibly empty."""
        return self._emoji

    def set_emoji(self, emoji: str) -> None:
        """Update the preview and stored emoji."""
        self._emoji = emoji.strip()
        self._preview.setText(self._emoji)

    def _choose_emoji(self) -> None:
        dialog = EmojiPickerDialog(
            self,
            current_emoji=self._emoji,
            presets=self._presets,
            allow_empty=self._allow_empty,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.set_emoji(dialog.selected_emoji())


class EmojiPickerDialog(QDialog):
    """Pick an emoji from a preset grid or paste a custom emoji."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        current_emoji: str = "",
        presets: Sequence[str] | None = None,
        allow_empty: bool = False,
        title: str = "Choose emoji",
    ) -> None:
        """Initialize the emoji picker dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `current_emoji` (`str`): Preselected emoji. Defaults to `""`.
        - `presets` (`Sequence[str] | None`): Grid emojis. Defaults to popular presets.
        - `allow_empty` (`bool`): Show Clear and keep an empty selection.
          Defaults to `False`.
        - `title` (`str`): Window title. Defaults to `Choose emoji`.

        """
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle(title)
        self.resize(420, 360)
        self._allow_empty = allow_empty
        self._presets = tuple(presets) if presets is not None else POPULAR_EMOJI_PRESETS
        self._selected = current_emoji.strip()

        root = QVBoxLayout(self)
        root.setSpacing(10)

        preview_row = QHBoxLayout()
        preview_label = QLabel("Selected:")
        self._preview = QLabel(self._selected)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setFixedSize(48, 48)
        self._preview.setStyleSheet(_PREVIEW_STYLE)
        preview_row.addWidget(preview_label)
        preview_row.addWidget(self._preview)
        preview_row.addStretch(1)
        if allow_empty:
            clear_button = QPushButton("Clear")
            clear_button.clicked.connect(lambda: self._select_emoji(""))
            preview_row.addWidget(clear_button)
        root.addLayout(preview_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setSpacing(6)
        for index, emoji in enumerate(self._presets):
            button = QPushButton(emoji)
            button.setFixedSize(40, 40)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(_CELL_STYLE)
            button.clicked.connect(lambda _checked=False, value=emoji: self._select_emoji(value))
            grid.addWidget(button, index // _GRID_COLUMNS, index % _GRID_COLUMNS)
        scroll.setWidget(grid_host)
        root.addWidget(scroll, 1)

        custom_row = QHBoxLayout()
        custom_row.addWidget(QLabel("Or paste emoji:"))
        self._custom_edit = QLineEdit(self._selected)
        self._custom_edit.setMaxLength(16)
        self._custom_edit.setPlaceholderText("Emoji")
        self._custom_edit.textChanged.connect(self._on_custom_changed)
        custom_row.addWidget(self._custom_edit, 1)
        root.addLayout(custom_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def selected_emoji(self) -> str:
        """Return the chosen emoji, possibly empty when `allow_empty` is set."""
        return self._selected.strip()

    def _on_custom_changed(self, text: str) -> None:
        value = text.strip()
        if value:
            self._select_emoji(value, sync_custom=False)
            return
        if self._allow_empty:
            self._select_emoji("", sync_custom=False)

    def _select_emoji(self, emoji: str, *, sync_custom: bool = True) -> None:
        self._selected = emoji.strip()
        self._preview.setText(self._selected)
        if not sync_custom:
            return
        self._custom_edit.blockSignals(True)  # noqa: FBT003
        self._custom_edit.setText(self._selected)
        self._custom_edit.blockSignals(False)  # noqa: FBT003

"""Dialog to add or edit one snippet item."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from harrix_swiss_knife.apps.snippets.constants import ZONE_COLOR, ZONE_SYMBOL
from harrix_swiss_knife.qt_app_font import apply_mono_font
from harrix_swiss_knife.qt_emoji_icon import CANCEL_BUTTON_EMOJI, OK_BUTTON_EMOJI, make_emoji_push_button


class ItemEditDialog(QDialog):
    """Single-item editor with value and optional hint."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str,
        zone: str,
        initial_value: str = "",
        initial_hint: str = "",
    ) -> None:
        """Build the form.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `title` (`str`): Window title.
        - `zone` (`str`): Snippet zone; symbols and colors show a hint field.
        - `initial_value` (`str`): Prefill for the value. Defaults to `""`.
        - `initial_hint` (`str`): Prefill for the hint. Defaults to `""`.

        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self._show_hint = zone in {ZONE_SYMBOL, ZONE_COLOR}
        self._value_edit = QLineEdit(initial_value)
        apply_mono_font(self._value_edit)
        self._hint_edit = QLineEdit(initial_hint)
        apply_mono_font(self._hint_edit)

        form = QFormLayout()
        form.addRow("Value", self._value_edit)
        if self._show_hint:
            self._hint_edit.setPlaceholderText("Example | meaning")
            form.addRow("Hint", self._hint_edit)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = make_emoji_push_button("Cancel", CANCEL_BUTTON_EMOJI)
        ok = make_emoji_push_button("OK", OK_BUTTON_EMOJI)
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(ok)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)
        self.resize(480, 140 if self._show_hint else 110)
        self._value_edit.setFocus()

    def values(self) -> tuple[str, str]:
        """Return `(value, hint)` after accept."""
        hint = self._hint_edit.text().strip() if self._show_hint else ""
        return self._value_edit.text().strip(), hint

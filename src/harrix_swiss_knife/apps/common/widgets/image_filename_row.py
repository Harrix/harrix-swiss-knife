"""Shared filename row UI for image drop widgets in template dialogs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QComboBox, QDateEdit, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import slugify_image_filename_base

if TYPE_CHECKING:
    from PySide6.QtCore import QDate


_HINT_STYLE = "font-size: 11px; color: #888; border: none; background: transparent;"


class ImageFilenameRow(QWidget):
    """Filename input row with hint and optional auto-sync from date / linked field."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        multiple: bool,
        date_edit: QDateEdit | None,
        source_widget: QLineEdit | QComboBox | None = None,
        source_field_name: str | None = None,
        initial_base: str | None = None,
        lock_auto_sync: bool = False,
    ) -> None:
        """Build filename row widgets."""
        super().__init__(parent)
        self.line_edit = QLineEdit()
        label_text = "Filename base:" if multiple else "Filename:"
        self.line_edit.setPlaceholderText(
            "Base name (e.g. date); images will be named base_01, base_02, ..."
            if multiple
            else "Filename (without extension)"
        )

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(QLabel(label_text))
        row.addWidget(self.line_edit, 1)

        hint = QLabel(build_image_filename_hint(multiple=multiple, source_field_name=source_field_name))
        hint.setWordWrap(True)
        hint.setStyleSheet(_HINT_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addLayout(row)
        layout.addWidget(hint)

        self._date_edit = date_edit
        self._source_widget = source_widget
        self._lock_auto_sync = lock_auto_sync
        self._manual_edit = False

        if initial_base:
            self.line_edit.setText(initial_base)
        elif not lock_auto_sync:
            self._apply_auto_base()

        if not lock_auto_sync:
            self.line_edit.textEdited.connect(self._on_manual_edit)
            if date_edit is not None:
                date_edit.dateChanged.connect(self._on_date_changed)
            if source_widget is not None:
                if isinstance(source_widget, QComboBox):
                    source_widget.currentTextChanged.connect(self._on_source_changed)
                else:
                    source_widget.textChanged.connect(self._on_source_changed)

    def _apply_auto_base(self) -> None:
        if self._lock_auto_sync or self._manual_edit:
            return
        base = compute_image_filename_base(date_edit=self._date_edit, source_widget=self._source_widget)
        if base:
            self.line_edit.setText(base)

    def _on_date_changed(self, _date: QDate) -> None:
        self._apply_auto_base()

    def _on_manual_edit(self, _text: str) -> None:
        self._manual_edit = True

    def _on_source_changed(self, _text: str) -> None:
        self._apply_auto_base()


def build_image_filename_hint(*, multiple: bool, source_field_name: str | None) -> str:
    """Return helper text shown below the filename input."""
    if multiple:
        prefix = "Base name for images saved to img/. Files are named base_01, base_02, …"
    else:
        prefix = "Filename for the image saved to img/ (without extension)."
    if source_field_name:
        return (
            f"{prefix} Default is the date; when {source_field_name} is filled, "
            f"it is replaced by a slug from that field."
        )
    return f"{prefix} Default is the date."


def compute_image_filename_base(
    *,
    date_edit: QDateEdit | None,
    source_widget: QLineEdit | QComboBox | None,
) -> str:
    """Compute filename base from linked source field or date."""
    source_text = _widget_text(source_widget)
    if source_text:
        slug = slugify_image_filename_base(source_text)
        if slug:
            return slug
    if date_edit is not None:
        return date_edit.date().toString("yyyy-MM-dd")
    return ""


def _widget_text(widget: QLineEdit | QComboBox | None) -> str:
    if widget is None:
        return ""
    if isinstance(widget, QComboBox):
        return widget.currentText().strip()
    return widget.text().strip()
